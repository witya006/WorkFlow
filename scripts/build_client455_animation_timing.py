"""Compile source animation timing and the focused numeric/constructor test."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/recovered/client455/animation-timing';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/character-timing455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';names=['client455_animation_timing.h','client455_animation_timing.cpp','test_client455_animation_timing.cpp'];hashes={}
    for name in names:src=WS/'scripts/native'/name;shutil.copyfile(src,root/name);hashes[name]=sha(src)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';cmd=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_animation_timing.cpp /Fotiming.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_animation_timing.cpp timing.obj /Fetiming-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''';batch=root/'build.cmd';batch.write_text(cmd,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise ValueError('Timing build:'+str(log))
    obj=root/'timing.obj';exe=root/'timing-probe.exe'
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Timing x86/MT required')
    result={'scope':'Source animation frame numeric kernel/known100-84byte initializers;real caller validation separate','architecture':'x86','runtime':'/MT','source_sha256':hashes,'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva'])};(WS/'inventory/client455-animation-timing-build.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS:animation timing x86/MT compiled')
if __name__=='__main__':main()
