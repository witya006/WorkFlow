"""Launch a verified own build on the local server for targeted startup checks."""
import argparse
import base64
import ctypes
import getpass
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from client455_asset_staging import ASSET_SUFFIXES, MAX_POOL_LINKS, sha
from client455_runtime_inputs import copy_lobby_audio
from probe_client455_live_launcher import auth_request, auth_reply, marshal_v4x, receive

RECEIPTS = (
    ROOT / 'artifacts/client455-progress/client455-world-entry-live-russia-native.json',
)
# Settings are changed by the live menu. Historical receipts stay immutable;
# each manual run takes a fresh snapshot of these two settings files only.
MUTABLE_SETTINGS = {Path('R3Engine.ini'), Path('DataTable/GameSetting.ini')}


def stage(current_build=False):
    from workspace_guard import require_budget
    require_budget()
    active = json.loads((ROOT / 'inventory/client455-normal-link.json').read_text(encoding='utf-8'))['executable']
    digest = active['sha256']
    for receipt in RECEIPTS:
        if receipt.is_file():
            report = json.loads(receipt.read_text(encoding='utf-8'))
            if report['entry_transition']['passed'] and (report['executable'] == active or current_build):
                break
    else:
        raise ValueError('No verified Russian live entry for the current build')
    source = (ROOT / report['staged_executable']).resolve()
    own = (ROOT / 'work/m9').resolve()
    if not source.is_relative_to(own) or sha(source) != report['executable']['sha256']:
        raise ValueError('The verified launch inputs belong to a different build')
    run = own / digest[:8] / 'manual-1080p'
    run.parent.mkdir(exist_ok=True)
    seen = {}
    for item in report['inputs']:
        listed = Path(item['file'])
        path = (ROOT / listed).resolve()
        if path.is_relative_to(source.parent):
            relative = path.relative_to(source.parent)
        elif item.get('original') and not listed.is_absolute() and '..' not in listed.parts:
            relative = listed
            path = (source.parent / relative).resolve()
        else:
            raise ValueError(f'Input is outside the verified run: {listed}')
        if not path.is_relative_to(source.parent):
            raise ValueError(f'Input is outside the verified run: {listed}')
        if relative in (Path('device.plan'), Path('System/DefaultSet.tmp')):
            continue
        if current_build and relative.name in ('RF_Online.bin', 'RF_Online.map'):
            continue
        if relative in seen:
            if relative not in MUTABLE_SETTINGS and seen[relative] != item['sha256']:
                raise ValueError(f'Conflicting staged input: {relative}')
            continue
        actual = sha(path)
        if relative not in MUTABLE_SETTINGS and actual != item['sha256']:
            raise ValueError(f'Changed staged input: {relative}')
        seen[relative] = actual
    return run, source.parent, active, seen


def populate(run, source, active, inputs, audio=False):
    linked = copied = 0
    run.mkdir(exist_ok=True)
    for relative, digest in inputs.items():
        if audio and relative == Path('R3Engine.ini'):
            continue
        path, target = source / relative, run / relative
        target.parent.mkdir(exist_ok=True, parents=True)
        if target.exists():
            if relative in MUTABLE_SETTINGS:
                continue  # Preserve settings already edited in this owned run.
            if not os.path.samefile(path, target) and sha(target) != digest:
                raise ValueError(f'Changed manual input: {relative}')
            continue
        if path.suffix.lower() in ASSET_SUFFIXES and path.stat().st_nlink < MAX_POOL_LINKS:
            os.link(path, target)
            linked += 1
        else:
            shutil.copyfile(path, target)
            copied += path.stat().st_size
    config_file = run / 'R3Engine.ini'
    current_exe = ROOT / active['file']
    if sha(current_exe) != active['sha256']:
        raise ValueError('Current executable changed after staging')
    target_exe = run / 'RF_Online.bin'
    if not target_exe.exists() or sha(target_exe) != active['sha256']:
        shutil.copyfile(current_exe, target_exe)
        copied += current_exe.stat().st_size
    if audio:
        original = (source / config_file.name).read_text(encoding='ascii')
        client = Path(json.loads((ROOT / 'config/paths.json').read_text())['client_455'])
        copy_lobby_audio(client, run)
        config_file.write_text(original.replace('Sound=FALSE', 'Sound=TRUE').replace('Music=FALSE', 'Music=TRUE')
                               + 'SoundVol=0.65\nMusicVol=0.45\n', encoding='ascii')
    config = config_file.read_text(encoding='ascii').splitlines()
    if not {'ScreenXSize=1920', 'ScreenYSize=1080', 'bFullScreen=FALSE'}.issubset(config):
        raise ValueError('Expected a 1920×1080 windowed configuration')
    return {'sha256': active['sha256'], 'entry_rva': active['entry_rva'], 'architecture': active['architecture'],
            'staged_executable': (run / 'RF_Online.bin').relative_to(ROOT).as_posix(),
            'linked_assets': linked, 'copied_input_bytes': copied}


def test_session(credentials_base64):
    if credentials_base64:
        raw = getpass.getpass('Test credentials base64 (hidden): ')
        credentials = json.loads(base64.urlsafe_b64decode(raw))
        request = auth_request(credentials['login'], credentials['password'])
    else:
        request = auth_request(input('Test account: '), getpass.getpass('Test password: '))
    with socket.create_connection(('127.0.0.1', 27831), timeout=8) as peer:
        peer.sendall(request)
        del request
        size, category, kind = struct.unpack('<HBB', receive(peer, 4))
        if not 4 <= size <= 4096 or (category, kind) != (0x6c, 4):
            raise ValueError('Unexpected launcher reply')
        accepted, account, identifier, _, key = auth_reply(receive(peer, size - 4))
    if not accepted or len(key) != 16:
        raise RuntimeError('The local server did not accept the test account')
    return marshal_v4x(account, identifier, key, nation=7)


def game_window(pid):
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    callback = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = (callback, wintypes.LPARAM)
    user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
    user32.GetClientRect.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.RECT))
    user32.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
    user32.IsWindowVisible.argtypes = (wintypes.HWND,)
    found = []

    @callback
    def inspect(hwnd, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            title = ctypes.create_unicode_buffer(256)
            bounds = wintypes.RECT()
            if user32.GetWindowTextW(hwnd, title, len(title)) and title.value.startswith('RF Online') and user32.GetClientRect(hwnd, ctypes.byref(bounds)):
                if (bounds.right, bounds.bottom) == (1920, 1080):
                    found.append(hwnd)
        return True

    user32.EnumWindows(inspect, 0)
    return found[0] if found else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true', help='Wait for startup screenshots, then close this run')
    parser.add_argument('--audio', action='store_true', help='Enable sound and music in the test copy')
    parser.add_argument('--flight', action='store_true', help='Verify the flight to character selection')
    parser.add_argument('--natural', action='store_true', help='Let the intro finish before checking for the menu')
    parser.add_argument('--credentials-base64', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--current-build', action='store_true', help='Use current own binary with verified Russian resource inputs for manual testing')
    parser.add_argument('--check-inputs', action='store_true', help='Validate launch inputs without logging in or launching the game')
    args = parser.parse_args()
    if args.natural and not args.verify:
        parser.error('--natural requires --verify')
    if args.flight and not (args.audio and args.verify and not args.natural):
        parser.error('--flight requires --audio --verify without --natural')
    parent, source, active, inputs = stage(args.current_build)
    if args.check_inputs:
        print(json.dumps({'status': 'PASS', 'scope': 'Launch inputs only; no server login or game run',
                          'inputs': len(inputs), 'build': active['sha256']}))
        return
    run = parent.with_name(f'{parent.name}-audio' if args.audio else f'{parent.name}-001')
    previous = run / ('manual-launch.json' if args.verify else 'interactive-launch.json')
    for receipt in (run / 'manual-launch.json', run / 'interactive-launch.json'):
        if receipt.is_file() and game_window(json.loads(receipt.read_text(encoding='utf-8'))['pid']):
            raise RuntimeError('The preceding test client is still open')
    evidence = populate(run, source, active, inputs, audio=args.audio)
    handoff = run / 'System/DefaultSet.tmp'
    payload = test_session(args.credentials_base64)
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith('RF455_')}
    if args.verify:
        env.update(RF455_CAPTURE_TITLE='1', RF455_CAPTURE_LOBBY_CAMERA='1')
    captures = ['title-logo.png', 'title-prologue.png', 'lobby-camera-menu.png']
    if args.flight:
        captures += ['lobby-camera-flight.png', 'lobby-camera-selection.png']
    preserved = run / 'natural-startup'
    if args.natural:
        preserved.mkdir(exist_ok=True)
        for frame in [*captures, 'title-logo-source.png', 'manual-launch.json']:
            existing = run / frame
            archive = preserved / ('previous-' + frame)
            if existing.is_file() and not archive.exists():
                shutil.copyfile(existing, archive)
    if args.verify:
        for frame in [*captures, 'title-logo-source.png']:
            (run / frame).unlink(missing_ok=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.PostMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    tick_ms = ctypes.windll.kernel32.GetTickCount64
    tick_ms.restype = ctypes.c_uint64
    game = None
    audio_meter = None
    complete = False
    try:
        with handoff.open('xb') as stream:
            stream.write(payload)
        del payload
        game = subprocess.Popen([str(ROOT / evidence['staged_executable'])], cwd=run, env=env,
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
        evidence['pid'] = game.pid
        if args.audio and args.verify:
            with (run / 'measurements.csv').open('w', encoding='ascii') as measurements:
                audio_meter = subprocess.Popen([str(ROOT / 'work/startup-audio-meter.exe'), str(game.pid), '25000'],
                                               cwd=run, stdout=measurements, creationflags=subprocess.CREATE_NO_WINDOW)
        started = time.monotonic()
        deadline = started + (360 if args.natural else 45)
        evidence['captures'] = {}
        evidence['capture_seconds'] = {}
        evidence['started_tick_ms'] = tick_ms()
        evidence['natural_mode'] = args.natural
        while time.monotonic() < deadline:
            if game.poll() is not None:
                raise RuntimeError(f'Test client exited during startup ({game.returncode})')
            if hwnd := game_window(game.pid):
                evidence['client_size'] = (1920, 1080)
                # WinMain reads the launcher handoff before creating the window.
                handoff.unlink(missing_ok=True)
                if not args.verify:
                    break
                if not args.natural and not evidence.get('esc_sent') and (run / 'title-prologue.png').is_file():
                    evidence['esc_sent'] = bool(user32.PostMessageW(hwnd, 0x0100, 0x1b, 1))
                    user32.PostMessageW(hwnd, 0x0101, 0x1b, 0xc0000001)
                for frame in captures:
                    if frame in evidence['captures']:
                        continue
                    path = run / frame
                    try:
                        with Image.open(path) as image:
                            image.load()
                            if image.size != (1920, 1080):
                                raise ValueError(f'Unexpected capture size: {frame}')
                        evidence['captures'][frame] = sha(path)
                        evidence['capture_seconds'][frame] = round(time.monotonic() - started, 2)
                        if frame == 'lobby-camera-menu.png':
                            evidence['menu_tick_ms'] = tick_ms()
                        if frame == 'lobby-camera-selection.png':
                            evidence['selection_tick_ms'] = tick_ms()
                        print(f'{frame} at {evidence["capture_seconds"][frame]} s', flush=True)
                    except OSError:
                        continue
                if args.flight and evidence.get('menu_tick_ms') and not evidence.get('start_tick_ms'):
                    if tick_ms() - evidence['menu_tick_ms'] >= 2200:
                        if not user32.PostMessageW(hwnd, 0x0100, 0x0d, 1):
                            raise RuntimeError('Could not start the flight from menu')
                        user32.PostMessageW(hwnd, 0x0101, 0x0d, 0xc0000001)
                        evidence['start_tick_ms'] = tick_ms()
                if len(evidence['captures']) == len(captures):
                    if audio_meter:
                        time.sleep(2.0)
                    break
            time.sleep(0.1)
        else:
            raise RuntimeError('Startup did not produce the expected Full HD window or frames')
        complete = True
    finally:
        handoff.unlink(missing_ok=True)
        evidence['private_handoff_removed'] = not handoff.exists()
        evidence['reached_lobby'] = complete if args.verify else None
        if game and (args.verify or not complete) and game.poll() is None:
            game.terminate()
            game.wait(timeout=10)
        if audio_meter and audio_meter.poll() is None:
            audio_meter.terminate()
            audio_meter.wait(timeout=5)
        if args.natural:
            for frame in evidence.get('captures', {}):
                shutil.copyfile(run / frame, preserved / frame)
                prior = preserved / ('previous-' + frame)
                if prior.is_file():
                    shutil.copyfile(prior, run / frame)
            (preserved / 'manual-launch.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
            prior = preserved / 'previous-manual-launch.json'
            if prior.is_file():
                previous.write_bytes(prior.read_bytes())
        else:
            previous.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(evidence, indent=2), flush=True)


if __name__ == '__main__':
    main()
