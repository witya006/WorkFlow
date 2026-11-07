"""Exercise actual source registry/storage consumers after455 identity migration."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))


def main():
    source=WS/'scripts/native/client455_storage_probe.cpp'
    exe=build_full_object_probe('storage',source)
    root=WS/'work/m9'/sha(exe)[:8]
    runs=[]
    for _ in range(3):
        index=1
        while (root/f'storage-{index:03d}').exists():index+=1
        folder=root/f'storage-{index:03d}';folder.mkdir(parents=True)
        target=folder/exe.name;shutil.copyfile(exe,target)
        # Independent pinned4FEF50 assembly accepts exactly0,1,5.
        fixture=folder/'storage-cases.txt'
        fixture.write_text(''.join(f'{i} {int(i in {0,1,5})}\n' for i in range(256)))
        result=subprocess.run([str(target)],cwd=folder,capture_output=True,timeout=60,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        console=folder/'console.txt';console.write_bytes(result.stdout+result.stderr)
        try:native=json.loads(result.stdout)
        except(ValueError,UnicodeError):native=None
        runs.append(dict(exe=record(target),fixture=record(fixture),console=record(console),
                         natural_exit=result.returncode,native=native))
    report=dict(scope='Actual canonical registry IDs,source storage constants,pack creation and ReturnItem guard;not complete455factory/item protocol/Tutorial',
                source=record(source),exe=record(exe),map=record(exe.with_suffix('.map')),
                architecture=pe(exe.read_bytes())['architecture'],runs=runs,
                normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),
                script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),
                input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-storage-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exits=[r['natural_exit'] for r in runs],native=runs[0]['native'])))
    if any(r['natural_exit'] or not r['native'] or r['native']['status']!='PASS' for r in runs):
        raise SystemExit('Actual storage probe failed;inspect recorded consoles')


if __name__=='__main__':main()
