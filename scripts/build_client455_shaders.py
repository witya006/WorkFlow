"""Build the recovered shader resource path and its real HAL probe."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/recovered/client455/shaders';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/shaders455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';names=['client455_shaders.h','client455_shaders.cpp','client455_shader_key.h','test_client455_shaders.cpp','client455_enhanced_lighting.h','client455_enhanced_lighting.inc','client455_enhanced_lighting_shader.h'];hashes={}
    for name in names:source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    ref=json.loads((WS/'inventory/client455-shaders-reference.json').read_text(encoding='utf-8'))
    if hashes['client455_shader_key.h']!=ref['key_header_sha256']:raise ValueError('Changed shader key')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';batch=root/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_shaders.cpp /Foshaders.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455Shaders.lib shaders.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_shaders.cpp RFClient455Shaders.lib kernel32.lib user32.lib /Feshaders-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise ValueError('Shader build:'+str(log))
    obj=root/'shaders.obj';library=root/'RFClient455Shaders.lib';exe=root/'shaders-probe.exe'
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Shader x86/MT required')
    report={'scope':'Source shader bootstrap/SHO/HLSL/COM resources,not full Character draw','architecture':'x86','runtime':'/MT','source_sha256':hashes,'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'library':library.relative_to(WS).as_posix(),'library_sha256':sha(library),'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva'])};(WS/'inventory/client455-shaders-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:shader resource source x86/MT compiled')
if __name__=='__main__':main()
