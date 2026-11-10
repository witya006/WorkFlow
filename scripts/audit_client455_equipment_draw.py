"""Pin equipment render producers, wrappers and queue without full-player claims."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from audit_client455_equipment import record

def main():
    primary=WS/'artifacts/client455-progress/equipment-draw149-reference/session.json'
    effects=WS/'artifacts/client455-progress/equipment-effects149-reference/session.json'
    render=WS/'artifacts/client455-progress/equipment-render148-reference/session.json'
    grade=WS/'artifacts/client455-progress/grade-overlay148-reference/session.json'
    proofs=[verify_regions(path) for path in [primary,effects,render,grade]]
    assert [(p['full_functions'],p['full_instructions'],p['positive_cfg_blocks']) for p in proofs[:2]]==[(13,1141,132),(3,1314,76)]
    functions={}
    for proof in proofs:
        for f in proof['references'][0]['functions']:
            if f['rva'] in functions:assert functions[f['rva']]==f
            functions[f['rva']]=f
    references=[]
    for i in range(2):
        ref=proofs[0]['references'][i]
        references.append(dict(file=ref['file'],sha256=ref['sha256'],architecture='x86',image_base='0x400000',functions=list(functions.values())))
    files=['client455_equipment_object.h','client455_equipment_object.cpp','client455_equipment_draw.inc','client455_equipment_draw_lifecycle.h','client455_player_equipment.h','client455_grade_overlay.inc','Character455.h','client455_normal_effects.cpp','client455_normal_effect_tables.cpp']
    previous_sources=WS/'artifacts/client455-progress/before149/recovered-source/manifest.json'
    for row in json.loads(previous_sources.read_text())['files']:
        assert record(WS/row['file'])['sha256']==row['sha256']
    report=dict(status='PARTIAL_SOURCE',scope='Typed equipment default/matrix Render,fade/alpha,overlay producer,retained effect queue and partial effect-draw adapter;full player and particle registry open',
        references=references,full_functions=len(functions),full_instructions=sum(f['instructions'] for f in functions.values()),positive_cfg_blocks=sum(f['positive_cfg_blocks'] for f in functions.values()),
        newly_pinned_functions=16,newly_pinned_instructions=2455,
        raw=record(primary),effects_raw=record(effects),reused_raw=[record(render),record(grade)],
        diagnostics=record(effects.parent/'additional-diagnostics.json'),script=record(Path(__file__)),
        region_verifier=record(WS/'scripts/client455_reference_regions.py'),decoder=record(WS/'scripts/decode_client455_cfg.py'),
        sources=[record(WS/'scripts/native'/name) for name in files],port=record(WS/'scripts/client455_equipment_port.py'),preparer=record(WS/'scripts/prepare_client455_normal.py'),
        runtime_base=record(WS/'artifacts/client455-progress/before149/manifest.json'),prior_source_snapshot=record(previous_sources),
        confirmed=['450330/450710 set equipment604 from metadata152 only for slots6/7;other slots get0',
            '404EA0 returns the complete payload113BYTE;it is not a boolean renderer grade',
            '46C470 draws primary then optional overlay;46C940 does overlay setup/end without secondary geometry',
            'EffectList keys are DWORD;unit kind37..43 uses100*(kind-37)+metadata0 without BYTE truncation',
            '527E70 caps256 andnodes>=64to63;physical cache stride4matrices/node retains cross-node aliases',
            '528190 increments start across calls;Clear resets counters/releases copied payload owners',
            '46CF10 repeats material/effect setup andalwaysuses effect scale1/lastflag0',
            '53F7A0 loads1072E40 from Chef/Siege.ini;the own source adds that loader'],
        gaps=['Ordinary CPlayerProc/Avatar13-slot controller,pose restore,Render/Animation/FrameMove andselection not connected',
            'Full46BE60constructor effects stillopen:target consumes rand()/100 into612;own wrapper/queue copy does notyet reproduce that PRNG consumption',
            'Nonzero particle/entity draw not verified by the equipment probe;adapter currently uses legacy global registry',
            'Legacy particle registry has1024slots/5clones;target uses dynamic vectors/6clones,load-attempt failure guard anddifferent lookup semantics;must migrate before full equipment acceptance',
            'Loader7BE640/7BF060 grows vectors when declared count+1>3072;default capacity andall registry lifecycle still require proof;do not assume2000 for this ordinary registry',
            'Out-of-allocation queue writes/palette>30 andBYTE reference overflow remain unsafe target domains;no invented correction is accepted',
            'Whole-client constructor/error/FP/CRT/stage/device/network/resource gaps inclient-acceptance.md remain'],
        input_exe_executed=False,server_modified=False,full_equipment=False,full_client=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-draw-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_SOURCE:equipment wrappers/overlay producer/queue pinned;ordinary player andcomplete particle registry stillopen')

if __name__=='__main__':main()
