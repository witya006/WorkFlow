"""Pin secondary-motion instructions/constants and independent scalar fixtures."""
import copy,hashlib,json,math,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from prepare_client455_legacy_runtime_inputs import parse

def sha(raw):return hashlib.sha256(raw).hexdigest()
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def pack_state(s):return struct.pack('<5f5i10fI',*s['v'],*s['d'],*s['lo'],*s['hi'],s['tick'])
def pack_globals(g):return struct.pack('<II3fIf',g['left'],g['right'],*g['position'],g['pony'],g['phase'])
NAMES=['plain','Bip01 Ponytail L1','Bip01 Ponytail L11','Bip01 R skirt','Bip01 L skirt','Bip01 B skirt']

def step(name,s,g,time,tilt):
    if (time-s['tick'])%2**32>10:
        s['tick']=time
        for i,weight in enumerate(map(f32,[1.3,1.2,.97,1,1])):
            if s['hi'][i]-.01<s['v'][i]:s['d'][i]=-1;s['v'][i]=f32(s['hi'][i]-.01)
            if s['lo'][i]+.01>s['v'][i]:
                s['d'][i]=1;s['v'][i]=f32(s['lo'][i]+.01)
                if s['lo'][i]<s['hi'][i]:
                    half=f32(s['hi'][i]*.5);s['hi'][i]=half
                    if s['lo'][i]+f32(.3)>half:s['hi'][i]=f32(s['lo'][i]+.3)
            half=s['hi'][i]*.5;difference=f32(abs(f32(half-s['v'][i])));rate=f32(((half-difference)*f32(.005)+.005)*(s['hi'][i]-s['lo'][i]))
            s['v'][i]=f32(rate*(s['d'][i]*weight)+s['v'][i])
    angles=[]
    if name==NAMES[1]:
        g['phase']=f32(g['phase']+f32(.001))
        if (time-g['pony'])%2**32>10:
            g['pony']=time;dz=f32(3-g['position'][2]);dy=f32(abs(f32(2-g['position'][1])))
            if dy>f32(.2):s['d'][3]=-1;s['lo'][3]=0;s['hi'][3]=1;s['v'][3]=f32(.4) if s['v'][3]>f32(.4) else s['v'][3]
            if dz<-.1:s['d'][3]=-1;s['lo'][3]=0;s['hi'][3]=1;s['v'][3]=f32(.1) if s['v'][3]>f32(.4) else s['v'][3]
            g['position']=[1,2,3]
        angles=[('Z',f32(f32(math.sin(g['phase']))*.2)),('X',f32(s['v'][3]*.5+f32(.1)))]
    if name==NAMES[2]:angles=[('X',f32(s['v'][3]*1.5))]
    if name in NAMES[3:5]:
        right=name==NAMES[3];key='right' if right else 'left'
        if tilt:
            s['d'][:3]=[-1]*3;s['lo'][:3]=[0]*3;s['hi'][:3]=[1.25]*3
            if (time-g[key])%2**32>10:
                g[key]=time;driven=1 if right else 0;centered=1-driven;s['v'][driven]=f32(s['v'][driven]+f32(.01));s['v'][2]=f32(s['v'][2]+f32(.01))
                if s['v'][centered]<.1980000029504299 or s['v'][centered]>.2020000030100346:s['v'][centered]=f32(s['v'][centered]-(s['v'][centered]-.2)*.8)
                if s['v'][driven]>.3:s['v'][driven]=f32(.3)
                if s['v'][2]>.3:s['v'][2]=f32(.3)
            s['hi'][2]=.5;s['hi'][0 if right else 1]=f32(.3)
        angles=[('A',s['v'][0 if right else 1])]
    if name==NAMES[5]:angles=[('Y',f32(.5-s['v'][2])),('Z',s['v'][2])]
    return angles

def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));refs=[];last=None;functions=[('secondary',0x91e270,0x80e),('borrow_actor_state',0x7cd430,0x105),('static_CIsin_dispatch_reference',0x873340,0x4f)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455')
        rows=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':sha(read_va(raw,va,size))} for name,va,size in functions]
        if last is not None and last!=rows:raise ValueError('Secondary bodies differ')
        last=rows;refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':rows})
    raw=(WS/'work/client-reference/reference-backup/RF_Online.bin').read_bytes();constant_addresses=[0xab03c8,0xb36b90,0xae5958,0xb3a5a8,0xb3a5a0,0xaa9730,0xaae568,0xaaa4b8,0xab0da8,0xb3a580,0xab0288,0xaaa3a0,0xaa9b98,0xb3a550,0xaab200,0xb3a540,0xb3a538,0xab0698]
    constants=[{'rva':hex(at-0x400000),'bits':read_va(raw,at,8).hex(),'double':struct.unpack('<d',read_va(raw,at,8))[0]} for at in constant_addresses]
    root=WS/'work/client-reference/character-secondary455';root.mkdir(parents=True,exist_ok=True);cases=[]
    for name in NAMES:
        for time in [10,11,0x10]:
            for bounded in [False,True]:
                state={'v':list(map(f32,[-.1,.9,.35,.8,.25] if bounded else [0]*5)),'d':[1]*5,'lo':[0]*5,'hi':list(map(f32,[.02,.5,.3,1,.5] if bounded else [1]*5)),'tick':0xfffffff8 if time==0x10 else 0};globals={'left':0,'right':0,'position':[0,0,4] if bounded else [0,0,0],'pony':0,'phase':f32(.25)};before=pack_state(state)+pack_globals(globals);angles=step(name,state,globals,time,bounded);cases.append((name,time,bounded,before,pack_state(state)+pack_globals(globals),angles))
    golden=bytearray(b'SS45'+struct.pack('<II',1,len(cases)))
    def text(s):
        b=s.encode('ascii');golden.extend(struct.pack('<H',len(b)));golden.extend(b)
    for name,time,tilt,before,after,angles in cases:
        text(name);golden+=struct.pack('<II',time,tilt)+before+after+struct.pack('<I',len(angles))
        for kind,angle in angles:golden+=kind.encode('ascii')+struct.pack('<f',angle)
    client=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455']);human=[]
    for original in ['Character/Player/Bone/Cora_Female.bn','Character/Player/Bone/CORFEMALE_ARMOR_061.bn']:
        source=client/original;data=source.read_bytes();parts=parse(data);names=[p['header'][:100].split(b'\0',1)[0].decode('ascii') for p in parts];chosen=[n for n in names if n in NAMES[1:]];target=root/f'human_{len(human)}.bn';target.write_bytes(data);human.append({'original':original,'copy':target.relative_to(WS).as_posix(),'sha256':sha(data),'parts':len(parts),'secondary_names':chosen})
    golden+=struct.pack('<I',len(human))
    for record in human:text(record['copy'])
    destination=root/'secondary.bin';destination.write_bytes(golden);report={'scope':'Secondary84/global28/pointer-and-time contract,source andselected scalar cases;staticCRT sine parity/normal consumers remainopen','references':refs,'constants':constants,'cases':len(cases),'golden':destination.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'human_models':human,'script_sha256':sha(Path(__file__).read_bytes()),'confirmed':['Owner84=5floatvalues+5signeddirections+5floatmin+5floatmax+DWORDtick;borrowed fromactor+500 throughmodel1184,FrameMove clears pointer','Unsigned timeGetTime delta>10,oncepereffect;globalponyphase andposition/left-right timers shared acrossactors','Skirt trigger isquaternionW*Z < -.2,notinitialweight1.3*1.2;timers use savedDWORDtime,notquaternionbits;decompilerstacktypeswrong','Pony preservestranslation afterrotationnormalization;L11 usesparentpose;R/Lskirt usemodelinverse1120/1056 andpose928/864;backskirt computesunusedRotationY beforeRotationZ','Source oscillator x87storeorder/constants preserved;current source sine ismandatory callback;reference static __CIsin includesSSE/defaultdispatch notrestored'], 'limits':['Scalar Python goldens finite/nearest53bit;notuncheckedNaN/OOM/CRTsin/arbitrarymatrix/fullreferenceexecution proof','Two humanBN fixtures arecontrolled inputs,notproof ofruntime character selection orstateconstructor defaults','No reference EXE executed;owned8115e37cclosed/save'],'raw_analysis':'artifacts/character-animation455/secondary-*.json andsecondary-insn.txt'}
    (WS/'inventory/client455-secondary-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'cases':len(cases),'human':human}))
if __name__=='__main__':main()
