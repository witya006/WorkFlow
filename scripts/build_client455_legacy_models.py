"""Build only the source intermediate MSH/BN parser; no original EXE execution."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    root=WS/'work/recovered/client455/legacy-models';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/character-legacy455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';hashes={}
    for name in ['client455_legacy_model.cpp','client455_legacy_model.h','test_client455_legacy_models.cpp','client455_model_lifecycle.h','client455_mesh_runtime.h','client455_mesh_bindings.h','client455_mesh08.h']:
        source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch=root/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_legacy_model.cpp /Folegacy.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455LegacyModel.lib legacy.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_legacy_models.cpp RFClient455LegacyModel.lib kernel32.lib /Felegacy-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError('Legacy model source build failed:'+str(log))
    obj=root/'legacy.obj';lib=root/'RFClient455LegacyModel.lib';exe=root/'legacy-probe.exe'
    if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Source parser x86/MT required')
    report={'scope':'Intermediate legacyMSH/BN source parser andlifetime compile;normal dispatcher/importer/converter notintegrated','architecture':'x86','runtime':'/MT','source_sha256':hashes,'library':lib.relative_to(WS).as_posix(),'library_sha256':sha(lib),'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva'])}
    (WS/'inventory/client455-legacy-models-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:bounded intermediate MSH/BN parser source built x86/MT')
if __name__=='__main__':main()
