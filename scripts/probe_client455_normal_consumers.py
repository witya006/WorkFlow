"""Run actual normal CUnity/CAnimation code with source455 manager/ANI facade."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_d3d9_port import ENGINE_DEFINITIONS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    root=WS/'work/client455-port/normal';art=WS/'artifacts/client455-normal';build=json.loads((WS/'inventory/client455-normal-build.json').read_text())
    if build['build_exit'] or build['objects']!=182:raise ValueError('Actual180originalsources+2production splits required')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';sdk=json.loads((WS/'inventory/d3dx9-headers.json').read_text());owner=json.loads((WS/'inventory/client455-renderer-owner-build.json').read_text());engine=WS/'work/client455-port/source/R3Engine'
    libraries=[root/'build/Release/RFClient455Facade.lib',root/'build/Release/RFClient455Kernels.lib']
    for name in ['client455-x87-math','jpeg6b-build']:
        report=json.loads((WS/f'inventory/{name}.json').read_text());libraries.append(WS/report['library'])
    libraries+=[WS/'work/client455-port/build-vs2026/Release/R3Engine455.lib',WS/'work/client455-port/dependencies/d3dx9_36.lib',engine/'mss32.lib']
    objects=[root/f'build/RFClient455Consumers.dir/Release/{name}.obj' for name in ['unity_managers','animation_control']]
    for path in libraries+objects:
        if not path.is_file():raise ValueError('Missing normal probe dependency:'+str(path))
    includes=[root/'include',root/'source',engine,engine/'1stclass',engine/'2ndclass',engine/'common',engine/'extension',engine/'d3d/include',WS/sdk['include']]
    source=WS/'scripts/native/client455_normal_consumers_probe.cpp';entry=root/'generated'/source.name;entry.write_bytes(source.read_bytes());exe=root/'build/normal-consumers-probe.exe';log=art/'consumer-probe-build.txt';batch=root/'generated/build-consumers-probe.cmd'
    definitions=sorted(set(ENGINE_DEFINITIONS+['_NEW_UI_','_WINDOWS','RF_CLIENT_455_FRUSTUM','RF_CLIENT_455_DRAW_ARGUMENTS','RF_CLIENT_455_EFFECT_LOG','RF_CLIENT_455_LOBBY_TRANSITION']))
    flags='/Zc:forScope- '+' '.join('/D'+name for name in definitions)+' '+' '.join('/I"'+str(p)+'"' for p in includes)
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env-probe.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W3 {flags} /FI"{WS/"work/client455-port/port_std.hpp"}" "{entry}" '+ ' '.join('"'+str(p)+'"' for p in objects+libraries)+f' d3d9.lib dinput8.lib dxguid.lib winmm.lib ws2_32.lib vfw32.lib advapi32.lib gdi32.lib user32.lib imm32.lib comdlg32.lib delayimp.lib /Fe"{exe}" /link /SUBSYSTEM:CONSOLE /OPT:REF /DELAYLOAD:mss32.dll /MAP:"{exe.with_suffix(".map")}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=entry.parent,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError('Normal consumers probe build failed:'+str(log))
    run=WS/'work/m9'/sha(exe)[:8];run.mkdir(parents=True,exist_ok=True);index=1
    while (run/f'normal{index:03d}').exists():index+=1
    run=run/f'normal{index:03d}';run.mkdir();shutil.copyfile(exe,run/exe.name)
    fixture=WS/'work/client-reference/character-animation455/sample_001.ani';shutil.copyfile(fixture,run/'sample.ani');output=run/'result.json'
    bbx=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'Character/Unit/Bone/GOLIATH.BBX';shutil.copyfile(bbx,run/'real.bbx')
    result=subprocess.run([str(run/exe.name),'.\\sample.ani',str(output)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Normal consumer run failed:'+str(run/'console.txt'))
    native=json.loads(output.read_text());mapping=exe.with_suffix('.map').read_text(errors='replace')
    if 'CharacterMR' in mapping or native['status']!='PASS' or not native['real_ani_loaded']:raise ValueError('Incomplete own normal consumers')
    report={'scope':'Actual production split CUnity/CAnimation modules from global.cpp/CResObject.cpp withsource455ANI integration;not normal WinMain/game acceptance','architecture':'x86','exe':(run/exe.name).relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'fixture':fixture.relative_to(WS).as_posix(),'fixture_sha256':sha(fixture),'libraries':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in libraries],'objects':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in objects],'source_sha256':sha(source),'normal_build_sha256':sha(WS/'inventory/client455-normal-build.json'),'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'legacy_character_linked':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['definitions']=definitions
    report['bbx_fixture']={'original':str(bbx),'copy':(run/'real.bbx').relative_to(WS).as_posix(),'sha256':sha(bbx)}
    report['contracts_reference_sha256']=sha(WS/'inventory/client455-normal-contracts-reference.json')
    (WS/'inventory/client455-normal-consumers.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(native))
if __name__=='__main__':main()
