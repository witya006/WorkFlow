"""Pin Linker view/input/image-text contracts and generate independent small oracles."""
import hashlib,json,math,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_sprites import sprite
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def dimensions(raw):
    out={};pos=8
    for action in range(struct.unpack_from('<I',raw,4)[0]):
        count=struct.unpack_from('<I',raw,pos)[0];pos+=4
        for frame in range(count):
            fields=struct.unpack_from('<6I',raw,pos);pos+=24+fields[5];out[(action,frame)]=fields[:5]
    require(pos==len(raw),'SPR extent');return out

def main():
    evidence=WS/'artifacts/client455-progress/linker-window097-reference.json';raw=json.loads(evidence.read_text());metadata=raw['ranges']['result'];require(len(metadata)==len(raw['functions'])==36 and all(r['code'] and not r['truncated'] for r in raw['functions']),'Static function coverage');heads={r['fn']['addr'].lower():r['fn'] for r in metadata};assembly=[];tails=[];constants={}
    for body in raw['assembly']:
        lines=[r for p in body['pages'] for r in p['asm']['lines']];a=int(body['addr'],16);end=a+int(heads[body['addr']]['size'],16);require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'] and body['pages'][-1]['cursor']['done'],'Assembly completeness');assembly.append(dict(rva=hex(a-0x400000),instructions=len(lines)))
        tails.extend(dict(rva=hex(int(r['addr'],16)-0x400000),bytes=15) for r in lines if not a<=int(r['addr'],16)<end)
        if body['addr']=='0x667c70':
            for line in lines:
                for ref in line.get('refs',[]):
                    if ref['name'].startswith('dbl_'):constants[ref['addr']]=ref['name']
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Pin identity');ranges=[]
        for fn in [r['fn'] for r in metadata]+[dict(addr=addr,size='0x8') for addr in constants]+[dict(addr='0x501be1',size='0x15')]:
            a,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()))
        windows=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        if refs:require(ranges==refs[0]['ranges'] and windows==refs[0]['external_assembly_windows'],'Pins differ')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=windows))
    require(read_va(binary,0x501beb,1)==b'\x7d','Signed active-bank JGE');message_evidence=WS/'artifacts/client455-progress/linker-window097-message-assembly.json'
    doubles={name:struct.unpack('<d',read_va(binary,int(addr,16),8))[0] for addr,name in constants.items()};require({1024.,38.,461.,46.,19.,43.,22.,2.,40.,5.,3.,20.,24.,4.}<=set(doubles.values()),'Layout double geometry')
    def immediate(va,prefix,size):
        data=read_va(binary,va,len(prefix)+size);require(data.startswith(prefix),'Expected binary geometry/glyph operand');return int.from_bytes(data[len(prefix):],'little')
    panel=immediate(0x667cbd,b'\xc7\x45\xf4',4);height=immediate(0x667cc4,b'\xc7\x45\xf8',4);gap=immediate(0x668447,b'\x6b\xd2',1);offset=immediate(0x66844a,b'\x83\xc2',1)
    require((panel,height,gap,offset)==(481,46,44,24),'Integer layout geometry')
    indexes=[immediate(va,b'\xc6\x45\xfb',1) for va in [0x642916,0x642928,0x642937,0x642946,0x642955,0x642964,0x64297c,0x64298b,0x64299a]];require(indexes==list(range(10,19)),'Glyph MOV values')
    root=WS/'work/client-reference/linker-window455';root.mkdir(parents=True,exist_ok=True);inputs=[];fixtures=[];client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for row in load('client455-linker-owners-reference')['inputs']:
        check(row);dest=root/Path(row['file']).name;shutil.copyfile(WS/row['file'],dest);inputs.append(record(dest))
    geometry={}
    for name in ['main.spr','common.spr']:
        folder='zh-tw' if (client/'SpriteImage/zh-tw'/name).exists() else 'Common';original=client/'SpriteImage'/folder/name;dest=root/name;shutil.copyfile(original,dest);data=dest.read_bytes();info=sprite(data);geometry[name]=dimensions(data);inputs.append(dict(**record(dest),runtime_relative=f'SpriteImage/{folder}/{name}',original_sha256=sha(original),**info))
    def save(name,magic,rows,fmt):
        path=root/name;path.write_bytes(magic+struct.pack('<I',len(rows))+b''.join(struct.pack(fmt,*r) for r in rows));fixtures.append(record(path))
    layout=[]
    for width in [320,640,800,1023,1024,1280,1920]:
        scale=min(width/1024.,1.)
        for x,y in [(0,0),(-13,-7),(101,89)]:layout.append([width,x,y,int(panel*scale),int(461*scale),int(height*scale),int(38*scale),int(y+4*scale)-y]+[int(x+(gap*j+offset)*scale)-x for j in range(10)])
    save('window-layout.bin',b'LW97',layout,'<18i')
    cycle=[]
    for active in range(5):
        for mask in range(32):
            for next_ in [0,1]:
                candidate=active+(1 if next_ else 4)
                for _ in range(4):
                    if mask&(1<<(candidate%5)):break
                    candidate+=1 if next_ else -1
                cycle.append((active,mask,next_,candidate%5))
    save('window-cycle.bin',b'LC97',cycle,'<4I')
    events=[]
    for event in [1,8,5]:
        for flags in range(16):
            drag,control,shift,alt=[bool(flags&(1<<i)) for i in range(4)];kind,code,quantity=0,0,0
            if event==1:kind=1;code=0x502 if drag else 0x512 if alt else 0x510 if control else 0x504;quantity=0 if drag else 1
            elif event==8:
                if shift:kind,code=1,0x3327
                elif not drag:kind=2
            elif not drag:kind,code=1,0x501
            events.append((event,flags,kind,code,4|(9<<8)|(quantity<<16)))
    save('window-events.bin',b'LE97',events,'<5I')
    glyphs=[];mapping=dict(zip('%./:APM+,',indexes));mapping['-']=16;imageWidth=geometry['common.spr'][(7,3)][1]
    for width in [0,7,8,255,65535,2147483647,-2147483648]:
        for c in range(256):
            index=c-48 if 48<=c<=57 else mapping.get(chr(c),255);extent=(width*(index+1))&0xffffffff;extent=extent-0x100000000 if extent>=0x80000000 else extent
            glyphs.append((c,width,imageWidth,index if index!=255 and extent<=imageWidth else 255))
    save('window-glyphs.bin',b'LG97',glyphs,'<4i')
    report=dict(status='CONFIRMED_SELECTED',scope='Actual Linker window banked layout/controls/input dispatch and image-text glyph drawing;gameplay item actions/timers/livecallbacks stillopen',script_sha256=sha(Path(__file__)),references=refs,assembly=assembly,actual_instructions=sum(r['instructions'] for r in assembly),raw_evidence=[record(evidence)],decoded_doubles=doubles,decoded_integer_geometry=[panel,height,gap,offset],decoded_glyph_indexes=indexes,inputs=inputs,fixtures=fixtures,layout_cases=len(layout),cycle_cases=len(cycle),event_cases=len(events),glyph_cases=len(glyphs),sprite_geometry={name:{f'{a}:{f}':list(v) for (a,f),v in rows.items()} for name,rows in geometry.items()},
        gaps=['Full privateGUIItem/Window ABI,unsafe zero-width image-text/OOM/concurrency/reset/lifetime domains notaccepted',
            'Window emits455messages;complete CLinkBoard item-event handlers/use/cooldown/typed timer/liveSF-Animus callbacks/lock stillrequired;typed timer callers explicitlyrefuse',
            'CGUIImageText clipped formula preserves target observed behavior;all numeric/allocator/error domains notaccepted',
            'Untyped legacy/mixedkind callers/Macro35/Vending27/fullCItemBoard.Add/bootstrap/remainingboards/Trunk/protocol/Tutorial/Login/auth/game/M6F/M7/M9 remainmandatory'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report['raw_evidence'].append(record(message_evidence));report['active_bank_signed_branch']=dict(rva='0x101beb',opcode='7d',negative_values_store_low_BYTE=True)
    (WS/'inventory/client455-linker-window-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(ranges=len(refs[0]['ranges']),instructions=report['actual_instructions'],layout=len(layout),cycle=len(cycle),events=len(events),glyphs=len(glyphs),sprites=[r.get('runtime_relative') for r in inputs if 'runtime_relative'in r])))
if __name__=='__main__':main()
