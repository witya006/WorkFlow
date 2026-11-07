"""Measure the actual normal source registry before wiring the 455 Tutorial."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = WS / 'scripts/native/client455_tutorial_dependencies_probe.cpp'
    exe = build_full_object_probe('tutorial-dependencies', source)
    def record(path):
        return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))

    # An initial unguarded audit executable faulted. Keep separate evidence from
    # repeated runs of this exact diagnostic PE rather than asserting stability.
    root = WS / 'work/m9' / sha(exe)[:8]
    runs = []
    for _ in range(8):
        index = 1
        while (root / f'tutorial-dependencies-{index:03d}').exists():
            index += 1
        folder = root / f'tutorial-dependencies-{index:03d}'
        folder.mkdir(parents=True)
        target = folder / exe.name
        shutil.copyfile(exe, target)
        run = subprocess.run([str(target)], cwd=folder, capture_output=True, timeout=60,
                             creationflags=subprocess.CREATE_NO_WINDOW)
        console = folder / 'console.txt'
        console.write_bytes(run.stdout + run.stderr)
        try:
            native = json.loads(run.stdout)
        except (ValueError, UnicodeError):
            native = None
        runs.append(dict(exe=record(target), console=record(console),
                         natural_exit=run.returncode, native=native))

    report = dict(
        scope='Current source construction/RTTI/layout only;not target equivalence or working Tutorial',
        architecture=pe(exe.read_bytes())['architecture'],
        source=record(source), exe=record(exe), map=record(exe.with_suffix('.map')),
        runs=runs, all_observed_runs_passed=all(row['natural_exit'] == 0 and row['native'] for row in runs),
        normal_link_sha256=sha(WS / 'inventory/client455-normal-link.json'),
        script_sha256=sha(Path(__file__)),
        builder_sha256=sha(WS / 'scripts/client455_own_probe.py'),
        input_exe_executed=False, server_modified=False, M6='OPEN', M9='OPEN',
    )
    (WS / 'inventory/client455-tutorial-dependencies-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(runs=len(runs), exits=[row['natural_exit'] for row in runs], native=runs[0]['native'])))
    if not report['all_observed_runs_passed']:
        raise SystemExit('Observed source construction failure; see recorded runs')
    for row in runs:
        native = row['native']
        if native['source_objects'] != len(native['boards']) or not native['equipment_alias']:
            raise ValueError('Inconsistent actual registry evidence')


if __name__ == '__main__':
    main()
