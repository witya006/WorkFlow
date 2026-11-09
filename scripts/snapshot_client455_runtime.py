"""Freeze the current client runtime/evidence before the next port step."""
import argparse,json,shutil
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import require,sha,load

def freeze(number,gate_name):
    gate=load(gate_name);root=WS/f'artifacts/client455-progress/before{number}';root.mkdir(parents=True,exist_ok=True)
    paths={WS/f'inventory/{gate_name}.json'}|{WS/x['file'] for x in gate['fresh_evidence'].values()}
    engine,link=load('client455-startup-engine-build'),load('client455-normal-link')
    paths.update([WS/engine['library'],WS/link['executable']['file'],WS/link['map']['file'],WS/link['link_response']['file']])
    paths.update(WS/engine[k]['file'] for k in ['camera_header_overlay','particle_header_overlay','vertex_header_overlay','material_header_overlay'])
    paths.update(WS/x['file'] for x in engine['derived_sources'])
    paths.update(WS/p for p in ['docs/project-memory.md','docs/next-steps.md','scripts/build_client455_engine_startup.py','scripts/client455_runtime_inputs.py','scripts/client455_particle_port.py'])
    rows=[]
    for source in sorted(paths):
        dest=root/source.relative_to(WS);dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():require(sha(dest)==sha(source),'Preserve the existing runtime snapshot')
        else:shutil.copyfile(source,dest)
        rows.append(dict(file=dest.relative_to(WS).as_posix(),original=source.relative_to(WS).as_posix(),sha256=sha(dest)))
    (root/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print('Exact runtime snapshot:',len(rows))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('number',type=int);p.add_argument('gate');a=p.parse_args();freeze(a.number,a.gate)
