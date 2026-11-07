"""Pin selected455 timer assembly; small state/label/radial geometry oracles."""
import hashlib,json,math,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def signed(v):return v-0x100000000 if v&0x80000000 else v
def wrap(v):return v&0xffffffff

def label(ms,context):
    # Result tuples preserve prefilled output values for target partial writes.
    value=ms;color=0x12345678;x=123;y=456;unit=99;scale=1.25
    if ms in (0,60000,3600000):return value,color,x,y,3,scale
    hours=ms>3600000;minutes=60000<ms<3600000
    if hours:value=ms//3600000;unit=2;color=0xffffffff
    elif minutes:value=ms//60000;unit=1;color=0xffffffff
    else:value=ms//1000+1;unit=0;color=0xffff0000 if value<10 else 0xffffff00
    if context<=5:
        group=0 if context in (0,1,5) else 1 if context in (2,3) else 2
        if hours:x=[-27,-32,-33][group]
        elif minutes:x=([-30,-37,-30] if ms//1000>600 else [-27,-32,-27])[group]
        else:x=([-22,-27,-24] if value<10 else [-25,-30,-31])[group]
        y=[24,27,24][group];scale=[.6,.8,.7][group]
    return value,color,x,y,unit,f32(scale)

def triangles(x,y,w,h,a,pi):
    cx,cy=f32(x+w/2),f32(y+h/2);right,bottom=signed(wrap(x+w)),signed(wrap(y+h));out=[]
    def tan(distance):return f32(math.tan(f32(distance*pi/180)))
    # Intersect each remaining clockwise sector with the rectangle. These
    # independent endpoint tuples are packed before the native sink runs.
    if a<45:out.append(((f32(cx+h/2*tan(a)),y),(right,y)))
    if a<135:out.append(((right,y if a<45 else f32(y+w/2*(1-tan(90-a))) if a<90 else f32(cy+w/2*tan(a-90))),(right,bottom)))
    if a<225:out.append(((right if a<135 else f32(cx+h/2*tan(180-a)) if a<180 else f32(x+h/2*(1-tan(a-180))),bottom),(x,bottom)))
    if a<315:out.append(((x,bottom if a<225 else f32(cy+w/2*tan(270-a)) if a<270 else f32(y+w/2*(1-tan(a-270)))),(x,y)))
    if a<360:out.append(((x if a<315 else f32(x+h/2*(1-tan(360-a))),y),(cx,y)))
    return [[(float(px),float(py),1.,1.,0xa0040204,0.,0.) for px,py in (p,q,(cx,cy))] for p,q in out]

def main():
    evidence=WS/'artifacts/client455-progress/gui-timer098-reference.json';raw=json.loads(evidence.read_text());functions=[r['fn'] for r in raw['functions']['result']];require(len(functions)==29 and all(functions),'Timer function coverage')
    assembly=raw['assembly'];require(len(assembly)==29 and all(p['cursor']['done'] and p['instruction_count']==len(p['asm']['lines'])==p['total_instructions'] for p in assembly),'Complete selected assembly')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Pin identity');ranges=[]
        for fn in functions+[dict(addr='0xb2b128',size='0x2'),dict(addr='0xada958',size='0x8'),dict(addr='0xada088',size='0x8')]:
            a,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()))
        tails=[]
        for fn,page in zip(functions,assembly):
            a=int(fn['addr'],16);end=a+int(fn['size'],16)
            for line in page['asm']['lines']:
                address=int(line['addr'],16)
                if not a<=address<end:tails.append(dict(rva=hex(address-0x400000),bytes=15,sha256=hashlib.sha256(read_va(binary,address,15)).hexdigest()))
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=tails))
    require(refs[0]['ranges']==refs[1]['ranges'] and refs[0]['external_assembly_windows']==refs[1]['external_assembly_windows'],'Pinned timer ranges differ')
    cw=struct.unpack('<H',read_va(binary,0xb2b128,2))[0];pi=struct.unpack('<d',read_va(binary,0xada958,8))[0];require(cw==0x27f and pi==3.1415927410125732421875 and read_va(binary,0xada088,8)==b'%dh\0%dm\0','Timer constants/inline formats')
    root=WS/'work/client-reference/gui-timer455';root.mkdir(parents=True,exist_ok=True);fixtures=[]
    def save(name,magic,rows,fmt):
        path=root/name;path.write_bytes(magic+struct.pack('<I',len(rows))+b''.join(struct.pack(fmt,*r) for r in rows));fixtures.append(record(path))
    states=[]
    for duration in [0,1,1000,60000,0x7fffffff,0x80000000,0xffffffff]:
        for start,now in [(100,100),(100,101),(100,1100),(0xfffffff0,0x20),(0,0xffffffff)]:
            for offset in [-1,0,1,1000,-2]:
                elapsed=wrap((0 if offset==-1 else wrap(offset))+now-start);difference=signed(wrap(duration-elapsed))
                states.append((duration,start,offset,now,wrap(offset) if offset!=-1 else 0,max(difference,0),1 if elapsed<duration else 0,f32(elapsed/duration*360) if elapsed<duration else 123.25))
    save('timer-states.bin',b'TS98',states,'<IIiIIIIf')
    labels=[]
    for ms in [0,1,999,1000,8999,9000,59999,60000,60001,600999,601000,3599999,3600000,3600001,7200000,0x7fffffff]:
        for context in range(7):labels.append((ms,context,*label(ms,context)))
    save('timer-labels.bin',b'TL98',labels,'<IIIIiiIf')
    angles=[0,.0001,44.999996185302734,45,45.000003814697266,89.99999237060547,90,134.99998474121094,135,179.99998474121094,180,224.99998474121094,225,269.9999694824219,270,314.9999694824219,315,359.9999694824219,360]
    path=root/'timer-rays.bin';data=bytearray(b'TR98'+struct.pack('<I',len(angles)*3));triangle_count=0
    for x,y,w,h in [(40,32,32,32),(-13,-7,38,38),(101,89,20,38)]:
        for angle in angles:
            angle=f32(angle);rays=triangles(x,y,w,h,angle,pi);triangle_count+=len(rays);data+=struct.pack('<4ifI',x,y,w,h,angle,len(rays))
            for ray in rays:
                for vertex in ray:data+=struct.pack('<4fI2f',*vertex)
    path.write_bytes(data);fixtures.append(record(path))
    prior=load('client455-linker-window-reference');inputs=prior['inputs']+[r for r in load('client455-item-icon-metadata-reference')['fixtures'] if Path(r['file']).name=='metadata-samples.bin']
    for row in inputs:check(row)
    report=dict(status='CONFIRMED_SELECTED',scope='Selected GUI timer state/update/default finite radial path/label/copy/fanout,typed ordinary icon integration',script_sha256=sha(Path(__file__)),raw_evidence=[record(evidence)],references=refs,assembly_functions=29,assembly_instructions=sum(p['instruction_count'] for p in assembly),decoded_control_word=cw,decoded_pi=pi,state_cases=len(states),label_cases=len(labels),radial_cases=len(angles)*3,radial_triangles=triangle_count,fixtures=fixtures,inputs=inputs,
        gaps=['Target CPU-selected SSE tan/FP exceptions/NaN/unsafe numeric/private ABI not accepted','Other GUIItem children/shake/lock and complete copy/empty/lifecycle remain open','Linker cooldown cache,actual use/remove/swap/hover handlers/live callbacks/Macro/Vending/full Add/bootstrap/remaining client gaps still mandatory'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-gui-timer-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['assembly_functions','assembly_instructions','state_cases','label_cases','radial_cases','radial_triangles']}))
if __name__=='__main__':main()
