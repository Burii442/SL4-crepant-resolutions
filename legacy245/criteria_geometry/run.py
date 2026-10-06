#!/usr/bin/env python3
"""Recompute the matrix and fan witnesses behind criteria D, H, I and Z."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,time
HERE=Path(__file__).resolve().parent
STEPS=[('cotangent','cotangent_audit.g','ALL_26_ACTUAL_COTANGENT_REFLECTION_HYPOTHESES_PASS'),
       ('representations','representation_bindings.py','ACTUAL_REPRESENTATION_BINDINGS_I_H_D_POSITIVE_PASS'),
       ('toric','toric_I.py','FULL_COHERENT_UNIMODULAR_EQUIVARIANT_FAN_AND_NO_ISOLATED_FIXED_POINTS_PASS'),
       ('towers','tower_bindings.py','ALL_8_TOWERS_RECHECKED')]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--gap',default=shutil.which('gap'))
    args=ap.parse_args()
    if not args.gap:ap.error('GAP unavailable; run with sage -python or set --gap')
    out=args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):ap.error('output directory must be new or empty')
    out.mkdir(parents=True,exist_ok=True);work=out/'work';work.mkdir()
    inputs=[HERE/'run.py',HERE/'tower_matrices.json']+[HERE/s for _,s,_ in STEPS]+[HERE.parent/'catalogue.json']
    for path in inputs:shutil.copy2(path,work/path.name)
    records=json.loads((work/'catalogue.json').read_text())
    assert [r['index'] for r in records]==list(range(1,246))
    (work/'ASL4.txt').write_text('ASL4:='+json.dumps([r['actual_generators'] for r in records])+';\n')
    report={'status':'RUNNING','complete':False,'input_sha256':{str(p.relative_to(HERE.parent)):digest(p) for p in inputs},'generated_asl4_sha256':digest(work/'ASL4.txt'),'steps':[],'scope':'26 cotangent character/reflection checks, 25 representation intertwiners, the equivariant fan and all eight tower group identifications. The article supplies the cited geometric theorems.'}
    def save():
        p=out/'report.tmp.json';p.write_text(json.dumps(report,indent=2)+'\n');p.replace(out/'report.json')
    save()
    try:
        for name,script,marker in STEPS:
            command=([args.gap,'-q'] if script.endswith('.g') else [sys.executable])+[str(work/script)]
            result={'name':name,'command':command,'status':'RUNNING'};report['steps'].append(result);save()
            start=time.monotonic();logpath=out/(name+'.log')
            with logpath.open('w') as log:
                proc=subprocess.Popen(command,cwd=work,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
                for line in proc.stdout:log.write(line);log.flush();print(line,end='',flush=True)
                code=proc.wait()
            assert code==0 and marker in logpath.read_text(),f'{name} did not complete every assertion'
            result.update(status='PASS',returncode=code,seconds=round(time.monotonic()-start,3),log_sha256=digest(logpath));save()
        report.update(status='ALL_CRITERIA_GEOMETRY_CHECKS_PASS',complete=True);save()
    except BaseException as error:
        report.update(status='FAILED',error=str(error));save();raise
    print('ALL_CRITERIA_GEOMETRY_CHECKS_PASS',flush=True)
if __name__=='__main__':main()
