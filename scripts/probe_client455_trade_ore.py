"""Exercise the restored item panels with the ordinary client objects."""
import argparse
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
    parser = argparse.ArgumentParser()
    panel = parser.add_mutually_exclusive_group()
    panel.add_argument('--item-work', action='store_true')
    panel.add_argument('--service-windows', action='store_true')
    panel.add_argument('--party', action='store_true')
    panel.add_argument('--targets', action='store_true')
    args = parser.parse_args()
    if args.targets:
        name = 'target-windows'
        skins = ('main.spr', 'renewal.spr', 'dungeon.spr')
    elif args.party:
        name = 'party-window'
        skins = ('main.spr', 'class.spr', 'EtcUI.spr')
    elif args.service_windows:
        name = 'service-windows'
        skins = ('exchange.spr', 'mining.spr', 'class.spr', 'main.spr')
    elif args.item_work:
        name = 'item-work'
        skins = ('itemmake.spr', 'itemupgrade.spr')
    else:
        name = 'trade-ore'
        skins = ('trade.spr', 'oreproc.spr')
    source = WS / 'scripts/native' / f'client455_{name.replace("-", "_")}_probe.cpp'
    exe = build_full_object_probe(name, source)
    parent = WS / 'work/m9' / sha(exe)[:8]
    index = 1
    while (parent / f'{name}-{index:03d}').exists():
        index += 1
    run = parent / f'{name}-{index:03d}'
    run.mkdir(parents=True)
    target = run / exe.name
    shutil.copyfile(exe, target)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    names = ['mss32.dll', 'System/010.TTF', 'System/console.jpg', 'System/shader/Grass1.vsh',
             'System/shader/grass1.vso', 'DataTable/zh-tw/NDLanguage.edf']
    names += [f'SpriteImage/{locale}/{skin}' for locale in ('Common', 'zh-tw')
              for skin in (*skins, 'common.spr', 'item.spr', 'inventory.spr', 'ItemLock.spr', 'SocketState.spr')]
    inputs = []
    for relative in names:
        original = client / relative
        if original.is_file():
            stage_asset(original, run / relative)
            inputs.append(dict(**record(run / relative), original=str(original)))
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
    passed = result.returncode == 0 and native and native.get('status') == 'PASS' and len(frames) == native.get('GPU_frames')
    report = dict(status='PASS' if passed else 'FAIL', nation='Taiwan', native=native,
                  normal_link_sha256=sha(WS / 'inventory/client455-normal-link.json'), natural_exit=result.returncode,
                  inputs=inputs, frames=frames, config=record(config), exe=record(target),
                  source=record(source), script=record(Path(__file__)), console=record(console),
                  output=record(output) if output.exists() else None, shared_staging=staging_stats(),
                  input_exe_executed=False, server_modified=False)
    if args.item_work or args.service_windows or args.party or args.targets:
        report['harness'] = record(source.with_name('client455_trade_ore_probe.cpp'))
    encoded = json.dumps(report, indent=2) + '\n'
    (run / 'probe-report.json').write_text(encoded)
    (WS / f'inventory/client455-{name}-native.json').write_text(encoded)
    print(json.dumps(dict(exit=result.returncode, run=run.relative_to(WS).as_posix(), native=native,
                          console=console.read_text(errors='replace')[-1500:])))
    require(passed, f'Native window checks for {name}')


if __name__ == '__main__':
    main()
