"""Compile and exercise the focused scene-frustum unit;no broad runtime suite."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/recovered/client455/frustum';root.mkdir(parents=True,exist_ok=True);art=WS/'artifacts/client455-frustum';art.mkdir(parents=True,exist_ok=True);log=art/'build.txt'
    names=['client455_frustum.h','client455_frustum.cpp','client455_frustum_system.cpp','test_client455_frustum.cpp'];hashes={}
    for name in names:source=WS/'scripts/native'/name;shutil.copyfile(source,root/name);hashes[name]=sha(source)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch=root/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_frustum.cpp client455_frustum_system.cpp > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_frustum.cpp client455_frustum.obj client455_frustum_system.obj /Fefrustum-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise ValueError('Frustum build:'+str(log))
    for name in ['client455_frustum.obj','client455_frustum_system.obj']:
        if '/DEFAULTLIB:"LIBCMT"' not in directives((root/name).read_bytes()):raise ValueError('Expected x86MT')
    ref=json.loads((WS/'inventory/client455-frustum-reference.json').read_text(encoding='utf-8'));dll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    if sha(dll)!=ref['provider_sha256']:raise ValueError('Changed matrix runtime')
    exe=root/'frustum-probe.exe';output=root/'result.json';run=subprocess.run([str(exe),str(WS/ref['golden']),str(output)],cwd=root,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);(art/'stdout.txt').write_bytes(run.stdout);(art/'stderr.txt').write_bytes(run.stderr)
    if run.returncode:raise ValueError(f'Frustum:{run.returncode}:{run.stderr.decode(errors="replace")[:4000]}')
    native=json.loads(output.read_text(encoding='utf-8'))
    if native['status']!='PASS' or native['failures'] or native['matrix_cases']!=ref['matrix_cases'] or native['bbox_cases']!=ref['bbox_cases']:raise ValueError('Incomplete frustum proof')
    report={'scope':'Source scene-frustum math and pinned system-matrix deployment adapter,not full game visibility','architecture':'x86','runtime':'/MT','source_sha256':hashes,'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'native':native,'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'reference_report_sha256':sha(WS/'inventory/client455-frustum-reference.json')}
    (WS/'inventory/client455-frustum-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(native))
if __name__=='__main__':main()
