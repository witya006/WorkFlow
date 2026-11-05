"""Build recovered Character draw routing with its existing source dependencies."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--compile-only',action='store_true');args=parser.parse_args();root=WS/'work/recovered/client455/character-draw';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/character-draw455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt'
    draw=json.loads((WS/'inventory/client455-draw-build.json').read_text(encoding='utf-8'));names=[n for n in draw['source_sha256'] if n.endswith('.h')]+['client455_character_draw.h','client455_character_draw_internal.h','client455_character_draw.cpp','client455_character_draw_core.cpp']
    if not args.compile_only:names+=['test_client455_draw.cpp','test_client455_character_draw.cpp']
    hashes={}
    for name in names:source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    dependencies=[{'file':draw['library'],'sha256':draw['library_sha256']}]+draw['dependencies']
    for r in dependencies:
        if sha(WS/r['file'])!=r['sha256']:raise ValueError('Changed draw dependency')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';batch=root/'build.cmd'
    command=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_character_draw_core.cpp /Focore.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_character_draw.cpp /Foroute.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455CharacterDraw.lib core.obj route.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
'''
    if not args.compile_only:command+='cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_character_draw.cpp RFClient455CharacterDraw.lib '+' '.join('"'+str(WS/r['file'])+'"' for r in dependencies)+f' kernel32.lib user32.lib gdi32.lib /Fecharacter-draw-probe.exe >> "{log}" 2>&1\n'
    command+='exit /b %errorlevel%\n';batch.write_text(command,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise ValueError('Character draw build:'+str(log))
    objects=[]
    for name in ['core.obj','route.obj']:
        obj=root/name
        if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Character draw x86/MT required')
        objects.append({'file':obj.relative_to(WS).as_posix(),'sha256':sha(obj)})
    lib=root/'RFClient455CharacterDraw.lib';report={'scope':'Source main/effect/transparent/batch/dynamic/shadow routes,not complete normal455 renderer','architecture':'x86','runtime':'/MT','source_sha256':hashes,'library':lib.relative_to(WS).as_posix(),'library_sha256':sha(lib),'objects':objects,'dependencies':dependencies,'compile_only':args.compile_only}
    if not args.compile_only:
        exe=root/'character-draw-probe.exe';report.update(exe=exe.relative_to(WS).as_posix(),exe_sha256=sha(exe),entry_rva=hex(pe(exe.read_bytes())['entry_rva']))
    (WS/'inventory/client455-character-draw-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:Character draw source compiled x86/MT')
if __name__=='__main__':main()
