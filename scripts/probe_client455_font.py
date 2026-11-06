"""Use real CMainApp device+CGUIText consumer and compare the455GDI atlas."""
import ctypes,hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_normal_link_evidence import validate_normal_link
from client455_d3d9_port import ENGINE_DEFINITIONS
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link);info=json.loads((WS/'inventory/msvc-verification.json').read_text());sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text());root=WS/'work/client455-port/font-probe';root.mkdir(parents=True,exist_ok=True);normal=WS/'work/client455-port/normal';engine=WS/'work/client455-port/source/R3Engine';native=WS/'scripts/native';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';cpp=native/'client455_font_probe.cpp';exe=root/'font-probe.exe';obj=root/'font-probe.obj';batch=root/'build.cmd';log=root/'build.txt'
    include=[normal/'include',normal/'source',engine,engine/'common',engine/'1stclass',engine/'2ndclass',engine/'extension',engine/'d3d/include',WS/sdk['include']];flags=' '.join('/I"'+str(p)+'"' for p in include)+' '+' '.join('/D'+v for v in sorted(set(ENGINE_DEFINITIONS+['_NEW_UI_','_WINDOWS','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION','RF_CLIENT_455_FRUSTUM'])))
    response=(WS/link['link_response']['file']).read_text().splitlines();changed=[]
    for line in response:
        if line.startswith('"/OUT:'):line='"/OUT:'+str(exe)+'"'
        elif line.startswith('"/MAP:'):line='"/MAP:'+str(exe.with_suffix('.map'))+'"'
        elif line.startswith('"/SUBSYSTEM:'):line='"/SUBSYSTEM:CONSOLE"'
        changed.append(line)
    responsePath=root/'link.rsp';responsePath.write_text('\n'.join(changed+['"'+str(obj)+'"'])+'\n',encoding='ascii')
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /Zc:forScope- /W3 {flags} /FI"{WS/"work/client455-port/port_std.hpp"}" "{cpp}" /Fo"{obj}" > "{log}" 2>&1\nif errorlevel 1 exit /b 1\nlink @"{responsePath}" >> "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    build=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    if build.returncode:raise ValueError('Font/full client probe build:'+str(log))
    paths=json.loads((WS/'config/paths.json').read_text());client=Path(paths['client_455']);refs=json.loads((WS/'inventory/client455-language-reference.json').read_text());parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);runs=[]
    for nation,folder in [('Korea','ko-kr'),('Russia','ru-ru')]:
        index=1
        while (parent/f'font-{folder}{index:03d}').exists():index+=1
        run=parent/f'font-{folder}{index:03d}';run.mkdir();copy=run/exe.name;shutil.copyfile(exe,copy);inputs=[]
        for name in ['System/shader/Grass1.vsh','System/shader/grass1.vso','System/console.jpg','System/010.TTF',f'DataTable/{folder}/NDLanguage.edf']:
            original=client/name;target=run/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,target);inputs.append({'file':target.relative_to(WS).as_posix(),'sha256':sha(target)})
        config=run/'R3Engine.ini';config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii');inputs.append({'file':config.relative_to(WS).as_posix(),'sha256':sha(config)})
        output=run/'result.json';startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        try:
            result=subprocess.run([str(copy),str(output)],cwd=run,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
        finally:
            removeFont=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;removeFont.argtypes=[ctypes.c_wchar_p];removeFont.restype=ctypes.c_int;removeFont(str(run/'System/010.TTF'))
        (run/'console.txt').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise ValueError(f'Font runtime:{result.returncode}:{run}')
        data=json.loads(output.read_text());pixels=run/'font-frame.bgra';raw=pixels.read_bytes();preview=run/'font-frame.bmp';preview.write_bytes(b'BM'+struct.pack('<IHHI',54+len(raw),0,0,54)+struct.pack('<IiiHHIIiiII',40,data['width'],-data['height'],1,32,0,len(raw),2835,2835,0,0)+raw)
        if data['status']!='PASS' or len(raw)!=data['width']*data['height']*4:raise ValueError('Incomplete text rendering')
        runs.append({'nation':nation,'folder':folder,'exit':result.returncode,'native':data,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'frame':pixels.relative_to(WS).as_posix(),'frame_sha256':sha(pixels),'preview':preview.relative_to(WS).as_posix(),'preview_sha256':sha(preview),'inputs':inputs,'exe':copy.relative_to(WS).as_posix(),'exe_sha256':sha(copy)})
    report={'scope':'Actual normal CMainApp device/CGUIText/engine bridge using real language strings;GDI oracle+atlas;not whole455UI acceptance','exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':cpp.relative_to(WS).as_posix(),'source_sha256':sha(cpp),'font_sources':{name:sha(native/name) for name in ['client455_font.cpp','client455_font.h','client455_font_settings.cpp','client455_font_settings.h','client455_text_bridge.inc']},'runs':runs,'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'reference_sha256':sha(WS/'inventory/client455-font-reference.json'),'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['script_sha256']=sha(Path(__file__));report['lab_land_initialized_before_exit']=True;report['full_game_create_executed']=False
    (WS/'inventory/client455-font-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'nation':r['nation'],**r['native']} for r in runs]))
if __name__=='__main__':main()
