"""Characteristic-zero ordinary kernel certificate via modular dimension bounds.

Every mathematical hypothesis is computed afresh; no previous status flag is
accepted as an input. The modular quotient supplies an upper bound, while
exact invariance and the Noether rank certificate supply the matching lower
bound. Exact polynomial identities connect the relation ideal to the map.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,time

def verify_ordinary(case, U, X, forms, output, emit):
    from sage.all import QQ,PolynomialRing
    root=Path(__file__).resolve().parent.parent
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    binding_file=root/'binding_verification/verify_binding.py'
    spec=importlib.util.spec_from_file_location('ordinary_actual_binding',binding_file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    emit('ORDINARY_CERTIFICATE_ACTUAL_BINDING_START')
    binding=module.verify_case(case,output/'binding.json')
    assert binding['status']=='PASS'
    emit('ORDINARY_CERTIFICATE_ACTUAL_BINDING_COMPLETE')
    generator_file=root/'full_verification/verify_generation.py'
    args=[sys.executable,str(generator_file),'--case',str(case),'--kernel-hilbert','--output-dir',str(output/'generation')]
    with (output/'generation.log').open('w') as stream:
        process=subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT)
    assert process.returncode==0,'The fresh modular generation/Hilbert computation failed; inspect generation.log.'
    proof=json.loads((output/'generation/generation_report.json').read_text())
    assert proof['complete'] and all(r['equals'] for r in proof['degrees'])
    assert proof['noether_bound']==binding['derived_order']
    assert len(proof['degrees'])==proof['generation_degree_bound']
    T=PolynomialRing(QQ,'t')
    def series(data,prefix=''):
        return T([QQ(c) for c in data[prefix+'numerator']])/T([QQ(c) for c in data[prefix+'denominator']])
    expected=series(binding,'molien_')
    assert expected==series(proof,'molien_')==series(proof['ordinary_relation_hilbert'])
    a=json.loads((root/str(case)/'invariants.json').read_text())
    # Parse rational presentations over QQ for substantially faster exact
    # sparse polynomial arithmetic, then use the canonical map into X.
    rational=all('zeta' not in f for f in a['base_relations'])
    C=PolynomialRing(QQ if rational else X.base_ring(),list(U.variable_names()))
    relations=[C(f) for f in a['base_relations']]
    physical_rational=all(c in QQ for f in forms for c in f.coefficients())
    if rational and physical_rational:
        exact_target=PolynomialRing(QQ,list(X.variable_names()))
        exact_forms=[exact_target({tuple(e):QQ(c) for e,c in f.dict().items()}) for f in forms]
    else:exact_target=X;exact_forms=forms
    phi=C.hom(exact_forms,exact_target)
    emit('ORDINARY_EXACT_DEFINING_IDENTITIES_START',relations=len(relations))
    for j,f in enumerate(relations,1):
        assert phi(f)==0,('Ordinary relation has a nonzero physical image',case,j)
        if j%16==0 or j==len(relations):emit('ORDINARY_EXACT_DEFINING_IDENTITIES_PROGRESS',checked=j,total=len(relations))
    result=dict(case=int(case),ordinary_kernel_complete=True,
        ordinary_invariant_generation_proved=True,ordinary_kernel_characteristic=0,
        proof_method='Exact actual-group binding and invariance, all product ranks through the Noether or proved parameter/Reynolds bound, exact relation identities, and a matching modular Hilbert upper bound.',
        base_relations=len(relations),prime=proof['prime'],noether_bound=proof['noether_bound'],generation_degree_bound=proof['generation_degree_bound'],parameter_certificate=proof['parameter_certificate'],
        numerator=binding['molien_numerator'],denominator=binding['molien_denominator'],
        inputs=binding['inputs'])
    (output/'ordinary_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    emit('ORDINARY_INVARIANT_GENERATION_AND_FULL_KERNEL_PROVED',relations=len(relations),noether_bound=proof['noether_bound'])
    return U.ideal([U(f) for f in relations]),result
