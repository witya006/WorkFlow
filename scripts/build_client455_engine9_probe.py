"""Link the migrated real engine andCharacter owner onthe pinnedD3DX9runtime."""
import hashlib,json,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_d3d9_port import migrate,ENGINE_DEFINITIONS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/client455-port';art=WS/'artifacts/client455-d3d9-port';build=json.loads((WS/'inventory/client455-d3d9-port-build.json').read_text(encoding='utf-8'));sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text(encoding='utf-8'));imports=json.loads((WS/'inventory/client455-d3dx-import.json').read_text(encoding='utf-8'));owner=json.loads((WS/'inventory/client455-renderer-owner-build.json').read_text(encoding='utf-8'));x87=json.loads((WS/'inventory/client455-x87-math.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['objects']!=67 or sha(WS/imports['library'])!=imports['library_sha256']:raise ValueError('Compiled67source engine andverified imports required')
    lab=root/'lab';lab.mkdir(parents=True,exist_ok=True);source=WS/'scripts/native/client_graphics_lab.inc';raw,_=migrate(source.read_bytes());raw=raw.replace(b'Direct3DCreate8',b'Direct3DCreate9');raw=raw.replace(b'#if defined(RF_CLIENT_455_MAP_TIME)',b'#if 0 /* CLand/network consumer is outside this engine-only probe. */');anchor=b'if (!graphicsHR(R3InitDevice(device,640,480))) return 87;'
    if raw.count(anchor)!=1:raise ValueError('Engine bringup anchor changed')
    confirm=b'{D3DCAPS9 caps={};if(!graphicsHR(device->GetDeviceCaps(&caps)) || !graphicsHR(R3ConfirmDevice(&caps,graphicsResult.flags,pp.BackBufferFormat)))return 91;}\r\n    '
    raw=raw.replace(anchor,confirm+anchor+b'\r\n    if (!graphicsCheck(GetR3State()->mIsUsedVertexShader && checkEnginePrograms())) return 92;\r\n    if (!graphicsCheck(connectCharacterOwner(device)==0)) return 90;')
    (lab/'client_graphics_lab.inc').write_bytes(raw)
    jpeg=json.loads((WS/'inventory/jpeg6b-build.json').read_text(encoding='utf-8'))
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';engine=root/'source/R3Engine';include=[engine,engine/'1stclass',engine/'2ndclass',engine/'common',engine/'extension',engine/'d3d/include',WS/sdk['include'],WS/'scripts/native',lab];libraries=[root/'build-vs2026/Release/R3Engine455.lib',WS/imports['library'],WS/owner['library']]+[WS/r['file'] for r in owner['dependencies']]+[WS/x87['library'],WS/jpeg['library'],engine/'mss32.lib']
    for path in libraries:
        if not path.is_file():raise ValueError('Missing probe dependency:'+str(path))
    entry=lab/'engine9_probe.cpp';entry.write_bytes((WS/'scripts/native/client455_engine9_probe.cpp').read_bytes())
    log=art/'probe-build.txt';batch=lab/'build.cmd';exe=lab/'engine9-probe.exe';flags=' '.join('/I"'+str(p)+'"' for p in include)
    definitions=ENGINE_DEFINITIONS;flags+=' '+' '.join('/D'+name for name in definitions)
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /Od /EHsc /std:c++14 /W3 /D_CRT_SECURE_NO_WARNINGS {flags} /FI"{root/'port_std.hpp'}" "{entry}" '''+' '.join('"'+str(p)+'"' for p in libraries)+f''' d3d9.lib dinput8.lib dxguid.lib winmm.lib ws2_32.lib vfw32.lib advapi32.lib gdi32.lib user32.lib imm32.lib comdlg32.lib delayimp.lib /Fe"{exe}" /link /SUBSYSTEM:WINDOWS /DELAYLOAD:mss32.dll /MAP:"{lab/'engine9-probe.map'}" > "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    run=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=lab)
    if run.returncode:raise ValueError('Engine9probe link:'+str(log))
    report={'scope':'OwnrealR3EngineD3D9 device test withCharacter455owner attached;notnormalclient455parity','exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'architecture':'x86','entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'engine_matching_definitions':definitions,'source_sha256':{p.relative_to(WS).as_posix():sha(p) for p in [WS/'scripts/native/client455_engine9_probe.cpp',source,lab/'client_graphics_lab.inc',WS/'scripts/native/client455_d3d9_port.h']},'libraries':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in libraries]};(WS/'inventory/client455-engine9-probe-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:realengine9+Characterowner probe linked')
if __name__=='__main__':main()
