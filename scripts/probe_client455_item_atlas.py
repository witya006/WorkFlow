"""Probe target atlas callbacks and typed automatic selection on production objects."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders,copy_item_icon_skins
from compare_client_binaries import WS,pe

def main():
    ref=load('client455-item-atlas-reference');source=WS/'scripts/native/client455_item_atlas_probe.cpp';exe=build_full_object_probe('item-atlas',source);holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'item-atlas-{index:03d}').exists():index+=1
    run=holder/f'item-atlas-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping);inputs=[]
    for row in ref['inputs']+ref['fixtures']:
        check(row);original=WS/row['file'];dest=run/('SpriteImage/Common/'+original.name if original.suffix=='.spr' else original.name);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(record(dest))
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF','DataTable/zh-tw/NDLanguage.edf']:
        original,dest=client/name,run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(record(dest))
    inputs+=copy_character_shaders(run);inputs+=copy_item_icon_skins(run);config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Taiwan\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n');inputs.append(record(config))
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';frames=[]
    for raw in sorted(run.glob('*.bgra')):
        preview=raw.with_suffix('.png');Image.frombytes('RGBA',(640,480),raw.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(raw),preview=record(preview)))
    for row in inputs:check(row)
    report=dict(scope=ref['scope'],script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),source=record(source),reference_sha256=sha(WS/'inventory/client455-item-atlas-reference.json'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),
        exe=record(target),map=record(mapping),console=record(console),output=record(output) if output.exists() else None,architecture=pe(target.read_bytes())['architecture'],inputs=inputs,inputs_unchanged=True,frames=frames,natural_exit=result.returncode,native=json.loads(output.read_text()) if output.exists() else None,
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-atlas-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-1500:])))
    require(result.returncode==0 and report['native'] and report['native']['status']=='PASS' and len(frames)==4,'Item-atlas native failure')
if __name__=='__main__':main()
