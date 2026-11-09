"""Exercise ordinary message entry/Login and live Avatar/BSP/effect/Miles hover cancel."""
import json,os,shutil,subprocess
from pathlib import Path
from PIL import Image
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders,copy_tagged_sound_providers
from compare_client_binaries import WS,pe


def main():
    # Avoid Windows' legacy installer heuristic for an EXE name containing
    # "patch" (even as part of "dispatch"). This is a regular offline lab.
    source=WS/'scripts/native/client455_message_dispatch_probe.cpp';exe=build_full_object_probe('message-output',source);holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'message-output-{index:03d}').exists():index+=1
    run=holder/f'message-output-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    world_manifest=WS/'inventory/client455-rvp-actor-native.json'
    for row in json.loads(world_manifest.read_text())['inputs']:
        if 'original' not in row:continue
        original=Path(row['original']);require(original.is_relative_to(client),'Actual world input');check(row);require(sha(original)==row['sha256'],'World input drift')
        dest=run/original.relative_to(client);dest.parent.mkdir(parents=True,exist_ok=True);os.link(WS/row['file'],dest);inputs.append(dict(**record(dest),original=str(original)))
    for row in load('client455-board-hover-reference')['inputs']:
        check(row);original=WS/row['file'];dest=run/row.get('runtime_relative',('SpriteImage/Common/'+original.name if original.suffix=='.spr' else original.name));dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(record(dest))
    for name in ['mss32.dll','Snd/WaveList.spt','Snd/Character/Newclear/Radar_00.wav','Effect/EffectEntity59.rpk','Effect/EffectEntityList.spt','Effect/MagicSptList.spt','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf','DataTable/ko-kr/Cska.txt']:
        original,dest=client/name,run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    inputs+=copy_character_shaders(run)+copy_tagged_sound_providers(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Path]\nSoundPath=.\\Snd\\\nEffectPath=.\\Effect\\\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append(record(config))
    settings=run/'DataTable/GameSetting.ini';settings.write_text('[ChatMode]\nAll=0\nParty=0\nGuild=0\nSystem=0\n[DefModeOn]\nAll=0\n',encoding='ascii');before=run/'settings-before.ini';shutil.copyfile(settings,before);inputs.append(record(before))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup);console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for path in sorted(run.glob('*.bgra')):
        preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(path),preview=record(preview)))
    for row in inputs:check(row)
    report=dict(scope='Actual ordinary formatter/MainApp/Login/4pane and live Avatar+real item+neutralAS1+effect6+Miles cancellation; Tutorial kernel only,CE7 registration/full stages remain open',script_sha256=sha(Path(__file__)),source=record(source),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),runtime_inputs_sha256=sha(WS/'scripts/client455_runtime_inputs.py'),reference_sha256=sha(WS/'inventory/client455-message-dispatch-reference.json'),world_input_manifest=record(world_manifest),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],console=record(console),inputs=inputs,inputs_unchanged=True,persisted_settings=record(settings),output=record(output) if output.exists() else None,frames=frames,native=json.loads(output.read_text()) if output.exists() else None,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-message-dispatch-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-2200:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS' and len(frames)==5,'Message dispatch native failure')


if __name__=='__main__':main()
