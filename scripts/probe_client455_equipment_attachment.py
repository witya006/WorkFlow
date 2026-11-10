"""Run source attachment providers onreal assembled parts andactual magic."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders
from audit_client455_equipment import record,sha
from checkpoint_client455_rvp_effects import load,check,require

def main():
    ref=load('client455-equipment-attachment-reference')
    for key in ['script','raw','reused_raw','decoder_script','regions_script']:check(ref[key])
    for source in ref['sources']:check(source)
    source=WS/'scripts/native/client455_equipment_attachment_probe.cpp';exe=build_full_object_probe('equipment-attachment',source);root=WS/'work/m9'/sha(exe)[:8];index=1
    while(root/f'equipment-attachment-{index:03d}').exists():index+=1
    run=root/f'equipment-attachment-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
    for row in ref['inputs']:
        dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=row['original']))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for relative in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf']:
        original=client/relative;dest=run/relative;stage_asset(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    inputs+=copy_character_shaders(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii');inputs.append(record(config))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope=ref['scope'],reference_sha256=sha(WS/'inventory/client455-equipment-attachment-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),staging_script=record(WS/'scripts/client455_asset_staging.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(exe.with_suffix('.map')),architecture=pe(target.read_bytes())['architecture'],inputs=inputs,
        console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'attachment-report.json').write_text(text);(WS/'inventory/client455-equipment-attachment-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1700:])))
    require(result.returncode==0 and native and native['status']=='PASS','Equipment attachment failed:'+str(console))
if __name__=='__main__':main()
