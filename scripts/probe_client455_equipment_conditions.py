"""Run typed equipment condition code withreal EDFs andsmall owned fixtures."""
import json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from audit_client455_equipment import record,sha
from checkpoint_client455_rvp_effects import load,check,require

def main():
    ref=load('client455-equipment-conditions-reference')
    for key in ['raw','reused_raw','script','decoder_script','regions_script','expected','synthetic']:check(ref[key])
    for row in ref['sources']:check(row)
    source=WS/'scripts/native/client455_equipment_conditions_probe.cpp';exe=build_full_object_probe('equipment-conditions',source);root=WS/'work/m9'/sha(exe)[:8];index=1
    while(root/f'equipment-conditions-{index:03d}').exists():index+=1
    run=root/f'equipment-conditions-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
    #Keep the map beside its run:future compilations must not overwrite this
    #run's evidence. The large client assets are unnecessary for this CPU path.
    saved_map=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),saved_map)
    for row in ref['inputs']:
        dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=row['original']))
    stage_asset(WS/ref['synthetic']['file'],run/'fixture.edf',expected=ref['synthetic']['sha256']);inputs.append(record(run/'fixture.edf'))
    shutil.copyfile(WS/ref['expected']['file'],run/'expected.bin');inputs.append(record(run/'expected.bin'))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);stage_asset(client/'mss32.dll',run/'mss32.dll');inputs.append(dict(**record(run/'mss32.dll'),original=str(client/'mss32.dll')))
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope=ref['scope'],reference_sha256=sha(WS/'inventory/client455-equipment-conditions-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),staging_script=record(WS/'scripts/client455_asset_staging.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(saved_map),architecture=pe(target.read_bytes())['architecture'],inputs=inputs,
        console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'conditions-report.json').write_text(text);(WS/'inventory/client455-equipment-conditions-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-2000:])))
    require(result.returncode==0 and native and native['status']=='PASS','Equipment condition source failed:'+str(console))
if __name__=='__main__':main()
