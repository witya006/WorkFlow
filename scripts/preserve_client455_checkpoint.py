"""Freeze owned checkpoint inputs;reuse identical prior immutable snapshot files."""
import argparse,hashlib,json,os,re,shutil
from pathlib import Path
from compare_client_binaries import WS


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--previous',required=True);parser.add_argument('--destination',required=True);parser.add_argument('--checkpoint',required=True);args=parser.parse_args()
    assert all(re.fullmatch('before[0-9]+',name) for name in [args.previous,args.destination])
    root=(WS/'artifacts/client455-progress').resolve();previous=root/args.previous;destination=root/args.destination
    assert not destination.exists(),'Preserving existing snapshot'
    old=json.loads((previous/'manifest.json').read_text());gate_file=WS/args.checkpoint;gate=json.loads(gate_file.read_text())
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text())
    assert gate['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json')
    assert sha(WS/link['executable']['file'])==gate['normal_executable']['sha256']
    files={row['original'] for row in old}|{args.checkpoint,'README.md','docs/function-coverage.md','docs/roadmap.md','docs/progress-report.md','docs/environment-audit.md','docs/client-acceptance.md','inventory/client455-function-coverage.json','inventory/client455-function-history.json','inventory/client-features.json'}
    files.update(row['file'] for row in gate['fresh_evidence'].values())
    #Only source records from evidence manifests;never recurse through input
    #assets/frames/traces and accidentally snapshot another full client tree.
    def source_records(value):
        if isinstance(value,dict):
            path=value.get('file')
            if isinstance(path,str) and path.startswith('scripts/') and value.get('sha256'):yield path
            for child in value.values():yield from source_records(child)
        elif isinstance(value,list):
            for child in value:yield from source_records(child)
    files.update(source_records(gate))
    for evidence in gate['fresh_evidence'].values():
        files.update(source_records(json.loads((WS/evidence['file']).read_text())))
    files.update(['scripts/native/client455_actor_lighting.inc','scripts/client455_actor_lighting_port.py','scripts/native/client455_player_owner_probe.cpp','scripts/probe_client455_player_owner.py','scripts/prepare_client455_normal.py','work/client455-port/normal/source/cresobject.cpp','work/client455-port/normal/source/cresobject.h'])
    rows=[];copied=linked=0
    for relative in sorted(files):
        assert not Path(relative).is_absolute() and '..' not in Path(relative).parts,relative
        source=(WS/relative).resolve();assert source.is_relative_to(WS.resolve()) and source.is_file(),relative
        digest=sha(source);target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        prior=previous/relative
        if prior.is_file() and sha(prior)==digest and not os.path.samefile(prior,source):
            os.link(prior,target);storage='shared_prior_snapshot';linked+=source.stat().st_size
        else:
            shutil.copyfile(source,target);storage='private_copy';copied+=source.stat().st_size
        assert sha(target)==digest
        rows.append(dict(file=target.relative_to(WS).as_posix(),original=relative,sha256=digest,storage=storage))
    (destination/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(dict(snapshot=destination.relative_to(WS).as_posix(),files=len(rows),copied_bytes=copied,shared_prior_snapshot_bytes=linked,own_executable=gate['normal_executable']['sha256'])))


if __name__=='__main__':main()
