"""Pin the ordinary initial item-loading path and make compact real-data oracles."""
import hashlib,json,struct,zlib
from pathlib import Path
from audit_client455_language import decode
from audit_client455_item_payloads import item_tables,localized,table
from audit_client455_resource_catalog import sha,record
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def main():
    raw_file=WS/'artifacts/client455-progress/item-bootstrap142-reference/session.json';raw=json.loads(raw_file.read_text());functions=[]
    for entry in raw['ranges']['result']:
        addr=int(entry['fn']['addr'],16);pages=raw['asm'][entry['query']];assert pages[-1]['cursor']['done']
        lines=[line for page in pages for line in page['asm']['lines']];starts={int(line['addr'],16) for line in lines}
        assert len(starts)==len(lines)==pages[0]['total_instructions'] and all(len(page['asm']['lines'])<=100 for page in pages)
        cfg=next(row for row in raw['cfg']['result'] if int(row['addr'],16)==addr);assert cfg['cursor']['done'] and cfg['count']==cfg['total_blocks']
        blocks=[b for b in cfg['blocks'] if b['size']>0];assert all(int(b['start'],16) in starts for b in blocks)
        assert all(any(int(b['start'],16)<=start<int(b['end'],16) for b in blocks) for start in starts)
        regions=[]
        for block in sorted(blocks,key=lambda b:int(b['start'],16)):
            first,last=int(block['start'],16),int(block['end'],16)
            if regions and regions[-1][1]==first:regions[-1][1]=last
            else:regions.append([first,last])
        functions.append(dict(rva=hex(addr-0x400000),instructions=len(lines),positive_cfg_blocks=len(blocks),regions=[dict(rva=hex(a-0x400000),bytes=b-a) for a,b in regions]))
    pins=json.loads((WS/'config/client-target.json').read_text());countries=json.loads((WS/'inventory/client455-launcher-reference.json').read_text())['countries'];references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();assert sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86'
        policies=[]
        for country in countries:
            slot=int(country['vtable'],16)+160;method=struct.unpack('<I',read_va(data,slot,4))[0];assert method in [0x8329b0,0x82c490]
            policies.append(dict(nation=country['nation'],vtable_rva=hex(int(country['vtable'],16)-0x400000),slot_rva=hex(slot-0x400000),method_rva=hex(method-0x400000),segmented=True))
        bodies=[dict(row,regions=[dict(region,sha256=hashlib.sha256(read_va(data,0x400000+int(region['rva'],16),region['bytes'])).hexdigest()) for region in row['regions']]) for row in functions]
        references.append(dict(**record(path),architecture='x86',image_base='0x400000',functions=bodies,country_item_policy=policies))
    assert references[0]['functions']==references[1]['functions'] and references[0]['country_item_policy']==references[1]['country_item_policy'] and len(functions)==4
    prior=json.loads((WS/'inventory/client455-item-payloads-reference.json').read_text());old_raw=WS/prior['raw_evidence'][0]['file']
    assert sha(old_raw)==prior['raw_evidence'][0]['sha256'] and prior['actual_instructions']==1796
    assert any(row['rva']=='0x1fee30' and row['instructions']==588 for row in prior['assembly'])
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);base=client/'DataTable/Item.edf';rows,arrays,sections=item_tables(decode(base.read_bytes()))
    assert sum(row['count'] for row in rows)==76049 and len(sections)==48
    set_file=client/'DataTable/ItemSetEffect.edf';set_row,set_end=table(decode(set_file.read_bytes()),0)
    root=WS/'artifacts/client455-item-bootstrap';root.mkdir(exist_ok=True);cases=[]
    for locale,setting,selector in [('ko-kr','Korea',-1),('zh-tw','Taiwan',-1),('ru-ru','Russia',-1),('zh-tw','Taiwan',1),('zh-tw','Taiwan',10),('ko-kr','Korea',1)]:
        suffix='' if selector==-1 else f'_{selector}';cash_file=client/f'DataTable/ItemCash{suffix}.edf';cash_row,cash_end=table(decode(cash_file.read_bytes()),0)
        cash_names=client/f'DataTable/{locale}/NDItemCash{suffix}.edf';cash_data=bytearray(cash_row['data']);cash_ok=False
        if cash_names.is_file():
            nd=decode(cash_names.read_bytes());count,ignored_stride=struct.unpack_from('<II',nd)
            if count==cash_row['count']:
                assert len(nd)>=8+4*count and (not count or cash_row['stride']>=20)
                for i in range(count):cash_data[i*cash_row['stride']+16:i*cash_row['stride']+20]=nd[8+4*i:12+4*i]
                cash_ok=True
        names_file=client/f'DataTable/{locale}/NDItem.edf';local_rows,descriptions,info=localized(rows,decode(names_file.read_bytes()))
        expected=b'IB42'+struct.pack('<i8I',selector,int(cash_ok),cash_row['count'],cash_row['stride'],zlib.crc32(cash_data),1,set_row['count'],set_row['stride'],zlib.crc32(set_row['data']))
        expected+=b''.join(struct.pack('<III',row['count'],row['stride'],zlib.crc32(row['data'])) for row in local_rows)
        expected+=struct.pack('<4I',zlib.crc32(arrays),zlib.crc32(descriptions),info['consumed'],76049)
        name=f'{locale}-'+('default' if selector==-1 else str(selector));fixture=root/(name+'.bin');fixture.write_bytes(expected)
        paths=[base,set_file,cash_file,names_file]+([cash_names] if cash_names.is_file() else [])
        inputs=[dict(original=str(path),relative=path.relative_to(client).as_posix(),sha256=sha(path),bytes=path.stat().st_size) for path in paths]
        cases.append(dict(name=name,locale=locale,setting=setting,selector=selector,cash_localization_expected=cash_ok,missing_cash_names=None if cash_names.is_file() else str(cash_names),expected=record(fixture),inputs=inputs,localization=info))
    out=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Ordinary Login initial ItemCash/ItemSet/Item47+ND path and real typed item consumers;remaining bootstrap/legacy items/appearance open',references=references,raw=record(raw_file),
        full_functions=4,full_instructions=sum(row['instructions'] for row in functions),positive_cfg_blocks=sum(row['positive_cfg_blocks'] for row in functions),
        reused_item_decoder_reference=record(WS/'inventory/client455-item-payloads-reference.json'),reused_item_decoder_raw=record(old_raw),reused_item_loader_instructions=588,
        country_source=record(WS/'inventory/client455-launcher-reference.json'),cases=cases,item_rows=76049,item_tables=47,
        sources=[record(WS/'scripts/native'/name) for name in ['client455_client_items.h','client455_item_bootstrap.h','client455_item_bootstrap.inc','client455_item_object.cpp']]+[record(WS/'scripts/client455_item_bootstrap_port.py')],
        script=record(Path(__file__)),snapshot=record(WS/'artifacts/client455-progress/before142/manifest.json'),
        gaps=['Legacy ITEM_DATA/derived CBoardItem consumers remain unmigrated;GetData455 is the typed route','Remaining character/class/quest/table bootstrap and ordinary selection/world','Full reload/failure/unsafe target domains and all client-acceptance gaps'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-bootstrap-reference.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(functions=4,instructions=out['full_instructions'],cfg=out['positive_cfg_blocks'],countries_segmented=11,cases=[dict(name=c['name'],cash_ok=c['cash_localization_expected']) for c in cases],rows=76049)))
if __name__=='__main__':main()
