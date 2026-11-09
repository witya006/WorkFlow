"""Exercise the MainGame-owned aiming core with real BSP, effects and Miles."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,require,sha
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders,copy_tagged_sound_providers
from compare_client_binaries import WS,pe


def main():
    source=WS/'scripts/native/client455_nuclear_aiming_probe.cpp';exe=build_full_object_probe('nuclear-aiming',source);holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'nuclear-aiming-{index:03d}').exists():index+=1
    run=holder/f'nuclear-aiming-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    world_manifest=WS/'inventory/client455-rvp-actor-native.json';world=json.loads(world_manifest.read_text())
    for row in world['inputs']:
        if 'original' not in row:continue
        original=Path(row['original']);require(original.is_relative_to(client),'Actual client input');check(row);require(sha(original)==row['sha256'],'Original input drift')
        dest=run/original.relative_to(client);dest.parent.mkdir(parents=True,exist_ok=True);os.link(WS/row['file'],dest);inputs.append(dict(**record(dest),original=str(original)))
    for name in ['mss32.dll','Snd/WaveList.spt','Snd/Character/Newclear/Radar_00.wav','Effect/EffectEntity59.rpk','Effect/EffectEntityList.spt','Effect/MagicSptList.spt']:
        original,dest=client/name,run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    inputs+=copy_character_shaders(run)+copy_tagged_sound_providers(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Path]\nSoundPath=.\\Snd\\\nEffectPath=.\\Effect\\\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii')
    missing=run/'missing-cue.spt';missing.write_text('[MagicSptList]\nend\n',encoding='ascii');inputs+=[record(config),record(missing)]
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
    for row in inputs:check(row)
    report=dict(scope='Actual MainGame-owned aiming core with real BSP cursor/archived effects/tagged Miles;this lab doesnot exercise the ordinary receiver/full world order',source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),runtime_inputs_sha256=sha(WS/'scripts/client455_runtime_inputs.py'),world_input_manifest=record(world_manifest),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],console=record(console),inputs=inputs,inputs_unchanged=True,output=record(output) if output.exists() else None,native=json.loads(output.read_text()) if output.exists() else None,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report['reference_sha256']=sha(WS/'inventory/client455-nuclear-aiming-reference.json')
    (WS/'inventory/client455-nuclear-aiming-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-1800:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS','Nuclear aiming native failure')


if __name__=='__main__':main()
