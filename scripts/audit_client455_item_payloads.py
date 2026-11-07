"""Pin Item framing/fresh payloads and build source-independent real-data oracles."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_language import decode,key_bytes,encode_with_envelope
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def word(data,at):return struct.unpack_from('<I',data,at)[0]
def table(data,at):
    n,s=struct.unpack_from('<II',data,at);start=at+8;end=start+n*s
    require(end<=len(data),'Table extent');return dict(count=n,stride=s,data=bytearray(data[start:end])),end
def sequential(data,n):
    out=[];at=0
    for i in range(n):row,at=table(data,at);out.append(row)
    require(at==len(data),'Unexpected root tail');return out
def item_tables(data):
    rows=[dict(count=0,stride=0,data=bytearray()) for _ in range(47)];at=0;sections=[];arrays=None
    while at<len(data):
        tag,n,offset=struct.unpack_from('<HII',data,at);end=offset+n+10;require(offset==at and end<=len(data),'Supplied section seek')
        ident=tag-0xf100 if 0xf100<=tag<=0xf12d else 46 if tag==0xf12f else None
        if ident is not None:
            rows[ident],used=table(data,at+10);require(used==end,'Supplied table section tail')
        elif tag==0xf130:arrays=data[at+10:end];require(len(arrays)==376,'Item directory')
        sections.append(dict(tag=hex(tag),offset=offset,bytes=n,index=ident));at=end
    require(arrays is not None and len(sections)==48,'Missing sections')
    return rows,arrays,sections
def flat(rows,arrays):return b''.join(struct.pack('<II',r['count'],r['stride'])+r['data'] for r in rows)+arrays
def localized(base_rows,nd):
    rows=[dict(count=r['count'],stride=r['stride'],data=bytearray(r['data'])) for r in base_rows];at=0;names=[]
    for kind,row in enumerate(rows):
        if kind in [44,45]:continue
        count=word(nd,at);at+=4;names.append(dict(kind=kind,count=count,base_count=row['count']))
        for i in range(min(count,row['count'])):
            where=i*row['stride']+8;row['data'][where:where+64]=nd[at+i*64:at+(i+1)*64]
        at+=count*64
    descriptions_start=at;counts=[]
    for kind in range(47):
        count=word(nd,at);at+=4;counts.append(count)
        for i in range(count):n=word(nd,at+8);at+=12+n;require(at<=len(nd),'Description extent')
    dungeons=word(nd,at);at+=4
    for i in range(dungeons):n=word(nd,at+68);at+=72+n;require(at<=len(nd),'Dungeon extent')
    return rows,nd[descriptions_start:at],dict(names=names,descriptions=sum(counts),dungeons=dungeons,consumed=at,tail=len(nd)-at)
def envelope(raw,plain):
    n=word(raw,29);encoded=raw[33+n:289+n];key=key_bytes(encoded)
    cipher=bytes((v+(key[(i+1)%256] if i%2==0 else -key[(i+1)%256]))&255 for i,v in enumerate(plain))
    out=raw[:29]+struct.pack('<I',len(plain))+cipher+encoded
    require(decode(out)==plain,'Own fixture envelope round trip');return out
def states(rows,quest):
    cases=[]
    for kind,row in enumerate(rows):
        if not row['count']:continue
        for index in sorted({0,row['count']//2,row['count']-1}):
            for selector in [0,2,3,4]:cases.append((selector,kind,index))
    cases += [(6,0,0),(255,0,0)]
    cases += [(5,17,index) for index in [0,quest[7]['count']//2,quest[7]['count']-1]+[0xf0000000+i for i in range(6)]]
    packed=[];unsafe=0
    for selector,kind,index in cases:
        payload=selector if 2<=selector<=5 else 0;size={0:200,2:136,3:192,4:100,5:116}[payload]
        mask=bytearray(size);value=bytearray(size);status=0
        def put(at,n,width=4):mask[at:at+width]=bytes([255])*width;value[at:at+width]=int(n).to_bytes(width,'little')
        def zero(at,n):mask[at:at+n]=bytes([255])*n;value[at:at+n]=bytes(n)
        actual_index=index
        if payload==5 and index>=0xf0000000:actual_index=index-(0xf0000000 if index<0xf0000003 else 0xf0000003)+quest[7]['count']-(9 if index<0xf0000003 else 3)
        row=quest[7] if payload==5 else rows[kind];start=actual_index*row['stride'];data=row['data']
        put(4,index|0xf0000000 if payload==5 else index|(kind<<24)|0xf0000000)
        put(8,index|0xf0000000 if payload==5 else index|(kind<<24)|0xf0000000)
        put(12,payload,1);put(20,0,1);put(21,0,1);put(88,0)
        metadata_kind=data[start+88] if payload!=5 else 0
        equipment=1<=metadata_kind<=10;split=metadata_kind in {13,16,17,20,22,23,26,30,31,32,34,35}
        def maximum():
            at=168 if equipment or metadata_kind in [19,27] else 152 if metadata_kind==15 else 160 if metadata_kind in [11,33] else 220 if metadata_kind in [42,43] else 172 if metadata_kind==34 else None
            if at is None:return 0
            return word(data,start+at)
        try:
            if payload==0:
                put(92,1,1);put(96,0 if split else maximum());put(104,0 if split else maximum());put(108,0)
                put(112,data[start+160] if equipment else 0,1);put(113,0,1);put(184,0,1);put(192,0,1);put(188,0)
                zero(116,28);zero(144,32);put(148,0x3f800000);put(157,255,1)
            elif payload==2:
                for at in [92,96,104,108,112,116,124,128]:put(at,0)
            elif payload in [3,4]:
                put(92,maximum());put(96,0)
                if payload==3:
                    zero(100,64);put(164,0,1);put(165,255,1);put(166,255,1)
                    for at in [168,172,176,180]:put(at,0)
            else:put(92,255,1);put(93,kind,1);zero(96,12);put(108,0)
        except (IndexError,struct.error):status=1;unsafe+=1
        name=bytes(64) if payload==5 else bytes(data[start+8:start+72])
        packed.append(struct.pack('<8I',selector,kind,index,payload,size,word(data,start),int(payload==5),status)+mask+value+name)
    return b'IP89'+struct.pack('<I',len(packed))+b''.join(packed),len(packed),unsafe
def main():
    raw_path=WS/'artifacts/client455-progress/item-payloads089-reference-complete.json';raw=json.loads(raw_path.read_text())
    require(len(raw['functions'])==50 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines'] for r in raw['functions']),'Incomplete pseudocode')
    metadata=raw['ranges']['result'];require(len(metadata)==50 and all(r['fn'] and not r['error'] for r in metadata),'Missing function')
    heads={r['fn']['addr'].lower():r['fn'] for r in metadata};assembly=[];tails=[]
    for body in raw['assembly']:
        lines=[line for page in body['pages'] for line in page['asm']['lines']];begin=int(body['addr'],16);end=begin+int(heads[body['addr'].lower()]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'],'Incomplete assembly')
        for line in lines:
            va=int(line['addr'],16)
            if not begin<=va<end:tails.append(dict(rva=hex(va-0x400000),bytes=15,owner_rva=hex(begin-0x400000)))
        assembly.append(dict(rva=hex(begin-0x400000),instructions=len(lines)))
    require(len(assembly)==19 and sum(r['instructions'] for r in assembly)==1796,'Assembly coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    language=json.loads((WS/'inventory/client455-language-reference.json').read_text());taiwan=language['references'][0]['codepages'][8]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Changed pin')
        ranges=[]
        for row in metadata:
            fn=row['fn'];va,n=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(va-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,va,n)).hexdigest()))
        extra=[dict(**r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in tails]
        address=0x400000+int(taiwan['vtable_rva'],16)+160;pointer=read_va(binary,address,4)
        require(int.from_bytes(pointer,'little')==0x82c490,'Installed profile does not select segmented Item branch')
        if references:require(references[0]['ranges']==ranges and references[0]['external_assembly_windows']==extra,'Selected functions differ')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=extra,
            Taiwan_item_flag=dict(slot_rva=hex(address-0x400000),slot_bytes=pointer.hex(),method_rva='0x42c490',value=1)))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);root=WS/'work/client-reference/item-payloads455';root.mkdir(parents=True,exist_ok=True)
    inputs=[];payloads={};encoded={}
    paths=[('item.edf',client/'DataTable/Item.edf'),('quest.edf',client/'DataTable/Quest.edf'),('character.edf',client/'DataTable/Character.edf')]+[(f'nd-{locale}.edf',client/f'DataTable/{locale}/NDItem.edf') for locale in ['zh-tw','ko-kr','ru-ru']]
    for name,path in paths:
        data=path.read_bytes();plain=decode(data);require(encode_with_envelope(data,plain)==data,'EDF round trip')
        copy=root/name;copy.write_bytes(data);payloads[name]=plain;encoded[name]=data;inputs.append(dict(original=str(path),original_sha256=sha(path),**record(copy)))
    rows,arrays,sections=item_tables(payloads['item.edf']);quest=sequential(payloads['quest.edf'],12);character=sequential(payloads['character.edf'],7)
    require(sum(r['count'] for r in rows)==76049 and character[6]['count']==648 and quest[7]['count']==2895,'Supplied corpus changed')
    fixtures=[];locale_info=[];localized_rows=None
    def save(name,data):path=root/name;path.write_bytes(data);fixtures.append(record(path))
    save('base.tables',flat(rows,arrays));save('flat.edf',envelope(encoded['item.edf'],flat(rows,arrays)))
    for locale in ['zh-tw','ko-kr','ru-ru']:
        localized_rows_current,descs,info=localized(rows,payloads['nd-'+locale+'.edf']);locale_info.append(dict(locale=locale,**info))
        save(locale+'.tables',flat(localized_rows_current,arrays));save(locale+'.descriptions',descs)
        if locale=='zh-tw':localized_rows=localized_rows_current
    save('quest.tables',payloads['quest.edf']);save('character.tables',payloads['character.edf'])
    cases,n,unsafe=states(localized_rows,quest);save('cases.bin',cases)
    level_cases=[];levels=character[6]
    for kind in list(range(8))+[255]:
        limits=[struct.unpack_from('<Q',levels['data'],i*levels['stride']+1)[0] for i in range(kind*81,min(kind*81+81,levels['count']))]
        values={0,1,0xffffffffffffffff}
        if limits:
            for value in [limits[0],limits[len(limits)//2],limits[-1]]:values|={value,max(0,value-1),min(0xffffffffffffffff,value+1)}
        for experience in sorted(values):
            found=next((kind*81+i for i,value in enumerate(limits) if experience<value),None)
            if found is None and experience and limits:found=kind*81+80
            level_cases.append(struct.pack('<IQI',kind,experience,0xffffffff if found is None else found))
    save('levels.bin',b'AL89'+struct.pack('<I',len(level_cases))+b''.join(level_cases))
    unknown=bytearray(payloads['item.edf']);struct.pack_into('<H',unknown,0,0xf12e);save('unknown.edf',envelope(encoded['item.edf'],unknown))
    bad=bytearray(payloads['item.edf']);struct.pack_into('<I',bad,6,len(bad));save('bad-offset.edf',envelope(encoded['item.edf'],bad))
    report=dict(status='CONFIRMED_SELECTED',scope='Item47 framing/localization/descriptions and five fresh payload factories with Character/Quest inputs;ordinary game binding open',
        references=references,assembly=assembly,actual_instructions=1796,raw_evidence=[record(raw_path)],inputs=inputs,fixtures=fixtures,
        sections=sections,item_rows=76049,quest_rows=2895,animus_level_rows=648,locales=locale_info,factory_cases=n,bounded_unsafe_cases=unsafe,level_cases=len(level_cases),
        script_sha256=sha(Path(__file__)),edf_helper_sha256=sha(WS/'scripts/audit_client455_language.py'),
        previous_SF_reference_sha256=sha(WS/'inventory/client455-skill-force-items-reference.json'),
        gaps=['Ordinary global/CItemObject/CResObject/board/hover/Linker/5x10 UI/network/game still open',
            'Fresh factory states are not full payload gameplay/copy/mutation/live UI methods or private C++ ABI',
            'Quest sentence expansion/localized Quest data and other Character consumers remain required',
            'Reload/duplicate table old-owner lifetime and unsafe out-of-owner/OOM/unwind domains not accepted',
            'Generic flag0 flat branch uses a generated real-table fixture;installed profile uses flag1 segmented'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-payloads-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(rows=76049,cases=n,unsafe=unsafe,levels=len(level_cases),locales=[{k:r[k] for k in ['locale','descriptions','dungeons','tail']} for r in locale_info])))
if __name__=='__main__':main()
