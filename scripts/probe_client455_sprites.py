"""Actual normal LoadData/GUI sprites,real payloads,rendering and clean process exit."""
import ctypes,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=WS/'scripts/native/client455_sprites_probe.cpp';exe=build_full_object_probe('sprites',source);ref=json.loads((WS/'inventory/client455-sprites-reference.json').read_text());client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);runs=[]
    for nation,folder in [('Korea','ko-kr'),('Russia','ru-ru')]:
        index=1
        while (parent/f'sprites-{folder}{index:03d}').exists():index+=1
        run=parent/f'sprites-{folder}{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
        for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF',f'DataTable/{folder}/NDLanguage.edf','SpriteImage/Common/mouse.spr',f'SpriteImage/{folder}/common.spr']:
            original=client/name;copy=run/name;copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,copy);inputs.append({'file':copy.relative_to(WS).as_posix(),'sha256':sha(copy)})
        names=run/'filenames.txt';names.write_text('\n'.join(ref['filenames'])+'\n',encoding='ascii');config=run/'R3Engine.ini';config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii')
        inputs +=[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in [names,config]];output=run/'result.json';startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        try:
            result=subprocess.run([str(target),str(output)],cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
        finally:
            remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
        (run/'console.txt').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError('Real normal sprite runtime:'+str(result.returncode)+':'+str(run))
        native=json.loads(output.read_text());frame=run/'sprite-frame.bgra';data=frame.read_bytes();preview=run/'sprite-frame.bmp';preview.write_bytes(b'BM'+struct.pack('<IHHI',54+len(data),0,0,54)+struct.pack('<IiiHHIIiiII',40,native['width'],-native['height'],1,32,0,len(data),2835,2835,0,0)+data)
        runs.append({'nation':nation,'folder':folder,'exit':result.returncode,'native':native,'exe':target.relative_to(WS).as_posix(),'exe_sha256':sha(target),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'frame':frame.relative_to(WS).as_posix(),'frame_sha256':sha(frame),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview),'inputs':inputs})
    report={'scope':'Actual normal CMainApp LoadData,CSpriteMgr,CGUIMouse and real managed textures;not full455UI/Create acceptance','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),'sources':{name:sha(WS/'scripts/native'/name) for name in ['client455_sprites.cpp','client455_sprites.h','client455_sprite_texture.inc']},'runs':runs,'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'reference_sha256':sha(WS/'inventory/client455-sprites-reference.json'),'engine_build_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'full_winmain_executed':False,'full_game_create_executed':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-sprites-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'nation':r['nation'],**r['native'],'exit':r['exit']} for r in runs]))
if __name__=='__main__':main()
