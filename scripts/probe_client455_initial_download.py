"""Check bounded native wire decoders against independent byte fixtures."""
import json
import subprocess
from pathlib import Path

from checkpoint_client455_rvp_effects import require, sha
from client455_own_probe import build_full_object_probe
from client455_ui_checkpoint import record
from compare_client_binaries import WS


def main():
    source = WS / 'scripts/native/client455_initial_download_probe.cpp'
    exe = build_full_object_probe('initial-download', source)
    run = subprocess.run([str(exe)], cwd=exe.parent, capture_output=True,
                         creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
    console = exe.parent / 'probe-console.txt'
    console.write_bytes(run.stdout + run.stderr)
    require(run.returncode == 0, 'Initial download native fixture: ' + run.stderr.decode(errors='replace'))
    parsed = json.loads(run.stdout)
    require(parsed['status'] == 'PASS', 'Native initial-download result')
    report = dict(status='PASS', native=parsed, source=record(source), script=record(Path(__file__)),
                  header=record(source.with_name('client455_initial_download.h')), executable=record(exe),
                  world_header=record(source.with_name('client455_world_updates.h')),
                  console=record(console), normal_link_sha256=sha(WS / 'inventory/client455-normal-link.json'))
    (WS / 'inventory/client455-initial-download-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(parsed))


if __name__ == '__main__':
    main()
