"""Pin equipped combat-mode switching,without claiming the full SetAction port."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions
from checkpoint_client455_rvp_effects import check,load,require,sha


def record(path):return dict(file=Path(path).relative_to(WS).as_posix(),sha256=sha(path))


def main():
    raw=WS/'artifacts/client455-progress/combat-transition156-reference/session.json';proof=verify_regions(raw)
    require(proof['full_functions']==3 and proof['full_instructions']==225,'Complete transition/fade/root observations')
    for pin in proof['references']:
        binary=(WS/pin['file']).read_bytes()
        require(read_va(binary,0xaaaeb4,8)==bytes([2,1,0,0,1,2,0,0]),'Actual animation/fade tables')
        for call,target in [(0x53bbcd,0x7e8ed0),(0x53bc1f,0x7e8f90)]:
            require(read_va(binary,call,5)==b'\xe8'+struct.pack('<i',target-call-5),'Login effects lifecycle callsite')
    sources=['scripts/client455_player_owner_port.py','scripts/native/client455_player_owner.cpp','scripts/native/client455_player_equipment.h','scripts/native/client455_player_owner_probe.cpp']
    report=dict(status='STATIC_CONFIRMED_PARTIAL',scope='44BE00 embedded weapon/shield combat transition and46E220 fade;44BB90 whole root recorded butnot fully ported',
        raw=record(raw),**proof,script=record(Path(__file__)),sources=[record(WS/path) for path in sources],
        facts=['Current612 equals previous613 returns before touching equipment',
               '44BE00 doesnot have the old mounted-unit early return',
               'Embedded processor5200 fetches both slots6/7 before mutations',
               'Animation virtual160 occurs beforefade46E220,weapon before shield',
               'Mode0 maps animation2/fade1;mode1 maps animation1/fade2',
               'FPS float is converted byx87 truncation toint32,then lowBYTE passed separately aftereach animation',
               'Fade budgetBYTE0 becomes60;fade1 starts atbudget,other fades start0'],
        gaps=['Full44BB90 action rewrite/savedframe restore/flags and44BF30 fullprior-state fields not accepted',
              'Transitional Login dummy scheduling andother legacy selection consumers are not a complete455stage port',
              'Login Create target tail is incorrectly split byIDA;only lifecycle callsites/order are verified here,not a fullCreate function',
              'Modes outside0/1 andnonfinite/out-of-int32 FPS domains remain unaccepted',
              'Full client stages/appearance/selection/world/gameplay andall client-acceptance requirements'],
        prior_runtime=record(WS/'artifacts/client455-progress/before156/manifest.json'),
        effects_lifecycle_calls=[dict(call_rva='0x13bbcd',target_rva='0x3e8ed0',stage='afterLoadData beforecreated=1'),dict(call_rva='0x13bc1f',target_rva='0x3e8f90',stage='afterbaseDestroy beforecamera/UnloadData')],
        effects_diagnostics=record(WS/'artifacts/client455-progress/combat-transition156-reference/grade-startup-diagnostics.json'),
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-combat-transition-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:combat transition/fade confirmed onboth pinned clients;full SetAction remains open')


if __name__=='__main__':main()
