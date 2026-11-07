"""Run typed owners and unchanged data/SF checks on actual production providers."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe

def main():
    ref=load('client455-item-object-reference');runs=[]
    for row in ref['inputs']+ref['fixtures']:check(row)
    names=[('item-object','client455_item_object_probe.cpp'),('item-object-data','client455_item_payloads_probe.cpp'),('item-object-sf','client455_skill_force_items_probe.cpp')]
    for name,source_name in names:
        source=WS/'scripts/native'/source_name;exe=build_full_object_probe(name,source);root=WS/'work/m9'/sha(exe)[:8];index=1
        while(root/f'{name}-{index:03d}').exists():index+=1
        run=root/f'{name}-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
        for row in ref['inputs']+ref['fixtures']:
            original=WS/row['file'];copy=run/original.name;shutil.copyfile(original,copy);inputs.append(record(copy))
        result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
        console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
        runs.append(dict(name=name,source=record(source),exe=record(target),map=record(exe.with_suffix('.map')),inputs=inputs,console=record(console),output=record(output) if output.exists() else None,
            architecture=pe(exe.read_bytes())['architecture'],natural_exit=result.returncode,native=json.loads(output.read_text()) if output.exists() else None))
    report=dict(scope='Ordinary typed item592/board620/CMainApp manager and actual pack removal/null-icon domain;production providers also pass previous payload/SF data probes',
        script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),reference_sha256=sha(WS/'inventory/client455-item-object-reference.json'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),runs=runs,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-object-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exits=[r['natural_exit'] for r in runs],native=[r['native'] for r in runs])))
    require(all(not r['natural_exit'] and r['native'] and r['native']['status']=='PASS' for r in runs),'Ordinary item-object runtime failed:inspect consoles')
if __name__=='__main__':main()
