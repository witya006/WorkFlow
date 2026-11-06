"""Let real normal global destructors run naturally in three bounded own labs."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_d3d9_port import ENGINE_DEFINITIONS
from client455_normal_link_evidence import validate_normal_link

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text())
    root=WS/'work/client455-port/lifecycle-probe';root.mkdir(parents=True,exist_ok=True)
    normal=WS/'work/client455-port/normal';engine=WS/'work/client455-port/source/R3Engine'
    cpp=WS/'scripts/native/client455_lifecycle_probe.cpp';exe=root/'lifecycle-probe.exe';obj=root/'lifecycle-probe.obj';log=root/'build.txt';batch=root/'build.cmd'
    dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    includes=[normal/'include',normal/'source',engine,engine/'common',engine/'1stclass',engine/'2ndclass',engine/'extension',engine/'d3d/include',WS/sdk['include']]
    flags=' '.join('/I"'+str(p)+'"' for p in includes)+' '+' '.join('/D'+v for v in sorted(set(ENGINE_DEFINITIONS+['_NEW_UI_','_WINDOWS','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION','RF_CLIENT_455_FRUSTUM'])))
    response=[]
    for line in (WS/link['link_response']['file']).read_text().splitlines():
        if line.startswith('"/OUT:'):line='"/OUT:'+str(exe)+'"'
        elif line.startswith('"/MAP:'):line='"/MAP:'+str(exe.with_suffix('.map'))+'"'
        elif line.startswith('"/SUBSYSTEM:'):line='"/SUBSYSTEM:CONSOLE"'
        response.append(line)
    rsp=root/'link.rsp';rsp.write_text('\n'.join(response+['"'+str(obj)+'"'])+'\n',encoding='ascii')
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /Zc:forScope- /W3 {flags} /FI"{WS/"work/client455-port/port_std.hpp"}" "{cpp}" /Fo"{obj}" > "{log}" 2>&1\nif errorlevel 1 exit /b 1\nlink @"{rsp}" >> "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    build=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    if build.returncode:raise ValueError('Lifecycle full-object build:'+str(log))
    parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);runs=[]
    for mode in ['uncreated','engine-only','created']:
        index=1
        while (parent/f'lifecycle-{mode}{index:03d}').exists():index+=1
        run=parent/f'lifecycle-{mode}{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);output=run/'result.json'
        result=subprocess.run([str(target),mode,str(output)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        (run/'console.txt').write_bytes(result.stdout+result.stderr)
        data=json.loads(output.read_text()) if output.exists() else {}
        runs.append({'mode':mode,'exit':result.returncode,'native':data,'exe':target.relative_to(WS).as_posix(),'exe_sha256':sha(target),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output) if output.exists() else None})
    report={'scope':'Actual normal global CMainApp/CLand beforeCreate and real legacyCreated-level cleanup;CRT exit observed,not whole455lifecycle acceptance','architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':cpp.relative_to(WS).as_posix(),'source_sha256':sha(cpp),'script_sha256':sha(Path(__file__)),'normal_land_source':{'file':(normal/'source/cland.cpp').relative_to(WS).as_posix(),'sha256':sha(normal/'source/cland.cpp')},'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'reference_sha256':sha(WS/'inventory/client455-lifecycle-reference.json'),'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'runs':runs,'debugger_used':False,'termination_requested':False,'full_winmain_executed':False,'full_game_create_executed':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-lifecycle-native.json').write_text(json.dumps(report,indent=2)+'\n')
    for run in runs:
        if run['exit'] or run['native'].get('status_before_crt_exit')!='PASS':raise ValueError('Lifecycle did not exit cleanly:'+str(run))
    print(json.dumps([{'mode':r['mode'],'exit':r['exit']} for r in runs]))
if __name__=='__main__':main()
