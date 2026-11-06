"""Build an own console entry against the exact normal client object/library set."""
import json,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_d3d9_port import ENGINE_DEFINITIONS
from client455_normal_link_evidence import validate_normal_link

def build_full_object_probe(name,source):
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text())
    root=WS/f'work/client455-port/{name}-probe';root.mkdir(parents=True,exist_ok=True)
    normal=WS/'work/client455-port/normal';engine=WS/'work/client455-port/source/R3Engine';exe=root/f'{name}-probe.exe';obj=root/f'{name}-probe.obj';log=root/'build.txt'
    includes=[normal/'include',normal/'source',engine,engine/'common',engine/'1stclass',engine/'2ndclass',engine/'extension',engine/'d3d/include',WS/sdk['include']]
    flags=' '.join('/I"'+str(p)+'"' for p in includes)+' '+' '.join('/D'+v for v in sorted(set(ENGINE_DEFINITIONS+['_NEW_UI_','_WINDOWS','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION','RF_CLIENT_455_FRUSTUM'])))
    response=[]
    for line in (WS/link['link_response']['file']).read_text().splitlines():
        if line.startswith('"/OUT:'):line='"/OUT:'+str(exe)+'"'
        elif line.startswith('"/MAP:'):line='"/MAP:'+str(exe.with_suffix('.map'))+'"'
        elif line.startswith('"/SUBSYSTEM:'):line='"/SUBSYSTEM:CONSOLE"'
        response.append(line)
    rsp=root/'link.rsp';rsp.write_text('\n'.join(response+['"'+str(obj)+'"'])+'\n',encoding='ascii')
    batch=root/'build.cmd';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /Zc:forScope- /W3 {flags} /FI"{WS/"work/client455-port/port_std.hpp"}" "{source}" /Fo"{obj}" > "{log}" 2>&1\nif errorlevel 1 exit /b 1\nlink @"{rsp}" >> "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError('Full-object probe build:'+str(log))
    return exe
