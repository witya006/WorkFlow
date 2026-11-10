"""Exercise source frame/ANI/attachment/audio against real pinned resources."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders,copy_tagged_sound_providers
from audit_client455_equipment import record,sha
from checkpoint_client455_rvp_effects import load,check,require

def main():
    ref=load('client455-equipment-frame-reference')
    for key in ['raw','script','decoder','verifier','preparer','owner_port','prior_runtime']:check(ref[key])
    for row in ref['sources']:check(row)
    source=WS/'scripts/native/client455_equipment_effects_probe.cpp';exe=build_full_object_probe('equipment-frame',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'equipment-frame-{index:03d}').exists():index+=1
    run=parent/f'equipment-frame-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    #Old manifests supply immutable resource bytes,not current source evidence.
    selected={};manifests=[]
    for name in ['equipment','equipment-providers','equipment-effects']:
        file=WS/f'inventory/client455-{name}-reference.json';body=json.loads(file.read_text());manifests.append(record(file))
        for row in body['inputs']:
            key=row['relative'].replace('\\','/').lower()
            if key in selected:require(selected[key]['sha256']==row['sha256'],'Contradictory resource bytes')
            selected[key]=row
    inputs=[]
    for row in selected.values():
        dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=row['original']))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for name in ['mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    inputs+=copy_character_shaders(run)+copy_tagged_sound_providers(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=TRUE\nMusic=FALSE\n[Path]\nSoundPath=.\\Snd\\\nEffectPath=.\\Effect\\\n',encoding='ascii');inputs.append(record(config))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frame=run/'frame-result.json'
    native=json.loads(output.read_text()) if output.exists() else None;frames=json.loads(frame.read_text()) if frame.exists() else None
    report=dict(scope=ref['scope'],reference=record(WS/'inventory/client455-equipment-frame-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],resource_manifests=manifests,inputs=inputs,
        console=record(console),output=record(output) if output.exists() else None,frame_output=record(frame) if frame.exists() else None,native=native,frame_native=frames,natural_exit=result.returncode,
        shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/'inventory/client455-equipment-frame-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,frame=frames,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1800:],run=run.relative_to(WS).as_posix())))
    require(result.returncode==0 and native and native['status']=='PASS' and frames and frames['status']=='PASS','Actual equipment frame execution failed:'+str(console))
    for row in inputs:check(row)

if __name__=='__main__':main()
