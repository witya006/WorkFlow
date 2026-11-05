"""Compile and run own Character clock with actual normal facade and engine."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ref=json.loads((WS/'inventory/client455-character-clock-reference.json').read_text());build=json.loads((WS/'inventory/client455-normal-build.json').read_text());normal=json.loads((WS/'inventory/client455-normal-consumers.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text())
    if build['build_exit'] or build['objects']!=182:raise ValueError('Current normal build required')
    root=WS/'work/client455-port/normal';art=WS/'artifacts/character-clock455';art.mkdir(parents=True,exist_ok=True)
    source=WS/'scripts/native/test_client455_character_clock.cpp';entry=root/'generated'/source.name;entry.write_bytes(source.read_bytes());exe=root/'build/character-clock-probe.exe';batch=root/'generated/build-character-clock.cmd';log=art/'build.txt';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    libraries=[WS/row['file'] for row in normal['libraries']]
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env-character-clock.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W3 /D_CRT_SECURE_NO_WARNINGS /I"{root/"include"}" "{entry}" '+' '.join('"'+str(path)+'"' for path in libraries)+f' d3d9.lib dinput8.lib dxguid.lib winmm.lib ws2_32.lib vfw32.lib advapi32.lib gdi32.lib user32.lib imm32.lib comdlg32.lib delayimp.lib /Fe"{exe}" /link /SUBSYSTEM:CONSOLE /OPT:REF /DELAYLOAD:mss32.dll /MAP:"{exe.with_suffix(".map")}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=entry.parent,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError('Character clock build:'+str(log))
    base=WS/'work/m9'/sha(exe)[:8];base.mkdir(parents=True,exist_ok=True);index=1
    while (base/f'character-clock{index:03d}').exists():index+=1
    run=base/f'character-clock{index:03d}';run.mkdir();shutil.copyfile(exe,run/exe.name);golden=WS/ref['golden'];output=run/'result.json'
    if sha(golden)!=ref['golden_sha256']:raise ValueError('Changed clock oracle')
    result=subprocess.run([str(run/exe.name),str(golden),str(output)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(run/'console.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Character clock run:'+str(run/'console.txt')+'; '+str(output))
    report={'scope':'Own Character clock through actual normal bridge and source engine;not normal WinMain/game acceptance','architecture':'x86','exe':(run/exe.name).relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':json.loads(output.read_text()),'source':source.relative_to(WS).as_posix(),'source_sha256':sha(source),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'map':exe.with_suffix('.map').relative_to(WS).as_posix(),'map_sha256':sha(exe.with_suffix('.map')),'libraries':[{'file':path.relative_to(WS).as_posix(),'sha256':sha(path)} for path in libraries],'reference_sha256':sha(WS/'inventory/client455-character-clock-reference.json'),'normal_build_sha256':sha(WS/'inventory/client455-normal-build.json'),'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-character-clock-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['native']))
if __name__=='__main__':main()
