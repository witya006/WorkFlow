"""Verify real source fullscreen render targets on own executable,never input EXEs."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe
from client455_runtime_inputs import copy_sky_resources
from client455_asset_staging import stage_asset,staging_stats

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source=WS/'scripts/native/client455_fullscreen_effect_probe.cpp';exe=build_full_object_probe('fullscreen-effect',source);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);holder=WS/'work/m9'/sha(exe)[:8];holder.mkdir(parents=True,exist_ok=True);index=1
    while (holder/f'fullscreen-effect-{index:03d}').exists():index+=1
    run=holder/f'fullscreen-effect-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping);inputs=[]
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg']:
        destination=run/name;destination.parent.mkdir(parents=True,exist_ok=True);stage_asset(client/name,destination);inputs.append({'file':destination.relative_to(WS).as_posix(),'sha256':sha(destination)})
    inputs+=copy_sky_resources(run)
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0;result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup);console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for frame in sorted(run.glob('*.bgra')):
        preview=frame.with_suffix('.png');Image.frombytes('RGBA',(640,480),frame.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append({'file':frame.relative_to(WS).as_posix(),'sha256':sha(frame),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview)})
    def record(path):return {'file':path.relative_to(WS).as_posix(),'sha256':sha(path)} if path.exists() else None
    report={'scope':'Real R3BeginScene/FullScreenEffect/R3EndScene texture/depth/viewport/UI and density paths;not water/bloom/fullgame acceptance','source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'engine_report_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'reference_sha256':sha(WS/'inventory/client455-fullscreen-effect-reference.json'),'architecture':pe(exe.read_bytes())['architecture'],'exe':record(target),'map':record(mapping),'console':record(console),'output':record(output),'inputs':inputs,'frames':frames,'natural_exit':result.returncode,'native':json.loads(output.read_text()) if output.exists() else None,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['shared_asset_staging']=staging_stats();report['asset_staging_script_sha256']=sha(WS/'scripts/client455_asset_staging.py')
    (WS/'inventory/client455-fullscreen-effect-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'exit':result.returncode,'run':run.relative_to(WS).as_posix(),'native':report['native'],'console':result.stderr.decode(errors='replace')[-2500:]}))
    if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
