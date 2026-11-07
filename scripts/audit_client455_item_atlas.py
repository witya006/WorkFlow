"""Decode target atlas mapping operands and stage real sprite/geometry oracles."""
import hashlib,json,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_sprites import sprite
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe

def pages(data):
    pos=8;out=[]
    for action in range(struct.unpack_from('<I',data,4)[0]):
        count=struct.unpack_from('<I',data,pos)[0];pos+=4
        for _ in range(count):
            fmt,w,h,tw,th,n=struct.unpack_from('<6I',data,pos);pos+=24+n
            if not action:out.append((w,h))
    require(pos==len(data),'SPR extent');return out

def main():
    evidence=WS/'artifacts/client455-progress/item-atlas093-reference.json';raw=json.loads(evidence.read_text());metadata=raw['ranges']['result']
    require(len(metadata)==17 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in raw['functions']),'Reference coverage')
    heads={r['fn']['addr']:r['fn'] for r in metadata};assembly=[];tails=[]
    for body in raw['assembly']:
        lines=[r for p in body['pages'] for r in p['asm']['lines']];a=int(body['addr'],16);end=a+int(heads[body['addr']]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],'Assembly incomplete');assembly.append(dict(rva=hex(a-0x400000),instructions=len(lines)))
        tails.extend(dict(rva=hex(int(r['addr'],16)-0x400000),bytes=15) for r in lines if not a<=int(r['addr'],16)<end)
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Changed pin');ranges=[]
        for fn in [r['fn'] for r in metadata]+[dict(addr='0x7b09d8',size=hex(72))]:
            a,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()))
        windows=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        if refs:require(ranges==refs[0]['ranges'] and windows==refs[0]['external_assembly_windows'],'Selected pins differ')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=windows))
    stores=[]
    def c6(va):
        data=read_va(binary,va,4);require(data[:2]==b'\xc6\x45','Expected byte store');stores.append(dict(rva=hex(va-0x400000),frame_offset=struct.unpack('b',data[2:3])[0],value=data[3]));return data[3]
    armor=[c6(0x7b0708+4*i) for i in range(10)];other=[c6(0x7b07e0+4*i) for i in range(30)]
    outer={i:c6(va) for i,va in [(1,0x7b0696),(2,0x7b06b1),(3,0x7b069f),(4,0x7b06a8),(6,0x7b06ba),(7,0x7b06c3),(8,0x7b06cc)]}
    root=WS/'work/client-reference/item-atlas455';root.mkdir(parents=True,exist_ok=True);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[];dimensions={}
    for target_id,name in [(6,'inventory.spr'),(8,'item.spr'),(19,'unitparts.spr')]:
        original=client/'SpriteImage/Common'/name;copy=root/name;shutil.copyfile(original,copy);data=copy.read_bytes();dimensions[target_id]=pages(data);inputs.append(dict(**record(copy),bytes=len(data),target_id=target_id,**sprite(data)))
    def plan(cls,id):
        top=cls>>28;kind=(cls>>16)&15;extension=(cls>>8)&255
        if top:return True,outer.get(top,0),id
        if kind==0:return extension<10,armor[extension] if extension<10 else 0,id
        if kind==1:return True,30 if extension in (29,30,31) else 0,id
        if kind==2:return True,4 if extension in (3,4,14) else 34 if extension==13 else 5,id
        if kind==3:
            if extension>=30:return False,0,id
            page=other[extension]
            if page==12 and id>=1024:return True,37 if id<2048 else 39,id-(1024 if id<2048 else 2048)
            return True,page,id
        if kind==4:return True,3 if extension<=5 else 23,id
        if kind==8:return True,38,id
        return False,0,id
    def divide(a,b):return a//b if b>0 else -(a//-b)
    def expected(kind,id,cls,width):
        ok,page,adjusted=plan(cls,id) if kind==0 else (True,cls,id);action,frame=0xaaaa,0xbbbb;success=False
        if kind==2:return (True,page,adjusted,True,(id>>8)&255,id&255)
        size=dimensions[8 if kind==0 else 19]
        if width and ok and page<len(size):
            w,h=size[page];action=(page<<8)&65535;columns=divide(w,width)
            if columns:
                divisor=columns&0xffffffff;action=(action|(adjusted%divisor))&65535;frame=(adjusted//divisor)&65535
                if frame<divide(h,width):success=True
                else:frame=0
        return ok,page,adjusted,success,action,frame
    classes=[(kind<<16)|(ext<<8) for kind,exts in [(0,list(range(11))+[255]),(1,[0,28,29,30,31,32,255]),(2,[0,3,4,12,13,14,15,255]),(3,list(range(31))+[255]),(4,[0,5,6,255]),(8,[0,255]) ] for ext in exts]+[k<<16 for k in [5,6,7,9,15]]+[i<<28 for i in range(1,16)]
    cases=[]
    def add(kind,id,cls,width):
        ok,page,adjusted,success,action,frame=expected(kind,id,cls,width)
        cases.append((kind,id,cls,width&0xffffffff,int(ok),adjusted,page,int(success),action,frame,action if success else 0,frame if success else 0))
    for cls in classes:
        for id in [0,1,255,256,1023,1024,2047,2048,0xffffffff]:add(0,id,cls,64)
    for width in [0,1,32,63,65,512,1024,65535,65536,-1,-64,-2147483648]:
        for id in [0,1,255,0x100000,0xffffffff]:add(0,id,1<<16,width)
    for page in [0,1,len(dimensions[19])-1,len(dimensions[19]),255,256,0xffffffff]:
        for id in [0,1,15,16,255,65536,0xffffffff]:add(1,id,page,64)
    for id in [0,1,0x302,0xabcd,0x12345678,0xffffffff]:add(2,id,0,0)
    fixture=root/'atlas-cases.bin';fixture.write_bytes(b'AT93'+struct.pack('<I',len(cases))+b''.join(struct.pack('<12I',*row) for row in cases))
    baseline=root/'item-icon092-native.json'
    if not baseline.exists():shutil.copyfile(WS/'inventory/client455-item-icon-native.json',baseline)
    previous=json.loads(baseline.read_text());require(previous['native']['status']=='PASS' and len(previous['frames'])==9,'Prior092 regression baseline')
    report=dict(status='CONFIRMED_SELECTED',scope='455item/unitparts/default atlas callbacks and typedGUIItem automatic core sprite selection;fullGUIItem children/gameplay still open',references=refs,assembly=assembly,actual_instructions=sum(r['instructions'] for r in assembly),regression_baseline=record(baseline),regression_frames=previous['frames'],
        script_sha256=sha(Path(__file__)),raw_evidence=[record(evidence)],decoded_byte_stores=stores,armor_pages=armor,other_pages=other,outer_pages=outer,inputs=inputs,fixtures=[record(fixture)],atlas_cases=len(cases),dimensions=dimensions,
        gaps=['Core typedSetSprite omits remaining61AF30 timer/overlay/common/lock child initialization;fullprivateGUIItemABI stillopen',
            'Source targetcache has55knownfilename slots;target manager has57slots;completeUnit registration/reload/error lifecycle remainsopen',
            'Actual payload-to-icon metadata/typedboard-hover/Linker integration,mixedconsumers and normal tablebootstrap remainopen',
            'Quest sentence expansion/fullpayload gameplay/36boards/Trunk/protocol/Tutorial/QBI/fourstage/Login/auth/game and priorM6F/M7/M9 gaps mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-atlas-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(ranges=18,instructions=report['actual_instructions'],decoded_stores=len(stores),cases=len(cases),dimensions=dimensions)))
if __name__=='__main__':main()
