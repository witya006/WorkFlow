"""Real455 upper HUD through ordinary client objects; no login or bulk suite."""
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
    parser=argparse.ArgumentParser()
    parser.add_argument('--avatar-health',action='store_true')
    args=parser.parse_args()
    source=WS/'scripts/native/client455_hud_probe.cpp';exe=build_full_object_probe('hud',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'hud-{index:03d}').exists():index+=1
    run=parent/f'hud-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    inputs=[];client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for folder in ['Common','ko-kr']:
        for name in ['main.spr','common.spr','EtcUI.spr']:
            path=client/'SpriteImage'/folder/name
            if path.is_file():
                dest=run/'SpriteImage'/folder/name;stage_asset(path,dest);inputs.append(dict(**record(dest),original=str(path)))
    for name in ['mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    inputs+=copy_character_shaders(run)
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    options=['--avatar-health'] if args.avatar_health else []
    try:result=subprocess.run([str(target),*options],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);out=run/'result.json';native=json.loads(out.read_text()) if out.exists() else None
    frames=[]
    for file in sorted(run.glob('*.bgra')):
        png=file.with_suffix('.png');Image.frombytes('RGBA',(640,480),file.read_bytes(),'raw','BGRA').convert('RGB').save(png);frames.append(dict(**record(file),preview=record(png)))
    report=dict(status='PASS' if result.returncode==0 and native else 'FAIL',normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),script=record(Path(__file__)),sources=[record(source)]+[record(WS/'scripts/native'/p) for p in ['client455_hud.inc','client455_hud_members.inc','client455_image_text.h','client455_image_text.cpp']],inputs=inputs,console=record(console),output=record(out) if out.exists() else None,natural_exit=result.returncode,native=native,frames=frames,shared_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text)
    if not args.avatar_health:
        (WS/'inventory/client455-hud-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,run=run.relative_to(WS).as_posix(),native=native,console=console.read_text(errors='replace')[-1200:])))
    require(report['status']=='PASS' and len(frames)==(4 if args.avatar_health else 3),'Actual HUD failed')
    if args.avatar_health:
        require(native['avatar_health']==dict(hp=[160000,90000,70000,0],impact_damage=70000,hp_after_impact=160000,
                                             invalid_lengths=2,mounted_player_hp_retained=True),
                'Authoritative avatar HP did not reach the real HUD')
    require((run/'hud-initial.bgra').read_bytes()!=(run/'hud-changed.bgra').read_bytes(),'Gauge/number change invisible')
    require((run/'hud-changed.bgra').read_bytes()==(run/'hud-reloaded.bgra').read_bytes(),'Actual sprite reacquisition drift')
if __name__=='__main__':main()
