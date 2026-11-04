"""Build own local clock-command parser and run deterministic boundary fixtures."""
import json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_clock import sha

def main():
    clock=json.loads((WS/'inventory/client455-clock.json').read_text(encoding='utf-8'))
    for name,digest in clock['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Clock source proof stale')
    library=WS/clock['library']
    if sha(library)!=clock['library_sha256']:raise ValueError('Clock library changed')
    work=WS/'work/recovered/client455/time-commands';work.mkdir(parents=True,exist_ok=True);hashes={}
    for name in ['client455_clock.h','client455_time_commands.h','client455_time_commands.cpp','test_client455_time_commands.cpp']:
        src=WS/'scripts/native'/name;shutil.copyfile(src,work/name);hashes[name]=sha(src)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';log=WS/'artifacts/client455-time-commands-build.txt';batch=work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_time_commands.cpp /Fotime-commands.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455TimeCommands.lib time-commands.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX test_client455_time_commands.cpp RFClient455TimeCommands.lib "{library}" /Fetime-commands-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:raise RuntimeError(f'Time command build failed:{log}')
    run=subprocess.run([str(work/'time-commands-probe.exe')],cwd=work,capture_output=True,timeout=20)
    (WS/'artifacts/client455-time-commands-native.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'Time command fixtures failed:{run.stdout!r}:{run.stderr!r}')
    native=json.loads(run.stdout)
    if native['failures'] or native['precision_rounding_modes']!=12 or native['cases']!=432:raise ValueError('Incomplete command fixtures')
    report={'library':(work/'RFClient455TimeCommands.lib').relative_to(WS).as_posix(),'library_sha256':sha(work/'RFClient455TimeCommands.lib'),'object_sha256':sha(work/'time-commands.obj'),'source_sha256':hashes,'clock_library_sha256':clock['library_sha256'],'native_test':native,'scope':'Time-command parsing,256byte cap/ASCII/cursor/strtol and independent clock effects. Static455parser contracts and actual client grade/input hook verified separately. Other local directives, full chat/network/locale and M9 remain open.'}
    (WS/'inventory/client455-time-commands.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:time commands {native["cases"]}cases/{native["checks"]}checks/12FP modes;ASCII/truncation/cursor/overflow boundaries.')

if __name__=='__main__':main()
