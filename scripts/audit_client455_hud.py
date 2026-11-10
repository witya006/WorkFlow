"""Pin the455 upper gauge panel and explicit source bindings,not full MainGame."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_reference_regions import verify_regions
from checkpoint_client455_rvp_effects import sha,require
from client455_normal_link_evidence import validate_normal_link
def record(path):
    path=Path(path);return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    raw=WS/'artifacts/client455-progress/hud159-reference/session.json';proof=verify_regions(raw)
    other=WS/'artifacts/client455-progress/hud159-reference/callbacks.json';callbacks=verify_regions(other)
    require(proof['full_functions']==11 and proof['full_instructions']==1100,'HUD full assembly/CFG')
    require(callbacks['full_functions']==8 and callbacks['full_instructions']==306,'Text callback reference')
    native=WS/'scripts/native'
    report=dict(status='STATIC_CONFIRMED_PARTIAL',raw=record(raw),**proof,callbacks=dict(raw=record(other),**callbacks),script=record(__file__),
        sources=[record(path) for path in [native/'client455_hud.inc',native/'client455_hud_members.inc',WS/'scripts/client455_hud_port.py',WS/'scripts/prepare_client455_normal.py',native/'client455_image_text.h',native/'client455_image_text.cpp']],
        facts=['Target4/main0/0 background,frames1..3 bars/4..6 icons,frames7..9 fourth-color;49/EtcUI0/1 notice',
               'Three horizontal bars plus fourth bottom-anchored vertical bar,17 child owners',
               'Unsigned clamp;zero maximum gives ratio1;fourth color thresholds0.2f/0.7f',
               'Common1/action7/frame3 cell7x9 signed padded current/max;frame4 cell8x11 BYTE level',
               'Level centered at36,23 in22x18 rectangle;target124-byte CharInfo fields3 and9..12',
               'Own target-ID pointer cache reacquired after unloading;no invented gaugeexp.spr alias'],
        gaps=['FullMainGame root/UI_LoadSprite and remaining old0.7 windows not ported',
              'Lower EXP/control flags/unit-mode routes andcaption/notice producers remainopen',
              'Fourth gameplay meaning/provider not yet accepted;do not rename it EXP/DP without proof',
              'Mouse/hover/icon state callbacks andcompleteUI lifecycle remainopen',
              'Whole455private class ABI,malformed sprite/FP edge domains andfullclient equivalence not claimed'],
        prior_runtime=record(WS/'artifacts/client455-progress/before159/manifest.json'),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-hud-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());require(validate_normal_link(link)=='PASS','Current own link')
    body=record(native/'client455_hud.inc')
    rows=[dict(rva=hex(addr-0x400000),symbol='CGUIGaugeExpWindow::'+symbol,source=body,scope='Actual target skins/GPU component;ordinary fullstage not yet accepted',complete_equivalence=False) for addr,symbol in [(0x66a0d0,'Init'),(0x66a4a0,'SetSprite'),(0x66a5c0,'SetFourthColor455'),(0x66a6c0,'SetGauge'),(0x66aa20,'SetLevel')]]
    bindings=dict(schema_version=1,reference_sha256=proof['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=rows)
    (WS/'inventory/client455-hud-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
    print('STATIC_CONFIRMED_PARTIAL:19functions/1406instructions,both455pins;5partial source bindings')
if __name__=='__main__':main()
