"""Run typed equipment resource/default owners with selected real assets."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders
from checkpoint_client455_rvp_effects import sha,require,load,check
from audit_client455_resource_catalog import record

def main():
    ref=load('client455-equipment-providers-reference');check(ref['script']);check(ref['expected'])
    for row in ref['sources']:check(row)
    source=WS/'scripts/native/client455_equipment_providers_probe.cpp';exe=build_full_object_probe('equipment-providers',source);root=WS/'work/m9'/sha(exe)[:8];index=1
    while(root/f'equipment-providers-{index:03d}').exists():index+=1
    run=root/f'equipment-providers-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for row in ref['inputs']:
        original=Path(row['original']);dest=run/row['relative'];stage_asset(original,dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=str(original)))
    for relative in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf']:
        original=client/relative;dest=run/relative;stage_asset(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    inputs+=copy_character_shaders(run);fixture=run/'expected.bin';shutil.copyfile(WS/ref['expected']['file'],fixture);inputs.append(record(fixture))
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope=ref['scope'],reference_sha256=sha(WS/'inventory/client455-equipment-providers-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),
        architecture=pe(exe.read_bytes())['architecture'],exe=record(target),map=record(exe.with_suffix('.map')),inputs=inputs,console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    serialized=json.dumps(report,indent=2)+'\n';(run/'equipment-providers-report.json').write_text(serialized);(WS/'inventory/client455-equipment-providers-native.json').write_text(serialized)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1500:])))
    require(result.returncode==0 and native and native['status']=='PASS','Typed equipment failed:'+str(console))
if __name__=='__main__':main()
