"""Pin frame producer/init bodies and construct an exact rational x87 oracle."""
import hashlib,json,struct
from fractions import Fraction
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(b):return hashlib.sha256(b).hexdigest()
def binary_round(v,p,mode):
    if not v:return v
    negative=v<0;x=abs(v);e=x.numerator.bit_length()-x.denominator.bit_length()
    if x<Fraction(2)**e:e-=1
    step=Fraction(2)**(e-p+1);scaled=x/step;q,r=divmod(scaled.numerator,scaled.denominator)
    if mode==0:q+=int(2*r>scaled.denominator or (2*r==scaled.denominator and q%2))
    elif mode==1:q+=int(negative and r!=0)
    elif mode==2:q+=int(not negative and r!=0)
    return (-1 if negative else 1)*q*step
def exact_frame(current,carry,elapsed,speed,p,mode):
    if elapsed&0x7f800000==0x7f800000 or speed&0x7f800000==0x7f800000:return 0
    f=lambda bits:Fraction(struct.unpack('<f',struct.pack('<I',bits))[0]);r=lambda n:binary_round(n,p,mode)
    value=r(f(elapsed)*1000);value=r(value*5);value=r(value+carry);spill=binary_round(value,53,mode);value=r(f(speed)*spill);value=r(value+current);integer=int(value)
    return integer%2**32 if -(2**63)<=integer<2**63 else 0
def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));refs=[];last=None;functions=[('frame_producer',0x7cd560,0x2ab),('animation_ctor',0x7ccc30,0x60),('secondary_ctor',0x91c490,0x76),('secondary_ctor_wrapper',0x7cd1b0,0x1e),('elapsed_getter',0x8b3e30,7),('speed_getter',0x448180,0x19)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for name,at,n in functions]
        if last is not None and last!=bodies:raise ValueError('Timing bodies differ')
        last=bodies
        if struct.unpack('<d',read_va(raw,0xaa9890,8))[0]!=1000.0 or struct.unpack('<d',read_va(raw,0xaa9778,8))[0]!=5.0:raise ValueError('Changed frame rate constants')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies})
    rows=[];times=[0,0x80000000,0x3d03126f,0x3c888889,0x3f800000,0xbf000000,0x00000001,0x7f7fffff,0x7fc00001,0x7f800000];speeds=[0,0x3f800000,0x3f000001,0xbf800000,0x3f8ccccd]
    for p in [24,53,64]:
        for mode in range(4):
            # A real frame boundary: old modern float expression gives310,
            # reference PC53-nearest double-spill path gives309 at .03f seconds.
            rows.append((p,mode,160,0,0x3cf5c28f,0x3f800000,exact_frame(160,0,0x3cf5c28f,0x3f800000,p,mode)))
            for i,dt in enumerate(times):
                for j,speed in enumerate(speeds):
                    current=[160,0xffffffff,0x80000001][(i+j)%3];carry=[0,0xffffffff,17][(i+2*j)%3];rows.append((p,mode,current,carry,dt,speed,exact_frame(current,carry,dt,speed,p,mode)))
    root=WS/'work/client-reference/character-timing455';root.mkdir(parents=True,exist_ok=True);golden=bytearray(b'AT45'+struct.pack('<II',1,len(rows)))
    for row in rows:golden+=struct.pack('<7I',*row)
    control=bytearray(100);struct.pack_into('<If',control,4,0xffffffff,1)
    for i in range(10):struct.pack_into('<I',control,16+4*i,0xffffffff)
    state=struct.pack('<5f5i10fI',.8,0,.4,0,0,*([1]*5),0,0,-.2,0,0,1.3,.9,.7,1,.5,0);golden+=control+state;target=root/'timing.bin';target.write_bytes(golden)
    report={'scope':'Normal client frame advance numeric contract andknown100/84byte constructors;not full actor/renderer acceptance','references':refs,'golden':target.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'cases':len(rows),'fp_modes':12,'oracle':'Independent Fraction precision24/53/64 and4rounding modes;double spill then signed64 truncation/lowDWORD. Masked nonfinite input yields integer-indefinite low0.','script_sha256':sha((WS/'scripts/audit_client455_animation_timing.py').read_bytes()),'confirmed':['CResObject7CD560 highlevel branches matchlegacy source;reference numericelapsedfloat*1000double*5double+unsignedcarry,spilldouble,speedfloat multiply+unsignedcurrent,truncate signed64/lowDWORD','CAnimation ctor7CCC30 zeros100,IDminus1/speed1,10invalid effectframes;91C490 initializesknown84secondaryinline region','Stop flag512 preventsadvance andretainscarry;loop256 restores160/old0;interpolationflag2048 advancesIPtime notboneframe;postwrite alwayspublishesmodel672 whenboneexists'],'limits':['Caller source stilluseslegacytypedCBone modelABI;455FrameMove/D3D9normalconsumer integration remainsopen','Masked FP oracle,notunmaskedtrap/full process FPU exception-state proof','Frame timing comesfromactualsourceR3GetLoopTime;full upstream455 elapsedclock equivalence notproved'],'raw_analysis':'artifacts/character-animation455/timing-*.json;owned77611a53closed/save'}
    (WS/'inventory/client455-animation-timing-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:6pinned ranges,{len(rows)}exact-rational cases,12FPmodes')
if __name__=='__main__':main()
