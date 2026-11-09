"""Actual Bellato CLevel frame,light queues,projected light passes and archivedFX."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,require,sha
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario
from quake455 import Quake,decode,f

def verify(run):
    rows=[json.loads(x) for x in (run/'lights.jsonl').read_text().splitlines()];lights=[];operations=0
    for row in rows:
        limit=row['limit'];op=row['op'];step=row['step']
        if op=='clear':lights=[];accepted=True
        else:
            accepted=len(lights)<10 and limit!=0
            if accepted:
                if len(lights)>=limit:lights=lights[1:limit]
                p=list(map(decode,row['input']));pos=p[:3];diameter=p[3];lo=[f(x-diameter) for x in pos];hi=[f(x+diameter) for x in pos]
                lights.append(dict(color=0x813b4c00+step if op=='insert' else 0xfedcba98,texture=step+1 if op=='insert' else 88,magic=(7 if step%3 else 0) if op=='insert' else -1,blend=step%4 if op=='insert' else 9,values=pos+[diameter]+lo+hi))
        require(bool(row['accepted'])==accepted and len(row['lights'])==len(lights),'Target queue count/return')
        for a,b in zip(row['lights'],lights):
            require({k:v for k,v in a.items() if k!='values'}=={k:v for k,v in b.items() if k!='values'} and list(map(decode,a['values']))==b['values'],'Target queue records/bounds')
        operations+=1
    q=Quake();clock=[json.loads(x) for x in (run/'clock-quake.jsonl').read_text().splitlines()]
    for i,row in enumerate(clock):
        dt=decode(row['dt'])
        if not i:q.start([f(.3),6.],dt)
        expected=q.vector(dt,row['toggle']);require(decode(row['remaining'])==q.remaining and all(abs(decode(a)-b)<=2e-5+abs(b)*5e-7 for a,b in zip(row['output'],expected)),'Live clock/quake coupling')
    require({r['toggle'] for r in clock}=={-1,1},'Both actual timer signs');world=json.loads((run/'world-frame.json').read_text());require(world['FX_light_frames']>0 and world['ray_hit'],'Actual world light producer')
    frames={p.name:p.read_bytes() for p in run.glob('frame-*.bgra')};require(len(frames)==5,'Five real frames');base=frames['frame-cleared.bgra'];diff={name:sum(a!=b for a,b in zip(base,value)) for name,value in frames.items()};require(diff['frame-magic.bgra']>20 and diff['frame-regular.bgra']>20 and diff['frame-effects.bgra']>20,'Visible actual projected light/effect output')
    return dict(queue_operations=operations,live_clock_samples=len(clock),clock_signs=[-1,1],world=world,changed_bytes_from_matched_clear=diff,full_world_equivalence=False)

def main():
    r=scenario('client455_world_frame_probe.cpp','world-frame','client455-world-frame-native','client455-world-bellato-native');run=(WS/r['exe']['file']).parent;r.update(status='PASS',verdict=verify(run),driver_script=record(Path(__file__)),oracle=record(WS/'scripts/quake455.py'),world_manifest=record(WS/'inventory/client455-world-bellato-native.json'),included_source=record(WS/'scripts/native/client455_world_probe.cpp'),trace=[record(run/n) for n in ['lights.jsonl','clock-quake.jsonl','world-frame.json']]);(WS/'inventory/client455-world-frame-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))

if __name__=='__main__':main()
