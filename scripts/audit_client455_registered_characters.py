"""Pin the complete455registered-character payload and actor-application owner."""
import hashlib,json,struct
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    file=WS/'artifacts/client455-progress/registered140-reference/session.json';raw=json.loads(file.read_text())
    cfg={int(row['addr'],16):row for row in raw['character_cfg']['result']};rows=[]
    for entry in raw['character_ranges']['result']:
        assert not entry['error'];addr,size=int(entry['fn']['addr'],16),int(entry['fn']['size'],16)
        pages=next(value for key,value in raw['character_assemblies'].items() if int(key,16)==addr)
        assert pages[-1]['cursor']['done'] and all(len(page['asm']['lines'])<=100 for page in pages)
        lines=[line for page in pages for line in page['asm']['lines']]
        assert len(lines)==pages[0]['total_instructions']
        starts={int(line['addr'],16) for line in lines};assert len(starts)==len(lines) and min(starts)==addr
        flow=cfg[addr];assert flow['cursor']['done'] and flow['count']==flow['total_blocks']
        blocks=[block for block in flow['blocks'] if block['size']>0]
        assert all(addr<=int(block['start'],16)<int(block['end'],16)<=addr+size and int(block['start'],16) in starts for block in blocks)
        rows.append(dict(rva=hex(addr-0x400000),bytes=size,instructions=len(lines),positive_cfg_blocks=len(blocks)))
    target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        assert sha(path)==target[key]['sha256'] and pe(data)['architecture']=='x86'
        assert read_va(data,0xAB2E10,8)==bytes([1,2,3,4,5,7,6,8])
        assert read_va(data,0x563091,5)==b'\xe8'+struct.pack('<i',0x56AE40-0x563096)
        ranges=[dict(row,sha256=hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()) for row in rows]
        pins.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path),architecture='x86',image_base='0x400000',functions=ranges))
    assert pins[0]['functions']==pins[1]['functions'] and len(rows)==9
    report=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Registered-character1/8 request and1/9 fixed506-byte reply/three164-byte records/real Avatar fields;not full bootstrap/classes/appearance/selection',
        raw=dict(file=file.relative_to(WS).as_posix(),sha256=sha(file)),references=pins,
        full_functions=len(rows),full_instructions=sum(row['instructions'] for row in rows),positive_cfg_blocks=sum(row['positive_cfg_blocks'] for row in rows),
        payload=dict(bytes=506,header_bytes=14,result_offset=0,count_offset=1,capacity=3,record_stride=164,
            record_offsets=dict(name=0,serial=17,race=21,slot=22,classCode=23,level=28,dalant=29,gold=37,baseShape=45,equipment=49,upgrade=65,reserved=73,lastConnection=156)),
        contracts=['Input always copies506bytes,including zero-count replies','Record has17wire name bytes,not21:serialDWORD is at17',
                   'slot>2 is skipped;duplicates are processed in order','level0 becomes1 with skipTutorial0;nonzero level sets skipTutorial1',
                   'Money and lastConnection use full signed64-bit values','Latest timestamp starts0 for each reply,strictgreater;zero-count retains previous selected slot and actors',
                   'Equipment uses8signed16-bit keys,5default nibble parts,face0 andhair10','Actor class-data lookup/gear/material callback fidelity remains dependent on other source components'],
        bootstrap_diagnostic=dict(file=file.relative_to(WS).as_posix(),status='PSEUDOCODE_ONLY_FOR_BOOTSTRAP_NOT_FULL_ASM_OR_ACCEPTANCE',
            root_rva='0x1e7be0',order=['ItemCash','ItemSetEffect','Item','Resource','PlayerCharacter/SkillForce/Store/Character/boards','Quest','EventShip','NDMsgMonster','ItemTimer','country slot296','NDMsgEvent','EventSound','SpecialStore','ItemCollection','Map','five default effects','Avatar finalization','registered-character request']),
        gaps=['Real bootstrap5E7BE0 and all tables/selector consumers','Full target class-tier names/lookup and appearance/resource/item consumers','Actual selection UI/auth/stages/world/gameplay and all historical client-acceptance gaps'],
        snapshot=dict(file='artifacts/client455-progress/before140/manifest.json',sha256=sha(WS/'artifacts/client455-progress/before140/manifest.json')),
        script=dict(file=Path(__file__).relative_to(WS).as_posix(),sha256=sha(Path(__file__))),input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-registered-characters-reference.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(functions=len(rows),instructions=report['full_instructions'],cfg_blocks=report['positive_cfg_blocks'],equal_pins=2,response_bytes=506,record_stride=164)))


if __name__=='__main__':main()
