"""Verify the ordinary center-message owner, real fonts/localization and GPU fade."""
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe


def main():
    source=WS/'scripts/native/client455_center_messages_probe.cpp';exe=build_full_object_probe('center-messages',source)
    holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'center-messages-{index:03d}').exists():index+=1
    run=holder/f'center-messages-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf']:
        original,dest=client/name,run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii');inputs.append(record(config))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for path in sorted(run.glob('*.bgra')):
        preview=path.with_suffix('.png');Image.frombytes('RGBA',(640,480),path.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(path),preview=record(preview)))
    for row in inputs:check(row)
    report=dict(scope='Ordinary MainGame member/center queue and real medium GDI/C1A/CE7/fade GPU; full dispatch/chat/live hover/stage teardown remain open',script_sha256=sha(Path(__file__)),source=record(source),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),reference_sha256=sha(WS/'inventory/client455-system-messages-reference.json'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],inputs=inputs,inputs_unchanged=True,console=record(console),output=record(output) if output.exists() else None,native=json.loads(output.read_text()) if output.exists() else None,frames=frames,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-center-messages-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],console=result.stderr.decode(errors='replace')[-1200:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS','Center message native failure')


if __name__=='__main__':main()
