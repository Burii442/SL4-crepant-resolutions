#!/usr/bin/env sage-python
"""Recompute the complete selected geometric endpoint using public Cox models."""
from pathlib import Path
import argparse,json,time,hashlib,sys,subprocess
from common import HERE,SUPPLEMENT
CASES=[114,138,140,143,151,161,167,171,173,174,177,178,179,194,206,221,222,227,231,233,243]
def run_case(case,out):
    out.mkdir(parents=True,exist_ok=True)
    if case in [138,171,173,178,179,227]:
        from negative_points import run
        result=run([case],out)[0];result.update(status='PASS',complete=True)
        (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n');return result
    if case in [140,243]:
        from negative_ci import run
        return run(case,out)
    if case in [161,167,177,221]:
        from fixed_strata import run
        return run(case,out)
    if case==194:
        subprocess.run([sys.executable,str(SUPPLEMENT/'194/verify194.py'),'--sections','group','charts','cover','--output-dir',str(out)],check=True)
        result=json.loads((out/'certificate.json').read_text());assert result['status']=='REQUESTED_SECTIONS_PASS'
        result.update(status='PASS',complete=True);return result
    if case==231:
        from case231.verify231 import run
        return run(out)
    if case==114:
        subprocess.run([sys.executable,str(HERE/'case114/verify114.py'),'--output-dir',str(out)],check=True)
        result=json.loads((out/'certificate.json').read_text());assert result['status']=='PASS' and result.get('complete') is True and result.get('complete_cover') is True;return result
    if case==233:
        subprocess.run([sys.executable,str(HERE/'case233/verify233.py'),'--output-dir',str(out)],check=True)
        result=json.loads((out/'certificate.json').read_text());assert result['status']=='PASS' and result.get('complete_cover') is True;result['complete']=True;return result
    from chart_endpoints import run
    return run(case,out)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',type=int,choices=CASES);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);start=time.time();cases=[args.case] if args.case else CASES
    report={'status':'RUNNING','complete':False,'requested_cases':cases,'results':[]};path=out/'report.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    try:
        for case in cases:
            names=['paper_model83.json','paper_invariants83.json','paper_charts83.json','verify194.py'] if case==194 else ['model.json','invariants.json']
            inputs=[SUPPLEMENT/str(case)/name for name in names]
            sources=list(HERE.glob('*.py'))+list(HERE.glob('*.cpp'))
            sources += [p for root in [HERE/'data'/str(case),HERE/f'case{case}'] if root.exists() for p in root.rglob('*') if p.is_file() and p.suffix in ['.json','.py','.sing']]
            hashes={str(p.relative_to(SUPPLEMENT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs+sources}
            result=run_case(case,out/str(case));assert result['status']=='PASS' and result['complete']
            assert hashes=={name:hashlib.sha256((SUPPLEMENT/name).read_bytes()).hexdigest() for name in hashes},'An input or verifier changed while this case ran'
            result['input_and_verifier_sha256']=hashes
            report['results'].append(result);path.write_text(json.dumps(report,indent=2)+'\n')
    except BaseException as error:
        report.update(status='FAILED',complete=False,error=type(error).__name__+': '+str(error),seconds=time.time()-start)
        path.write_text(json.dumps(report,indent=2)+'\n');raise
    report.update(status='ALL_REQUESTED_ENDPOINT_CHECKS_PASS',complete=True,seconds=time.time()-start)
    path.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],cases,flush=True)
if __name__=='__main__':main()
