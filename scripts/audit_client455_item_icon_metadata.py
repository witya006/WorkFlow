"""Pin physical icon metadata/usable rules and build real table-based oracles."""
import hashlib,json,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record,item_tables,localized
from audit_client455_language import decode
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def main():
    evidence=WS/'artifacts/client455-progress/item-metadata094-reference.json';raw=json.loads(evidence.read_text());metadata=raw['ranges']['result'];require(len(metadata)==22 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in raw['functions']),'Static coverage')
    heads={r['fn']['addr']:r['fn'] for r in metadata};assembly=[];tails=[]
    for body in raw['assembly']:
        lines=[r for p in body['pages'] for r in p['asm']['lines']];a=int(body['addr'],16);end=a+int(heads[body['addr']]['size'],16);require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],'Assembly extent');assembly.append(dict(rva=hex(a-0x400000),instructions=len(lines)))
        tails.extend(dict(rva=hex(int(r['addr'],16)-0x400000),bytes=15) for r in lines if not a<=int(r['addr'],16)<end)
    extra=[(0xaa9264,68),(0xaabf4c,68),(0xaa94c4,68),(0xaa9664,68),(0xaac0bc+136,4),(0xadd5ac+208,16)]
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Reference pin');ranges=[]
        for fn in [r['fn'] for r in metadata]+[dict(addr=hex(a),size=hex(n)) for a,n in extra]:
            a,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()))
        windows=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        if refs:require(ranges==refs[0]['ranges'] and windows==refs[0]['external_assembly_windows'],'Pins differ')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=windows))
    offsets=[]
    def displacement(va,prefix,width):
        data=read_va(binary,va,len(prefix)+width);require(data.startswith(prefix),'Expected metadata read instruction');value=int.from_bytes(data[len(prefix):],'little');offsets.append(dict(rva=hex(va-0x400000),displacement=value));return value
    mesh=displacement(0x41695d,b'\x8b\x40',1);icon=displacement(0x465ebd,b'\x8b\x40',1);grade=displacement(0x45fdfe,b'\x8a\x81',4);quantity=displacement(0x404e8f,b'\x8a\x40',1)
    addresses={27:0x45fffc,13:0x460020,25:0x460044,26:0x460068,28:0x46008c,33:0x4600b0,34:0x4600d4,35:0x4600f8,36:0x46011c,31:0x46013a,30:0x460158}
    levels={kind:displacement(va,b'\x8a\x81',4) for kind,va in addresses.items()};equipmentLevel=levels[27]
    mask_code=read_va(binary,0x61c9de,5);require(mask_code[0]==0x25,'AND EAX mask');user_mask=int.from_bytes(mask_code[1:],'little');require(user_mask==0x0ff00000,'User field mask')
    for vt,expected in [(0xaa9264,0x404e80),(0xaabf4c,0x405c60),(0xaa94c4,0x405c60),(0xaa9664,0x405c60)]:require(int.from_bytes(read_va(binary,vt+64,4),'little')==expected,'Quantity virtual slot')
    root=WS/'work/client-reference/item-icon-metadata455';root.mkdir(parents=True,exist_ok=True);base=load('client455-item-object-reference');inputs=[]
    wanted=['item.edf','nd-zh-tw.edf','quest.edf','character.edf','base.edf','zh-tw.edf','cases.bin']
    for name in wanted:
        choices=[r for r in base['inputs'] if Path(r['file']).name==name];require(choices and len({r['sha256'] for r in choices})==1,'Unambiguous input '+name);check(choices[0]);copy=root/name;shutil.copyfile(WS/choices[0]['file'],copy);inputs.append(record(copy))
    for row in load('client455-item-icon-reference')['inputs']:
        check(row);copy=root/Path(row['file']).name;shutil.copyfile(WS/row['file'],copy);inputs.append(record(copy))
    rows,_,_=item_tables(decode((root/'item.edf').read_bytes()));rows,_,_=localized(rows,decode((root/'nd-zh-tw.edf').read_bytes()));cases=(root/'cases.bin').read_bytes();require(cases[:4]==b'IP89','Case matrix');at=8;out=[];samples=[];seen=set();bounded=0
    for _ in range(int.from_bytes(cases[4:8],'little')):
        selector,kind,index,payload,size,_,quest,_=struct.unpack_from('<8I',cases,at);at+=32+size*2+64;result=[selector,kind,index,0,0,0,0,0,2 if quest else 0]
        if not quest:
            table=rows[kind];data=table['data'];start=index*table['stride']
            try:
                item_id=struct.unpack_from('<I',data,start+mesh)[0];sprite_id=struct.unpack_from('<I',data,start+icon)[0];equip=data[start+88];level_at=equipmentLevel if 1<=equip<=10 else levels.get(equip)
                req=data[start+level_at] if level_at is not None else 0;frame=data[start+grade] if 1<=equip<=10 else 0;result[3:8]=[item_id,sprite_id,1,req,frame]
                if selector==0 and index>0 and sprite_id>0 and item_id!=0xffffffff and kind not in seen and len(samples)<16:seen.add(kind);samples.append((selector,kind,index))
            except (IndexError,struct.error):result[8]=1;bounded+=1
        out.append(result)
    require(at==len(cases) and len(out)==575 and len(samples)==16,'Real case/sample coverage')
    fixture=root/'metadata-cases.bin';fixture.write_bytes(b'MD94'+struct.pack('<I',len(out))+b''.join(struct.pack('<9I',*r) for r in out))
    sample=root/'metadata-samples.bin';sample.write_bytes(b'MS94'+struct.pack('<I',len(samples))+b''.join(struct.pack('<3I',*r) for r in samples))
    usable=[];race_masks={0:1,1:2,2:4,3:8,4:16,5:21,6:10,7:3,8:12,9:15,10:31,11:21,255:21}
    for user,mask in race_masks.items():
        for race in [0,1,2,3,4,5,254,255]:
            allowed=bool(mask&(1<<race)) if race<5 else user==10 or user==9 or (user==6 and race%2==1) or (user in [5,11,255] and race%2==0)
            for level,required in [(0,0),(1,2),(2,2),(254,255),(255,254)]:usable.append(((user<<20)&user_mask,race,level,required,int(allowed and (level==255 or required==255 or level>=required))))
    use=root/'usable-cases.bin';use.write_bytes(b'US94'+struct.pack('<I',len(usable))+b''.join(struct.pack('<5I',*r) for r in usable))
    report=dict(status='CONFIRMED_SELECTED',scope='Basic physical icon fields/race-level predicate and real inventory icon-owner handoff;not fullCItemBoard.Add or fullgame',script_sha256=sha(Path(__file__)),references=refs,assembly=assembly,actual_instructions=sum(r['instructions'] for r in assembly),raw_evidence=[record(evidence)],decoded_offsets=offsets,user_mask=hex(user_mask),inputs=inputs,fixtures=[record(fixture),record(sample),record(use)],metadata_cases=len(out),bounded_metadata_cases=bounded,real_inventory_samples=16,usable_cases=len(usable),
        gaps=['SF/Quest dedicated metadata/units remainexplicit;Basic2/3/4 metadata is not fullAnimus/MAUwindow integration',
            'Inventory handoff uses actualCGUIInventoryBoard and caller race;full ordinaryCItemBoard.Add clone/notifications/cooldown/board6-35-27 dependencies and event/remove integration remainopen',
            'Global legacyboard IsEqualItemType and mixedderived consumers need coordinatedmigration;do not cast typedbasewrappers to oldpayloadclasses',
            'FullGUIItemchildren/copy/sharedquantity-usability propagation/targetUnit57lifecycle/normalbootstrap/Linker/Tutorial/Login/auth/game and priorM6F/M7/M9 gaps remainmandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-icon-metadata-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(ranges=28,instructions=report['actual_instructions'],cases=575,bounded=bounded,samples=16,usable_cases=len(usable))))
if __name__=='__main__':main()
