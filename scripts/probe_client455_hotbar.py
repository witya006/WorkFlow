"""Verify ordinary Linker delta-save through the actual client send ring/AES."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    source=WS/'scripts/native/client455_hotbar_probe.cpp';exe=build_full_object_probe('hotbar',source)
    root=WS/'work/m9'/sha(exe)[:8];index=1
    while(root/f'hotbar-{index:03d}').exists():index+=1
    run=root/f'hotbar-{index:03d}';run.mkdir(parents=True)
    target=run/exe.name;shutil.copyfile(exe,target)
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';packets=run/'packets.txt'
    report=dict(scope='Actual source Linker snapshot/delta-save/periodic branch and real send ring/AES;not fullLinker GUI/clone/ownership/input or server acceptance',
        source=record(source),exe=record(target),map=record(exe.with_suffix('.map')),console=record(console),
        output=record(output)if output.exists()else None,packets=record(packets)if packets.exists()else None,
        native=json.loads(output.read_text())if output.exists()else None,natural_exit=result.returncode,
        normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),script_sha256=sha(Path(__file__)),
        builder_sha256=sha(WS/'scripts/client455_own_probe.py'),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-hotbar-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exit=result.returncode,native=report['native'],console=console.read_text(errors='replace')[-1500:])))
    if result.returncode or not report['native']:raise SystemExit(1)
if __name__=='__main__':main()
