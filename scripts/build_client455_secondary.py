"""Build a targeted secondary-motion executable from the owned pose archive."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof=json.loads((WS/'inventory/client455-pose-build.json').read_text(encoding='utf-8'));root=WS/'work/recovered/client455/pose';art=WS/'artifacts/character-pose455';log=art/'secondary-build.txt';src=WS/'scripts/native/test_client455_secondary.cpp';shutil.copyfile(src,root/src.name)
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Stale secondary source:'+name)
    if sha(WS/proof['library'])!=proof['library_sha256']:raise ValueError('Changed source pose library')
    for record in proof['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Changed secondary dependency')
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';libs=[WS/proof['library']]+[WS/r['file'] for r in proof['dependencies']]
    cmd=f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env-secondary.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_secondary.cpp '+' '.join('"'+str(p)+'"' for p in libs)+f' kernel32.lib user32.lib gdi32.lib /Fesecondary-probe.exe > "{log}" 2>&1\nexit /b %errorlevel%\n';batch=root/'secondary-build.cmd';batch.write_text(cmd,encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root).returncode:raise RuntimeError('Secondary test build:'+str(log))
    exe=root/'secondary-probe.exe';report={'architecture':'x86','runtime':'/MT','source':src.relative_to(WS).as_posix(),'source_sha256':sha(src),'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'entry_rva':hex(pe(exe.read_bytes())['entry_rva']),'pose_build_sha256':sha(WS/'inventory/client455-pose-build.json')};(WS/'inventory/client455-secondary-build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:secondary targeted test compiled')
if __name__=='__main__':main()
