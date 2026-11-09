"""Freeze the actual455world-entry request/reply and its ordinary dispatch."""
import hashlib
import json
import struct
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    file=WS/'artifacts/client455-progress/world-entry139-reference/session.json'
    raw=json.loads(file.read_text())
    cfg={int(row['addr'],16):row for row in raw['cfg']['result']};rows=[]
    for row in raw['ranges']['result']:
        assert not row['error']
        addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16)
        pages=next(value for key,value in raw['assemblies'].items() if int(key,16)==addr)
        assert pages[-1]['cursor']['done'] and all(len(page['asm']['lines'])<=100 for page in pages)
        lines=[line for page in pages for line in page['asm']['lines']]
        assert len(lines)==pages[0]['total_instructions']
        starts={int(line['addr'],16) for line in lines};assert len(starts)==len(lines) and min(starts)==addr
        blocks=[block for block in cfg[addr]['blocks'] if block['size']>0]
        assert cfg[addr]['cursor']['done'] and cfg[addr]['count']==cfg[addr]['total_blocks']
        assert all(addr<=int(block['start'],16)<int(block['end'],16)<=addr+size and int(block['start'],16) in starts for block in blocks)
        rows.append(dict(rva=hex(addr-0x400000),bytes=size,instructions=len(lines),positive_cfg_blocks=len(blocks)))
    target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        assert sha(path)==target[key]['sha256'] and pe(data)['architecture']=='x86'
        assert read_va(data,0xAB327C,33)==b'75a32d4a6daff548fcfcb40fea838a0d\0'
        assert struct.unpack('<I',read_va(data,0xBF72D8,4))[0]==0x12ab34cc
        assert read_va(data,0x56306F,5)==b'\xe8'+struct.pack('<i',0x56A960-0x563074)
        ranges=[dict(row,sha256=hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()) for row in rows]
        pins.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path),architecture='x86',image_base='0x400000',functions=ranges))
    assert pins[0]['functions']==pins[1]['functions'] and len(rows)==8
    report=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Ordinary world-entry request58/reply12,core dispatcher,selectors and response callback;not authentication/bootstrap/selection acceptance',
        raw=dict(file=file.relative_to(WS).as_posix(),sha256=sha(file)),references=pins,
        full_functions=len(rows),full_instructions=sum(row['instructions'] for row in rows),positive_cfg_blocks=sum(row['positive_cfg_blocks'] for row in rows),
        request=dict(group=1,opcode=1,bytes=58,account_offset=0,transformed_keys_offset=4,fullscreen_offset=20,version_offset=21,version=126455,signature_offset=25,signature_bytes_including_null=33),
        response=dict(group=1,opcode=2,bytes=12,result_offset=0,grade_offset=1,kind_offset=2,selectors=[dict(name=name,flag_offset=at,index_offset=at+1,index_bytes=2,disabled_value=-1) for name,at in [('cashShop',3),('npcShop',6),('quest',9)]]),
        contracts=['Key transform is DWORD modular arithmetic with initial multiplier12AB34CC',
                   'Request writes close-request flag435992=1 before sending through normal LoadSendMsg',
                   'Every full reply writes result/grade/responseSeen/selectors even for a failure result',
                   'Any nonzero selector flag enables an unsigned16-bit index;zero means-1',
                   'ReceiveResponseMsg occurs before kind is stored at436025',
                   'Ordinary core dispatcher562F50 group1/op2 calls56A960;Login getter53EF80 reads435973'],
        gaps=['Real response→client bootstrap5E7BE0 and its selector consumers','Full Login state handling,all tables and actual selection/world flow',
              'Other core/35processor payloads and all historical client-acceptance gaps'],
        snapshot=dict(file='artifacts/client455-progress/before139/manifest.json',sha256=sha(WS/'artifacts/client455-progress/before139/manifest.json')),
        script=dict(file=Path(__file__).relative_to(WS).as_posix(),sha256=sha(Path(__file__))),input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-world-entry-reference.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(functions=len(rows),instructions=report['full_instructions'],cfg_blocks=report['positive_cfg_blocks'],equal_pins=2,request_bytes=58,response_bytes=12)))


if __name__=='__main__':main()
