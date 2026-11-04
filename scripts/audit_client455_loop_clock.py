"""Pin the loop clock and build finite instruction-derived state goldens."""
import hashlib,json,struct
from fractions import Fraction
from audit_client455_animation_timing import binary_round
from build_client455_x87_math import read_va
from compare_client_binaries import WS

def sha(b):return hashlib.sha256(b).hexdigest()
def fl(v):return struct.unpack('<I',struct.pack('<f',v))[0]
def f(bits):return Fraction(struct.unpack('<f',struct.pack('<I',bits))[0])
def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];previous=None
    ranges=[('ticks',0x8b3ae0,0x4a),('duration',0x8b3b30,0x30),('toggle30',0x8b3b70,0x5a),('toggle15',0x8b3be0,0x5a),('toggle7_tail',0x8b3c50,0x5a),('scale_set',0x8b3cb0,0xb),('update',0x8b3cc0,0x16a),('loop_get_set_real_get_set_minfps',0x8b3e30,0x4f)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=target[key]['sha256']:raise ValueError('Changed pin')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for name,at,n in ranges]
        if previous and previous!=bodies:raise ValueError('Loop bodies differ')
        previous=bodies
        for at,expected in [(0xbf7358,struct.pack('<f',1)),(0xbf735c,struct.pack('<3i',1,1,1)),(0xbf7368,struct.pack('<f',1))]:
            if read_va(raw,at,len(expected))!=expected:raise ValueError('Changed loop defaults')
        thresholds=[]
        for at in [0xb36b10,0xb36b20,0xb36b30]:
            double,small=struct.unpack('<df',read_va(raw,at,12))
            if double!=small:raise ValueError('Unexpected toggle double')
            thresholds.append(fl(small))
        references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies})
    def state(old=100,loop=.003,real=0,maximum=1,scale=1,count=0,hop=0,phases=(0,0,0),toggles=(1,1,1)):
        return [1,old,count,hop,*map(fl,[loop,real,maximum,scale]),*map(fl,phases),*[v%2**32 for v in toggles]]
    cases=[(110,state()),(130,state()),(100,state(scale=2)),(8,state(old=0xfffffffc)),(3,state(old=0,hop=0xfffffffe)),(120,state(count=0x7ffffffe)),(120,state(count=0x80000000)),(100,state(loop=-.1,maximum=.2,scale=.5)),(1100,state(maximum=.05,scale=.5)),(100,state(loop=0,phases=(1/30,1/15,1/7))),(100,state(loop=.5,toggles=(-2147483648,0,-1))),(110,state(loop=.03,scale=-1))]
    rows=[]
    for p in [24,53,64]:
        for mode in range(4):
            r=lambda v:binary_round(v,p,mode)
            store=lambda v:fl(float(binary_round(v,24,mode)))
            unsigned=lambda v:r(Fraction(v)) if v>=2**31 else Fraction(v)
            for now,before in cases:
                after=before.copy();after[2]=(after[2]+1)%2**32;after[3]=(after[3]+now-after[1])%2**32
                if after[3]>10:
                    after[4]=store(r(r(unsigned(after[3])/unsigned(after[2]))/1000));after[2]=after[3]=0
                after[1]=now
                if f(after[6])<f(after[4]) or f(after[4])<0:after[4]=after[6]
                after[4]=store(r(f(after[4])*f(after[7])));after[5]=store(r(f(after[5])+f(after[4])))
                for i,threshold in enumerate(thresholds):
                    after[8+i]=store(r(f(after[4])+f(after[8+i])))
                    if f(after[8+i])>=f(threshold):
                        after[11+i]=(-after[11+i])%2**32;difference=r(f(after[8+i])-f(threshold))
                        # Exact x87 cancellation under round-down produces -0.
                        after[8+i]=0x80000000 if difference==0 and mode==1 else store(difference)
                        if f(after[8+i])>=f(threshold):after[8+i]=0
                rows.append((p,mode,now,before,after))
    root=WS/'work/client-reference/loop-clock455';root.mkdir(parents=True,exist_ok=True);golden=bytearray(b'LC45'+struct.pack('<II',1,len(rows)))
    for p,mode,now,before,after in rows:golden+=struct.pack('<3I',p,mode,now)+struct.pack('<14I',*before)+bytes(40)+struct.pack('<14I',*after)+bytes(40)
    path=root/'loop-clock.bin';path.write_bytes(golden)
    report={'scope':'Complete selected R3CalculateTime flow and clock API/own state;not full client runtime acceptance','references':references,'cases':len(rows),'fp_modes':12,'golden':path.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'script_sha256':sha((WS/'scripts/audit_client455_loop_clock.py').read_bytes()),'oracle':'Fraction model from cached x87 instructions;finite fields,explicit float spills,unsigned wrapping,12precision-rounding modes. OS callback lifecycle separately exercised in native test.','raw_analysis':'artifacts/character-animation455/elapsed-*.json;ownedc215239f closed/save','remaining':['RTMovie event0x0B caller notported;only reference setter established','Original process timers/scheduling/frequency values not dynamically observed;no input EXE runs','NaN payload/unmasked exceptions/CPU feature process state not certified']}
    (WS/'inventory/client455-loop-clock-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:8ranges bothpins/{len(rows)}finite loop-state cases')
if __name__=='__main__':main()
