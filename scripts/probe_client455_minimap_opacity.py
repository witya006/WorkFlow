"""Run actual minimap owner EX input and GPU against localized455resources."""
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
    reference_path = WS / 'inventory/client455-minimap-opacity-reference.json'
    reference = json.loads(reference_path.read_text())
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_minimap_opacity.py'):
        raise ValueError('Refresh opacity reference')
    source = WS / 'scripts/native/client455_minimap_opacity_probe.cpp'
    exe = build_full_object_probe('minimap-opacity', source)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    parent = WS / 'work/m9' / sha(exe)[:8]
    parent.mkdir(parents=True, exist_ok=True)
    runs = []
    for row in reference['inputs']:
        nation, folder = row['nation'], row['folder']
        index = 1
        while (parent / f'opacity-{folder}-{index:03d}').exists():
            index += 1
        run = parent / f'opacity-{folder}-{index:03d}'
        run.mkdir()
        target = run / exe.name
        shutil.copyfile(exe, target)
        pairs = [(client / name, run / name) for name in ['System/shader/Grass1.vsh', 'System/shader/grass1.vso', 'System/console.jpg', 'System/010.TTF', f'DataTable/{folder}/NDLanguage.edf', 'SpriteImage/Common/mouse.spr']]
        for name in ['common', 'main']:
            original = Path(row[name]['file'])
            pairs.append((original, run / original.relative_to(client)))
        inputs = []
        for original, destination in pairs:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination)
            inputs.append({'file': destination.relative_to(WS).as_posix(), 'sha256': sha(destination)})
        config = run / 'R3Engine.ini'
        config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n', encoding='ascii')
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
            raise ValueError(f'Opacity {nation} runtime {result.returncode}:{run}:{result.stderr.decode(errors="replace")}')
        output, frames = run / 'result.json', []
        for name in ['full', 'half', 'low']:
            frame, preview = run / f'minimap-opacity-{name}.bgra', run / f'minimap-opacity-{name}.png'
            Image.frombytes('RGBA', (640, 480), frame.read_bytes(), 'raw', 'BGRA').convert('RGB').save(preview)
            frames.append({'file': frame.relative_to(WS).as_posix(), 'sha256': sha(frame), 'width': 640, 'height': 480,
                           'preview': preview.relative_to(WS).as_posix(), 'preview_sha256': sha(preview)})
        if len({frame['sha256'] for frame in frames}) != 3:
            raise ValueError('Distinct opacity GPU output required')
        runs.append({'nation': nation, 'exe': {'file': target.relative_to(WS).as_posix(), 'sha256': sha(target)},
                     'output': {'file': output.relative_to(WS).as_posix(), 'sha256': sha(output)}, 'inputs': inputs,
                     'frames': frames, 'native': json.loads(output.read_text()), 'exit': result.returncode})
    names = ['client455_minimap_opacity.h', 'client455_minimap_opacity.cpp', 'client455_minimap_opacity_owner.inc']
    report = {'scope': reference['scope'], 'architecture': 'x86', 'entry_rva': hex(pe(exe.read_bytes())['entry_rva']),
              'source': source.relative_to(WS).as_posix(), 'source_sha256': sha(source),
              'sources': {name: sha(WS / 'scripts/native' / name) for name in names},
              'script_sha256': sha(Path(__file__)), 'builder_sha256': sha(WS / 'scripts/client455_own_probe.py'),
              'generator_sha256': sha(WS / 'scripts/prepare_client455_normal.py'),
              'reference_sha256': sha(reference_path), 'normal_link_sha256': sha(WS / 'inventory/client455-normal-link.json'),
              'map': {'file': exe.with_suffix('.map').relative_to(WS).as_posix(), 'sha256': sha(exe.with_suffix('.map'))},
              'runs': runs, 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-minimap-opacity-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps([{'nation': row['nation'], **row['native']} for row in runs]))


if __name__ == '__main__':
    main()
