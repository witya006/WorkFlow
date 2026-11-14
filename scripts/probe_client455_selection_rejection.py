"""Actual selection callback, encrypted replies, NetworkInput and modal; no server."""
import json
import re
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_asset_staging import stage_asset, sha
from client455_own_probe import build_full_object_probe


def main():
    source = WS / 'scripts/native/client455_selection_rejection_probe.cpp'
    login = WS / 'work/client455-port/normal/source/gameprogress/cgp_login.cpp'
    # Exact enum declarations keep test assertions independent of numeric states.
    enum = re.search(rb'enum\s+LOGINSTATE\s*\{.*?\};', login.read_bytes(), re.S)
    if not enum:
        raise RuntimeError('Missing ordinary login states')
    root = WS / 'work/selection-rejection455'
    root.mkdir(exist_ok=True)
    generated = root / 'probe.cpp'
    generated.write_bytes(enum[0] + b'\n' + source.read_bytes())
    exe = build_full_object_probe('selection-rejection', generated)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    runs = []
    for nation, folder in [('Russia', 'ru-ru'), ('Korea', 'ko-kr')]:
        run = root / 'runtime' / folder
        run.mkdir(parents=True, exist_ok=True)
        inputs = []
        def record(path):
            return dict(file=path.relative_to(WS).as_posix(), sha256=sha(path))
        for name in ['System/010.TTF', 'SpriteImage/Common/mouse.spr',
                     f'SpriteImage/{folder}/common.spr', f'DataTable/{folder}/NDLanguage.edf']:
            stage_asset(client / name, run / name)
            inputs.append(record(run / name))
        (run / 'R3Engine.ini').write_text(
            f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=1920\nScreenYSize=1080\n'
            'bFullScreen=FALSE\n[Sound]\nSound=FALSE\nMusic=FALSE\n', encoding='ascii')
        output = run / 'result.json'
        if output.exists():
            output.unlink()
        result = subprocess.run([str(exe)], cwd=run, capture_output=True, timeout=35,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        console = run / 'console.txt'
        console.write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(f'{nation}: exit {result.returncode}: {console.read_text(errors="replace")}')
        runs.append(dict(nation=nation, inputs=inputs, result=record(output),
                         native=json.loads(output.read_text()), console=record(console)))
    report = dict(status='PASS', resolution=[1920, 1080], runs=runs,
                  executable=record(exe), source=record(source), generated=record(generated),
                  login_source=record(login), runner=record(Path(__file__)),
                  normal_executable=json.loads((WS / 'inventory/client455-normal-link.json').read_text())['executable'],
                  scope='Actual UI and network handlers with controlled encrypted replies; no live server or full scene',
                  server_modified=False, authentication_performed=False, user_session_touched=False)
    (WS / 'inventory/client455-selection-rejection.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='PASS', runs=[dict(nation=r['nation'], **r['native']) for r in runs])))


if __name__ == '__main__':
    main()
