"""Drive and render the real six-track aiming cue through ordinary client methods."""
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require, sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def main():
    source=WS/'scripts/native/client455_effect_runtime_probe.cpp';exe=build_full_object_probe('effect-runtime',source)
    holder=WS/'work/m9'/sha(exe)[:8];index=1
    while (holder/f'effect-runtime-{index:03d}').exists():index+=1
    run=holder/f'effect-runtime-{index:03d}';run.mkdir(parents=True);target=run/exe.name
    shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['Effect/EffectEntity59.rpk','Effect/EffectEntityList.spt','Effect/MagicSptList.spt','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso']:
        original,dest=client/name,run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    config=run/'R3Engine.ini';config.write_text('[Path]\nEffectPath=.\\Effect\\\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append(record(config))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for path in sorted(run.glob('*.bgra')):
        preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(path),preview=record(preview)))
    report=dict(scope='Actual ordinary effect scheduler/render passes and cancellation with real aiming resources on controlled D3D camera; full nuclear owner/world order/device lifecycle remain open',source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),reference_sha256=sha(WS/'inventory/client455-effect-runtime-reference.json'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],console=record(console),inputs=inputs,frames=frames,output=record(output) if output.exists() else None,native=json.loads(output.read_text()) if output.exists() else None,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-effect-runtime-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-1300:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS' and len(frames)==4,'Effect runtime failure')


if __name__=='__main__':main()
