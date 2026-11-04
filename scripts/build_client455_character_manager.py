"""Build the owned Character455 record/manager/cache/raw-MSH source module."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    root=WS/'work/recovered/client455/character-manager';root.mkdir(parents=True,exist_ok=True)
    art=WS/'artifacts/character-manager455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';hashes={}
    for name in ['client455_character_manager.cpp','client455_character_manager.h','test_client455_character_manager.cpp','client455_model_loader.h','client455_model_lifecycle.h','client455_shared_buffers.h','client455_texture.h','client455_character_rfs.h','client455_mesh_runtime.h','client455_mesh_bindings.h','client455_mesh08.h']:
        source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    dependencies=[]
    for name in ['client455-models-build','client455-shared-buffers-build','client455-texture-build','client455-mesh-runtime','client455-mesh-bindings','client455-mesh08']:
        proof=json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'));lib=WS/proof['library']
        if sha(lib)!=proof['library_sha256']:raise ValueError('Changed Character dependency:'+name)
        dependencies.append(lib)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    commands=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_character_manager.cpp /Fomanager.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455CharacterManager.lib manager.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
'''
    commands+='cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_character_manager.cpp RFClient455CharacterManager.lib '+' '.join('"'+str(p)+'"' for p in dependencies)+f' kernel32.lib user32.lib gdi32.lib /Femanager-probe.exe >> "{log}" 2>&1\nexit /b %errorlevel%\n'
    batch=root/'build.cmd';batch.write_text(commands,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError('Character manager source build failed:'+str(log))
    obj=root/'manager.obj'
    if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Character x86/MT required')
    lib=root/'RFClient455CharacterManager.lib';exe=root/'manager-probe.exe'
    report={'scope':'Source record/manager/cache/raw-MSH IO compile;not full Character/dispatcher ABI','architecture':'x86','runtime':'/MT','library':lib.relative_to(WS).as_posix(),'library_sha256':sha(lib),'objects':[{'file':obj.relative_to(WS).as_posix(),'sha256':sha(obj)}],'source_sha256':hashes,'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'dependencies':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in dependencies]}
    (WS/'inventory/client455-character-manager-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:Character455 record/manager/cache/raw IO source built x86/MT')
if __name__=='__main__':main()
