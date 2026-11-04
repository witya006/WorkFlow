"""Compile the source Character RFS/DDS/D3D9texture backend;tests recorded separately."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--compile-only',action='store_true');args=cli.parse_args()
    root=WS/'work/recovered/client455/texture';root.mkdir(parents=True,exist_ok=True);artifact=WS/'artifacts/character-texture455';artifact.mkdir(parents=True,exist_ok=True);log=artifact/'build.txt'
    names=['client455_character_rfs.cpp','client455_character_rfs.h','client455_character_dds_key.h','client455_texture.cpp','client455_texture.h','client455_mesh_runtime.h','client455_mesh_bindings.h','client455_mesh08.h']
    if not args.compile_only:names+=['test_client455_texture.cpp']
    hashes={}
    for name in names:
        source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    commands=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_character_rfs.cpp /Forfs.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_texture.cpp /Fotexture.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455Texture.lib rfs.obj texture.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
'''
    if not args.compile_only:
        runtime=json.loads((WS/'inventory/client455-mesh-runtime.json').read_text(encoding='utf-8'));framing=json.loads((WS/'inventory/client455-mesh08.json').read_text(encoding='utf-8'))
        for proof in [runtime,framing]:
            if sha(WS/proof['library'])!=proof['library_sha256']:raise ValueError('Source mesh prerequisite changed')
        commands+=f'cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_texture.cpp RFClient455Texture.lib "{WS/runtime["library"]}" "{WS/framing["library"]}" kernel32.lib user32.lib gdi32.lib /Fetexture-probe.exe >> "{log}" 2>&1\n'
    commands+='exit /b %errorlevel%\n';batch=root/'build.cmd';batch.write_text(commands,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError(f'Character texture build failed:{log}')
    objects=[]
    for name in ['rfs.obj','texture.obj']:
        obj=root/name
        if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Texture object must be x86/MT')
        objects.append({'file':obj.relative_to(WS).as_posix(),'sha256':sha(obj)})
    report={'scope':'Source455Character texture backend compile only;native tests/physical GPU acceptance recorded separately','architecture':'x86','runtime':'/MT','library':(root/'RFClient455Texture.lib').relative_to(WS).as_posix(),'library_sha256':sha(root/'RFClient455Texture.lib'),'source_sha256':hashes,'objects':objects,'compile_only':args.compile_only}
    if not args.compile_only:
        exe=root/'texture-probe.exe';report['exe']=exe.relative_to(WS).as_posix();report['exe_sha256']=sha(exe);report['entry_rva']=hex(pe(exe.read_bytes())['entry_rva'])
    (WS/'inventory/client455-texture-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:Character RFS/DDS/texture source compiled x86/MT;this build record does not certify runtime.')
if __name__=='__main__':main()
