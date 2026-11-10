"""Exercise actual ordinary Character matrix code without GPU/asset copies."""
import json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from audit_client455_equipment import record,sha
from checkpoint_client455_rvp_effects import load,check,require

def main():
    ref=load('client455-character-palette-reference')
    for key in ['raw','reused_raw','script','decoder_script','regions_script','port_script','preparer','original_source_snapshot','runtime_base']:check(ref[key])
    for row in ref['sources']:check(row)
    source=WS/'scripts/native/client455_character_palette_probe.cpp';exe=build_full_object_probe('character-palette',source);root=WS/'work/m9'/sha(exe)[:8];index=1
    while(root/f'character-palette-{index:03d}').exists():index+=1
    run=root/f'character-palette-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);stage_asset(client/'mss32.dll',run/'mss32.dll')
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW);console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope=ref['scope'],reference_sha256=sha(WS/'inventory/client455-character-palette-reference.json'),source=record(source),script=record(Path(__file__)),builder=record(WS/'scripts/client455_own_probe.py'),staging_script=record(WS/'scripts/client455_asset_staging.py'),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],inputs=[dict(**record(run/'mss32.dll'),original=str(client/'mss32.dll'))],
        console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'palette-report.json').write_text(text);(WS/'inventory/client455-character-palette-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1200:])))
    require(result.returncode==0 and native and native['status']=='PASS','Ordinary Character palette failed:'+str(console))
if __name__=='__main__':main()
