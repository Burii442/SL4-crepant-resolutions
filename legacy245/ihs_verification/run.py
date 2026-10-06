#!/usr/bin/env python3
"""Fresh exact finite-group checks for the explicit Part VI matrix models."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,time
P=Path(__file__).resolve().parent
CHECKS={'torsion':('verify_seven_torsion.g','ALL_PART6_SEVEN_TORSION_EXCLUSIONS_PASSED'),'models':('verify_extra_models.g','ALL_PART6_EXTRA_FINITE_CHECKS_PASSED')}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',choices=CHECKS,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--gap',default=shutil.which('gap'));args=ap.parse_args()
    if not args.gap:ap.error('GAP unavailable; run with sage -python or set --gap')
    out=args.output_dir.resolve()
    if out.exists() and any(out.iterdir()):ap.error('output directory must be new or empty')
    out.mkdir(parents=True,exist_ok=True);script,marker=CHECKS[args.check];source=P/script
    shutil.copy2(source,out/script);report={'check':args.check,'status':'RUNNING','input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Finite assertions for the explicitly displayed Part VI matrix models; no claim of a new classification proof.'}
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();start=time.monotonic();command=[args.gap,'-q',str(out/script)]
    try:
        with (out/'stdout.log').open('w') as log:
            proc=subprocess.Popen(command,cwd=out,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            for line in proc.stdout:log.write(line);log.flush();print(line,end='',flush=True)
            code=proc.wait()
        text=(out/'stdout.log').read_text();assert code==0 and marker in text,'GAP did not reach all completion assertions'
        report.update(status='PASS',returncode=code,command=command,seconds=time.monotonic()-start,log_sha256=hashlib.sha256((out/'stdout.log').read_bytes()).hexdigest());save()
    except BaseException as error:
        report.update(status='FAILED',error=str(error),seconds=time.monotonic()-start);save();raise
if __name__=='__main__':main()
