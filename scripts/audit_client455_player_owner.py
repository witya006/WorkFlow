"""Pin primary player-owner callbacks and member-copy semantics to both455PEs."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from audit_client455_equipment import record


def main():
    sources=['client455_player_owner.cpp','client455_player_equipment.h','client455_equipment_object.h','client455_equipment_object.cpp',
             'client455_equipment_conditions.h','client455_equipment_frame.inc','client455_equipment_effects.h',
             'client455_skill_force_items.h','client455_skill_force_items.cpp','client455_tagged_audio.cpp',
             'client455_player_owner_probe.cpp']
    files=['player-owner154-reference/session.json','player-owner154-copy-reference/session.json','player-owner154-avatar-reference/session.json']
    proofs=[]
    for name in files:
        file=WS/'artifacts/client455-progress'/name
        proof=verify_regions(file);proofs.append(dict(raw=record(file),**proof))
    assert [p['full_functions'] for p in proofs]==[15,7,2]
    reused=[]
    for name in ['player-visual150-reference/complete-session.json','equipment-draw149-reference/session.json','equipment-providers146-reference/session.json','equipment-conditions146-reference/session.json','equipment-frame153-reference/session.json']:
        file=WS/'artifacts/client455-progress'/name
        reused.append(dict(raw=record(file),**verify_regions(file)))
    facts=[
        'CPlayer44A750 sets currentProc to embedded5200 andbothProc.actor links tothis;profile17796 starts0',
        'Base skill-level callback43E600 is truly empty;Avatar41A060 routes to actual skill board7/490EB0',
        'Skill loop visits every actual pack/socket via GetObject;463740 writes101 andupdates the bound icon',
        '463780 subtype2 returns1;otherwise baseOnly returns100,andBYTE(100+101) wraps before clamp7',
        '4513C0 is an empty return1;450BD0 skips a missing mesh after trying that default helper',
        '450BD0 rematches/resets weapon andshield,then object.FrameMove/Animation andactorPSetVertexBlendingTRUE',
        '450330 uses actor part caches,overlay slots andordinary position/yaw/scale;slot9 has a separate Siege predicate',
        'Avatar403330 calls Player403D70,which copies currentProc verbatim andcalls embedded404A40',
        '404A40 independently copies12CEquip members;405A40 keeps old actor/bone/box links',
        '4042D0/404F40/405D30 copy payload/owner/random/mesh/fade/event fields without rand orAddRef',
        'Queue527E70 instead constructs a fresh wrapper,consumes rand andretains the payload;these copy routes must differ',
        'Copied actor/proc pointers are not rebound to the destination Avatar;unsafe aliases are not silently repaired',
        '419BB0 restores an actual default wrapper forparts0..4 afterbase removal;27refreshes UI',
        '419BB0 cloak8/Siege46 returnsfalse AFTER removal when skillboard7exists but pack2slot0/1 ismissing',
    ]
    gaps=[
        'Full455Avatar/CPlayer/Unit/Character copy anddestruction under all pointer aliases,GUI/board ownership andfailure domains remain unaccepted',
        'Ordinary legacy GetEquipItem/GetNormalItem andCEquipItem overload consumers are still unmigrated andexplicitly reject mixed nonempty typed data',
        'CurrentUI refresh uses its actual existing owner,butcomplete455metrics/23fieldlayout,PremiumUI andfullSFwidget/population remainopen',
        'Avatar removal witha populated cloak/Siege specialskill needs actual Linker6/board35 unlink,icon state andmovement transition providers',
        'Siege slot9 flags/provider,activeUnit equipment,action-category byte614 producers andprofile17796 nonzero writers remainopen',
        'Shared particle vectors/nonzero rendering,ground wrapper,complete shadow behavior andall race/class variants remainopen',
        'Complete normal character appearance,selection,world,control/gameplay andM9 are not proven by the isolated own entry',
        'Target uninitialised/unsafe index12/buffer/FP/CRT/OOM/lifecycle domains remain explicit requirements',
    ]
    report=dict(status='PARTIAL_SOURCE',scope='Primary embedded CPlayerProc typed equipment ownership/frame/render/condition callbacks andtarget member-copy links',
        proof=proofs,reused_reference_proof=reused,script=record(Path(__file__)),
        decoder=record(WS/'scripts/decode_client455_cfg.py'),verifier=record(WS/'scripts/client455_reference_regions.py'),
        preparer=record(WS/'scripts/prepare_client455_normal.py'),owner_port=record(WS/'scripts/client455_player_owner_port.py'),
        sources=[record(WS/'scripts/native'/name) for name in sources],prior_runtime=record(WS/'artifacts/client455-progress/before154/manifest.json'),
        facts=facts,gaps=gaps,input_exe_executed=False,server_modified=False,full_player=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-owner-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],new_functions=sum(p['full_functions'] for p in proofs),both_pins_match=True)))


if __name__=='__main__':main()
