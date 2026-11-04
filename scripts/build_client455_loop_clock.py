"""Build the recovered elapsed clock and its focused state/provider check."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/recovered/client455/loop-clock';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/client455-loop-clock';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';names=['client455_loop_clock.h','client455_loop_clock.cpp','client455_loop_clock_bridge.inc','test_client455_loop_clock.cpp'];hashes={}
    for name in names:source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch=root/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_loop_clock.cpp /Foloop-clock.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_loop_clock.cpp loop-clock.obj /Feloop-clock-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise ValueError('Loop clock build:'+str(log))
    obj=root/'loop-clock.obj';exe=root/'loop-clock-probe.exe'
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Loop clock x86/MT required')
    report={'scope':'Recovered loop clock,not fullclient acceptance','architecture':'x86','runtime':'/MT','source_sha256':hashes,'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva'])};(WS/'inventory/client455-loop-clock-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:loopclock x86/MT built')
if __name__=='__main__':main()
