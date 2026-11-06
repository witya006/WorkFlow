"""Compile and exercise the production country/path module against pinned fixtures."""
import hashlib,json,subprocess
from pathlib import Path
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ref=json.loads((WS/'inventory/client455-nation-paths-reference.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text());root=WS/'work/client455-port/nation-paths';native=WS/'scripts/native';exe=root/'nation-paths.exe';log=root/'build.txt';batch=root/'build.cmd';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    source=[native/'client455_nation_paths.cpp',native/'test_client455_nation_paths.cpp'];batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\nif errorlevel 1 exit /b 1\ncl /nologo /MT /O2 /EHsc /std:c++14 /W3 /D_CRT_SECURE_NO_WARNINGS /I"{native}" '+ ' '.join('"'+str(p)+'"' for p in source)+f' user32.lib /Fe"{exe}" /link /MAP:"{root/"nation-paths.map"}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    build=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,creationflags=subprocess.CREATE_NO_WINDOW)
    if build.returncode:raise ValueError('Nation/path build:'+str(log))
    fixture=WS/ref['fixture']
    if sha(fixture)!=ref['fixture_sha256']:raise ValueError('Changed binary-derived fixture')
    result=subprocess.run([str(exe),str(fixture),str(root/'cases.ini')],cwd=root,capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW);output=root/'result.txt';output.write_bytes(result.stdout+result.stderr)
    if result.returncode or not result.stdout.startswith(b'PASS:'):raise ValueError('Nation/path test failed:'+str(result.returncode))
    report={'status':'PASS','scope':'Production country/path module,not complete language/launcher initialization','source_sha256':{p.name:sha(p) for p in source+[native/'client455_nation_paths.h']},'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe),'output':output.relative_to(WS).as_posix(),'output_sha256':sha(output),'reference_sha256':sha(WS/'inventory/client455-nation-paths-reference.json'),'countries':11,'profile_case_invalid_missing_truncated_reload':'PASS','M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-nation-paths-native.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.decode().strip())
if __name__=='__main__':main()
