"""Build selected ownership source and verify with byte oracles/recording host."""
import json
import shutil
import subprocess
from pathlib import Path

from audit_client455_item_ownership import record
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def main():
    reference=load('client455-item-ownership-reference')
    require(reference['script_sha256']==sha(WS/'scripts/audit_client455_item_ownership.py'),'Stale reference')
    for row in reference['raw_evidence']+reference['fixtures']:check(row)
    root=WS/'work/client455-port/item-ownership';root.mkdir(parents=True,exist_ok=True)
    native=WS/'scripts/native';source=native/'client455_item_ownership.cpp';probe=native/'client455_item_ownership_probe.cpp'
    info=load('msvc-verification');dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    library=root/'RF455ItemOwnership.lib';exe=root/'item-ownership-probe.exe';log=root/'build.txt'
    source_obj=root/'item-ownership.obj';probe_obj=root/'probe.obj';batch=root/'build.cmd'
    batch.write_text('\n'.join([
        '@echo off',f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1','if errorlevel 1 exit /b 1',
        f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /I"{native}" "{source}" /Fo"{source_obj}" > "{log}" 2>&1',
        'if errorlevel 1 exit /b 1',f'lib /nologo /OUT:"{library}" "{source_obj}" >> "{log}" 2>&1',
        'if errorlevel 1 exit /b 1',
        f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /I"{native}" "{probe}" /Fo"{probe_obj}" >> "{log}" 2>&1',
        'if errorlevel 1 exit /b 1',
        f'link /nologo /SUBSYSTEM:CONSOLE /MACHINE:X86 /OUT:"{exe}" /MAP:"{exe.with_suffix(".map")}" "{probe_obj}" "{library}" kernel32.lib >> "{log}" 2>&1',
        'exit /b %errorlevel%'])+'\n',encoding='ascii')
    built=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
    require(built.returncode==0,'Ownership build failed:'+str(log))
    # Link the exact same standalone library into the own full-object entry.
    # Separate compilation keeps real API call/link boundaries observable;
    # this is coexistence with client objects,not a production ownership host.
    entry=root/'full-object-entry.cpp'
    entry.write_text(f'#pragma comment(lib,"{library.as_posix()}")\n#include "{probe.as_posix()}"\n',encoding='ascii')
    full=build_full_object_probe('item-ownership',entry)
    runs=[]
    for label,binary in [('standalone',exe),('full_object',full)]:
        parent=WS/'work/m9'/sha(binary)[:8];index=1
        while(parent/f'item-ownership-{index:03d}').exists():index+=1
        folder=parent/f'item-ownership-{index:03d}';folder.mkdir(parents=True)
        target=folder/binary.name;shutil.copyfile(binary,target);inputs=[]
        for row in reference['fixtures']:
            original=WS/row['file'];dest=folder/original.name;shutil.copyfile(original,dest);inputs.append(record(dest))
        result=subprocess.run([str(target)],cwd=folder,timeout=25,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        console=folder/'console.txt';console.write_bytes(result.stdout+result.stderr);output=folder/'result.json'
        runs.append(dict(mode=label,exe=record(target),map=record(binary.with_suffix('.map')),console=record(console),
            output=record(output) if output.exists() else None,inputs=inputs,natural_exit=result.returncode,
            native=json.loads(output.read_text()) if output.exists() else None,architecture=pe(binary.read_bytes())['architecture']))
    report=dict(scope='Selected CItem record/copy/clone/reference release with independent byte oracles and recording manager host;ordinary Linker integration remains open',
        script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-item-ownership-reference.json'),
        sources=[record(path) for path in [source,source.with_suffix('.h'),probe,entry]],
        library=library.relative_to(WS).as_posix(),library_sha256=sha(library),build_log=record(log),
        objects=[record(p) for p in [source_obj,probe_obj]],runs=runs,
        builder_sha256=sha(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),
        normal_client_relinked=False,ordinary_Linker_changed=False,input_exe_executed=False,server_modified=False,
        M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-ownership-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exits=[r['natural_exit'] for r in runs],native=[r['native'] for r in runs])))
    require(all(not r['natural_exit'] and r['native'] and r['native']['status']=='PASS' for r in runs),'Ownership runtime:inspect recorded consoles')


if __name__=='__main__':main()
