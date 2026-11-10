"""Run actual Avatar class/name writers against three real localized class tables."""
import json,shutil,subprocess
from pathlib import Path
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from compare_client_binaries import WS,pe
from checkpoint_client455_rvp_effects import sha,require,check,load
from audit_client455_resource_catalog import record

def main():
    ref=load('client455-avatar-classes-reference');check(ref['script'])
    for row in ref['sources']:check(row)
    source=WS/'scripts/native/client455_avatar_classes_probe.cpp';exe=build_full_object_probe('avatar-classes',source);root=WS/'work/m9'/sha(exe)[:8];runs=[];mapping=None
    for case in ref['cases']:
        index=1
        while(root/(case['name']+f'-{index:03d}')).exists():index+=1
        run=root/(case['name']+f'-{index:03d}');run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);inputs=[]
        if mapping is None:
            mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
        for row in case['inputs']:
            dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=row['original']))
        check(case['expected']);shutil.copyfile(WS/case['expected']['file'],run/'expected.bin');inputs.append(record(run/'expected.bin'))
        (run/'R3Engine.ini').write_text('[Setup]\nLanguage='+case['setting']+'\n',encoding='ascii')
        result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=35,creationflags=subprocess.CREATE_NO_WINDOW)
        console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
        runs.append(dict(name=case['name'],locale=case['locale'],exe=record(target),inputs=inputs,console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode))
        print(json.dumps(dict(case=case['name'],exit=result.returncode,native=native,console_tail=console.read_text(errors='replace')[-1000:])),flush=True)
        if result.returncode:break
    report=dict(scope=ref['scope'],reference_sha256=sha(WS/'inventory/client455-avatar-classes-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),architecture=pe(exe.read_bytes())['architecture'],map=record(mapping),runs=runs,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    serialized=json.dumps(report,indent=2)+'\n';(root/'avatar-classes-report.json').write_text(serialized);(WS/'inventory/client455-avatar-classes-native.json').write_text(serialized)
    require(len(runs)==len(ref['cases']) and all(not r['natural_exit'] and r['native'] and r['native']['status']=='PASS' for r in runs),'Actual Avatar class writers failed;inspect recorded console')
    print(json.dumps(dict(cases=len(runs),staging=report['shared_asset_staging'])))
if __name__=='__main__':main()
