"""Check actual ordinary MobControl owners,shared movement and local command messages."""
import ctypes,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders
from checkpoint_client455_rvp_effects import sha,require

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    source=WS/'scripts/native/client455_mob_control_probe.cpp';exe=build_full_object_probe('mob-control',source);parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'mob-control-{index:03d}').exists():index+=1
    run=parent/f'mob-control-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['SpriteImage/Common/common.spr','SpriteImage/ko-kr/common.spr','SpriteImage/Common/main.spr','SpriteImage/ko-kr/main.spr','SpriteImage/Common/summon.spr','SpriteImage/ko-kr/summon.spr','mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        if not(client/name).is_file():continue
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    inputs+=copy_character_shaders(run)
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=50,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None;frames=[]
    for file in sorted(run.glob('*.bgra')):
        preview=file.with_suffix('.png');Image.frombytes('RGBA',(640,480),file.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(file),preview=record(preview)))
    accepted=result.returncode==0 and native and native.get('status')=='PASS' and len(frames)==4
    report=dict(status='PASS' if accepted else 'FAIL',normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),script=record(Path(__file__)),sources=[record(source),record(WS/'scripts/native/client455_mob_control.h'),record(WS/'scripts/native/client455_mob_control.inc'),record(WS/'scripts/native/client455_gui_move.inc')],inputs=inputs,console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,frames=frames,shared_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/'inventory/client455-mob-control-native.json').write_text(text);print(json.dumps(dict(exit=result.returncode,run=run.relative_to(WS).as_posix(),native=native,console=console.read_text(errors='replace')[-1200:])));require(accepted,'Actual MobControl/shared movement/GPU failed')
if __name__=='__main__':main()
