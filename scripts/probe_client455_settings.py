"""Five native settings pages at Full HD, draft/cancel/apply; no authentication."""
import json
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_asset_staging import stage_asset, sha
from client455_own_probe import build_full_object_probe


def main():
    source = WS / 'scripts/native/client455_settings_probe.cpp'
    root = WS / 'work/settings455'
    root.mkdir(exist_ok=True)
    generated = root / 'probe.cpp'
    generated.write_bytes(source.read_bytes())
    exe = build_full_object_probe('settings', generated)
    run = root / 'runtime'
    run.mkdir(exist_ok=True)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    for name in ['System/010.TTF', 'SpriteImage/Common/common.spr',
                 'SpriteImage/Common/system.spr', 'SpriteImage/ru-ru/common.spr',
                 'SpriteImage/ru-ru/system.spr', 'SpriteImage/ko-kr/system.spr',
                 'DataTable/ru-ru/NDLanguage.edf']:
        if (client / name).is_file():
            stage_asset(client / name, run / name)
    (run / 'R3Engine.ini').write_text(
        '[Setup]\nLanguage=Russia\n[RenderState]\nScreenXSize=1920\nScreenYSize=1080\n'
        'bFullScreen=FALSE\nMSAA=4\nEnhancedActorLighting=0\n'
        '[Sound]\nSound=FALSE\nMusic=FALSE\n', encoding='ascii')
    (run / 'DataTable').mkdir(exist_ok=True)
    output = run / 'result.json'
    if output.exists():
        output.unlink()
    result = subprocess.run([str(exe)], cwd=run, capture_output=True, timeout=45,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    console = run / 'console.txt'
    console.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'Settings: {result.returncode}: {console.read_text(errors="replace")}')
    def record(path):
        return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))
    frames = [record(run / f'settings-{page}.png') for page in range(5)]
    report = dict(status='PASS', source=record(source), executable=record(exe),
                  native=json.loads(output.read_text()), result=record(output), frames=frames,
                  runner=record(Path(__file__)), console=record(console),
                  normal_executable=json.loads((WS / 'inventory/client455-normal-link.json').read_text())['executable'],
                  scope='Real native widgets and persistence with controlled HWND; gameplay backend requires live verification',
                  server_modified=False, authentication_performed=False)
    (WS / 'inventory/client455-settings.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='PASS', run=run.relative_to(WS).as_posix(), native=report['native'])))


if __name__ == '__main__':
    main()
