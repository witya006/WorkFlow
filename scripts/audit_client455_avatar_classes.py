"""Prove selected class writers and prepare real class/name oracles."""
import hashlib,json,struct,zlib
from pathlib import Path
from audit_client455_character_tables import character_localized
from audit_client455_language import decode
from audit_client455_item_payloads import sequential
from audit_client455_resource_catalog import sha,record
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def main():
    raw_file=WS/'artifacts/client455-progress/avatar-classes144-reference/session.json';raw=json.loads(raw_file.read_text());functions=[]
    for entry in raw['ranges']['result']:
        addr=int(entry['fn']['addr'],16);pages=raw['asm'][entry['query']];assert pages[-1]['cursor']['done']
        lines=[line for p in pages for line in p['asm']['lines']];starts={int(line['addr'],16) for line in lines}
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
    assert refs[0]['functions']==refs[1]['functions'] and len(functions)==14
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);root=WS/'artifacts/client455-avatar-classes';root.mkdir(exist_ok=True)
    base_file=client/'DataTable/Character.edf';base=sequential(decode(base_file.read_bytes()),7);cases=[]
    for locale,setting,cp in [('ko-kr','Korea',949),('zh-tw','Taiwan',950),('ru-ru','Russia',1251)]:
        names=client/f'DataTable/{locale}/NDCharacter.edf';rows,_,_,_,short_reads,ok=character_localized(base,decode(names.read_bytes()),cp);assert ok
        table=rows[0];assert table['count']==165
        expected=b'AC44'+struct.pack('<III',table['count'],table['stride'],zlib.crc32(table['data']))
        entries=[]
        for i in range(table['count']):
            row=table['data'][i*table['stride']:(i+1)*table['stride']];code=bytes(row[12:44]);name=bytes(row[112:144]);assert b'\0' in code and b'\0' in name
            index=struct.unpack_from('<I',row,4)[0];expected+=struct.pack('<I',index)+code+name;entries.append(dict(index=index,code=code.split(b'\0')[0].decode('ascii')))
        assert len({e['index'] for e in entries})==len(entries) and len({e['code'] for e in entries})==len(entries)
        fixture=root/(locale+'.bin');fixture.write_bytes(expected)
        cases.append(dict(name=locale,locale=locale,setting=setting,codepage=cp,classes=entries,ignored_names_reads=short_reads,expected=record(fixture),inputs=[dict(original=str(p),relative=p.relative_to(client).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in [base_file,names]]))
    sources=[record(WS/'scripts/client455_avatar_classes_port.py'),record(WS/'scripts/native/client455_avatar_classes.inc')]
    out=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Ordinary Avatar class index/name writers through real455class tables;dedicated23value widgets;full skill callback/CharInfo layout/equipment/selection open',
        references=refs,raw=record(raw_file),full_functions=len(functions),full_instructions=sum(f['instructions'] for f in functions),positive_cfg_blocks=sum(f['positive_cfg_blocks'] for f in functions),sources=sources,cases=cases,
        reused_class_table_reference=record(WS/'artifacts/client455-progress/before144/inventory/client455-character-tables-reference.json'),snapshot=record(WS/'artifacts/client455-progress/before144/manifest.json'),script=record(Path(__file__)),
        gaps=['CreateClassSkill caller restored but existing production board implementation remains unported;tests cover board-absent branch','23value widgets own text state;full455CharInfo layout/input/render and other writers remain open','Equipment/registered appearance/full bootstrap/selection/world/gameplay and all client-acceptance/unsafe/concurrent domains open'],input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-avatar-classes-reference.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(functions=len(functions),instructions=out['full_instructions'],cfg=out['positive_cfg_blocks'],locales=len(cases),classes=165)))
if __name__=='__main__':main()
