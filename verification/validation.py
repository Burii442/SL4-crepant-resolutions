"""Validate completed legacy calculations; never infer success from exit zero.

This checks certificates and their binding to one isolated legacy invocation.
It does not rerun algebra or replace the mathematical proofs in the paper.
The caller must freeze inputs and retain the returned file hashes for resume.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path


COX_CASES = (114, 138, 140, 143, 151, 161, 167, 171, 173, 174, 177,
             178, 179, 194, 206, 221, 222, 227, 231, 233, 243)
COMMON = ('criteria', 'criteria-geometry', 'catalogue', 'representatives',
          'geometry', 'cox-models', 'geometry-132',
          'geometry-234', 'geometry-236')
GEOMETRY = {
    132: [('verify_132_resolution.py', '"result": "PASS"')],
    234: [('validate_inputs.py', 'DISCRIMINANT_AND_CONTRACTED_CHART_INPUTS_PASS'),
          ('validate234_geometry.py', 'PASS_GEOMETRIC_YES_234_235'),
          ('root_audit234.py', 'PASS_INDEPENDENT_INPUT_BINDING_AND_LOCAL_GEOMETRY')],
    236: [('validate_inputs.py', 'DISCRIMINANT_AND_CONTRACTED_CHART_INPUTS_PASS'),
          ('validate236_geometry.py', 'PASS_GEOMETRIC_YES_236_237'),
          ('root_audit236.py', 'PASS_INDEPENDENT_236_INPUT_CENTERS_REES_AND_COVER')],
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _product(a, b):
    a, b = list(map(Fraction, a)), list(map(Fraction, b))
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def validate_legacy(result_dir, expected_steps):
    """Return PASS plus SHA256s of checked files, or raise ValueError.

    expected_steps is an ordered iterable. A Cox step must be preceded by its
    binding in the same invocation; endpoint-only historical runs are rejected
    when presented as a complete Cox bundle. Paths in the returned ``files``
    mapping are relative to result_dir and may be rehashed on resume.
    """
    try:
        return _validate_legacy(Path(result_dir).resolve(), list(expected_steps))
    except ValueError:
        raise
    except (OSError, KeyError, TypeError, IndexError, AttributeError, ZeroDivisionError) as error:
        raise ValueError(f'Malformed or incomplete legacy result: {error}') from error


def _validate_legacy(root, expected):
    files = {}

    def read(relative):
        path = (root/relative).resolve()
        _require(root in path.parents and path.is_file(), f'Missing/unsafe result file: {relative}')
        data = path.read_bytes()
        files[str(path.relative_to(root))] = hashlib.sha256(data).hexdigest()
        return data

    def load(relative):
        return json.loads(read(relative))

    def log(relative, digest=None, marker=None):
        value = read(relative).decode('utf-8')
        key = str((root/relative).resolve().relative_to(root))
        if digest is not None:
            _require(files[key] == digest, f'Log hash mismatch: {relative}')
        if marker is not None:
            _require(marker in value, f'Missing completion marker in {relative}: {marker}')
        return value

    allowed = set(COMMON) | {f'{kind}-{n}' for n in COX_CASES
                                for kind in ('binding', 'cox', 'endpoint')}
    _require(expected and len(expected) == len(set(expected)), 'Expected steps must be nonempty and unique')
    _require(set(expected) <= allowed, 'Unknown expected legacy step')
    report = load('verification.json')
    _require(report.get('status') == 'PASS', 'Legacy invocation did not PASS')
    _require(report.get('selected_steps') == expected, 'Legacy selected_steps differ from the requested ordered steps')
    steps = report.get('steps')
    _require(isinstance(steps, list) and [s.get('name') for s in steps] == expected,
             'Missing, extra, reordered or duplicate completed steps')
    manifest = load('input_manifest.json')
    _require(isinstance(manifest, dict) and manifest, 'Empty input manifest')
    manifest_sha = files['input_manifest.json']
    _require(report.get('input_manifest_sha256') == manifest_sha, 'Input manifest hash mismatch')
    _require(report.get('input_files') == len(manifest), 'Input manifest file count mismatch')

    def bind(hashes, prefix=''):
        _require(isinstance(hashes, dict) and hashes, 'Missing input hashes in certificate')
        for key, digest in hashes.items():
            _require(manifest.get(prefix+key) == digest, f'Certificate input does not match frozen manifest: {prefix+key}')

    def source(relative):
        value = load('supplement/'+relative)
        _require(files['supplement/'+relative] == manifest.get(relative), f'Changed copied input: {relative}')
        return value

    catalogue = source('catalogue.json')
    _require([r['index'] for r in catalogue] == list(range(1, 246)), 'Wrong legacy catalogue indices')
    step_by_name = dict(zip(expected, steps))
    ordinary = report.get('ordinary_generation', {})
    _require(isinstance(ordinary, dict), 'Malformed ordinary_generation')

    for step in steps:
        name = step['name']
        target = 'steps/'+name+'/'
        _require(step.get('status') == 'PASS' and step.get('returncode') == 0,
                 f'{name}: incomplete or unsuccessful subprocess')
        _require(step.get('input_manifest_sha256') == manifest_sha, f'{name}: inconsistent input manifest')
        _require(step.get('log') == target+'stdout.log', f'{name}: unexpected log path')
        _require(isinstance(step.get('log_sha256'), str), f'{name}: missing log hash')
        output = log(step['log'], step['log_sha256'])

        if name == 'criteria':
            proof = load('supplement/criteria_verification.json')
            _require(proof.get('cases') == 245 and proof.get('all_cases_covered') is True,
                     'Incomplete criterion coverage')
            _require(proof.get('decisions') == {'YES': 182, 'NO': 63}
                     and proof.get('criteria') == sorted('ABCDEGHIUZ'), 'Incorrect criterion totals/families')
        elif name == 'catalogue':
            proof = load(target+'catalogue.json')
            summary, rows = proof['summary'], proof['cases']
            _require(summary.get('status') == 'PASS' and summary.get('groups_reconstructed') == 245,
                     'Catalogue reconstruction incomplete')
            _require([r['index'] for r in rows] == list(range(1, 246)), 'Catalogue output indices incomplete')
            _require(summary.get('decision_labels') == {'YES': 182, 'NO': 63}, 'Wrong catalogue decision totals')
            _require(summary.get('catalogue_sha256') == manifest['catalogue.json']
                     and summary.get('criteria_sha256') == manifest['criteria_incidence.csv'], 'Catalogue input binding mismatch')
            _require(summary.get('group_elements') == sum(r['order'] for r in rows), 'Wrong total group elements')
            for row, original in zip(rows, catalogue):
                _require(all(row.get(k) == original[k] for k in ('order', 'junior_classes', 'age2_classes')),
                         f'Catalogue numeric mismatch: {row["index"]}')
        elif name == 'representatives':
            proof = load(target+'representatives.json')
            _require(proof.get('status') == 'PASS' and proof.get('transfers') == 73
                     and len(proof.get('records', [])) == 73, 'Incomplete representative transfers')
            _require(proof.get('catalogue_sha256') == manifest['catalogue.json']
                     and proof.get('witnesses_sha256') == manifest['representative_conjugacies.json'],
                     'Representative input binding mismatch')
            expected_transfers = {r['index']: r['representative'] for r in catalogue if r['index'] != r['representative']}
            _require({r['index']: r['representative'] for r in proof['records']} == expected_transfers,
                     'Representative transfers omitted or substituted cases')
        elif name == 'geometry':
            proof = load('supplement/geometry_verification.json')
            rings = proof.get('invariant_rings', [])
            _require(proof.get('toric_fans') == 46 and proof.get('tetrahedra') == 337
                     and sorted(r['index'] for r in rings) == [72, 85, 91, 107, 127, 145, 190, 204, 219, 224, 241, 245],
                     'Incomplete rings/fans')
            _require(all(all(r.get(k) is True for k in ('invariant_ring', 'full_kernel', 'molien_hilbert'))
                         for r in rings), 'Incomplete invariant-ring proof')
        elif name == 'cox-models':
            proof = load('supplement/cox_model_checks.json')
            _require(sorted(r['case'] for r in proof) == list(COX_CASES), 'Cox model checks omitted cases')
            for row in proof:
                _require(row.get('raw_valuation_binding') == row.get('primitive_grading_and_homogeneity') == 'PASS'
                         and row.get('modular_image_consistency', {}).get('result') == 'PASS'
                         and row['modular_image_consistency'].get('evaluation_points') == 3,
                         'Cox model consistency checks incomplete')
        elif name == 'criteria-geometry':
            proof = load(target+'result/report.json')
            _require(proof.get('status') == 'ALL_CRITERIA_GEOMETRY_CHECKS_PASS' and proof.get('complete') is True,
                     'Incomplete criteria geometry')
            bind(proof['input_sha256'])
            checks = [('cotangent', 'ALL_26_ACTUAL_COTANGENT_REFLECTION_HYPOTHESES_PASS'),
                      ('representations', 'ACTUAL_REPRESENTATION_BINDINGS_I_H_D_POSITIVE_PASS'),
                      ('toric', 'FULL_COHERENT_UNIMODULAR_EQUIVARIANT_FAN_AND_NO_ISOLATED_FIXED_POINTS_PASS'),
                      ('towers', 'ALL_8_TOWERS_RECHECKED')]
            _require([s.get('name') for s in proof.get('steps', [])] == [n for n, _ in checks],
                     'Missing criteria geometry substeps')
            for child, (n, marker) in zip(proof['steps'], checks):
                _require(child.get('status') == 'PASS' and child.get('returncode') == 0, f'Incomplete {n} check')
                log(target+'result/'+n+'.log', child['log_sha256'], marker)
        elif name.startswith('geometry-'):
            number = int(name.split('-')[1])
            proof = load(target+'result/run.json')
            _require(proof.get('status') == 'PASS' and proof.get('case') == number, f'{name}: incomplete geometry')
            bind(proof['inputs'])
            _require([s.get('script') for s in proof.get('steps', [])] == [s for s, _ in GEOMETRY[number]],
                     f'{name}: omitted detailed stages')
            for child, (_, marker) in zip(proof['steps'], GEOMETRY[number]):
                _require(child.get('status') == 'PASS' and child.get('returncode') == 0, f'{name}: failed detailed stage')
                log(target+'result/'+child['log'], child['log_sha256'], marker)
            _require(f'GEOMETRY_{number}_ALL_FRESH_CHECKS_PASS' in output, f'{name}: missing final marker')
        elif name.startswith('binding-'):
            number = int(name.split('-')[1])
            proof = load(target+'binding.json')
            _require(proof.get('status') == 'PASS' and proof.get('case') == number
                     and proof.get('all_junior_classes_covered') is True, f'{name}: incomplete group/junior binding')
            bind(proof['inputs'])
            _require(proof.get('group_order') == catalogue[number-1]['order'], f'{name}: wrong group order')
        elif name.startswith('cox-'):
            number = int(name.split('-')[1])
            binding_name = f'binding-{number}'
            _require(binding_name in expected and expected.index(binding_name) < expected.index(name),
                     f'{name}: binding must occur earlier in the same invocation')
            _require(ordinary.get(str(number)) is True and
                     step.get('ordinary_invariant_generation', {}).get('passed') is True,
                     f'{name}: ordinary invariant generation was not certified')
            if number == 194:
                proof = load(target+'result/certificate.json')
                _require(proof.get('status') == 'ALL_PAPER83_CHECKS_PASS' and proof.get('case') == 194,
                         'Dedicated case194 proof incomplete')
                _require(proof.get('sections') == ['group', 'algebra', 'charts', 'cover'],
                         'Dedicated case194 proof omitted sections')
                _require(proof.get('literal_catalogue_generators_checked') == [194, 195, 196, 197],
                         'Dedicated case194 proof omitted literal catalogue bindings')
                _require(proof['input_sha256'].get('catalogue.json') == manifest['catalogue.json'],
                         'Dedicated case194 catalogue hash mismatch')
                for filename in ('paper_charts83.json', 'paper_invariants83.json', 'paper_model83.json', 'verify194.py'):
                    _require(proof['input_sha256'].get(filename) == manifest.get('194/'+filename),
                             f'Dedicated case194 input mismatch: {filename}')
                _require('ALL_PAPER83_CHECKS_PASS' in output, 'Dedicated case194 completion marker missing')
            else:
                proof = load(target+'result/report.json')
                model = source(f'{number}/model.json')
                _require(proof.get('case') == number and proof.get('stage') == 'all'
                         and proof.get('complete_simultaneous_criterion') is True
                         and proof.get('public_presentation_equals_full_kernel') is True
                         and proof.get('completed_juniors') == list(range(1, model['junior_count']+1)),
                         f'{name}: incomplete full Cox reconstruction')
                binding = load(f'steps/{binding_name}/binding.json')
                hilbert = load(target+'result/base_hilbert.json')
                _require(hilbert.get('ordinary_kernel_complete') is True
                         and hilbert.get('ordinary_kernel_characteristic') == 0, f'{name}: incomplete ordinary kernel')
                for filename in (f'{number}/model.json', f'{number}/invariants.json'):
                    _require(proof['input_hashes'].get(filename) == hilbert['input_hashes'].get(filename)
                             == binding['inputs'].get(filename) == manifest.get(filename),
                             f'{name}: binding/Hilbert/Cox inputs differ')
                _require(any(map(Fraction, hilbert['denominator'])) and any(map(Fraction, binding['molien_denominator'])),
                         f'{name}: zero Hilbert/Molien denominator')
                _require(_product(hilbert['numerator'], binding['molien_denominator']) ==
                         _product(binding['molien_numerator'], hilbert['denominator']),
                         f'{name}: exact Hilbert/Molien series mismatch')
        elif name.startswith('endpoint-'):
            number = int(name.split('-')[1])
            _require(f'cox-{number}' in expected and expected.index(f'cox-{number}') < expected.index(name),
                     f'{name}: full Cox stage must precede the endpoint in this invocation')
            proof = load(target+'result/report.json')
            _require(proof.get('status') == 'ALL_REQUESTED_ENDPOINT_CHECKS_PASS'
                     and proof.get('complete') is True and proof.get('requested_cases') == [number]
                     and len(proof.get('results', [])) == 1, f'{name}: incomplete endpoint report')
            endpoint = proof['results'][0]
            _require(endpoint.get('case') == number and endpoint.get('status') == 'PASS'
                     and endpoint.get('complete') is True, f'{name}: wrong/incomplete endpoint')
            bind(endpoint['input_and_verifier_sha256'])

    return {'status': 'PASS', 'selected_steps': expected, 'files': dict(sorted(files.items())),
            'ordinary_generation': {str(n): True for n in COX_CASES if f'cox-{n}' in expected},
            'scope': 'Validated exact requested legacy certificates, log hashes, input bindings and Cox generation prerequisites; algebra was not rerun by this validator.'}
