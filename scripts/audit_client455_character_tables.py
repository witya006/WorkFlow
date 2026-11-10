"""Pin character-table loaders and build independent compact corpus oracles."""
import ctypes,hashlib,json,struct,zlib
from pathlib import Path
from audit_client455_language import decode,encode_with_envelope
from audit_client455_item_payloads import table,sequential
from audit_client455_skill_force_items import tables as sf_tables,localized_payload
from audit_client455_resource_catalog import sha,record
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

lead=ctypes.WinDLL('kernel32.dll').IsDBCSLeadByteEx;lead.argtypes=[ctypes.c_uint,ctypes.c_ubyte];lead.restype=ctypes.c_int
def character_localized(base,names,cp,dbcs_fixture=False):
    rows=[dict(count=row['count'],stride=row['stride'],data=bytearray(row['data'])) for row in base];names=bytearray(names);at=0;patch_at=None;failed_reads=0;declared=0
    def read(size):
        nonlocal at,failed_reads
        if size>len(names)-at:failed_reads+=1;return None
        out=names[at:at+size];at+=size;return out
    for group in range(4):
        header=read(4)
        if header is not None:declared=struct.unpack('<I',header)[0]
        read(4);row=rows[group]
        for i in range(row['count']):
            start=i*row['stride']
            def copy(offset,size):
                value=read(size)
                if value is not None:row['data'][start+offset:start+offset+size]=value
            if group==0:copy(112,32);copy(508,1024)
            elif group==1:
                for j in range(3):copy(1+32*j,32)
            elif group==2:
                if dbcs_fixture and i==0:patch_at=at;names[at:at+32]=b'A'*30+b'\xb0\xa1'
                value=read(32)
                if value is None:value=bytearray(row['data'][start+8:start+40])
                if value[31]:
                    value[31]=0;position=0
                    while position<=30:
                        if lead(cp,value[position]):
                            if position==30:value[30]=0;break
                            position+=2
                        else:position+=1
                row['data'][start+8:start+40]=value
            else:copy(12,32)
        if declared>row['count'] and group<3:
            if read((declared-row['count'])*(1056 if group==0 else 32)) is None:return rows,bytes(names),at,patch_at,failed_reads,False
    return rows,bytes(names),at,patch_at,failed_reads,True

def store_localized(base,names):
    count=struct.unpack_from('<I',names)[0];row=dict(count=base['count'],stride=2076,data=bytearray(base['data']));descs=[b'']*base['count'];at=4
    if count!=row['count']:return row,descs,False
    for i in range(count):
        assert len(names)-at>=136;ignored=struct.unpack_from('<I',names,at)[0];at+=4;start=i*2076
        row['data'][start+17:start+81]=names[at:at+64];at+=64;row['data'][start+81:start+145]=names[at:at+64];at+=64
        n=struct.unpack_from('<I',names,at)[0];at+=4;assert n<=len(names)-at;descs[i]=names[at:at+n];at+=n
    return row,descs,True

def main():
    raw_file=WS/'artifacts/client455-progress/character-tables143-reference/session.json';raw=json.loads(raw_file.read_text());functions=[]
    for entry in raw['ranges']['result']:
        addr=int(entry['fn']['addr'],16);pages=raw['asm'][entry['query']];assert pages[-1]['cursor']['done']
        lines=[line for page in pages for line in page['asm']['lines']];starts={int(line['addr'],16) for line in lines}
        assert len(starts)==len(lines)==pages[0]['total_instructions'] and all(len(p['asm']['lines'])<=100 for p in pages)
        cfg=next(r for r in raw['cfg']['result'] if int(r['addr'],16)==addr);assert cfg['cursor']['done'] and cfg['count']==cfg['total_blocks']
        blocks=[b for b in cfg['blocks'] if b['size']>0];assert all(int(b['start'],16) in starts for b in blocks)
        assert all(any(int(b['start'],16)<=a<int(b['end'],16) for b in blocks) for a in starts)
        regions=[]
        for b in sorted(blocks,key=lambda b:int(b['start'],16)):
            first,last=int(b['start'],16),int(b['end'],16)
            if regions and regions[-1][1]==first:regions[-1][1]=last
            else:regions.append([first,last])
        functions.append(dict(rva=hex(addr-0x400000),instructions=len(lines),positive_cfg_blocks=len(blocks),regions=[dict(rva=hex(a-0x400000),bytes=b-a) for a,b in regions]))
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();assert sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86'
        refs.append(dict(**record(path),architecture='x86',image_base='0x400000',functions=[dict(f,regions=[dict(r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in f['regions']]) for f in functions]))
    assert refs[0]['functions']==refs[1]['functions'] and len(functions)==15
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);root=WS/'artifacts/client455-character-tables';root.mkdir(exist_ok=True)
    player_file=client/'DataTable/PlayerCharacter.edf';player,_=table(decode(player_file.read_bytes()),0)
    char_file=client/'DataTable/Character.edf';character=sequential(decode(char_file.read_bytes()),7)
    sf_file=client/'DataTable/SkillForce.edf';sf_base=decode(sf_file.read_bytes());cases=[]
    for locale,setting,cp,selector,fixture in [('ko-kr','Korea',949,-1,False),('zh-tw','Taiwan',950,-1,False),('ru-ru','Russia',1251,-1,False),('zh-tw','Taiwan',950,1,False),('ko-kr','Korea',949,-1,True)]:
        suffix='' if selector==-1 else f'_{selector}';store_file=client/f'DataTable/Store{suffix}.edf';plain=decode(store_file.read_bytes());n,ignored=struct.unpack_from('<II',plain);assert n<=(len(plain)-8)//2076
        store=dict(count=n,stride=2076,data=plain[8:8+n*2076]);store_names=client/f'DataTable/{locale}/NDStore.edf';store,descs,store_ok=store_localized(store,decode(store_names.read_bytes()))
        sf_names=client/f'DataTable/{locale}/NDSkillForce.edf';sf_local,sf_failed=localized_payload(sf_base,decode(sf_names.read_bytes()));sf,_=sf_tables(sf_local)
        char_names=client/f'DataTable/{locale}/NDCharacter.edf';char_rows,nd,consumed,patched,short_reads,char_ok=character_localized(character,decode(char_names.read_bytes()),cp,fixture)
        inputs=[player_file,char_file,sf_file,store_file,store_names,sf_names,char_names];override=None
        name=locale+('-store1' if selector==1 else '-dbcs' if fixture else '-default')
        if fixture:
            override=root/(name+'.edf');override.write_bytes(encode_with_envelope(char_names.read_bytes(),nd));assert decode(override.read_bytes())==nd and patched is not None
        expected=b'CT43'+struct.pack('<i4I',selector,1,int(sf_failed is None),int(store_ok),int(char_ok))
        for row in [player,store]+sf+char_rows:expected+=struct.pack('<III',row['count'],row['stride'],zlib.crc32(row['data']))
        desc_bytes=b''.join(struct.pack('<I',len(d))+d for d in descs);expected+=struct.pack('<II',zlib.crc32(desc_bytes),character[6]['count']//81)
        expected_file=root/(name+'.bin');expected_file.write_bytes(expected)
        staged=[]
        for path in inputs:
            used=override if path==char_names and override else path
            staged.append(dict(original=str(used),relative=path.relative_to(client).as_posix(),sha256=sha(used),bytes=used.stat().st_size,synthetic=used!=path))
        cases.append(dict(name=name,locale=locale,setting=setting,codepage=cp,selector=selector,dbcs_fixture=fixture,inputs=staged,expected=record(expected_file),results=dict(player=True,skill=sf_failed is None,store=store_ok,character=char_ok),character_counts=[r['count'] for r in char_rows],skill_counts=[r['count'] for r in sf],player_count=player['count'],store_count=store['count'],character_names_consumed=consumed,ignored_character_short_reads=short_reads))
    sources=[record(WS/'scripts/native'/name) for name in ['client455_character_tables.h','client455_character_tables.cpp','client455_item_payloads.h','client455_item_payloads.cpp']]+[record(WS/'scripts/client455_character_tables_port.py')]
    out=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Ordinary PlayerCharacter/SF5/Store/Character7+ND loaders,typed class lookups and source board dimensions;legacy character/skill population/Avatar/class UI consumers open',references=refs,raw=record(raw_file),
        full_functions=15,full_instructions=sum(f['instructions'] for f in functions),positive_cfg_blocks=sum(f['positive_cfg_blocks'] for f in functions),sources=sources,cases=cases,script=record(Path(__file__)),snapshot=record(WS/'artifacts/client455-progress/before143/manifest.json'),
        gaps=['Actual Avatar class setters/names and legacy Player/Monster/Store/skill consumers remain unmigrated','Skill/force board dimensions and owners restored;population/UI/game callbacks remain legacy','Remaining bootstrap/selection/world/gameplay/client acceptance and full unsafe/reload domains'],input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-character-tables-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=15,instructions=out['full_instructions'],cfg=out['positive_cfg_blocks'],cases=[dict(name=c['name'],results=c['results'],character=c['character_counts'],skills=c['skill_counts'],players=c['player_count'],stores=c['store_count'],short_reads=c['ignored_character_short_reads']) for c in cases])))
if __name__=='__main__':main()
