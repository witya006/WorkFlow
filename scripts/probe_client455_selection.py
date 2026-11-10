"""Small selected-character production send/fragmented dispatcher test,no login."""
import json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from checkpoint_client455_rvp_effects import sha,require


def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))


def main():
    source=WS/'scripts/native/client455_selection_probe.cpp';exe=build_full_object_probe('selection',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while (parent/f'selection-{index:03d}').exists():index+=1
    run=parent/f'selection-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);relative='DataTable/ko-kr/NDLanguage.edf';stage_asset(client/relative,run/relative)
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n',encoding='ascii')
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
    native=json.loads(output.read_text()) if output.exists() else None
    report=dict(status='PASS' if result.returncode==0 and native else 'FAIL',exe=record(target),sources=[record(source),record(WS/'scripts/native/client455_selection.h'),record(WS/'scripts/native/client455_selection.inc')],
        script=record(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,
        shared_staging=staging_stats(),input_exe_executed=False,authentication_performed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-selection-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exit=result.returncode,native=native,console=console.read_text(errors='replace')[-1200:],run=run.relative_to(WS).as_posix())))
    require(report['status']=='PASS','Selected-character production test failed')


if __name__=='__main__':main()
