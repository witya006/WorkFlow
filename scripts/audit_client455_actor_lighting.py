"""Pin the actual455 actor material/light consumer and explicit blink fields."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions


def record(path):
    path=Path(path)
    return dict(file=path.relative_to(WS).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    raw=WS/'artifacts/client455-progress/lighting157-reference/session.json'
    proof=verify_regions(raw)
    assert proof['full_functions']==3 and proof['full_instructions']==208
    constants=[]
    for pin in proof['references']:
        binary=(WS/pin['file']).read_bytes()
        rows=[]
        for address,wanted in [(0xaecf08,.15),(0xaaa3a0,.1),(0xaaa4b8,.2),(0xae5958,.3)]:
            code=read_va(binary,address,8);value=struct.unpack('<d',code)[0]
            assert value==struct.unpack('<f',struct.pack('<f',wanted))[0]
            rows.append(dict(rva=hex(address-0x400000),bytes=8,hex=code.hex(),value=value))
        assert struct.unpack('<f',read_va(binary,0xaa9740,4))[0]==10.0
        if constants:assert constants==rows
        constants=rows
    report=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Loaded-BSP or explicit-override actor map lighting;not full actor/ground-item state consumers',
        raw=record(raw),**proof,numeric_literals=constants,script=record(__file__),
        sources=[record(WS/path) for path in ['scripts/client455_actor_lighting_port.py','scripts/native/client455_actor_lighting.inc','scripts/prepare_client455_normal.py']],
        facts=['44D230 callsbase7CE7A0 thenactual current-processor material virtual96',
               'GetLightFromPoint uses position80/84/88 anddiff2',
               'After-image0x80000 colorFFA0A0FF overrides enabled blinkDWORD476',
               '7CEA00 stores fullBOOL472 andDWORD476 evenwhendisabling',
               'Light direction isnegated,ambient RGB is1;materialdiffuse adds.15/.1/.1,ambient adds.2',
               'Specular RGB isupdateddiffuse*.3,alpha1,power10;thenactualCharIF SetLight'],
        gaps=['NoBSP/nooverride targetuninitialised color isnotreproduced;ownroute throws explicitly',
              'Legacy one-argument SetBlink caller andplayer44DEE0 state producers areunported;explicit455color API isavailable',
              'FullFP/NaN/Inf/statusflag parity andall actor/clone/world/gameplay acceptance remainopen'],
        prior_runtime=record(WS/'artifacts/client455-progress/before157/manifest.json'),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-actor-lighting-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('STATIC_CONFIRMED_PARTIAL:3functions/208instructions,both455pins;fullclientopen')


if __name__=='__main__':main()
