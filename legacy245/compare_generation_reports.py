#!/usr/bin/env python3
"""Join explicitly selected fresh binding and Cox runs without repeating them.

This checks consistency and the exact Molien/Hilbert equality. It is not a
replacement for executing the mathematical validators. Both isolated input
snapshots must be supplied, so their actual bytes can be checked against each
certificate. Historical reports without matching snapshots are not accepted.
"""
import argparse,hashlib,json,re
from functools import lru_cache
from pathlib import Path
from run_verification import same_rational_series

def require(condition,message):
    if not condition:raise ValueError(message)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
@lru_cache(maxsize=None)
def snapshot_programs(snapshot):
    return {str(p.relative_to(snapshot)):digest(p) for p in sorted(snapshot.rglob('*'))
            if p.is_file() and p.suffix in {'.py','.sage','.g','.sing','.lib'}}
def checked_inputs(values,snapshot):
    checked={}
    for name,value in values.items():
        if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value):continue
        path=(snapshot/name).resolve()
        require(snapshot in path.parents,'Input path escapes the isolated snapshot')
        require(path.is_file(),f'Missing snapshot input: {name}')
        require(digest(path)==value,f'Snapshot bytes differ from the certificate: {name}')
        checked[name]=value
    require(checked,'Certificate contains no input file hashes')
    return checked

def compare(entry):
    case=int(entry['case'])
    require(case!=194,'Case 194 uses its dedicated paper83 generation certificate')
    binding_path=Path(entry['binding_report']).resolve()
    cox_dir=Path(entry['cox_directory']).resolve()
    binding_snapshot=Path(entry['binding_snapshot']).resolve()
    cox_snapshot=Path(entry['cox_snapshot']).resolve()
    binding=read(binding_path);proof=read(cox_dir/'report.json');hilbert=read(cox_dir/'base_hilbert.json')
    require(binding.get('case')==proof.get('case')==hilbert.get('case')==case,'Mismatched cases')
    require(binding.get('status')=='PASS' and binding.get('all_junior_classes_covered') is True,'Incomplete representation binding')
    require(proof.get('complete_simultaneous_criterion') is True and proof.get('public_presentation_equals_full_kernel') is True,'Incomplete Cox criterion')
    require(proof.get('stage')=='all','Only a complete Cox stage can be joined')
    require(hilbert.get('ordinary_kernel_complete') is True and hilbert.get('ordinary_kernel_characteristic')==0,'No complete characteristic-zero ordinary kernel')
    require(proof['input_hashes']==hilbert['input_hashes'],'Cox and Hilbert reports have different inputs')
    bh=checked_inputs(binding['inputs'],binding_snapshot)
    ch=checked_inputs(proof['input_hashes'],cox_snapshot)
    required=[f'{case}/model.json',f'{case}/invariants.json']
    require('catalogue.json' in bh,'Binding certificate does not identify its catalogue')
    require(digest(cox_snapshot/'catalogue.json')==bh['catalogue.json'],'The two snapshots use different catalogues')
    for name in required:
        require(name in bh and name in ch and bh[name]==ch[name],f'Mathematical input differs: {name}')
    for name in set(bh)&set(ch):
        if name.endswith('.json'):require(bh[name]==ch[name],f'Common mathematical witness differs: {name}')
    invariants=read(cox_snapshot/f'{case}/invariants.json')
    juniors=len(invariants['junior_orders'])
    require(proof['completed_juniors']==list(range(1,juniors+1)),'Not every junior test was completed')
    require(binding.get('valuations_checked')==len(invariants['generator_polynomials'])*juniors,'Incomplete valuation coverage')
    require(same_rational_series(hilbert['numerator'],hilbert['denominator'],binding['molien_numerator'],binding['molien_denominator']),'Molien and full-kernel Hilbert series differ')
    return {'case':case,'ordinary_invariant_generation':True,
        'complete_simultaneous_criterion':True,'actual_representation_bound':True,
        'method':'Exact cross-product equality of full characteristic-zero kernel Hilbert series and commutator Molien series',
        'binding_report':str(binding_path),'binding_report_sha256':digest(binding_path),
        'cox_report':str(cox_dir/'report.json'),'cox_report_sha256':digest(cox_dir/'report.json'),
        'hilbert_report_sha256':digest(cox_dir/'base_hilbert.json'),
        'binding_snapshot':str(binding_snapshot),'cox_snapshot':str(cox_snapshot),
        'binding_input_hashes':bh,'cox_input_hashes':ch,
        'binding_snapshot_program_hashes':snapshot_programs(binding_snapshot),
        'cox_snapshot_program_hashes':snapshot_programs(cox_snapshot)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pairs',type=Path,required=True,help='JSON list with case, binding_report, cox_directory, binding_snapshot, cox_snapshot')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();entries=read(args.pairs)
    require(isinstance(entries,list) and entries,'A nonempty explicit list is required')
    require(len({int(e['case']) for e in entries})==len(entries),'Duplicate case')
    result={'status':'RUNNING','scope':'Consistency and exact generation comparison of the explicitly selected completed fresh certificates; no validator is rerun.','pairs_sha256':digest(args.pairs),'comparator_sha256':digest(Path(__file__)),'arithmetic_helper_sha256':digest(Path(__file__).with_name('run_verification.py')),'cases':[]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        for entry in entries:
            result['cases'].append(compare(entry))
            print(f'GENERATION_COMPARISON_PASS {entry["case"]}',flush=True)
        result['status']='PASS'
    except Exception as error:
        result['status']='FAILED';result['error']=str(error)
        raise
    finally:args.output.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
