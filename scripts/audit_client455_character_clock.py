"""Pin Character's separate millisecond clock and generate finite x87 goldens."""
import hashlib,json,struct
from fractions import Fraction
from audit_client455_animation_timing import binary_round
from build_client455_x87_math import read_va
from compare_client_binaries import WS
from audit_client455_effect_tables import loaded

def sha(data):return hashlib.sha256(data).hexdigest()
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def number(value):return Fraction(struct.unpack('<f',struct.pack('<I',value))[0])
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];last=None
    ranges=[('character_clock',0x91ea80,0x153),('duplicate_clock_no_found_xrefs',0x91ebe0,0x153),('main_loop_two_distinct_calls',0x7d13a2,10),('frame_consumer',0x924700,0x19e),('self_timed_frame_consumer',0x9248a0,0x1a3)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed pinned455')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for name,at,size in ranges]
        if last is not None and bodies!=last:raise ValueError('Clock code differs between pins')
        last=bodies
        if read_va(raw,0xb369b0,4)!=struct.pack('<f',2**32):raise ValueError('Changed unsigned correction')
        initial=[]
        for at,size in [(0x11894f8,4),(0x1189500,8),(0x1189508,8),(0x1189518,24)]:
            value=loaded(raw,at,size)
            if any(value):raise ValueError('Clock defaults not zero in PE image')
            initial.append({'rva':hex(at-0x400000),'bytes':size,'sha256':sha(value),'all_zero':True})
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'initial_globals':initial,'unsigned_bias':{'rva':'0x7369b0','bytes':4,'sha256':sha(read_va(raw,0xb369b0,4))}})
    def state(perf=1,freq=1000,previous=100,elapsed=.125,delta=.25,old=100,samples=0,window=0):
        return [1,perf,freq&0xffffffff,(freq>>32)&0xffffffff,previous&0xffffffff,(previous>>32)&0xffffffff,bits(elapsed),bits(delta),old,samples,window]
    cases=[(110,state()),(1000000007,state(freq=10000000,previous=1000000000)),(0x8000000000000001,state(freq=123456789,previous=0x8000000000000100)),(3,state(freq=3579545,previous=0xfffffffffffffffc)),(0x400000000000ffff,state(freq=3000000000,previous=1)),(0xfedcba9876543210,state(freq=9223372036854775807,previous=9)),(120,state(perf=0,window=180)),(121,state(perf=0,window=180)),(8,state(perf=0,old=0xfffffffc,window=190)),(3,state(perf=0,old=0,window=0xfffffffe)),(310,state(perf=0,samples=0x80000000)),(350,state(perf=0,samples=0xfffffffe)),(0x80000001,state(perf=0)),(150,state(perf=0,elapsed=20,delta=17))]
    rows=[]
    for precision in [24,53,64]:
        for mode in range(4):
            rounding=lambda x:binary_round(x,precision,mode)
            store=lambda x:bits(float(binary_round(x,24,mode)))
            signed64=lambda n:n if n<2**63 else n-2**64
            for now,before in cases:
                after=before.copy()
                if before[1]:
                    previous=before[4]|before[5]<<32;freq=before[2]|before[3]<<32
                    product=((now-previous)*1000)%2**64
                    after[4:6]=[now&0xffffffff,now>>32]
                    after[7]=store(rounding(Fraction(signed64(product),signed64(freq))))
                    after[6]=store(rounding(number(before[6])+number(after[7])));returned=product&0xffffffff
                else:
                    after[9]=(after[9]+1)%2**32;after[10]=(after[10]+now-after[8])%2**32
                    if after[10]>200:
                        unsigned=lambda n:rounding(Fraction(n)) if n>=2**31 else Fraction(n)
                        after[7]=store(rounding(unsigned(after[10])/unsigned(after[9])));after[9]=after[10]=0
                    after[8]=now;returned=now
                rows.append([precision,mode,now&0xffffffff,now>>32,*before,*after,returned])
    out=WS/'work/client-reference/character-clock455';out.mkdir(parents=True,exist_ok=True)
    golden=b'CC45'+struct.pack('<II',1,len(rows))+b''.join(struct.pack('<27I',*row) for row in rows)
    path=out/'clock.bin';path.write_bytes(golden)
    report={'scope':'Separate Character millisecond timer and actual normal bridge;not whole animation/game acceptance','references':refs,'golden':path.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'cases':len(rows),'fp_modes':12,'oracle':'Instruction-derived Fraction/x87 rounding with signed64 multiplication wrap, unsigned fallback bias, float spills; no clamp/scale and no fallback elapsed accumulation','script_sha256':sha((WS/'scripts/audit_client455_character_clock.py').read_bytes()),'gaps':['Failure-without-output QPC/QPF leaves original unspecified stack bytes; source zero seed is not equivalent in that domain','Unmasked exceptions/NaN payloads/process timer scheduling not accepted','Frame methods924700/9248A0 are reference consumers, not newly restored normal animation APIs; full lifecycle remains open']}
    (WS/'inventory/client455-character-clock-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:Character timer pinned;'+str(len(rows))+'finite state cases/12FP modes')
if __name__=='__main__':main()
