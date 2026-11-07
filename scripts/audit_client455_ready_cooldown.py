"""Pin ready-animation/cooldown routes and independent small state/grid fixtures."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def f32(n):return struct.unpack('<f',struct.pack('<f',n))[0]
def bits(n):return struct.unpack('<I',struct.pack('<f',n))[0]

def main():
    base=load('client455-linker-cooldown-reference')
    for row in base['raw_evidence']+[base['session']]:check(row)
    path=WS/'artifacts/client455-progress/ready-cooldown099-additional.json';raw=json.loads(path.read_text());require(len(raw['ranges'])==len(raw['assembly'])==len(raw['functions'])==8 and all(r['cursor']['done'] for r in raw['assembly']),'Additional provider coverage');references=[]
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        source=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=source.read_bytes();require(sha(source)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Pinned client');ranges=[]
        for fn in raw['ranges']+[dict(addr='0xaa9284',size='0x14'),dict(addr='0xaa9414',size='0x14'),dict(addr='0xaa9438',size='0x4'),dict(addr='0xad9f94',size='0x4')]:
            va,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(va-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,va,n)).hexdigest()))
        require(struct.unpack('<f',read_va(binary,0xad9f94,4))[0]==34,'Ready FPS binary constant');references.append(dict(sha256=sha(source),architecture='x86',image_base='0x400000',ranges=ranges))
    require(references[0]['ranges']==references[1]['ranges'],'Additional provider pins differ')
    root=WS/'work/client-reference/ready-cooldown455';root.mkdir(parents=True,exist_ok=True);fixtures=[]
    def save(name,magic,rows):
        path=root/name;path.write_bytes(magic+struct.pack('<I',len(rows))+b''.join(struct.pack('<'+'I'*len(row),*row) for row in rows));fixtures.append(record(path))
    states=[]
    settings=[(frame,f32(dt),loop,shown,stopped,paused,1001,1000,1) for frame in [0,38.75] for dt in [0,.03,.25,1.25] for loop in [0,3] for shown in [0,1] for stopped in [0,7] for paused in [0,2]]
    settings += [(0,.03,1,1,0,1,now,start,interval) for now,start,interval in [(1002,1000,1),(0x20,0xfffffff0,48),(0x21,0xfffffff0,48),(0,0xffffffff,0)]]
    for frame,dt,loop,shown,stopped,paused,now,start,interval in settings:
        frame=f32(frame);fps=f32(34);uv=list(map(f32,[.2,.4,.3,.6]));calls=clocks=0;next_frame=frame;next_stopped=stopped;next_paused=paused;next_start=start
        if shown and not stopped:
            if paused:
                clocks=1
                if ((now-start)&0xffffffff)>interval:next_paused=0
            else:
                calls=1;next_frame=f32(float(dt)*fps+frame)
                if next_frame>=40:
                    if loop:next_paused=1;next_start=now;clocks=1;next_frame=0
                    else:next_frame=39.;next_stopped=1
                index=int(next_frame);u=f32(index%8*.125);v=f32(index//8*.125);uv=[u,f32(u+.125),v,f32(v+.125)]
        states.append([shown,stopped,paused,loop,40,8,bits(frame),bits(fps),bits(dt),now,start,interval,bits(.125),bits(.125),bits(next_frame),next_stopped,next_paused,next_start,*map(bits,uv),calls,clocks])
    save('animation-states.bin',b'AS99',states)
    grids=[]
    for ox,oy,tx,ty in [(1024,640,1024,1024),(65,31,128,64),(0,0,0,0),(7,3,0,64)]:
        for cols in [0,8,255]:
            for rows in [0,5]:
                for fixed in [0,128]:
                    c,r=cols or 1,rows or 1;w,h=ox//c,oy//r;u,v=(f32((fixed or w)/tx),f32((fixed or h)/ty)) if tx and ty else (f32(.2),f32(.3))
                    grids.append([ox,oy,tx,ty,cols,rows,fixed,fixed,w,h,c*r,c,bits(u),bits(v)])
    save('animation-grids.bin',b'AG99',grids)
    inputs=load('client455-gui-timer-reference')['inputs']
    for row in inputs:check(row)
    report=dict(status='CONFIRMED_SELECTED',scope='Source-owned ready-animation,mode3 draw andordinary Linker cooldown records/timer routes;fullhandlers/gameplay remain open',script_sha256=sha(Path(__file__)),base_reference_sha256=sha(WS/'inventory/client455-linker-cooldown-reference.json'),raw_evidence=[record(path)],references=references,inputs=inputs,fixtures=fixtures,state_cases=len(states),grid_cases=len(grids),additional_instructions=sum(r['instruction_count'] for r in raw['assembly']),
        gaps=['Full gameplay use/remove/swap/hover handlers/live source-board callbacks/lock/potion cache/Macro/Vending/fullAdd/bootstrap remain mandatory','Generic animation clipped draw andblend modes other than ready3 remain explicit refusals','Complete privateABI/FP-numeric/unsafe/OOM/concurrency/shutdown andallpriorclient gaps not accepted'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-ready-cooldown-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(state_cases=len(states),grid_cases=len(grids),provider_ranges=12)))
if __name__=='__main__':main()
