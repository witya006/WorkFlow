"""Exercise concrete SF factory/manager against actual supplied EDF data."""
import json
import shutil
import subprocess
from pathlib import Path

from audit_client455_skill_force_items import record
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def main():
    reference=load('client455-skill-force-items-reference')
    require(reference['script_sha256']==sha(WS/'scripts/audit_client455_skill_force_items.py'),'Stale SF reference')
    for row in reference['raw_evidence']+reference['inputs']+reference['golden']:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Normal object set')
    facade=next(row for row in link['libraries'] if row['file'].endswith('/RFClient455Facade.lib'));check(facade)
    root=WS/'work/client455-port/skill-force-items';root.mkdir(parents=True,exist_ok=True)
    native=WS/'scripts/native';names=['client455_item_ownership.cpp','client455_skill_force_items.cpp']
    probe=native/'client455_skill_force_items_probe.cpp';info=load('msvc-verification')
    dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    library=root/'RF455SkillForceItems.lib';exe=root/'skill-force-items-probe.exe';log=root/'build.txt';batch=root/'build.cmd'
    lines=['@echo off',f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1','if errorlevel 1 exit /b 1'];objects=[]
    for index,name in enumerate(names+['client455_character_rfs.cpp',probe.name]):
        obj=root/(Path(name).stem+'.obj');objects.append(obj)
        lines+=[f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /D_CRT_SECURE_NO_WARNINGS /I"{native}" "{native/name}" /Fo"{obj}" {">" if index==0 else ">>"} "{log}" 2>&1',
                'if errorlevel 1 exit /b 1']
    lines+=[f'lib /nologo /OUT:"{library}" '+' '.join(f'"{p}"' for p in objects[:2])+f' >> "{log}" 2>&1','if errorlevel 1 exit /b 1',
            f'link /nologo /OPT:REF /SUBSYSTEM:CONSOLE /MACHINE:X86 /OUT:"{exe}" /MAP:"{exe.with_suffix(".map")}" "{objects[-1]}" "{objects[-2]}" "{library}" "{WS/facade["file"]}" kernel32.lib user32.lib >> "{log}" 2>&1',
            'exit /b %errorlevel%']
    batch.write_text('\n'.join(lines)+'\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=root,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
    require(result.returncode==0,'Source SF build failed:'+str(log))
    entry=root/'full-object-entry.cpp';entry.write_text(f'#pragma comment(lib,"{library.as_posix()}")\n#include "{probe.as_posix()}"\n',encoding='ascii')
    full=build_full_object_probe('skill-force-items',entry);runs=[]
    for mode,binary in [('standalone',exe),('full_object',full)]:
        parent=WS/'work/m9'/sha(binary)[:8];index=1
        while(parent/f'skill-force-items-{index:03d}').exists():index+=1
        run=parent/f'skill-force-items-{index:03d}';run.mkdir(parents=True);target=run/binary.name;shutil.copyfile(binary,target);inputs=[]
        for row in reference['inputs']+reference['golden']:
            original=WS/row['file'];copy=run/original.name;shutil.copyfile(original,copy);inputs.append(record(copy))
        result=subprocess.run([str(target)],cwd=run,timeout=60,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
        runs.append(dict(mode=mode,exe=record(target),map=record(binary.with_suffix('.map')),console=record(console),
            output=record(output) if output.exists() else None,inputs=inputs,natural_exit=result.returncode,
            native=json.loads(output.read_text()) if output.exists() else None,architecture=pe(binary.read_bytes())['architecture']))
    report=dict(scope='Concrete SF selector1 source factory/primary manager/087ownership and real five-table EDF/localization;not ordinary game-global binding or other payload factories',
        script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),
        reference_sha256=sha(WS/'inventory/client455-skill-force-items-reference.json'),
        sources=[record(native/name) for name in names+['client455_item_ownership.h','client455_skill_force_items.h',probe.name]]+[record(entry)],
        library=library.relative_to(WS).as_posix(),library_sha256=sha(library),objects=[record(p) for p in objects],
        edf_dependency=facade,edf_source_sha256=sha(native/'client455_language.cpp'),build_log=record(log),runs=runs,
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_client_relinked=False,
        ordinary_Linker_changed=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-skill-force-items-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exits=[r['natural_exit'] for r in runs],native=[r['native'] for r in runs])))
    require(all(not r['natural_exit'] and r['native'] and r['native']['status']=='PASS' for r in runs),'Concrete SF runtime failed:inspect console')


if __name__=='__main__':main()
