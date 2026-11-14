"""Build draw primitives and one real animated HAL integration probe."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--compile-only',action='store_true');args=parser.parse_args()
    root=WS/'work/recovered/client455/draw';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/draw455';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt'
    pose=json.loads((WS/'inventory/client455-pose-build.json').read_text(encoding='utf-8'));shader=json.loads((WS/'inventory/client455-shaders-build.json').read_text(encoding='utf-8'))
    names=list(dict.fromkeys([n for n in pose['source_sha256'] if n.endswith('.h')]+['client455_shaders.h','client455_draw.h','client455_draw_observer.h','client455_draw.cpp','test_client455_draw.cpp']))
    hashes={}
    for name in names:source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    dependencies=[{'file':pose['library'],'sha256':pose['library_sha256']}]+pose['dependencies']+[{'file':shader['library'],'sha256':shader['library_sha256']}]
    # Resolve remaining transitive production libraries without rebuilding them.
    for report in ['client455-models-build','client455-shared-buffers-build','client455-texture-build','client455-mesh-runtime','client455-mesh-bindings','client455-mesh08']:
        r=json.loads((WS/f'inventory/{report}.json').read_text(encoding='utf-8'));item={'file':r['library'],'sha256':r['library_sha256']}
        if item not in dependencies:dependencies.append(item)
    for item in dependencies:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed draw dependency:'+item['file'])
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';batch=root/'build.cmd'
    command=f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_draw.cpp /Fodraw.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455Draw.lib draw.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
'''
    if not args.compile_only:command+=f'cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_draw.cpp RFClient455Draw.lib '+ ' '.join('"'+str(WS/r['file'])+'"' for r in dependencies)+f' kernel32.lib user32.lib gdi32.lib /Fedraw-probe.exe >> "{log}" 2>&1\n'
    command+='exit /b %errorlevel%\n';batch.write_text(command,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise ValueError('Draw build:'+str(log))
    obj=root/'draw.obj';lib=root/'RFClient455Draw.lib';exe=root/'draw-probe.exe'
    if obj.read_bytes()[:2]!=b'\x4c\x01' or '/DEFAULTLIB:"LIBCMT"' not in directives(obj.read_bytes()):raise ValueError('x86/MT draw required')
    report={'scope':'Source state/palette/material/program/shared draw primitives; runtime verification belongs to the full client','architecture':'x86','runtime':'/MT','source_sha256':hashes,'object':obj.relative_to(WS).as_posix(),'object_sha256':sha(obj),'library':lib.relative_to(WS).as_posix(),'library_sha256':sha(lib),'dependencies':dependencies,'compile_only':args.compile_only}
    if not args.compile_only:report.update(exe=exe.relative_to(WS).as_posix(),exe_sha256=sha(exe),entry_rva=hex(pe(exe.read_bytes())['entry_rva']))
    (WS/'inventory/client455-draw-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:source draw primitives x86/MT compiled')
if __name__=='__main__':main()
