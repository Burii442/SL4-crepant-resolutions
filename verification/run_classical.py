#!/usr/bin/env python3
"""Re-enumerate CrystCat and compare the groups in a private working copy."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--gap', required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    out = a.output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        p.error('Output directory must be new or empty')
    out.mkdir(parents=True, exist_ok=True)
    work = out/'classification'
    shutil.copytree(a.repo/'classification', work)
    for name in ('all_qclasses.json', 'comparison.json'):
        (work/name).unlink(missing_ok=True)
    subprocess.run([a.gap, '-q', '--quitonbreak', str(work/'count_crystcat.g')],
                   cwd=work, check=True)
    data = json.loads((work/'all_qclasses.json').read_text())
    if data['counts'] != dict(all_qclasses=227, all_zclasses=710,
                             det_one_qclasses=106, det_one_zclasses=245):
        raise ValueError('Unexpected fresh CrystCat enumeration')
    subprocess.run([sys.executable, str(work/'compare_catalogue.py'),
                    str(a.repo.resolve()/'manuscript106/catalogue/catalogue.json')],
                   cwd=work, check=True)
    proof = json.loads((work/'comparison.json').read_text())
    if proof.get('status') != 'PASS':
        raise ValueError('Fresh comparison failed')
    (out/'report.json').write_text(json.dumps(proof, indent=2)+'\n')


if __name__ == '__main__':
    main()
