"""Run actual window value/child owners andthe current ordinaryAvatar caller."""
import json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from audit_client455_equipment import record,sha
from checkpoint_client455_rvp_effects import load,check,require

def main():
    ref=load('client455-char-info-values-reference')
    for key in ['raw','script','verifier','decoder','preparer','prior_runtime']:check(ref[key])
    for row in ref['sources']:check(row)
    source=WS/'scripts/native/client455_char_info_values_probe.cpp';exe=build_full_object_probe('char-info-values',source)
    root=WS/'work/m9'/sha(exe)[:8];index=1
    while (root/f'char-info-values-{index:03d}').exists():index+=1
    run=root/f'char-info-values-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);dest=run/'mss32.dll';stage_asset(client/'mss32.dll',dest)
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope=ref['scope'],reference=record(WS/'inventory/client455-char-info-values-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],
        inputs=[record(dest)],console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,
        shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'char-info-values-report.json').write_text(text);(WS/'inventory/client455-char-info-values-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console=console.read_text(errors='replace')[-1800:])))
    require(result.returncode==0 and native and native['status']=='PASS','OrdinaryCharInfo values failed:'+str(console))

if __name__=='__main__':main()
