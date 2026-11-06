"""Run actual ordinary modal controls for Korean/Russian packs on own D3D client."""
import ctypes,hashlib,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    reference_path=WS/'inventory/client455-modal-reference.json';reference=json.loads(reference_path.read_text())
    if reference['script_sha256']!=sha(WS/'scripts/audit_client455_modal.py'):raise ValueError('Refresh modal reference')
    cpp=WS/'scripts/native/client455_modal_probe.cpp';exe=build_full_object_probe('modal',cpp)
    parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);runs=[]
    for row in reference['inputs']:
        nation,folder=row['nation'],row['folder'];index=1
        while(parent/f'modal-{folder}-{index:03d}').exists():index+=1
        run=parent/f'modal-{folder}-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
        for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF',f'DataTable/{folder}/NDLanguage.edf','SpriteImage/Common/mouse.spr',f'SpriteImage/{folder}/common.spr']:
            source=client/name;destination=run/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
            inputs.append({'file':destination.relative_to(WS).as_posix(),'sha256':sha(destination)})
        config=run/'R3Engine.ini';config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
        startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
        finally:
            remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
        (run/'console.txt').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError(f'Modal {nation} runtime {result.returncode}:{run}:{result.stderr.decode(errors="replace")}')
        output=run/'result.json';frames=[]
        for name in ['modal-normal','modal-hover','modal-disabled','modal-rich','modal-rich-wrapper']:
            raw=run/(name+'.bgra');preview=run/(name+'.png')
            Image.frombytes('RGBA',(640,480),raw.read_bytes(),'raw','BGRA').convert('RGB').save(preview)
            frames.append({'file':raw.relative_to(WS).as_posix(),'sha256':sha(raw),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview),'width':640,'height':480})
        runs.append({'nation':nation,'folder':folder,'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'inputs':inputs,'frames':frames,'native':json.loads(output.read_text()),'exit':result.returncode})
    names=['client455_modal.h','client455_modal.cpp','client455_modal_init.inc','client455_modal_message.inc','client455_dialog_input.inc','client455_font.h','client455_font.cpp']
    report={'scope':'Actual normal modal controls/outline/input with Korean/Russian packs;full455text/scrollbar and game remainOPEN',
            'architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),
            'source':cpp.relative_to(WS).as_posix(),'source_sha256':sha(cpp),'sources':{name:sha(WS/'scripts/native'/name)for name in names},
            'script_sha256':sha(Path(__file__)),'builder_sha256':sha(WS/'scripts/client455_own_probe.py'),
            'reference_sha256':sha(reference_path),'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),
            'map':{'file':exe.with_suffix('.map').relative_to(WS).as_posix(),'sha256':sha(exe.with_suffix('.map'))},'runs':runs,
            'normal_client_relinked':True,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-modal-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{'nation':row['nation'],**row['native']}for row in runs]))
if __name__=='__main__':main()
