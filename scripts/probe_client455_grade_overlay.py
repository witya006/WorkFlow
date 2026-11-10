"""Exercise real grade textures,material bytes,shaders and device states."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders,copy_grade_overlay_inputs
from audit_client455_equipment import record,sha
from test_map455 import archive

def main():
    source=WS/'scripts/native/client455_grade_overlay_probe.cpp';exe=build_full_object_probe('grade-overlay',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'grade-overlay-{index:03d}').exists():index+=1
    run=parent/f'grade-overlay-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    ref=json.loads((WS/'inventory/client455-equipment-reference.json').read_text())
    for row in ref['inputs']:
        dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=row['original']))
    fixture=WS/ref['expected']['file'];assert sha(fixture)==ref['expected']['sha256'];shutil.copyfile(fixture,run/'expected.bin');inputs.append(record(run/'expected.bin'))
    inputs+=copy_character_shaders(run)+copy_grade_overlay_inputs(run,mutable_materials=True)
    fixture_root=run/'grade-archive-flag';(fixture_root/'dir').mkdir(parents=True);(fixture_root/'fixture.rpk').write_bytes(archive());(fixture_root/'dir/a.spt').write_bytes(b'Loose')
    inputs+=[record(fixture_root/'fixture.rpk'),record(fixture_root/'dir/a.spt')]
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope='Actual grade material loader/UV shader constants9-10 andreal equipment geometry in controlled pose;full ordinary equipment draw stillopen',source=record(source),source_include=record(WS/'scripts/native/client455_equipment_probe.cpp'),script=record(Path(__file__)),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),inputs=inputs,console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,
        frame=record(run/'grade-model.png') if (run/'grade-model.png').exists() else None,baseline_frame=record(run/'grade-model-base.png') if (run/'grade-model-base.png').exists() else None,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/'inventory/client455-grade-overlay-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1000:],run=run.relative_to(WS).as_posix())))
    if result.returncode or not native or native['status']!='PASS':raise ValueError('Actual grade overlay failed;inspect '+str(run))
    assert all(sha(WS/row['file'])==row['sha256'] for row in inputs),'Private fixture must restore input bytes'
if __name__=='__main__':main()
