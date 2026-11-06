"""Real camera files via ordinary CAniCamera,typed materialization,playback and device projection."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    source=WS/'scripts/native/client455_camera_probe.cpp';exe=build_full_object_probe('camera',source);ref=json.loads((WS/'inventory/client455-camera-reference.json').read_text());client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    while (parent/f'camera-{index:03d}').exists():index+=1
    run=parent/f'camera-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg']+[row['relative'] for row in ref['inputs']]:
        original=client/name;copy=run/name;copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=35,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup);(run/'console.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Actual camera455 runtime:'+str(result.returncode)+':'+str(run))
    outputs=[]
    for row in ref['inputs']:
        original=Path(row['file']);out=run/(original.stem+'.roundtrip.cam')
        if sha(original)!=row['sha256'] or out.read_bytes()!=original.read_bytes():raise ValueError('Camera parser/materialization roundtrip:'+str(out))
        outputs.append({'file':out.relative_to(WS).as_posix(),'sha256':sha(out)})
    synthetic=run/'synthetic13.cam';syntheticOut=run/'synthetic13.roundtrip.cam'
    if synthetic.read_bytes()!=syntheticOut.read_bytes():raise ValueError('Synthetic1.3 roundtrip')
    outputs +=[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in [synthetic,syntheticOut]]
    output=run/'result.json';report={'scope':'Ordinary CAniCamera1.2/1.3 load/materialization/play/projection/release and rawroundtrip;not fullTutorial or allmatrix numericdomains','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'sources':{name:sha(WS/'scripts/native'/name) for name in ['client455_camera.h','client455_camera.cpp','client455_camera_load.inc','client455_camera_play.inc']},'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'map':{'file':exe.with_suffix('.map').relative_to(WS).as_posix(),'sha256':sha(exe.with_suffix('.map'))},'inputs':inputs,'roundtrip_outputs':outputs,'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'native':json.loads(output.read_text()),'reference_sha256':sha(WS/'inventory/client455-camera-reference.json'),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'engine_build_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'natural_exit':result.returncode,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-camera-native.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report['native']))
if __name__=='__main__':main()
