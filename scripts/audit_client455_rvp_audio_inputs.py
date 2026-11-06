"""Read actual RVP wave references; no substitution for missing exact assets."""
import hashlib,json
from pathlib import Path
from audit_client455_rvp import decode
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);files=[];assets={};ambient=events=0
    for path in sorted((client/'Map').rglob('*.rvp')):
        doc=decode(path.read_bytes());actors=[a for a in doc['actors'] if a['wave']];tracks=[t for t in doc['tracks'] if t['kind']==0x89]
        ambient+=len(actors);events+=len(tracks)
        for name in [a['wave'] for a in actors]+[t['resource'] for t in tracks]:
            source=client/name
            assets[name]=dict(relative=name,file=str(source),exists=source.is_file(),extension=source.suffix.lower())
            if source.is_file():assets[name].update(sha256=sha(source),bytes=source.stat().st_size)
        files.append(dict(file=str(path),sha256=sha(path),ambient=actors,events=tracks))
    report=dict(scope='Read-only exact-path RVP ambient/event audio inputs;not runtime sound equivalence',files=files,assets=list(assets.values()),ambient=ambient,events=events,script_sha256=sha(Path(__file__)),input_exe_executed=False,server_modified=False)
    (WS/'inventory/client455-rvp-audio-inputs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(RVP=len(files),ambient=ambient,events=events,assets=len(assets),present=sum(a['exists'] for a in assets.values()),extensions=sorted({a['extension'] for a in assets.values()}))))
if __name__=='__main__':main()
