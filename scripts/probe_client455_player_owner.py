"""Run actual embedded player equipment,pose,draw,skill and sound routes."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders,copy_tagged_sound_providers
from audit_client455_equipment import record,sha
from checkpoint_client455_rvp_effects import check,require


def main():
    source=WS/'scripts/native/client455_player_owner_probe.cpp'
    exe=build_full_object_probe('player-owner',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'player-owner-{index:03d}').exists():index+=1
    run=parent/f'player-owner-{index:03d}';run.mkdir(parents=True)
    target=run/exe.name;shutil.copyfile(exe,target)
    mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    selected={};manifests=[]
    for name in ['equipment','equipment-providers','equipment-effects']:
        file=WS/f'inventory/client455-{name}-reference.json'
        manifests.append(record(file))
        for row in json.loads(file.read_text())['inputs']:
            key=row['relative'].replace('\\','/').lower()
            if key in selected:require(selected[key]['sha256']==row['sha256'],'Contradictory owner resource')
            selected[key]=row
    inputs=[]
    for row in selected.values():
        dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256'])
        inputs.append(dict(**record(dest),original=row['original']))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for name in ['DataTable/SkillForce.edf','mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    inputs+=copy_character_shaders(run)+copy_tagged_sound_providers(run)
    world=json.loads((WS/'inventory/client455-graphics-runtime.json').read_text())
    lobby=next(case for case in world['cases'] if case['case']=='level-lobby')
    for row in lobby['archives']:
        if not row['path'].lower().startswith('map/lobby/'):continue
        dest=run/row['path'];stage_asset(client/row['path'],dest,row['sha256']);inputs.append(dict(**record(dest),original=str(client/row['path'])))
    config=run/'R3Engine.ini'
    config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=TRUE\nMusic=FALSE\n[Path]\nSoundPath=.\\Snd\\\nEffectPath=.\\Effect\\\n',encoding='ascii')
    inputs.append(record(config))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:
        result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int
        remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr)
    output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    frames=[record(path) for path in sorted(run.glob('player-owner-*.png'))]
    sources=[record(WS/'scripts/native'/name) for name in ['client455_player_owner.cpp','client455_player_owner_probe.cpp','client455_player_equipment.h','client455_equipment_object.h','client455_equipment_object.cpp','client455_equipment_frame.inc','client455_equipment_conditions.h','client455_skill_force_items.h','client455_skill_force_items.cpp','client455_grade_overlay_probe.cpp','client455_equipment_probe.cpp']]
    report=dict(scope='Actual primary embedded CPlayerProc numeric equipment/pose/render and Avatar skill-board callbacks;partial client integration',
        script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),sources=sources,
        owner_port=record(WS/'scripts/client455_player_owner_port.py'),preparer=record(WS/'scripts/prepare_client455_normal.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],
        inputs=inputs,resource_manifests=manifests,console=record(console),output=record(output) if output.exists() else None,native=native,frames=frames,
        natural_exit=result.returncode,actor_lighting=record(run/'actor-lighting.jsonl') if (run/'actor-lighting.jsonl').exists() else None,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text)
    (WS/'inventory/client455-player-owner-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,frames=len(frames),staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1800:],run=run.relative_to(WS).as_posix())))
    require(result.returncode==0 and native and native['status']=='PASS','Actual player owner execution failed:'+str(console))
    require(len(frames)==3,'Missing ordinary equipment frames')
    for row in inputs:check(row)


if __name__=='__main__':main()
