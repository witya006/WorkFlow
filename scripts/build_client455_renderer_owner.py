"""Build the real renderer owner with its existing source dependencies."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--compile-only',action='store_true');args=parser.parse_args()
    root=WS/'work/recovered/client455/renderer-owner';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/client455-renderer-owner';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt';draw=json.loads((WS/'inventory/client455-character-draw-build.json').read_text(encoding='utf-8'))
    names=[n for n in draw['source_sha256'] if n.endswith('.h')]+['client455_renderer_owner.h','client455_renderer_owner.cpp','client455_renderer_owner_constants.h','test_client455_renderer_owner.cpp'];names=list(dict.fromkeys(names));hashes={}
    for name in names:source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    dependencies=[{'file':draw['library'],'sha256':draw['library_sha256']}]+draw['dependencies']
    for item in dependencies:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed renderer dependency')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';batch=root/'build.cmd'
    command=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_renderer_owner.cpp /Foowner.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455RendererOwner.lib owner.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
'''
    if not args.compile_only:command+='cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_renderer_owner.cpp RFClient455RendererOwner.lib '+' '.join('"'+str(WS/r['file'])+'"' for r in dependencies)+f' kernel32.lib user32.lib gdi32.lib /Ferenderer-owner-probe.exe >> "{log}" 2>&1\n'
    command+='exit /b %errorlevel%\n';batch.write_text(command,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise ValueError('Renderer owner build:'+str(log))
    obj=root/'owner.obj';exe=root/'renderer-owner-probe.exe';library=root/'RFClient455RendererOwner.lib'
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Expected x86MT')
    report={'scope':'Recovered455renderer owner with typed source load/draw adapters; runtime acceptance remains separate','architecture':'x86','runtime':'/MT','source_sha256':hashes,'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'library':library.relative_to(WS).as_posix(),'library_sha256':sha(library),'dependencies':dependencies,'compile_only':args.compile_only}
    if not args.compile_only:report.update(exe=exe.relative_to(WS).as_posix(),exe_sha256=sha(exe),entry_rva=hex(pe(exe.read_bytes())['entry_rva']))
    (WS/'inventory/client455-renderer-owner-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:source renderer owner compiled x86MT')
if __name__=='__main__':main()
