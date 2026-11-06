"""Run the full source briefing provider,capture routing and real portraits."""
import ctypes,hashlib,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    reference_path=WS/'inventory/client455-briefing-window-reference.json';reference=json.loads(reference_path.read_text())
    if reference['script_sha256']!=sha(WS/'scripts/audit_client455_briefing_window.py'):raise ValueError('Refresh window reference')
    source=WS/'scripts/native/client455_briefing_window_probe.cpp';exe=build_full_object_probe('briefing-window',source)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);holder=WS/'work/m9'/sha(exe)[:8];holder.mkdir(parents=True,exist_ok=True);runs=[]
    for row in reference['inputs']:
        nation,folder=row['nation'],row['folder'];index=1
        while (holder/f'briefing-window-{folder}-{index:03d}').exists():index+=1
        run=holder/f'briefing-window-{folder}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
        names=['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF',f'DataTable/{folder}/NDLanguage.edf','SpriteImage/Common/mouse.spr',row['common']['relative'],row['tutorial']['relative']]+[p['relative'] for p in row['portraits']]
        expected={r['relative']:r['sha256'] for r in [row['common'],row['tutorial'],*row['portraits']]}
        for name in names:
            path,destination=client/name,run/name
            if name in expected and sha(path)!=expected[name]:raise ValueError('Changed resource:'+name)
            destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,destination);inputs.append({'file':destination.relative_to(WS).as_posix(),'sha256':sha(destination)})
        config=run/'R3Engine.ini';config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
        startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
        finally:
            remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes,remove.restype=[ctypes.c_wchar_p],ctypes.c_int;remove(str(run/'System/010.TTF'))
        (run/'console.txt').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError('Briefing window runtime:'+str(result.returncode)+':'+str(run)+':'+result.stderr.decode(errors='replace'))
        output=run/'result.json';frames=[]
        for frame in sorted(run.glob('*.bgra')):
            preview=frame.with_suffix('.png');Image.frombytes('RGBA',(640,480),frame.read_bytes(),'raw','BGRA').convert('RGB').save(preview)
            frames.append({'file':frame.relative_to(WS).as_posix(),'sha256':sha(frame),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview),'width':640,'height':480})
        runs.append({'nation':nation,'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'inputs':inputs,'frames':frames,'native':json.loads(output.read_text()),'exit':result.returncode})
    names=['client455_briefing_window.h','client455_briefing_window.cpp','client455_screen_message.inc','client455_briefing_controls.h','client455_briefing_controls.cpp','client455_gui_text_typing_board.h','client455_gui_text_typing_board.cpp']
    report={'scope':'Actual source briefing window/provider,real GUI screen capture and portrait resources;actual Tutorial stage not connected','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'sources':{name:sha(WS/'scripts/native'/name) for name in names},'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'reference_sha256':sha(reference_path),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'map':{'file':exe.with_suffix('.map').relative_to(WS).as_posix(),'sha256':sha(exe.with_suffix('.map'))},'runs':runs,'actual_Tutorial_stage_connected':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-briefing-window-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'nation':row['nation'],**row['native']} for row in runs]))
if __name__=='__main__':main()
