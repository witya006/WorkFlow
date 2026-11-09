"""Freeze the exact133 runtime and evidence before shader-owner migration."""
import json,shutil
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import require,sha


def main():
    root=WS/'artifacts/client455-progress/before134';root.mkdir(parents=True,exist_ok=True)
    gate=json.loads((WS/'inventory/client455-material-layout-checkpoint.json').read_text())
    paths={WS/'inventory/client455-material-layout-checkpoint.json'}
    paths.update(WS/x['file'] for x in gate['fresh_evidence'].values())
    engine=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text());link=json.loads((WS/'inventory/client455-normal-link.json').read_text())
    paths.update([WS/engine['library'],WS/link['executable']['file'],WS/link['map']['file'],WS/link['link_response']['file']])
    paths.update(WS/engine[k]['file'] for k in ['camera_header_overlay','particle_header_overlay','vertex_header_overlay','material_header_overlay'])
    paths.update(WS/p for p in ['docs/project-memory.md','docs/next-steps.md','scripts/build_client455_engine_startup.py','scripts/client455_runtime_inputs.py'])
    records=[]
    for path in sorted(paths):
        dest=root/path.relative_to(WS);dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():require(sha(dest)==sha(path),'Do not replace existing pre134 snapshot')
        else:shutil.copyfile(path,dest)
        records.append(dict(file=dest.relative_to(WS).as_posix(),original=path.relative_to(WS).as_posix(),sha256=sha(dest)))
    (root/'manifest.json').write_text(json.dumps(records,indent=2)+'\n');print('Exact133 snapshot:',len(records))


if __name__=='__main__':main()
