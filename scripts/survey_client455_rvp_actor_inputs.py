"""Find exact-path actor resources for reproducible real RVP execution inputs."""
import hashlib,json
from pathlib import Path
from audit_client455_rvp import decode
from compare_client_binaries import WS

def main():
    root=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);rows=[]
    for path in sorted((root/'Map').rglob('*.rvp')):
        doc=decode(path.read_bytes());actors=[a for a in doc['actors'] if not a['flags']&2]
        if not actors:continue
        names=sorted({name for a in actors for name in [a['mesh'],a['bone']]+a['animations'] if name})
        present=[name for name in names if (root/name).is_file()];missing=sorted(set(names)-set(present))
        rows.append(dict(relative=path.relative_to(root).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            actors=len(actors),magic=len(doc['actors'])-len(actors),animations=sum(len(a['animations']) for a in actors),
            exact_paths_present=present,exact_paths_missing=missing))
    report=dict(scope='Exact paths only;RFS resolution/failure semantics not inferred',rows=rows,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),server_modified=False)
    (WS/'inventory/client455-rvp-actor-inputs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([dict(file=r['relative'],actors=r['actors'],magic=r['magic'],animations=r['animations'],missing=len(r['exact_paths_missing'])) for r in rows]))
if __name__=='__main__':main()
