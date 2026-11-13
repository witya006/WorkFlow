"""Check the D3D9 reset boundary with real hardware and deterministic driver failures."""
import json
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_asset_staging import sha


def main():
    run = WS / 'work/presentation-reset455'
    run.mkdir(parents=True, exist_ok=True)
    source = WS / 'scripts/native/client455_presentation_reset_probe.cpp'
    exe = run / 'presentation-reset.exe'
    vs = json.loads((WS / 'inventory/msvc-verification.json').read_text())
    dev = Path(vs['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    batch = run / 'build.cmd'
    batch.write_text(
        f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1\n'
        'if errorlevel 1 exit /b 1\n'
        f'cl /nologo /MT /O2 /EHsc /std:c++17 /W4 "{source}" '
        f'/Fe"{exe}" d3d9.lib user32.lib > build.txt 2>&1\nexit /b %errorlevel%\n',
        encoding='ascii')
    subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=run, check=True,
                   timeout=90, creationflags=subprocess.CREATE_NO_WINDOW)
    (run / 'R3Engine.ini').write_text('[RenderState]\nMSAA=4\n', encoding='ascii')
    result = subprocess.run([str(exe)], cwd=run, capture_output=True, timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    (run / 'result.txt').write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError((result.stdout + result.stderr).decode(errors='replace'))
    def record(path):
        return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))
    report = dict(status='PASS', scope='D3D9 reset helper, not full-client display acceptance',
                  resolution=[1920, 1080], hardware_resets=3,
                  deterministic_driver_cases=['fallback', 'both_attempts_failed', 'device_lost', 'MSAA_disabled'],
                  source=record(source), helper=record(WS / 'scripts/native/client455_multisampling.h'),
                  executable=record(exe), output=record(run / 'result.txt'),
                  original_executable_executed=False, server_modified=False,
                  visible_window_flicker_verified=False)
    (WS / 'inventory/client455-presentation-reset.json').write_text(json.dumps(report, indent=2) + '\n')
    print(result.stdout.decode(errors='replace'))


if __name__ == '__main__':
    main()
