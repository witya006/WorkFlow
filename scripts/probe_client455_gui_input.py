"""Exercise recovered ordinary GUI input/focus/queue using full client objects."""
import ctypes
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
    reference_path = WS / 'inventory/client455-gui-input-reference.json'
    reference = json.loads(reference_path.read_text())
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_gui_input.py'):
        raise ValueError('Refresh input reference')
    source = WS / 'scripts/native/client455_gui_input_probe.cpp'
    exe = build_full_object_probe('gui-input', source)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    parent = WS / 'work/m9' / sha(exe)[:8]
    parent.mkdir(parents=True, exist_ok=True)
    runs = []
    for row, folder in zip(reference['inputs'], ['ko-kr', 'ru-ru']):
        index = 1
        while (parent / f'input-{folder}-{index:03d}').exists():
            index += 1
        run = parent / f'input-{folder}-{index:03d}'
        run.mkdir()
        target = run / exe.name
        shutil.copyfile(exe, target)
        inputs = []
        for name in ['System/shader/Grass1.vsh', 'System/shader/grass1.vso', 'System/console.jpg', 'System/010.TTF', f'DataTable/{folder}/NDLanguage.edf', 'SpriteImage/Common/mouse.spr', f'SpriteImage/{folder}/common.spr']:
            original, destination = client / name, run / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination)
            inputs.append({'file': destination.relative_to(WS).as_posix(), 'sha256': sha(destination)})
        config = run / 'R3Engine.ini'
        config.write_text(f'[Setup]\nLanguage={row["nation"]}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n', encoding='ascii')
        inputs.append({'file': config.relative_to(WS).as_posix(), 'sha256': sha(config)})
        startup = subprocess.STARTUPINFO()
        startup.dwFlags, startup.wShowWindow = subprocess.STARTF_USESHOWWINDOW, 0
        try:
            result = subprocess.run([str(target)], cwd=run, capture_output=True, timeout=45,
                                    creationflags=subprocess.CREATE_NO_WINDOW, startupinfo=startup)
        finally:
            remove = ctypes.WinDLL('gdi32.dll').RemoveFontResourceW
            remove.argtypes, remove.restype = [ctypes.c_wchar_p], ctypes.c_int
            remove(str(run / 'System/010.TTF'))
        (run / 'console.txt').write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError(f'GUI input {folder} runtime {result.returncode}:{run}:{result.stderr.decode(errors="replace")}')
        output = run / 'result.json'
        runs.append({'nation': row['nation'], 'exe': {'file': target.relative_to(WS).as_posix(), 'sha256': sha(target)},
                     'output': {'file': output.relative_to(WS).as_posix(), 'sha256': sha(output)}, 'inputs': inputs,
                     'native': json.loads(output.read_text()), 'exit': result.returncode})
    names = ['client455_gui_input.h', 'client455_gui_input.cpp', 'client455_gui_input_object.inc', 'client455_gui_input_container.inc', 'client455_gui_input_queue.inc', 'client455_gui_scrollbar.cpp', 'client455_minimap_opacity_owner.inc']
    report = {'scope': reference['scope'], 'architecture': 'x86', 'entry_rva': hex(pe(exe.read_bytes())['entry_rva']),
              'source': source.relative_to(WS).as_posix(), 'source_sha256': sha(source),
              'sources': {name: sha(WS / 'scripts/native' / name) for name in names},
              'script_sha256': sha(Path(__file__)), 'builder_sha256': sha(WS / 'scripts/client455_own_probe.py'),
              'generator_sha256': sha(WS / 'scripts/prepare_client455_normal.py'),
              'reference_sha256': sha(reference_path), 'normal_link_sha256': sha(WS / 'inventory/client455-normal-link.json'),
              'map': {'file': exe.with_suffix('.map').relative_to(WS).as_posix(), 'sha256': sha(exe.with_suffix('.map'))},
              'runs': runs, 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-gui-input-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps([{'nation': row['nation'], **row['native']} for row in runs]))


if __name__ == '__main__':
    main()
