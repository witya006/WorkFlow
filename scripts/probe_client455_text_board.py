"""Exercise actual ordinary TextBoard caches,markup/WORD boundaries and GPU output."""
import ctypes
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    reference_path = WS / 'inventory/client455-text-board-reference.json'
    reference = json.loads(reference_path.read_text())
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_text_board.py'):
        raise ValueError('Refresh TextBoard reference')
    source = WS / 'scripts/native/client455_gui_text_board_probe.cpp'
    exe = build_full_object_probe('text-board', source)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    parent = WS / 'work/m9' / sha(exe)[:8]
    parent.mkdir(parents=True, exist_ok=True)
    runs = []
    for row in reference['inputs']:
        nation, folder = row['nation'], row['folder']
        index = 1
        while (parent / f'text-board-{folder}-{index:03d}').exists():
            index += 1
        run = parent / f'text-board-{folder}-{index:03d}'
        run.mkdir()
        target = run / exe.name
        shutil.copyfile(exe, target)
        inputs = []
        for name in ['System/shader/Grass1.vsh', 'System/shader/grass1.vso', 'System/console.jpg', 'System/010.TTF', f'DataTable/{folder}/NDLanguage.edf']:
            original, destination = client / name, run / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination)
            inputs.append({'file': destination.relative_to(WS).as_posix(), 'sha256': sha(destination)})
        config = run / 'R3Engine.ini'
        config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n', encoding='ascii')
        inputs.append({'file': config.relative_to(WS).as_posix(), 'sha256': sha(config)})
        startup = subprocess.STARTUPINFO()
        startup.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        try:
            result = subprocess.run([str(target)], cwd=run, capture_output=True, timeout=90,
                                    creationflags=subprocess.CREATE_NO_WINDOW, startupinfo=startup)
        finally:
            remove = ctypes.WinDLL('gdi32.dll').RemoveFontResourceW
            remove.argtypes, remove.restype = [ctypes.c_wchar_p], ctypes.c_int
            remove(str(run / 'System/010.TTF'))
        (run / 'console.txt').write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError(f'TextBoard {nation} runtime {result.returncode}:{run}:{result.stderr.decode(errors="replace")}')
        output = run / 'result.json'
        frames = []
        for name in ['colors', 'markup', 'bottom', 'highlight']:
            frame, preview = run / f'textboard-{name}.bgra', run / f'textboard-{name}.png'
            Image.frombytes('RGBA', (640, 480), frame.read_bytes(), 'raw', 'BGRA').convert('RGB').save(preview)
            frames.append({'file': frame.relative_to(WS).as_posix(), 'sha256': sha(frame), 'width': 640, 'height': 480,
                           'preview': preview.relative_to(WS).as_posix(), 'preview_sha256': sha(preview)})
        runs.append({'nation': nation, 'exe': {'file': target.relative_to(WS).as_posix(), 'sha256': sha(target)},
                     'output': {'file': output.relative_to(WS).as_posix(), 'sha256': sha(output)}, 'inputs': inputs,
                     'frames': frames, 'native': json.loads(output.read_text()), 'exit': result.returncode})
    names = ['client455_gui_text_board.h', 'client455_gui_text_board.cpp']
    report = {
        'scope': reference['scope'], 'architecture': 'x86', 'entry_rva': hex(pe(exe.read_bytes())['entry_rva']),
        'source': source.relative_to(WS).as_posix(), 'source_sha256': sha(source),
        'sources': {name: sha(WS / 'scripts/native' / name) for name in names},
        'script_sha256': sha(Path(__file__)), 'builder_sha256': sha(WS / 'scripts/client455_own_probe.py'),
        'generator_sha256': sha(WS / 'scripts/prepare_client455_normal.py'),
        'reference_sha256': sha(reference_path), 'normal_link_sha256': sha(WS / 'inventory/client455-normal-link.json'),
        'map': {'file': exe.with_suffix('.map').relative_to(WS).as_posix(), 'sha256': sha(exe.with_suffix('.map'))},
        'runs': runs, 'input_exe_executed': False, 'server_modified': False,
        'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN',
    }
    (WS / 'inventory/client455-text-board-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps([{'nation': row['nation'], **row['native']} for row in runs]))


if __name__ == '__main__':
    main()
