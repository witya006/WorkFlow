"""Pin complete equipment frame bodies and the actual wrapper discriminators."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions
from audit_client455_equipment import record

def main():
    path=WS/'artifacts/client455-progress/equipment-frame153-reference/session.json'
    proof=verify_regions(path);raw=json.loads(path.read_text())
    assert proof['full_functions']==13 and len(raw['ranges']['result'])==len({r['query'] for r in raw['ranges']['result']})
    predicates=[]
    for ref in proof['references']:
        binary=(WS/ref['file']).read_bytes();tables=[]
        for vtable,expected in [(0xaa92bc,0x405040),(0xaa8f64,0x4043c0)]:
            slot=vtable+120;actual=struct.unpack('<I',read_va(binary,slot,4))[0];assert actual==expected
            tables.append(dict(vtable_rva=hex(vtable-0x400000),slot=120,predicate_rva=hex(actual-0x400000),bytes=read_va(binary,slot,4).hex()))
        predicates.append(dict(reference_sha256=ref['sha256'],architecture='x86',image_base='0x400000',tables=tables))
    assert predicates[0]['tables']==predicates[1]['tables']
    sources=['client455_equipment_frame.inc','client455_equipment_effects.h','client455_equipment_object.h','client455_equipment_object.cpp','client455_player_equipment.h','client455_effect_positions.h','client455_equipment_effects_probe.cpp','client455_equipment_frame_probe.inc']
    report=dict(status='PARTIAL_SOURCE',scope='CMesh/CEquip FrameMove,Animation,end transitions,dummy/always/motion effect ownership andequipment-position wave calls;ordinary fullplayer not yet connected',
        **proof,raw=record(path),script=record(Path(__file__)),decoder=record(WS/'scripts/decode_client455_cfg.py'),verifier=record(WS/'scripts/client455_reference_regions.py'),
        sources=[record(WS/'scripts/native'/n) for n in sources],preparer=record(WS/'scripts/prepare_client455_normal.py'),owner_port=record(WS/'scripts/client455_equipment_port.py'),prior_runtime=record(WS/'artifacts/client455-progress/before153/manifest.json'),
        wrapper_predicates=predicates,
        facts=['46D190 performs baseAnimation before disable128/mesh andmeshFrameMove',
            '46E520 rejects a null item before genericAnimation;46DBC0 performs baseFrameMove before kind-dependent end transitions',
            '46D200 performs always-effect update then baseFrameMove,enabled-state update andactor attachment/yaw follow;missing magic clears632',
            '46D9B0 binds10dummyindices once behind mesh/flags0x21000/render2 guards',
            '7DBE20/7F2C50 query virtual120(kind2),not byte4;CMesh returnsfalse,CEquip accepts1only,so neither uses ground magic creation/jitter',
            '46D3D0 magic uses actorposition butwave requests read equipmentposition+80;these can differ',
            'Ordinary sixAvatar default objects now use derivedCEquip source wrappers,not genericCMesh wrappers'],
        frozen_transition_modes=dict(cloak={'1':3,'4':3,'2':0,'5':0},kind9and46={'4':7,'5':0,'6':6,'7':0,'8':0,'9':0,'10':0},other={'1':0,'3':0,'4':0}),
        gaps=['Primary12-slot ordinaryCPlayerProc ownership andits frame/animation/render/condition/UI/effect providers stillopen',
            'Ground wrapper/create/jitter is a different unported class andis not accepted by this result',
            'Full shared particle registry/nonzero particle rendering,allNPC/actor/effect variants andordinary appearance/selection remainopen',
            'Target uninitialised position branches,unsafe stack/buffer/index12 andallCRT/FP/lifecycle errors remainexplicit gaps'],
        ordinary_full_player_connected=False,full_appearance=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-frame-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],functions=proof['full_functions'],instructions=proof['full_instructions'],blocks=proof['positive_cfg_blocks'],both_pins_match=True)))

if __name__=='__main__':main()
