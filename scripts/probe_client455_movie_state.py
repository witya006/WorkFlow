"""Exercise actual movie state/display/FOV on own GPU and inspect actual player stub."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source=WS/'scripts/native/client455_movie_state_probe.cpp';exe=build_full_object_probe('movie-state',source);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);holder=WS/'work/m9'/sha(exe)[:8];holder.mkdir(parents=True,exist_ok=True);index=1
    while (holder/f'movie-state-{index:03d}').exists():index+=1
    run=holder/f'movie-state-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping);inputs=[]
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg']:
        destination=run/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(client/name,destination);inputs.append({'file':destination.relative_to(WS).as_posix(),'sha256':sha(destination)})
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
    raw=exe.read_bytes();frame=symbol(mapping.read_text(),'?RTMovieFrameMove@@YAXXZ');entry=read_va(raw,frame,16);stub={'rva':hex(frame-pe(raw)['image_base']),'entry_bytes':entry.hex(),'compiled_player_stub':entry.startswith(b'\xc3') or entry.startswith(b'\x55\x8b\xec\x5d\xc3')}
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0;result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup);console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for image in sorted(run.glob('*.bgra')):
        preview=image.with_suffix('.png');Image.frombytes('RGBA',(640,480),image.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append({'file':image.relative_to(WS).as_posix(),'sha256':sha(image),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview)})
    def record(path):return {'file':path.relative_to(WS).as_posix(),'sha256':sha(path)} if path.exists() else None
    report={'scope':'Real positive flags/display/defaultFOV;full RVP player remains a confirmed compiled stub','source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'engine_report_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'reference_sha256':sha(WS/'inventory/client455-movie-state-reference.json'),'architecture':pe(raw)['architecture'],'exe':record(target),'map':record(mapping),'console':record(console),'output':record(output),'inputs':inputs,'frames':frames,'player_evidence':stub,'natural_exit':result.returncode,'native':json.loads(output.read_text()) if output.exists() else None,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-movie-state-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'exit':result.returncode,'run':run.relative_to(WS).as_posix(),'native':report['native'],'player_evidence':stub,'console':result.stderr.decode(errors='replace')[-2200:]}))
    if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
