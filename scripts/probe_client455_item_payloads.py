"""Build source item readers/factories and exercise their real EDF corpus."""
import json
import shutil
import subprocess
from pathlib import Path

from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def main():
    reference=load('client455-item-payloads-reference');sf=load('client455-skill-force-items-reference')
    require(reference['script_sha256']==sha(WS/'scripts/audit_client455_item_payloads.py'),'Stale item reference')
    fixture_rows=reference['inputs']+reference['fixtures']+sf['inputs']+sf['golden']
    for row in reference['raw_evidence']+fixture_rows:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Normal object set')
    facade=next(row for row in link['libraries'] if row['file'].endswith('/RFClient455Facade.lib'));check(facade)
    root=WS/'work/client455-port/item-payloads';root.mkdir(parents=True,exist_ok=True)
    native=WS/'scripts/native';names=['client455_item_ownership.cpp','client455_skill_force_items.cpp','client455_item_payloads.cpp']
    probes=[('item-payloads','client455_item_payloads_probe.cpp'),('item-payloads-sf','client455_skill_force_items_probe.cpp')]
    dev=Path(load('msvc-verification')['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    library=root/'RF455ItemPayloads.lib';log=root/'build.txt';batch=root/'build.cmd'
    lines=['@echo off',f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1','if errorlevel 1 exit /b 1'];objects=[]
    for index,name in enumerate(names+['client455_character_rfs.cpp']+[r[1] for r in probes]):
        obj=root/(Path(name).stem+'.obj');objects.append(obj)
        lines+=[f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /D_CRT_SECURE_NO_WARNINGS /I"{native}" "{native/name}" /Fo"{obj}" {">" if index==0 else ">>"} "{log}" 2>&1',
                'if errorlevel 1 exit /b 1']
    lines+=[f'lib /nologo /OUT:"{library}" '+' '.join(f'"{p}"' for p in objects[:3])+f' >> "{log}" 2>&1','if errorlevel 1 exit /b 1']
    for index,(name,_) in enumerate(probes):
        exe=root/(name+'-probe.exe')
        lines+=[f'link /nologo /OPT:REF /SUBSYSTEM:CONSOLE /MACHINE:X86 /OUT:"{exe}" /MAP:"{exe.with_suffix(".map")}" "{objects[4+index]}" "{objects[3]}" "{library}" "{WS/facade["file"]}" kernel32.lib user32.lib >> "{log}" 2>&1',
                'if errorlevel 1 exit /b 1']
    lines+=['exit /b 0'];batch.write_text('\n'.join(lines)+'\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
    require(result.returncode==0,'Source item payload build failed:'+str(log))
    runs=[];entries=[]
    for name,probe in probes:
        entry=root/(name+'-full-entry.cpp');entry.write_text(f'#pragma comment(lib,"{library.as_posix()}")\n#include "{(native/probe).as_posix()}"\n',encoding='ascii');entries.append(record(entry))
        full=build_full_object_probe(name,entry)
        for mode,binary in [('standalone',root/(name+'-probe.exe')),('full_object',full)]:
            target_root=WS/'work/m9'/sha(binary)[:8];index=1
            while(target_root/f'{name}-{index:03d}').exists():index+=1
            run=target_root/f'{name}-{index:03d}';run.mkdir(parents=True);target=run/binary.name;shutil.copyfile(binary,target);inputs=[]
            for row in fixture_rows:
                original=WS/row['file'];copy=run/original.name;shutil.copyfile(original,copy);inputs.append(record(copy))
            result=subprocess.run([str(target)],cwd=run,timeout=60,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
            runs.append(dict(probe=name,mode=mode,exe=record(target),map=record(binary.with_suffix('.map')),console=record(console),
                output=record(output) if output.exists() else None,inputs=inputs,natural_exit=result.returncode,
                native=json.loads(output.read_text()) if output.exists() else None,architecture=pe(binary.read_bytes())['architecture']))
    report=dict(scope='Concrete fresh payload/readers/manager and087owned wrappers on real Item/Quest/Character files;SF regression on same new library;ordinary game binding open',
        script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),reference_sha256=sha(WS/'inventory/client455-item-payloads-reference.json'),
        SF_reference_sha256=sha(WS/'inventory/client455-skill-force-items-reference.json'),
        sources=[record(native/name) for name in names+['client455_item_ownership.h','client455_skill_force_items.h','client455_item_payloads.h']+[r[1] for r in probes]]+entries,
        library=library.relative_to(WS).as_posix(),library_sha256=sha(library),objects=[record(p) for p in objects],
        edf_dependency=facade,edf_source_sha256=sha(native/'client455_language.cpp'),build_log=record(log),runs=runs,
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_client_relinked=False,
        ordinary_Linker_changed=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-payloads-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exits=[r['natural_exit'] for r in runs],native=[r['native'] for r in runs])))
    require(all(not r['natural_exit'] and r['native'] and r['native']['status']=='PASS' for r in runs),'Source item runtime failed:inspect consoles')


if __name__=='__main__':main()
