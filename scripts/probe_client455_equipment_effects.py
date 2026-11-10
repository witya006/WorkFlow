"""Run source equipment-effect ownership with actual magic and Miles audio."""
import json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_tagged_sound_providers
from audit_client455_equipment import record,sha
from checkpoint_client455_rvp_effects import load,check,require

def main():
    ref=load('client455-equipment-effects-reference');check(ref['script']);check(ref['raw'])
    for source in ref['sources']:check(source)
    source=WS/'scripts/native/client455_equipment_effects_probe.cpp';exe=build_full_object_probe('equipment-effects',source);root=WS/'work/m9'/sha(exe)[:8];index=1
    while(root/f'equipment-effects-{index:03d}').exists():index+=1
    run=root/f'equipment-effects-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
    for row in ref['inputs']:
        original=Path(row['original']);dest=run/row['relative'];stage_asset(original,dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=str(original)))
    inputs+=copy_tagged_sound_providers(run)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);stage_asset(client/'mss32.dll',run/'mss32.dll');inputs.append(record(run/'mss32.dll'))
    config=run/'R3Engine.ini';config.write_text('[Sound]\nSound=TRUE\nMusic=FALSE\n[Path]\nSoundPath=.\\Snd\\\nEffectPath=.\\Effect\\\n',encoding='ascii');inputs.append(record(config))
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope=ref['scope'],reference_sha256=sha(WS/'inventory/client455-equipment-effects-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(exe.with_suffix('.map')),architecture=pe(target.read_bytes())['architecture'],inputs=inputs,
        console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-effects-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1600:])))
    require(result.returncode==0 and native and native['status']=='PASS','Equipment effect source execution failed:'+str(console))
if __name__=='__main__':main()
