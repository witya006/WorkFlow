"""Build own x86/MT source shared buffers and capture/HAL test executable."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/recovered/client455/shared-buffers';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/character-gpu455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';hashes={}
    names=['client455_shared_buffers.cpp','client455_shared_buffers.h','test_client455_shared_buffers.cpp','client455_mesh_runtime.h','client455_mesh_bindings.h','client455_mesh08.h']
    for name in names:
        path=WS/'scripts/native'/name;shutil.copyfile(path,root/name);hashes[name]=sha(path)
    proofs=[json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8')) for name in ['client455-mesh-runtime','client455-mesh08']]
    for proof in proofs:
        if sha(WS/proof['library'])!=proof['library_sha256']:raise ValueError('Pinned mesh library changed')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch=root/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_shared_buffers.cpp /Foshared-buffers.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455SharedBuffers.lib shared-buffers.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_shared_buffers.cpp RFClient455SharedBuffers.lib "{WS/proofs[0]['library']}" "{WS/proofs[1]['library']}" kernel32.lib user32.lib gdi32.lib /Febuffer-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError(f'Shared buffer build failed:{log}')
    obj=root/'shared-buffers.obj';exe=root/'buffer-probe.exe';library=root/'RFClient455SharedBuffers.lib'
    if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('x86/MT shared buffer object required')
    report={'scope':'Own source shared buffers compiled;CPU capture andphysical GPU results recorded separately','architecture':'x86','runtime':'/MT','library':library.relative_to(WS).as_posix(),'library_sha256':sha(library),'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'source_sha256':hashes,'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'mesh_prerequisite_library_sha256':[p['library_sha256'] for p in proofs]}
    (WS/'inventory/client455-shared-buffers-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:shared buffer source compiled x86/MT;runtime evidence pending')
if __name__=='__main__':main()
