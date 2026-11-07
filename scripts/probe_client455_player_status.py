"""Run actual source CAvatar/status/hover against the full normal object set."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe


def main():
    source=WS/'scripts/native/client455_player_status_probe.cpp';exe=build_full_object_probe('player-status',source)
    holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'player-status-{index:03d}').exists():index+=1
    run=holder/f'player-status-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=35,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
    report=dict(script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),source=record(source),
                exe=record(target),map=record(exe.with_suffix('.map')),architecture=pe(target.read_bytes())['architecture'],console=record(console),
                output=record(output) if output.exists() else None,natural_exit=result.returncode,native=json.loads(output.read_text()) if output.exists() else None,
                normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),reference_sha256=sha(WS/'inventory/client455-player-status-reference.json'),
                input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-status-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-1500:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS','Player status native failure')


if __name__=='__main__':main()
