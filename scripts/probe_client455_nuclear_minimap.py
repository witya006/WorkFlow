"""Run real MiniMap marker ownership and selected UI rendering in a private lab."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe


def main():
    source=WS/'scripts/native/client455_nuclear_minimap_probe.cpp';exe=build_full_object_probe('nuclear-minimap',source)
    compatibility_source=WS/'scripts/native/client455_linker_window_probe.cpp';compatibility_exe=build_full_object_probe('linker-window-compat',compatibility_source)
    holder=WS/'work/m9'/sha(exe)[:8];n=1
    while(holder/f'nuclear-minimap-{n:03d}').exists():n+=1
    run=holder/f'nuclear-minimap-{n:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    reference=load('client455-minimap-opacity-reference');resources=next(row for row in reference['inputs'] if row['nation']=='Korea')
    relative_resources=[]
    for name in ['common','main']:
        original=Path(resources[name]['file']);require(original.is_relative_to(client) and sha(original)==resources[name]['sha256'],'Pinned actual UI resource');relative_resources.append(original.relative_to(client).as_posix())
    for relative in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf','SpriteImage/Common/mouse.spr']+relative_resources:
        original,dest=client/relative,run/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append(record(config))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for path in sorted(run.glob('*.bgra')):
        preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(path),preview=record(preview)))
    for row in inputs:check(row)
    report=dict(scope='Actual MiniMap3marker owners/init/bounds and typed post-lookup operations,real main/common sprites and natural alpha pulse;registry/race/world-geometry producer/ordinary receiver remain open',script_sha256=sha(Path(__file__)),source=record(source),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],inputs=inputs,console=record(console),output=record(output) if output.exists() else None,native=json.loads(output.read_text()) if output.exists() else None,frames=frames,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report['header_compatibility_build']=dict(source=record(compatibility_source),exe=record(compatibility_exe),map=record(compatibility_exe.with_suffix('.map')),executed=False)
    (WS/'inventory/client455-nuclear-minimap-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=str(run),exit=result.returncode,native=report['native'],header_compatibility_build=True,stderr=result.stderr.decode(errors='replace')[-1400:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS' and len(frames)==6,'Nuclear MiniMap native failure')


if __name__=='__main__':main()
