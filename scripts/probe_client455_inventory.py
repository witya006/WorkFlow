"""Exercise ordinary inventory/pack/equipment view methods with exact stock skins."""
import argparse,ctypes,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders
from checkpoint_client455_rvp_effects import sha,require

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--nation',choices=['Taiwan','Korea'],default='Taiwan');args=parser.parse_args();folder='zh-tw' if args.nation=='Taiwan' else 'ko-kr'
    source=WS/'scripts/native/client455_inventory_probe.cpp';exe=build_full_object_probe('inventory',source);parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'inventory-{index:03d}').exists():index+=1
    run=parent/f'inventory-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    names=['mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso',f'DataTable/{folder}/NDLanguage.edf']+[f'SpriteImage/{locale}/{name}' for locale in ['Common',folder] for name in ['common.spr','inventory.spr','SocketState.spr']]
    for name in names:
        if not(client/name).is_file():continue
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    inputs+=copy_character_shaders(run)
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage='+args.nation+'\n[RenderState]\nScreenXSize=800\nScreenYSize=600\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None;frames=[]
    for file in sorted(run.glob('*.bgra')):
        preview=file.with_suffix('.png');Image.frombytes('RGBA',(800,600),file.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(file),preview=record(preview)))
    accepted=result.returncode==0 and native and native.get('status')=='PASS' and len(frames)==4
    report=dict(status='PASS' if accepted else 'FAIL',nation=args.nation,normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),script=record(Path(__file__)),sources=[record(source),record(WS/'scripts/native/client455_inventory.inc'),record(WS/'scripts/client455_inventory_port.py')],inputs=inputs,console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,frames=frames,shared_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/'inventory/client455-inventory-native.json').write_text(text);print(json.dumps(dict(exit=result.returncode,run=run.relative_to(WS).as_posix(),native=native,console=console.read_text(errors='replace')[-1200:])));require(accepted,'Actual inventory/pack/equipment view probe failed')
if __name__=='__main__':main()
