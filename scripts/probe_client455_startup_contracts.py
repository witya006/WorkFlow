"""Exercise real engine startup contracts with a test-only virtualCreate override."""
import hashlib,json,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_d3d9_port import ENGINE_DEFINITIONS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    build=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text());sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text());base=WS/'work/client455-port';root=base/'startup-engine/contracts';root.mkdir(parents=True,exist_ok=True);engine=base/'source/R3Engine';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';exe=root/'contracts.exe';cpp=WS/'scripts/native/test_client455_startup_contracts.cpp';batch=root/'build.cmd';log=root/'build.txt'
    jpeg=json.loads((WS/'inventory/jpeg6b-build.json').read_text());x87=json.loads((WS/'inventory/client455-x87-math.json').read_text());libraries=[WS/build['library'],WS/jpeg['library'],WS/x87['library'],base/'dependencies/d3dx9_36.lib',engine/'mss32.lib',base/'normal/build/Release/RFClient455Facade.lib']
    flags=' '.join('/I"'+str(p)+'"' for p in [engine,engine/'common',engine/'1stclass',engine/'2ndclass',engine/'extension',engine/'d3d/include',WS/sdk['include'],WS/'scripts/native']);flags+=' '+' '.join('/D'+v for v in ENGINE_DEFINITIONS)
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > "{root/"env.txt"}" 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W3 /D_CRT_SECURE_NO_WARNINGS {flags} /FI"{base/"port_std.hpp"}" "{cpp}" '+' '.join('"'+str(p)+'"' for p in libraries)+f' d3d9.lib dinput8.lib dxguid.lib winmm.lib ws2_32.lib vfw32.lib advapi32.lib gdi32.lib user32.lib imm32.lib comdlg32.lib delayimp.lib /Fe"{exe}" /Fo"{root/"contracts.obj"}" /link /SUBSYSTEM:CONSOLE /OPT:REF /DELAYLOAD:mss32.dll /MAP:"{root/"contracts.map"}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError('Startup contract build:'+str(log))
    parent=WS/'work/m9'/sha(exe)[:8];parent.mkdir(parents=True,exist_ok=True);index=1
    while (parent/f'startup-contracts{index:03d}').exists():index+=1
    run=parent/f'startup-contracts{index:03d}';run.mkdir();cases=[]
    for name,number in [('success','0'),('s_false','1'),('e_fail','80004005')]:
        output=run/(name+'.txt');result=subprocess.run([str(exe),number,str(output)],cwd=run,capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW);lines=output.read_text().splitlines() if output.exists() else []
        expected=['create:640:480:0']+(['after:0:0'] if name=='success' else [])+['atexit']
        if result.returncode or lines!=expected:raise ValueError('Startup contract case:'+name+':'+str(lines)+':'+str(result.returncode))
        cases.append({'name':name,'exit':result.returncode,'file':output.relative_to(WS).as_posix(),'sha256':sha(output)})
    layout=subprocess.run([str(exe),'layout'],cwd=run,capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    if layout.returncode:raise ValueError('Layout inspection failed')
    report={'scope':'Real derived engine color32 and Create exit protocol with test-only virtualCreate;not graphics/window acceptance','exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'source':cpp.relative_to(WS).as_posix(),'source_sha256':sha(cpp),'cases':cases,'layout':json.loads(layout.stdout),'libraries':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in libraries],'map':{'file':(root/'contracts.map').relative_to(WS).as_posix(),'sha256':sha(root/'contracts.map')},'build_sha256':sha(WS/'inventory/client455-startup-engine-build.json'),'reference_sha256':sha(WS/'inventory/client455-startup-contracts-reference.json'),'status':'PASS','color32_preserves_window_mode':True,'nonzero_create_exits_zero':True,'M6':'OPEN','M9':'OPEN','input_exe_executed':False,'server_modified':False}
    (WS/'inventory/client455-startup-contracts-native.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:color32 preservesbothwindow modes;Create S_OK/S_FALSE/E_FAIL exact exit policy;'+str(report['layout']))
if __name__=='__main__':main()
