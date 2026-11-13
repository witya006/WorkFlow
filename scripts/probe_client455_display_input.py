"""Targeted hidden-window checks; never logs in or touches the player's client."""
import json
import subprocess
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import sha


def main():
    source = WS / 'scripts/native/client455_display_input_probe.cpp'
    exe = build_full_object_probe('display-input', source)
    run = WS / 'work/display-input455'
    run.mkdir(exist_ok=True)
    (run / 'R3Engine.ini').write_text(
        '[RenderState]\nScreenXSize=1920\nScreenYSize=1080\nbFullScreen=FALSE\n'
        '[Sound]\nSound=FALSE\nMusic=FALSE\n', encoding='ascii')
    result = subprocess.run([str(exe)], cwd=run, capture_output=True, timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    output = run / 'result.txt'
    output.write_bytes(result.stdout + result.stderr)
    print(output.read_text(errors='replace'))
    if result.returncode:
        raise RuntimeError(f'Display input probe failed: {result.returncode}')
    def record(path):
        return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))
    report = dict(status='PASS', scope='Actual engine projection and window handler; wheel-distance helper',
                  resolution=[1920, 1080], source=record(source), executable=record(exe), output=record(output),
                  normal_executable=json.loads((WS / 'inventory/client455-normal-link.json').read_text())['executable'],
                  visible_lobby_verified=False, live_world_wheel_verified=False,
                  user_session_touched=False, server_modified=False)
    (WS / 'inventory/client455-display-input.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
