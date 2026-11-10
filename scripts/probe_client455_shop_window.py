"""Exercise the ordinary merchant window on the stock Taiwan skins."""
import ctypes
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image

from checkpoint_client455_rvp_effects import require, sha
from client455_asset_staging import stage_asset, staging_stats
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_character_shaders
from client455_ui_checkpoint import record
from compare_client_binaries import WS


def main():
    source = WS / 'scripts/native/client455_shop_window_probe.cpp'
    executable = build_full_object_probe('shop-window', source)
    parent = WS / 'work/m9' / sha(executable)[:8]
    index = 1
    while (parent / f'shop-window-{index:03d}').exists():
        index += 1
    run = parent / f'shop-window-{index:03d}'
    run.mkdir(parents=True)
    target = run / executable.name
    shutil.copyfile(executable, target)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    names = ['mss32.dll', 'System/010.TTF', 'System/console.jpg', 'System/shader/Grass1.vsh',
             'System/shader/grass1.vso', 'DataTable/zh-tw/NDLanguage.edf']
    names += [f'SpriteImage/{locale}/{name}' for locale in ('Common', 'zh-tw')
              for name in ('common.spr', 'shop.spr', 'item.spr', 'inventory.spr', 'ItemLock.spr')]
    inputs = []
    for name in names:
        original = client / name
        if original.is_file():
            stage_asset(original, run / name)
            inputs.append(dict(**record(run / name), original=str(original)))
    inputs += copy_character_shaders(run)
    config = run / 'R3Engine.ini'
    config.write_text('[Setup]\nLanguage=Taiwan\n[RenderState]\nScreenXSize=640\nScreenYSize=480\n'
                      'bFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n')
    startup = subprocess.STARTUPINFO()
    startup.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    try:
        result = subprocess.run([str(target)], cwd=run, capture_output=True, timeout=60,
                                creationflags=subprocess.CREATE_NO_WINDOW, startupinfo=startup)
    finally:
        remove_font = ctypes.WinDLL('gdi32.dll').RemoveFontResourceW
        remove_font.argtypes = [ctypes.c_wchar_p]
        remove_font(str(run / 'System/010.TTF'))
    console = run / 'console.txt'
    console.write_bytes(result.stdout + result.stderr)
    output = run / 'result.json'
    native = json.loads(output.read_text()) if output.exists() else None
    frames = []
    for file in sorted(run.glob('*.bgra')):
        preview = file.with_suffix('.png')
        Image.frombytes('RGBA', (640, 480), file.read_bytes(), 'raw', 'BGRA').convert('RGB').save(preview)
        frames.append(dict(**record(file), preview=record(preview)))
    passed = result.returncode == 0 and native and native.get('status') == 'PASS' and len(frames) == 3
    report = dict(status='PASS' if passed else 'FAIL', nation='Taiwan', native=native,
                  natural_exit=result.returncode, normal_link_sha256=sha(WS / 'inventory/client455-normal-link.json'),
                  inputs=inputs, config=record(config), frames=frames, exe=record(target),
                  script=record(Path(__file__)), source=record(source), console=record(console),
                  output=record(output) if output.exists() else None, shared_staging=staging_stats(),
                  input_exe_executed=False, server_modified=False)
    encoded = json.dumps(report, indent=2) + '\n'
    (run / 'probe-report.json').write_text(encoded)
    (WS / 'inventory/client455-shop-window-native.json').write_text(encoded)
    print(json.dumps(dict(exit=result.returncode, run=run.relative_to(WS).as_posix(), native=native,
                          console=console.read_text(errors='replace')[-1200:])))
    require(passed, 'Merchant window native checks')


if __name__ == '__main__':
    main()
