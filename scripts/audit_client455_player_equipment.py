"""Full controller/normal-clone static evidence;not full actor acceptance."""
import hashlib,json,struct
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe
from audit_client455_equipment import record,sha

def main():
    source=WS/'artifacts/client455-progress/player-equipment146-reference/session.json'
    raw=json.loads(source.read_text());functions=[]
    for entry in raw['ranges']['result']:
        assert entry['fn'] and not entry['error'];address=int(entry['fn']['addr'],16)
        pages=raw['asm'][entry['query']];assert pages[-1]['cursor']['done']
        lines=[line for page in pages for line in page['asm']['lines']]
        starts={int(line['addr'],16) for line in lines}
        assert len(starts)==len(lines)==pages[0]['total_instructions']
        assert all(len(page['asm']['lines'])<=100 for page in pages)
        cfg=next(row for row in raw['cfg']['result'] if int(row['addr'],16)==address)
        assert cfg['cursor']['done'] and cfg['count']==cfg['total_blocks']
        blocks=[b for b in cfg['blocks'] if b['size']>0]
        assert all(int(b['start'],16) in starts for b in blocks)
        assert all(any(int(b['start'],16)<=a<int(b['end'],16) for b in blocks) for a in starts)
        regions=[]
        for block in sorted(blocks,key=lambda b:int(b['start'],16)):
            a,b=int(block['start'],16),int(block['end'],16)
            if regions and regions[-1][1]==a:regions[-1][1]=b
            else:regions.append([a,b])
        functions.append(dict(rva=hex(address-0x400000),instructions=len(lines),positive_cfg_blocks=len(blocks),regions=[dict(rva=hex(a-0x400000),bytes=b-a) for a,b in regions]))
    assert len(functions)==32
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=file.read_bytes()
        assert sha(file)==pins[key]['sha256'] and pe(binary)['architecture']=='x86'
        assert read_va(binary,0xbcb1b4,19).startswith(b'.?AVCPlayerProc@@\0')
        assert struct.unpack('<I',read_va(binary,0xaa9160,4))[0]==0xb7a494
        slots={56:0x452fe0,60:0x4531e0,64:0x453100,68:0x453030,72:0x453550,76:0x4536c0,80:0x453730}
        assert all(struct.unpack('<I',read_va(binary,0xaa9164+offset,4))[0]==target for offset,target in slots.items())
        assert read_va(binary,0xbcb200,18).startswith(b'.?AVCNormalItem@@\0')
        assert struct.unpack('<I',read_va(binary,0xaa9264+20,4))[0]==0x461cc0
        confirmed=[dict(f,regions=[dict(r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in f['regions']]) for f in functions]
        rtti=[dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()) for a,n in [(0xbcb1ac,28),(0xb7a494,20),(0xaa9160,128),(0xbcb1f8,28),(0xaa9260,28)]]
        references.append(dict(**record(file),architecture='x86',image_base='0x400000',functions=confirmed,rtti=rtti))
    assert references[0]['functions']==references[1]['functions'] and references[0]['rtti']==references[1]['rtti']
    create=[line['instruction'] for page in raw['asm']['0x453760'] for line in page['asm']['lines']]
    assert 'call sub_453A80' in create
    owner=[line['instruction'] for page in raw['asm']['0x453a80'] for line in page['asm']['lines']]
    assert 'mov [eax+24Ch], ecx' in owner
    report=dict(status='PARTIAL_COMPONENT_STATIC',scope='13-slot source equipment controller and detached normal-item copy;required production condition/animation/effect providers remain open',
        raw=record(source),references=references,full_functions=len(functions),full_instructions=sum(f['instructions'] for f in functions),positive_cfg_blocks=sum(f['positive_cfg_blocks'] for f in functions),
        controller_rtti=True,normal_clone_rtti=True,owner_pointer_call_confirmed=True,
        sources=[record(WS/'scripts/native'/name) for name in ['client455_player_equipment.h','client455_normal_item_copy.h','client455_player_equipment_probe.cpp']],script=record(Path(__file__)),
        runtime_base=record(WS/'inventory/client455-equipment-checkpoint.json'),snapshot=record(WS/'artifacts/client455-progress/before146/manifest.json'),
        production_controller_connected=False,full_player_appearance_or_draw=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-equipment-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=report['full_functions'],instructions=report['full_instructions'],blocks=report['positive_cfg_blocks'],both_pins_equal=True,production_controller_connected=False)))
if __name__=='__main__':
    raise SystemExit('Historical146 producer superseded:13-slot inference was wrong. Use audit_client455_player_visual.py;historical evidence remains archived.')
