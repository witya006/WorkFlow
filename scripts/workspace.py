"""Supported workspace entry: check budget, verify pinned build, build current sources."""
import argparse,json,subprocess,sys
from pathlib import Path
from workspace_guard import ROOT,inspect,require_budget
from client455_normal_link_evidence import validate_normal_link

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['status','verify','build'])
    args=parser.parse_args()
    if args.action=='status':
        result=inspect();print(json.dumps(result,indent=2));return 0 if result['passed'] else 1
    require_budget()
    if args.action=='build':
        # Existing dependency validators stop if a changed native dependency needs rebuilding.
        # Do not silently rebuild every historical probe or regenerate all asset inventories.
        for name in ['prepare_client455_normal.py','build_client455_normal.py',
                     'probe_client455_normal_consumers.py','link_client455_normal.py']:
            subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,check=True)
    link=json.loads((ROOT/'inventory/client455-normal-link.json').read_text())
    state=validate_normal_link(link)
    if state!='PASS':raise RuntimeError('Current build is incomplete')
    print(json.dumps(dict(status='PASS',scope='Pinned build and workspace budget; not gameplay acceptance',
                          executable=link['executable'])))
    return 0

if __name__=='__main__':raise SystemExit(main())
