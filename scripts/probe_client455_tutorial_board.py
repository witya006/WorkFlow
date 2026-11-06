"""Exercise the new board with actual client GUI objects and a native D3D modal."""
import ctypes
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_d3d9_port import ENGINE_DEFINITIONS
from client455_normal_link_evidence import validate_normal_link
from PIL import Image


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    reference_path=WS/'inventory/client455-tutorial-board-reference.json'
    reference=json.loads(reference_path.read_text())
    if reference['script_sha256']!=sha(WS/'scripts/audit_client455_tutorial_board.py'):
        raise ValueError('Refresh board reference first')
    link_path=WS/'inventory/client455-normal-link.json';link=json.loads(link_path.read_text());validate_normal_link(link)
    action_path=WS/'inventory/client455-tutorial-actions-native.json';action=json.loads(action_path.read_text())
    library=WS/action['library']
    if sha(library)!=action['library_sha256']:raise ValueError('Changed processor library')
    for name,digest in action['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed processor source:'+name)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text())
    root=WS/'work/client455-port/tutorial-board-probe';root.mkdir(parents=True,exist_ok=True)
    normal=WS/'work/client455-port/normal';engine=WS/'work/client455-port/source/R3Engine';native=WS/'scripts/native'
    exe=root/'tutorial-board-probe.exe';map_file=exe.with_suffix('.map');log=root/'build.txt'
    sources=[native/'client455_tutorial_board.cpp',native/'client455_tutorial_board_probe.cpp']
    objects=[root/(path.stem+'.obj') for path in sources]
    includes=[normal/'include',normal/'source',engine,engine/'common',engine/'1stclass',engine/'2ndclass',engine/'extension',engine/'d3d/include',WS/sdk['include']]
    flags=' '.join('/I"'+str(path)+'"' for path in includes)+' '+' '.join('/D'+value for value in sorted(set(ENGINE_DEFINITIONS+['_NEW_UI_','_WINDOWS','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION','RF_CLIENT_455_FRUSTUM'])))
    response=[]
    for line in (WS/link['link_response']['file']).read_text().splitlines():
        if line.startswith('"/OUT:'):line='"/OUT:'+str(exe)+'"'
        elif line.startswith('"/MAP:'):line='"/MAP:'+str(map_file)+'"'
        elif line.startswith('"/SUBSYSTEM:'):line='"/SUBSYSTEM:CONSOLE"'
        response.append(line)
    response += ['"'+str(path)+'"' for path in [*objects,library]]
    rsp=root/'link.rsp';rsp.write_text('\n'.join(response)+'\n',encoding='ascii')
    dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    lines=['@echo off',f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1','if errorlevel 1 exit /b 1']
    for index,(source,obj) in enumerate(zip(sources,objects)):
        lines += [f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /Zc:forScope- /W3 {flags} /FI"{WS/"work/client455-port/port_std.hpp"}" "{source}" /Fo"{obj}" {">" if index==0 else ">>"} "{log}" 2>&1','if errorlevel 1 exit /b 1']
    lines += [f'link @"{rsp}" >> "{log}" 2>&1','exit /b %errorlevel%']
    batch=root/'build.cmd';batch.write_text('\n'.join(lines)+'\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW,timeout=90)
    if result.returncode:raise ValueError('Board build:'+str(log))
    parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    while (parent/f'tutorial-board-{index:03d}').exists():index+=1
    run=parent/f'tutorial-board-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF','DataTable/ko-kr/NDLanguage.edf','SpriteImage/Common/mouse.spr','SpriteImage/ko-kr/common.spr']:
        source=client/name;destination=run/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
        inputs.append({'file':destination.relative_to(WS).as_posix(),'sha256':sha(destination)})
    for row in reference['inputs']:
        source=Path(row['file'])
        if sha(source)!=row['sha256']:raise ValueError('Changed script input')
        destination=run/row['name'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
        inputs.append({'file':destination.relative_to(WS).as_posix(),'sha256':sha(destination)})
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii')
    inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Board runtime '+str(result.returncode)+':'+str(run)+':'+result.stderr.decode(errors='replace'))
    output=run/'result.json';frame=run/'modal2.bgra';actual=json.loads(output.read_text())
    preview=run/'modal2.png'
    Image.frombytes('RGBA',(actual['frame_width'],actual['frame_height']),frame.read_bytes(),'raw','BGRA').convert('RGB').save(preview)
    report={'scope':'Board control rules,real client modal2/3 objects and D3D draw;visibility/rich/stage providers are test fixtures',
            'architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),
            'sources':{path.name:sha(path) for path in sources+[native/'client455_tutorial_board.h']},
            'script_sha256':sha(Path(__file__)),'reference_sha256':sha(reference_path),
            'normal_link_sha256':sha(link_path),'processor_report_sha256':sha(action_path),
            'processor_library':{'file':library.relative_to(WS).as_posix(),'sha256':sha(library)},
            'objects':[{'file':path.relative_to(WS).as_posix(),'sha256':sha(path)} for path in objects],
            'exe':{'file':target.relative_to(WS).as_posix(),'sha256':sha(target)},
            'map':{'file':map_file.relative_to(WS).as_posix(),'sha256':sha(map_file)},
            'build_log':{'file':log.relative_to(WS).as_posix(),'sha256':sha(log)},
            'link_response':{'file':rsp.relative_to(WS).as_posix(),'sha256':sha(rsp)},
            'output':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},
            'frame':{'file':frame.relative_to(WS).as_posix(),'sha256':sha(frame),'width':actual['frame_width'],'height':actual['frame_height'],'format':'BGRA8'},
            'preview':{'file':preview.relative_to(WS).as_posix(),'sha256':sha(preview)},
            'inputs':inputs,'native':actual,'natural_exit':result.returncode,
            'normal_client_relinked':False,'input_exe_executed':False,'server_modified':False,
            'M6':'OPEN','M6F':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-board-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['native']))


if __name__=='__main__':main()
