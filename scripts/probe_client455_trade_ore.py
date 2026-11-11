"""Exercise the restored trade and ore views with the ordinary client objects."""
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
    source = WS / 'scripts/native/client455_trade_ore_probe.cpp'
    exe = build_full_object_probe('trade-ore', source)
    parent = WS / 'work/m9' / sha(exe)[:8]
    index = 1
    while (parent / f'trade-ore-{index:03d}').exists():
        index += 1
    run = parent / f'trade-ore-{index:03d}'
    run.mkdir(parents=True)
    target = run / exe.name
    shutil.copyfile(exe, target)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    names = ['mss32.dll', 'System/010.TTF', 'System/console.jpg', 'System/shader/Grass1.vsh',
             'System/shader/grass1.vso', 'DataTable/zh-tw/NDLanguage.edf']
    names += [f'SpriteImage/{locale}/{name}' for locale in ('Common', 'zh-tw')
              for name in ('common.spr', 'trade.spr', 'oreproc.spr', 'item.spr', 'inventory.spr',
                           'ItemLock.spr', 'SocketState.spr')]
    inputs = []
    for name in names:
        original = client / name
        if original.is_file():
            stage_asset(original, run / name)
            inputs.append(dict(**record(run / name), original=str(original)))
    inputs += copy_character_shaders(run)
    config = run / 'R3Engine.ini'
    config.write_text('[Setup]\nLanguage=Taiwan\n[RenderState]\nScreenXSize=800\nScreenYSize=600\n'
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
        Image.frombytes('RGBA', (800, 600), file.read_bytes(), 'raw', 'BGRA').convert('RGB').save(preview)
        frames.append(dict(**record(file), preview=record(preview)))
    passed = result.returncode == 0 and native and native.get('status') == 'PASS' and len(frames) == 3
    report = dict(status='PASS' if passed else 'FAIL', nation='Taiwan', native=native,
                  normal_link_sha256=sha(WS / 'inventory/client455-normal-link.json'), natural_exit=result.returncode,
                  inputs=inputs, frames=frames, config=record(config), exe=record(target),
                  source=record(source), script=record(Path(__file__)), console=record(console),
                  output=record(output) if output.exists() else None, shared_staging=staging_stats(),
                  input_exe_executed=False, server_modified=False)
    encoded = json.dumps(report, indent=2) + '\n'
    (run / 'probe-report.json').write_text(encoded)
    (WS / 'inventory/client455-trade-ore-native.json').write_text(encoded)
    print(json.dumps(dict(exit=result.returncode, run=run.relative_to(WS).as_posix(), native=native,
                          console=console.read_text(errors='replace')[-1500:])))
    require(passed, 'Player trade and ore native checks')


if __name__ == '__main__':
    main()
