"""Verify actual ordinary common-object constructors/copies and lifecycle."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe

def main():
    reference=load('client455-resource-object-reference')
    for row in reference['fixtures']:check(row)
    source=WS/'scripts/native/client455_resource_object_probe.cpp';exe=build_full_object_probe('resource-object',source)
    root=WS/'work/m9'/sha(exe)[:8];index=1
    while(root/f'resource-object-{index:03d}').exists():index+=1
    run=root/f'resource-object-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
    for row in reference['fixtures']:
        original=WS/row['file'];copy=run/original.name;shutil.copyfile(original,copy);inputs.append(record(copy))
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
    report=dict(scope='Actual ordinary CObject80/CResObject584 construction/copy/name/flags/effect-clear on source providers;live FX cache/game/itemwrapper not accepted',
        script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),source=record(source),
        reference_sha256=sha(WS/'inventory/client455-resource-object-reference.json'),exe=record(target),map=record(exe.with_suffix('.map')),
        console=record(console),output=record(output) if output.exists() else None,inputs=inputs,architecture=pe(exe.read_bytes())['architecture'],
        native=json.loads(output.read_text()) if output.exists() else None,natural_exit=result.returncode,
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-resource-object-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exit=result.returncode,native=report['native'],console=console.read_text(errors='replace')[-1500:])))
    require(result.returncode==0 and report['native'] and report['native']['status']=='PASS','Actual resource-object probe failed')
if __name__=='__main__':main()
