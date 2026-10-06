#!/usr/bin/env python3
"""Run supported checks afresh in an isolated copy, with live logs and input hashes."""
import argparse,datetime,hashlib,json,os,shutil,signal,subprocess,sys,time
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent
IGNORED={'__pycache__','.DS_Store','verification_runs','cox_sources.tar.xz','supplement.tar.gz','criteria_verification.json','geometry_verification.json','cox_model_checks.json','cox_exact_image_checks.json'}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def same_rational_series(a_num,a_den,b_num,b_den):
    def multiply(a,b):
        a=list(map(Fraction,a));b=list(map(Fraction,b));c=[Fraction(0)]*(len(a)+len(b)-1)
        for i,x in enumerate(a):
            for j,y in enumerate(b):c[i+j]+=x*y
        while len(c)>1 and c[-1]==0:c.pop()
        return c
    if not any(map(Fraction,a_den)) or not any(map(Fraction,b_den)):raise ValueError('Zero denominator in a generated series')
    return multiply(a_num,b_den)==multiply(b_num,a_den)
def registry():
    steps={
      'criteria':('verify_criteria.py',[], 'Coverage and consistency of recorded criterion incidences'),
      'criteria-geometry':('criteria_geometry/run.py',['--output-dir','{out}/result'],'26 cotangent checks, 25 D/H/I intertwiners, the equivariant fan, and eight tower group identifications'),
      'catalogue':('verify_catalogue.py',['--output','{out}/catalogue.json'],'All 245 matrix closures and group data; exact criteria A/B/C'),
      'representatives':('verify_representatives.py',['--output','{out}/representatives.json'],'All 73 rational representative conjugacies, comparing the complete groups'),
      'compact':('verify_compact_cases.py',['--output','{out}/compact.json'],'Invariant forms for 245 entries; 25 closures, ten full stabilizers, five integral conjugacies'),
      'integral-lattices':('verify_integral_lattices.py',[],'Finite Hurwitz and order-32 lattice arithmetic'),
      'named-hodge':('ihs_verification/verify_named_hodge.py',['--output','{out}/hodge.json'],'Ten named full Hodge profiles and independent commuting-pair Euler formula'),
      'seven-torsion':('ihs_verification/run.py',['--check','torsion','--output-dir','{out}/result'],'All seven explicit finite torsion exclusions in Part VI'),
      'extra-models':('ihs_verification/run.py',['--check','models','--output-dir','{out}/result'],'Type V automorphism and the G32 matrix model'),
      'geometry':('verify_geometry.py',[],'Twelve complete invariant-ring presentations and all 46 toric fans'),
      'cox-models':('check_cox_models.sage.py',[],'Gradings, homogeneity and modular consistency only; not full Cox generation')}
    for case in [132,234,236]:steps[f'geometry-{case}']=('geometry_proofs/run.py',['--case',str(case),'--output-dir','{out}/result'],f'Full fresh geometry validation for representative {case}')
    cases=sorted(int(p.name) for p in ROOT.iterdir() if p.is_dir() and (p/'model.json').is_file())
    for case in cases:
        steps[f'binding-{case}']=('binding_verification/verify_binding.py',['--case',str(case),'--output','{out}/binding.json'],f'Full group, junior classes, commutator invariance, valuations, character grading and Molien series for case {case}')
        if case==194:steps[f'cox-{case}']=('194/verify194.py',['--output-dir','{out}/result'],'Dedicated full model and six-slice verification for case 194')
        else:steps[f'cox-{case}']=('full_verification/verify_cox.py',['--case',str(case),'--output-dir','{out}/result','--stage','all'],f'Complete polynomial-map kernels and simultaneous valuation criterion for case {case}')
        steps[f'endpoint-{case}']=('endpoint_verification/verify_endpoints.py',['--case',str(case),'--output-dir','{out}/result'],f'Positive charts or negative point/cone obstruction for case {case}')
    return steps

def main():
    checks=registry();ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--list',action='store_true',help='List the supported mathematical checks without running them')
    ap.add_argument('--profile',choices=['core','geometry','ihs','bindings','cox','endpoints','all'],default='all')
    ap.add_argument('--steps',help='Comma-separated exact step names; overrides --profile')
    ap.add_argument('--output-dir',type=Path,help='New or empty directory outside this supplement')
    ap.add_argument('--sage',default=shutil.which('sage'),help='Sage executable, discovered on PATH by default')
    ap.add_argument('--keep-going',action='store_true',help='Run remaining independent steps after failure; overall result remains failed')
    args=ap.parse_args()
    if args.list:
        for name,(script,argv,scope) in checks.items():print(f'{name}: {scope}\n  sage -python {script} '+ ' '.join(argv))
        return
    if not args.output_dir:ap.error('--output-dir is required for a fresh run')
    if not args.sage:ap.error('Sage executable unavailable; pass --sage /path/to/sage')
    selected=args.steps.split(',') if args.steps else [name for name in checks if args.profile=='all' or (args.profile=='core' and name in ['criteria','criteria-geometry','catalogue','representatives','compact','integral-lattices','named-hodge','seven-torsion','extra-models','geometry','cox-models']) or (args.profile=='geometry' and (name=='geometry' or name.startswith('geometry-'))) or (args.profile=='ihs' and name in ['compact','integral-lattices','named-hodge','seven-torsion','extra-models']) or (args.profile=='bindings' and name.startswith('binding-')) or (args.profile=='cox' and name.startswith('cox-') and name!='cox-models') or (args.profile=='endpoints' and name.startswith('endpoint-'))]
    if len(selected)!=len(set(selected)):ap.error('duplicate steps would repeat a calculation')
    for name in selected:
        if name not in checks:ap.error(f'unknown step {name}; use --list')
        if not (ROOT/checks[name][0]).is_file():ap.error(f'supported entry point {checks[name][0]} is absent; no result can be claimed')
    out=args.output_dir.resolve()
    if out==ROOT or ROOT in out.parents:ap.error('output directory must be outside the distributed supplement')
    if out.exists() and any(out.iterdir()):ap.error('output directory must be new or empty; no old result is reused')
    out.mkdir(parents=True,exist_ok=True);work=out/'supplement';reportpath=out/'verification.json'
    report={'status':'PREPARING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected_steps':selected,'steps':[],'ordinary_generation':{},'scope':'Only the selected calculations; no old PASS files or checkpoints are consumed.'}
    def save():
        p=out/'verification.json.tmp';p.write_text(json.dumps(report,indent=2)+'\n');p.replace(reportpath)
    save()
    sys.path.insert(0,str(ROOT))
    from runtime_cache import allocate_sage_cache,terminate_owned_process_group
    sage_cache=None;process_groups=[]
    try:
        sage_cache=allocate_sage_cache(out/'sage-cache')
        report['sage_cache']=sage_cache.metadata();save()
        shutil.copytree(ROOT,work,ignore=lambda folder,names:[n for n in names if n in IGNORED or n.endswith(('.pyc','.tar.gz','.tar.xz'))])
        manifest={str(p.relative_to(work)):digest(p) for p in sorted(work.rglob('*')) if p.is_file()}
        (out/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');report['input_manifest_sha256']=digest(out/'input_manifest.json')
        report['input_files']=len(manifest);report['sage']=str(Path(args.sage).resolve());report['status']='RUNNING';save()
        env=os.environ.copy();env['DOT_SAGE']=str(sage_cache.path);env['PYTHONUNBUFFERED']='1'
        for name in selected:
            target=out/'steps'/name;target.mkdir(parents=True);script,argv,scope=checks[name]
            command=[args.sage,'-python',str(work/script)]+[a.replace('{out}',str(target)) for a in argv]
            step={'name':name,'scope':scope,'status':'RUNNING','command':command,'log':str((target/'stdout.log').relative_to(out)),'input_manifest_sha256':report['input_manifest_sha256']};report['steps'].append(step);save()
            print(f'START {name}: {scope}',flush=True);start=time.monotonic()
            with (target/'stdout.log').open('w') as log:
                proc=subprocess.Popen(command,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,start_new_session=True)
                process_groups.append(proc.pid)
                step['process_id']=proc.pid;save()
                try:
                    for line in proc.stdout:log.write(line);log.flush();print(f'[{name}] {line}',end='',flush=True)
                    code=proc.wait()
                except BaseException:
                    step['process_group_termination']=terminate_owned_process_group(proc,process_groups)
                    raise
            passed=(code==0)
            if passed and name=='criteria-geometry':
                proof=json.loads((target/'result/report.json').read_text())
                if proof.get('status')!='ALL_CRITERIA_GEOMETRY_CHECKS_PASS' or not proof.get('complete'):
                    passed=False;step['error']='The D/H/I/Z matrix and fan checks were not completed in full.'
            if passed and name.startswith('binding-'):
                proof=json.loads((target/'binding.json').read_text())
                if proof.get('status')!='PASS' or not proof.get('all_junior_classes_covered'):
                    passed=False;step['error']='The full physical group and polynomial binding was not completed.'
            if passed and name.startswith('cox-') and name not in ['cox-models','cox-194']:
                proof=json.loads((target/'result/report.json').read_text())
                if not proof.get('complete_simultaneous_criterion') or not proof.get('public_presentation_equals_full_kernel'):
                    passed=False;step['error']='The requested full polynomial-map criterion was not completed.'
                binding_name='binding-'+name.split('-')[1]
                if passed and any(s['name']==binding_name and s['status']=='PASS' for s in report['steps']):
                    binding_path=out/'steps'/binding_name/'binding.json'
                    hilbert_path=target/'result/base_hilbert.json'
                    binding=json.loads(binding_path.read_text());hilbert=json.loads(hilbert_path.read_text())
                    case=name.split('-')[1]
                    if hilbert.get('ordinary_kernel_complete') is not True or hilbert.get('ordinary_kernel_characteristic')!=0:
                        raise ValueError('Fresh Hilbert output does not certify a complete characteristic-zero ordinary kernel')
                    if binding['inputs']['catalogue.json']!=manifest['catalogue.json']:
                        raise ValueError('Fresh binding uses a different catalogue from the isolated input manifest')
                    for filename in [case+'/model.json',case+'/invariants.json']:
                        if binding['inputs'][filename]!=hilbert['input_hashes'][filename] or binding['inputs'][filename]!=manifest[filename]:
                            raise ValueError('Fresh binding and Hilbert calculations use different mathematical inputs')
                    equals=same_rational_series(hilbert['numerator'],hilbert['denominator'],binding['molien_numerator'],binding['molien_denominator'])
                    step['ordinary_invariant_generation']={'method':'Exact equality of fresh full-kernel Hilbert and commutator Molien series','passed':equals,'binding_report':str(binding_path.relative_to(out)),'hilbert_report':str(hilbert_path.relative_to(out))}
                    if not equals:
                        passed=False;step['error']='The full-kernel Hilbert series differs from the commutator Molien series.'
                    else:report['ordinary_generation'][case]=True
            if passed and name=='cox-194':
                proof=json.loads((target/'result/certificate.json').read_text())
                if proof.get('status')!='ALL_PAPER83_CHECKS_PASS':
                    passed=False;step['error']='The dedicated Case 194 proof was not completed in full.'
                else:
                    report['ordinary_generation']['194']=True
                    step['ordinary_invariant_generation']={'method':'Dedicated paper83 group check: exact invertible span of the complete C3-invariant monomial generators','passed':True}
            if passed and name.startswith('endpoint-'):
                proof=json.loads((target/'result/report.json').read_text())
                if proof.get('status')!='ALL_REQUESTED_ENDPOINT_CHECKS_PASS' or not proof.get('complete'):
                    passed=False;step['error']='The requested geometric endpoint was not completed in full.'
            step.update(returncode=code,seconds=round(time.monotonic()-start,3),log_sha256=digest(target/'stdout.log'),status='PASS' if passed else 'FAILED');save()
            print(f'{step["status"]} {name} ({step["seconds"]} s)',flush=True)
            if not passed and not args.keep_going:break
        report['status']='PASS' if len(report['steps'])==len(selected) and all(s['status']=='PASS' for s in report['steps']) else 'FAILED'
    except BaseException as error:
        report['status']='INTERRUPTED' if isinstance(error,(KeyboardInterrupt,SystemExit)) else 'FAILED';report['error']=str(error)
        if report['steps'] and report['steps'][-1]['status']=='RUNNING':
            report['steps'][-1].update(status=report['status'],error=str(error))
        raise
    finally:
        if sage_cache is not None:report['sage_cache_cleanup']=sage_cache.cleanup(process_groups)
        report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    print(f'VERIFICATION_{report["status"]}: {reportpath}',flush=True)
    if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
