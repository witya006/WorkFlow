"""Test the linked engine's UV ABI at every455material layer,withoutGPU."""
import json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from audit_client455_equipment import record,sha

def main():
    source=WS/'scripts/native/client455_material_uv_probe.cpp';exe=build_full_object_probe('material-uv',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while (parent/f'material-uv-{index:03d}').exists():index+=1
    run=parent/f'material-uv-{index:03d}';run.mkdir(parents=True)
    target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);stage_asset(client/'mss32.dll',run/'mss32.dll')
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';body=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope='Actual linked engine GetTextureMatrix ABI for7material layers;not full UV/material/renderer acceptance',source=record(source),script=record(Path(__file__)),
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_build_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),
        exe=record(target),map=record(mapping),console=record(console),output=record(output) if output.exists() else None,native=body,natural_exit=result.returncode,
        staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/'inventory/client455-material-uv-native.json').write_text(text)
    print(json.dumps(dict(native=body,exit=result.returncode,console=console.read_text(errors='replace')[-900:],run=run.relative_to(WS).as_posix())))
    if result.returncode:raise ValueError('Actual7layer UV probe failed;exact attempt saved in '+str(run))
if __name__=='__main__':main()
