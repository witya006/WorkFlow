"""Verify actual EX/Var objects with queued input and D3D readback."""
import ctypes
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path
from PIL import Image
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    reference_path = WS / 'inventory/client455-scrollbar-variants-reference.json'
    reference = json.loads(reference_path.read_text())
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_scrollbar_variants.py'):
        raise ValueError('Refresh variant reference')
    source = WS / 'scripts/native/client455_gui_scrollbar_variants_probe.cpp'
    exe = build_full_object_probe('scrollbar-variants', source)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    parent = WS / 'work/m9' / sha(exe)[:8]
    parent.mkdir(parents=True, exist_ok=True)
    runs = []
    for row in reference['inputs']:
        nation, folder = row['nation'], row['folder']
        index = 1
        while (parent / f'variants-{folder}-{index:03d}').exists():
            index += 1
        run = parent / f'variants-{folder}-{index:03d}'
        run.mkdir()
        target = run / exe.name
        shutil.copyfile(exe, target)
        inputs = []
        pairs = [(client / name, run / name) for name in ['System/shader/Grass1.vsh', 'System/shader/grass1.vso', 'System/console.jpg', 'System/010.TTF', f'DataTable/{folder}/NDLanguage.edf']]
        pairs.append((Path(row['sprite']['file']), run / 'common.spr'))
        for original, destination in pairs:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination)
            inputs.append({'file': destination.relative_to(WS).as_posix(), 'sha256': sha(destination)})
        config = run / 'R3Engine.ini'
        config.write_text(f'[Setup]\nLanguage={nation}\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n', encoding='ascii')
        inputs.append({'file': config.relative_to(WS).as_posix(), 'sha256': sha(config)})
        #Target loader requires actions<16,so action15 is unreachable through it.
        #Keep that restriction;this fixture exercises row2 and missing-cap behavior.
        fixture = run / 'variant-fixture.spr'
        raw = bytearray(struct.pack('<II', 0x3f8ccccd, 15))
        for action in range(15):
            count = 6 if action in [2, 14] else 1
            raw += struct.pack('<I', count)
            for frame in range(count):
                ink = ({1: 0xff00ff00, 4: 0xff00ffff}.get(frame, 0xffffffff) if action == 2
                       else {0: 0xffff0000, 2: 0xff0000ff, 3: 0xffffff00, 5: 0xffff00ff}.get(frame, 0xff808080))
                pixels = b''.join(struct.pack('<I', (ink if action != 2 or y == 2 else 0xff808080) if x < 6 and y < 6 else 0)
                                  for y in range(8) for x in range(8))
                raw += struct.pack('<6I', 21, 6, 6, 8, 8, len(pixels)) + pixels
        fixture.write_bytes(raw)
        inputs.append({'file': fixture.relative_to(WS).as_posix(), 'sha256': sha(fixture)})
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
            raise ValueError(f'Variants {nation} runtime {result.returncode}:{run}:{result.stderr.decode(errors="replace")}')
        frames = []
        for name in ['ex', 'var', 'var-pressed']:
            frame, preview = run / f'scrollbar-{name}.bgra', run / f'scrollbar-{name}.png'
            Image.frombytes('RGBA', (640, 480), frame.read_bytes(), 'raw', 'BGRA').convert('RGB').save(preview)
            frames.append({'file': frame.relative_to(WS).as_posix(), 'sha256': sha(frame), 'width': 640, 'height': 480,
                           'preview': preview.relative_to(WS).as_posix(), 'preview_sha256': sha(preview)})
        if frames[1]['sha256'] == frames[2]['sha256']:
            raise ValueError('Var pressed appearance unchanged')
        output = run / 'result.json'
        runs.append({'nation': nation, 'exe': {'file': target.relative_to(WS).as_posix(), 'sha256': sha(target)},
                     'output': {'file': output.relative_to(WS).as_posix(), 'sha256': sha(output)}, 'inputs': inputs,
                     'frames': frames, 'native': json.loads(output.read_text()), 'exit': result.returncode})
    names = ['client455_gui_scrollbar.h', 'client455_gui_scrollbar.cpp']
    report = {'scope': reference['scope'], 'architecture': 'x86', 'entry_rva': hex(pe(exe.read_bytes())['entry_rva']),
              'source': source.relative_to(WS).as_posix(), 'source_sha256': sha(source),
              'sources': {name: sha(WS / 'scripts/native' / name) for name in names},
              'script_sha256': sha(Path(__file__)), 'builder_sha256': sha(WS / 'scripts/client455_own_probe.py'),
              'generator_sha256': sha(WS / 'scripts/prepare_client455_normal.py'),
              'reference_sha256': sha(reference_path), 'normal_link_sha256': sha(WS / 'inventory/client455-normal-link.json'),
              'map': {'file': exe.with_suffix('.map').relative_to(WS).as_posix(), 'sha256': sha(exe.with_suffix('.map'))},
              'runs': runs, 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-scrollbar-variants-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps([{'nation': row['nation'], **row['native']} for row in runs]))


if __name__ == '__main__':
    main()
