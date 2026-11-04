"""Build recovered pose evaluators and connected FrameMove pose phases."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cli=argparse.ArgumentParser();cli.add_argument('--compile-only',action='store_true');args=cli.parse_args();root=WS/'work/recovered/client455/pose';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/character-pose455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt'
    animation=json.loads((WS/'inventory/client455-animation-build.json').read_text(encoding='utf-8'));names=[n for n in animation['source_sha256'] if n.endswith('.h')]+['client455_pose.h','client455_pose.cpp','client455_secondary.h','client455_secondary.cpp']
    if not args.compile_only:names+=['test_client455_pose.cpp']
    hashes={}
    for name in names:
        src=WS/'scripts/native'/name;shutil.copyfile(src,root/name);hashes[name]=sha(src)
    dependencies=[{'file':animation['library'],'sha256':animation['library_sha256']}]+animation['dependencies']
    for record in dependencies:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Changed pose dependency')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    cmd=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_pose.cpp /Fopose.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_secondary.cpp /Fosecondary.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455Pose.lib pose.obj secondary.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
'''
    if not args.compile_only:cmd+='cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_pose.cpp RFClient455Pose.lib '+' '.join('"'+str(WS/r['file'])+'"' for r in dependencies)+f' kernel32.lib user32.lib gdi32.lib /Fepose-probe.exe >> "{log}" 2>&1\n'
    cmd+='exit /b %errorlevel%\n';batch=root/'build.cmd';batch.write_text(cmd,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError('Pose build failed:'+str(log))
    obj=root/'pose.obj';lib=root/'RFClient455Pose.lib'
    if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('Pose x86/MT required')
    report={'scope':'Connected pose/transition/ramp/bone andsecondary source;staticCRT sine parity/normal consumers separate','architecture':'x86','runtime':'/MT','compile_only':args.compile_only,'source_sha256':hashes,'library':lib.relative_to(WS).as_posix(),'library_sha256':sha(lib),'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'dependencies':dependencies}
    secondary=root/'secondary.obj';report['secondary_object']={'file':secondary.relative_to(WS).as_posix(),'sha256':sha(secondary)}
    if not args.compile_only:
        exe=root/'pose-probe.exe';report.update(exe=exe.relative_to(WS).as_posix(),exe_sha256=sha(exe),entry_rva=hex(pe(exe.read_bytes())['entry_rva']))
    (WS/'inventory/client455-pose-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:source pose x86/MT compiled')
if __name__=='__main__':main()
