"""Fresh full invariant rings for source140/243, using the pinned finvar library."""
from pathlib import Path
import re
import shutil
import subprocess
import hashlib
from sage.all import QQ, matrix
from sage.env import SINGULAR_BIN
from common import require, closure

RELATIONS = {
    140: ['252*u3^2+11*u1^3*u4-11*u1^3*u5+11*u2^3*u5-10*u4*u5+10*u5^2+9*u3*u6-u6^2',
          '112*u1^3*u2^3-45*u1^3*u4+45*u1^3*u5-45*u2^3*u5+18*u4*u5-18*u5^2+9*u3*u6-u6^2'],
    243: ['22*u2^3*u3-9*u3*u4-u5^2',
          '22*u1^2*u2^3-11*u1^2*u4+8*u3*u4-4*u5^2+33*u6^2']}
WEIGHTS = {140: [2,2,6,6,6,6], 243: [2,2,4,6,5,5]}


def marker_values(text, marker, count=1):
    lines = text.splitlines()
    positions = [i for i,s in enumerate(lines) if s.strip() == marker]
    require(len(positions) == 1, 'Missing/duplicate Singular marker: '+marker)
    values = []
    for line in lines[positions[0]+1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            continue
        require(re.fullmatch(r'-?\d+', stripped) is not None,
                'Invalid numeric output after '+marker+': '+stripped)
        values.append(int(stripped))
        if len(values) == count:
            return values
    raise AssertionError('Truncated Singular output: '+marker)


def check_protocol(text, source_case):
    require(not re.search(r'^\s*\?', text, re.M), 'Singular reported an error')
    wanted = {'INDEX':source_case, 'EXPLICIT_GENERATORS_MATCH_FINVAR':1,
              'DISPLAYED_RELATIONS_SUBSTITUTE_TO_ZERO':1,
              'NUMBER_OF_INVARIANT_GENERATORS':6, 'NUMBER_OF_MINIMAL_RELATIONS':2,
              'QUOTIENT_DIMENSION':4, 'EMBEDDING_DIMENSION_AT_ORIGIN':6,
              'MINIMAL_EMBEDDING_PASS':1, 'INVARIANT_AUDIT_PASS':1,
              'PRINTED_RELATIONS_IN_FULL_KERNEL':1,
              'FULL_KERNEL_IN_PRINTED_RELATIONS':1, 'DHZ_COMPLETE':1}
    for key, value in wanted.items():
        require(marker_values(text,key) == [value], 'Failed Singular check: '+key)
    require(marker_values(text,'GENERATOR_DEGREES',6) == WEIGHTS[source_case],
            'Invariant-generator order/degrees changed')
    relation_degree = 12 if source_case == 140 else 10
    require(marker_values(text,'MINIMAL_RELATION_DEGREES',2) == [relation_degree]*2,
            'Relation degrees changed')
    require(all(k >= 2 for k in marker_values(text,'MINIMAL_RELATION_M_ADIC_ORDERS',2)),
            'Linear relation contradicts minimal embedding')
    return wanted


def run(source_case, record, here, out):
    original = here/'singular'/f'invariants_{source_case}.sing'
    script = original.read_text()
    matrices = []
    for label, raw in re.findall(r'matrix A(\d+)\[4\]\[4\]=(.*?);',script,re.S):
        matrices.append((int(label),matrix(QQ,4,4,[QQ(x.strip()) for x in raw.split(',')])))
    matrices = [m for _,m in sorted(matrices)]
    actual = [matrix(QQ,m) for m in record['actual_generators']]
    require(matrices == actual, 'Singular matrices differ from the actual catalogue')
    require(all(m.det() == 1 for m in actual), 'Non-special-linear generator')
    group = closure(actual,record['order'])
    work = out/'singular'
    (work/'singular/vendor').mkdir(parents=True)
    vendor = here/'singular/vendor/finvar.lib'
    shutil.copy2(vendor,work/'singular/vendor/finvar.lib')
    printed = [re.sub(r'u(\d+)',lambda m:'var('+m.group(1)+')',p)
               for p in RELATIONS[source_case]]
    extra = '\nideal printedIdeal='+','.join(printed)+';\n'
    extra += '"PRINTED_RELATIONS_IN_FULL_KERNEL";size(simplify(reduce(printedIdeal,std(G)),2))==0;\n'
    extra += '"FULL_KERNEL_IN_PRINTED_RELATIONS";size(simplify(reduce(G,std(printedIdeal)),2))==0;\n'
    extra += '"DHZ_COMPLETE";1;\nquit;\n'
    require(script.count('quit;') == 1, 'Unexpected Singular source ending')
    generated = work/'verify.sing'
    generated.write_text(script.replace('quit;',extra))
    log = out/'singular.log'
    with log.open('w') as handle:
        result = subprocess.run([str(SINGULAR_BIN),'-q',generated.name],cwd=work,
                                stdout=handle,stderr=subprocess.STDOUT,check=False)
    require(result.returncode == 0, 'Singular process failed')
    text = log.read_text()
    checks = check_protocol(text,source_case)
    return {'method':'Pinned finvar full invariant generation, full relation kernel, both printed-ideal inclusions',
            'actual_catalogue_binding':True,'actual_group_order':len(group),
            'full_invariant_ring':True,'complete_relation_kernel':True,
            'complete_intersection':True,'minimal_embedding':True,
            'embedding_dimension':6,'dimension':4,'generator_degrees':WEIGHTS[source_case],
            'relations':RELATIONS[source_case], 'relation_degrees':[12 if source_case==140 else 10]*2,
            'singular_checks':checks,'singular_executable':str(SINGULAR_BIN),
            'finvar_sha256':hashlib.sha256(vendor.read_bytes()).hexdigest(),
            'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
