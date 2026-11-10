"""Check corrected slot construction andactual resource-backed visual guards."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders
from audit_client455_equipment import record,sha

def main():
    ref=json.loads((WS/'inventory/client455-player-visual-reference.json').read_text())
    for row in ref['sources']+[ref['raw'],ref['script']]:assert sha(WS/row['file'])==row['sha256']
    source=WS/'scripts/native/client455_player_equipment_probe.cpp';exe=build_full_object_probe('player-visual',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'player-visual-{index:03d}').exists():index+=1
    run=parent/f'player-visual-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    old=json.loads((WS/'inventory/client455-equipment-reference.json').read_text())
    for row in old['inputs']:
        dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=row['original']))
    for name in ['mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    inputs+=copy_character_shaders(run);fixture=WS/old['expected']['file'];assert sha(fixture)==old['expected']['sha256'];shutil.copyfile(fixture,run/'expected.bin');inputs.append(record(run/'expected.bin'))
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=50,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope=ref['scope'],reference=record(WS/'inventory/client455-player-visual-reference.json'),source=record(source),script=record(Path(__file__)),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),inputs=inputs,console=record(console),output=record(output) if output.exists() else None,
        native=native,natural_exit=result.returncode,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/'inventory/client455-player-visual-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1200:],run=run.relative_to(WS).as_posix())))
    if result.returncode or not native or native['status']!='PASS':raise ValueError('Player visual source failed;inspect '+str(run))
    assert all(sha(WS/row['file'])==row['sha256'] for row in inputs)

if __name__=='__main__':main()
