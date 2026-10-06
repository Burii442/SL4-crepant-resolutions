#!/usr/bin/env python3
"""Run a complete supported geometry validator in a new isolated work directory."""
import argparse,datetime,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path

BASE=Path(__file__).resolve().parent
SUPPLEMENT=BASE.parent
STEPS={132:[('verify_132_resolution.py','"result": "PASS"')],234:[('validate_inputs.py','DISCRIMINANT_AND_CONTRACTED_CHART_INPUTS_PASS'),('validate234_geometry.py','PASS_GEOMETRIC_YES_234_235'),('root_audit234.py','PASS_INDEPENDENT_INPUT_BINDING_AND_LOCAL_GEOMETRY')],236:[('validate_inputs.py','DISCRIMINANT_AND_CONTRACTED_CHART_INPUTS_PASS'),('validate236_geometry.py','PASS_GEOMETRIC_YES_236_237'),('root_audit236.py','PASS_INDEPENDENT_236_INPUT_CENTERS_REES_AND_COVER')]}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case',type=int,required=True,choices=sorted(STEPS))
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--singular',help='Path to the Singular executable (otherwise use PATH)')
    ap.add_argument('--gap',help='Path to the GAP executable (otherwise use PATH)')
    args=ap.parse_args();out=args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):ap.error('output directory must be new or empty; a fresh run never consumes previous outputs')
    out.mkdir(parents=True,exist_ok=True);work=out/'work';work.mkdir();logs=out/'logs';logs.mkdir()
    inputs=sorted(p for p in (BASE/str(args.case)).iterdir() if p.is_file())
    if args.case!=132:inputs.append(BASE/'validate_inputs.py')
    inputs.extend([Path(__file__).resolve(),SUPPLEMENT/'catalogue.json',SUPPLEMENT/'runtime_cache.py'])
    report={'case':args.case,'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'inputs':{str(p.relative_to(SUPPLEMENT)):digest(p) for p in inputs},'steps':[]}
    def save():
        tmp=out/'run.json.tmp';tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(out/'run.json')
    save()
    sys.path.insert(0,str(SUPPLEMENT))
    from runtime_cache import allocate_sage_cache
    sage_cache=None
    try:
        sage_cache=allocate_sage_cache(out/'sage-cache',inherited=os.environ.get('DOT_SAGE'))
        report['sage_cache']=sage_cache.metadata();save()
        for p in inputs:
            if p.name!='run.py':shutil.copy2(p,work/p.name)
        catalogue=json.loads((work/'catalogue.json').read_text())
        (work/'ASL4.txt').write_text('ASL4 := '+json.dumps([r['actual_generators'] for r in catalogue])+';\n')
        env=os.environ.copy();env['PYTHONUNBUFFERED']='1';env['DOT_SAGE']=str(sage_cache.path)
        wrappers=out/'bin';wrappers.mkdir()
        if args.case!=132:
            for name,requested in [('Singular',args.singular),('gap',args.gap)]:
                executable=requested or shutil.which(name)
                if not executable:raise RuntimeError(f'{name} is required; run under sage -python or supply its executable path')
                executable=str(Path(executable).resolve());(wrappers/name).symlink_to(executable)
                report.setdefault('executables',{})[name]=executable
            env['PATH']=str(wrappers)+os.pathsep+env.get('PATH','')
        for n,(script,marker) in enumerate(STEPS[args.case],1):
            command=[sys.executable,str(work/script)];log=logs/f'{n:02d}-{Path(script).stem}.log'
            step={'script':script,'command':command,'log':str(log.relative_to(out)),'status':'RUNNING'};report['steps'].append(step);save()
            print(f'START geometry {args.case}: {script}',flush=True);start=time.monotonic()
            with log.open('w') as stream:
                proc=subprocess.Popen(command,cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
                for line in proc.stdout:stream.write(line);stream.flush();print(line,end='',flush=True)
                code=proc.wait()
            text=log.read_text();step.update(returncode=code,seconds=round(time.monotonic()-start,3),log_sha256=digest(log))
            if code or marker not in text:
                step['status']='FAILED';save();raise RuntimeError(f'{script} failed or omitted its completion assertion; see {log}')
            step['status']='PASS';save()
        report['status']='PASS';print(f'GEOMETRY_{args.case}_ALL_FRESH_CHECKS_PASS',flush=True)
    except BaseException as error:
        report['status']='INTERRUPTED' if isinstance(error,(KeyboardInterrupt,SystemExit)) else 'FAILED';report['error']=str(error);raise
    finally:
        # A standalone geometry runner shares its process group with children.
        # Defer deletion while that group survives; a nested runner inherits
        # the top-level owner's cache and never removes it independently.
        if sage_cache is not None:report['sage_cache_cleanup']=sage_cache.cleanup([os.getpgrp()])
        report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
if __name__=='__main__':main()
