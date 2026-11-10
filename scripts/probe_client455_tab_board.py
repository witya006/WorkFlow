"""Actual455 expandable sections/scrolling;CharInfo caller integration remains open."""
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
    source=WS/'scripts/native/client455_gui_tab_board_probe.cpp';exe=build_full_object_probe('tab-board',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'tab-board-{index:03d}').exists():index+=1
    run=parent/f'tab-board-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['SpriteImage/Common/common.spr','SpriteImage/ko-kr/common.spr','mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        if not(client/name).is_file():continue
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    inputs+=copy_character_shaders(run)
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);out=run/'result.json';native=json.loads(out.read_text()) if out.exists() else None
    frames=[]
    for file in sorted(run.glob('*.bgra')):
        preview=file.with_suffix('.png');Image.frombytes('RGBA',(640,480),file.read_bytes(),'raw','BGRA').convert('RGB').save(preview);frames.append(dict(**record(file),preview=record(preview)))
    relations={}
    if len(frames)==4:
        relations['scroll_changes_image']=(run/'tabs-expanded.bgra').read_bytes()!=(run/'tabs-scrolled.bgra').read_bytes()
        before,after=Image.open(run/'tabs-collapsed.png'),Image.open(run/'tabs-reloaded.png')
        #7B4E30(style0) resets the thumb to6x18.639590(total0) keeps its
        #previous extent. Require that original reset while the header pixels
        #remain exactly stable;full-frame equality was the wrong oracle.
        relations['target_thumb_reset_changes_image']=before.tobytes()!=after.tobytes()
        relations['header_region_unchanged']=before.crop((0,0,227,480)).tobytes()==after.crop((0,0,227,480)).tobytes()
    accepted=result.returncode==0 and native and native.get('status')=='PASS' and len(frames)==4 and all(relations.values())
    report=dict(status='PASS' if accepted else 'FAIL',frame_relations=relations,normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),script=record(Path(__file__)),sources=[record(source)]+[record(WS/'scripts/native'/p) for p in ['client455_gui_tab_board.h','client455_gui_tab_board.cpp']],inputs=inputs,console=record(console),output=record(out) if out.exists() else None,native=native,natural_exit=result.returncode,frames=frames,shared_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/'inventory/client455-tab-board-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,run=run.relative_to(WS).as_posix(),native=native,console=console.read_text(errors='replace')[-1200:])))
    require(report['status']=='PASS','Real tab-board/target reset failed')
if __name__=='__main__':main()
