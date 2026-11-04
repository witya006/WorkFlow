"""Build source ANI/record/attachment andcharacter-dispatch module."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--compile-only',action='store_true');args=cli.parse_args();root=WS/'work/recovered/client455/animation';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/character-animation455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';hashes={}
    names=['client455_animation.cpp','client455_animation.h','client455_character_manager.h','client455_legacy_runtime.h','client455_legacy_model.h','client455_model_loader.h','client455_model_lifecycle.h','client455_shared_buffers.h','client455_texture.h','client455_character_rfs.h','client455_mesh_runtime.h','client455_mesh_bindings.h','client455_mesh08.h']
    if not args.compile_only:names+=['test_client455_animation.cpp']
    for name in names:
        p=WS/'scripts/native'/name;shutil.copyfile(p,root/name);hashes[name]=sha(p)
    dependencies=[]
    for name in ['client455-legacy-runtime-build','client455-legacy-models-build','client455-character-manager-build','client455-models-build','client455-shared-buffers-build','client455-texture-build','client455-mesh-runtime','client455-mesh-bindings','client455-mesh08']:
        proof=json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'));lib=WS/proof['library']
        if sha(lib)!=proof['library_sha256']:raise ValueError('Changed animationdependency:'+name)
        dependencies.append(lib)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    commands=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_animation.cpp /Foanimation.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455Animation.lib animation.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
'''
    if not args.compile_only:commands+='cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_animation.cpp RFClient455Animation.lib '+' '.join('"'+str(p)+'"' for p in dependencies)+f' kernel32.lib user32.lib gdi32.lib /Feanimation-probe.exe >> "{log}" 2>&1\n'
    commands+='exit /b %errorlevel%\n';batch=root/'build.cmd';batch.write_text(commands,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError('Animation source buildfailed:'+str(log))
    obj=root/'animation.obj';lib=root/'RFClient455Animation.lib'
    if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Animation x86/MT required')
    report={'scope':'Source ANI/record/attachment/character dispatch compilation;full pose/normal consumers separate','architecture':'x86','runtime':'/MT','compile_only':args.compile_only,'source_sha256':hashes,'library':lib.relative_to(WS).as_posix(),'library_sha256':sha(lib),'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'dependencies':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in dependencies]}
    if not args.compile_only:
        exe=root/'animation-probe.exe';report.update(exe=exe.relative_to(WS).as_posix(),exe_sha256=sha(exe),entry_rva=hex(pe(exe.read_bytes())['entry_rva']))
    (WS/'inventory/client455-animation-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:ANI/record/attachment/character dispatch source compiled x86/MT')
if __name__=='__main__':main()
