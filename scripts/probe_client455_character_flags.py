"""Run source Character flags/actual Avatar predicate and selected server producer."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe


def main():
    source=WS/'scripts/native/client455_character_flags_probe.cpp';exe=build_full_object_probe('character-flags',source);holder=WS/'work/m9'/sha(exe)[:8];n=1
    while(holder/f'character-flags-{n:03d}').exists():n+=1
    run=holder/f'character-flags-{n:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);path=run/'result.json';native=json.loads(path.read_text()) if path.exists() else None
    report=dict(scope='Actual Character internal flag owner/any-none/IsDeath/selected server control writers; action traces use callback kernel,full action/movement/status/receiver not accepted',script_sha256=sha(Path(__file__)),source=record(source),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],console=record(console),output=record(path) if path.exists() else None,native=native,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-character-flags-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=str(run),exit=result.returncode,native=native,stderr=result.stderr.decode(errors='replace')[-1200:])))
    require(not result.returncode and native and native['status']=='PASS','Character flags native failure')


if __name__=='__main__':main()
