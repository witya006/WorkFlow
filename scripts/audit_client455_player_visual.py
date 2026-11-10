"""Correct the constructed slot count and pin real player visual guards."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from audit_client455_equipment import record

def main():
    path=WS/'artifacts/client455-progress/player-visual150-reference/complete-session.json'
    proof=verify_regions(path);assert (proof['full_functions'],proof['full_instructions'],proof['positive_cfg_blocks'])==(11,684,107)
    rand_path=path.parent/'rand-session.json';rand_proof=verify_regions(rand_path)
    assert (rand_proof['full_functions'],rand_proof['full_instructions'],rand_proof['positive_cfg_blocks'])==(1,9,1)
    raw=json.loads(path.read_text())
    instructions=lambda addr:[i for p in raw['asm'][addr] for i in p['asm']['lines']]
    ctor=instructions('0x4501b0');dtor=instructions('0x4502b0')
    assert any(i['bytes']=='6a0c' for i in ctor) and any(i['bytes']=='6a0c' for i in dtor)
    assert any(i['bytes']=='6884020000' for i in ctor) and any(i['bytes']=='6884020000' for i in dtor)
    assert 'rand() / 100.0' in raw['functions']['0x46be60']['code']
    assert 16+12*644==1936*4==7744
    files=['client455_player_equipment.h','client455_equipment_object.h','client455_equipment_object.cpp','client455_player_equipment_probe.cpp']
    report=dict(status='PARTIAL_SOURCE_CORRECTION',scope='12 constructed player equipment objects,explicit unsafe index12 boundary,ctor/copy PRNG consumption andrace/helmet visibility guard;ordinary full player not connected',
        **proof,raw=record(path),script=record(Path(__file__)),decoder=record(WS/'scripts/decode_client455_cfg.py'),verifier=record(WS/'scripts/client455_reference_regions.py'),
        rand_reference=rand_proof,rand_raw=record(rand_path),target_rand_recurrence=dict(multiplier=214013,increment=2531011,shift=16,mask=32767,seed=1109,first_values=[3660,150,7964],thirteenth=9923),
        sources=[record(WS/'scripts/native'/name) for name in files],preparer=record(WS/'scripts/prepare_client455_normal.py'),
        runtime_base=record(WS/'artifacts/client455-progress/before150/manifest.json'),
        physical_equipment_slots=12,slot_bytes=644,array_offset=16,first_field_after_array=7744,
        erroneous_previous_claim='13constructedslots inferred fromgetter/create index<=12;superseded bycomplete constructor/destructor bodies',
        target_index12_is_constructed=False,own_index12_policy='Explicit out_of_range;not accepted as target failure/memory-corruption equivalence',
        facts=['4501B0/4502B0 passcount12,stride644 tovector constructor/destructor;following state beginsat7744',
            '46BE60 consumes rand()/100.0 andstoresfloat612;queue firstconstructs46BD60then46C130copies640bytes,so destinationstillconsumesrand',
            '450810 filters hair/head fromrace,helmet rawmetadata236 andequipment/index<80 before empty/flags/meshload checks',
            '450BD0 performs12equipment FrameMove/Animation/cache-save steps;451330rematchesweapon/shield andresetsmesh animation',
            '4513E0 is a real empty player processor FrameMove;not a missing body',
            '46D9B0/46D200 equipment FrameMove has actual effect/dummy/follow dependencies;not equivalent to inheritedCResObject movement'],
        gaps=['Ordinary CPlayerProc/CPlayer/Avatar ownership andequipment/frame/animation/render providers not yet connected',
            'Animation owner/action/profile/condition/UI andnonzero particle registry remain open',
            'Target index12 aliases processor state;unsafe target domain is not reproduced or accepted',
            'Full constructor/destructor/CRT/FP/error/resource/world/client acceptance remains open'],
        full_player_appearance=False,ordinary_controller_connected=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-visual-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_SOURCE:12constructedslots confirmed onbothpins;index12isnotaslot;PRNG/visibilitysource;ordinaryplayerstillopen')

if __name__=='__main__':main()
