"""Launch a verified own build on the local server for targeted startup checks."""
import argparse
import base64
import ctypes
import getpass
import hashlib
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CRASH_RECORDER = ROOT / 'work/tools/own-client-startup/own-crash-recorder.exe'
CRASH_TRACE = ROOT / 'artifacts/resource-cache/beta-world-entry-manual.jsonl'
sys.path.insert(0, str(ROOT / 'scripts'))
from client455_asset_staging import ASSET_SUFFIXES, MAX_POOL_LINKS, sha, stage_asset
from client455_runtime_inputs import copy_lobby_audio
from client455_orbit_assets import stage_orbit_assets,stage_material_assets
from probe_client455_live_launcher import auth_request, auth_reply, marshal_v4x, receive

RECEIPTS = (
    ROOT / 'artifacts/client455-progress/client455-world-entry-live-russia-native.json',
)
TAIWAN_RECEIPT = ROOT / 'inventory/client455-character-selection-live-taiwan-native.json'
LOCALES = {'ru-ru': (b'Russia', 7), 'zh-tw': (b'Taiwan', 8)}
# Selected live NeutralB merchant dependencies; hashes stay in the existing
# resource manifest so ordinary startup staging and this launcher share them.
NEUTRALB_NPC_INPUTS = (
    'Character/Npc/Ani/NBNPCA.RFS',
    'Character/Npc/Mesh/NBNPCM.RFS',
    'Character/Npc/Mesh/RFSInfo.dat',
    'Character/Npc/Tex/NBNPCT.RFS',
    'Character/Npc/Tex/RFSInfo.dat',
)
# Additional stock sprites used by the current 455 sprite registry.
SUPPLEMENTAL_SPRITES = {
    'ru-ru': {
        'CashShop.spr': '5d95af6a86dbc7bde4149df0f4e46b4b1158eb54a966b6b693443ac9b91b7218',
    },
    'zh-tw': {
        'CashShop.spr': '5d95af6a86dbc7bde4149df0f4e46b4b1158eb54a966b6b693443ac9b91b7218',
        'guild.spr': '5341c29cc7609071b0a8d2b8d27b43057e3fe3626043b032c636f6bc5824bce7',
        'journal.spr': 'dacea37f17ca82ddef829fb4004e838b3763f3472425c6d0e7e736ae39323d45',
        'macro.spr': '151394c83a1dbd1fbbb05bc449d0d19dacd880ab46fdbcea1db9dfb695ba83d0',
        'patriarch.spr': 'cfd78e01e88ae374f718ddc40fd4da38b3c0658ae6398300bd42cd84c807b91d',
        'post.spr': 'a1dcd0408aafb8a40ef560c69777749eef64e146e323bb8e975fbe390a1f8058',
    },
}
# Settings are changed by the live menu. Historical receipts stay immutable;
# each manual run takes a fresh snapshot of these two settings files only.
MUTABLE_SETTINGS = {Path('R3Engine.ini'), Path('DataTable/GameSetting.ini')}


def stage(current_build=False):
    from workspace_guard import require_budget
    require_budget()
    active = json.loads((ROOT / 'inventory/client455-normal-link.json').read_text(encoding='utf-8'))['executable']
    if sha(ROOT / active['file']) != active['sha256']:
        raise ValueError('Current executable does not match the normal link receipt')
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
    run = ROOT / 'work/client455-preview/runtime'
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


def locale_inputs(locale):
    config = json.loads((ROOT / 'config/paths.json').read_text(encoding='utf-8'))
    client = Path(config['client_455']).resolve(strict=True)
    expected = {}
    if locale == 'zh-tw':
        report = json.loads(TAIWAN_RECEIPT.read_text(encoding='utf-8'))
        historical_run = (ROOT / report['staged_executable']).parent
        for item in report['inputs']:
            listed = Path(item['file'])
            absolute = ROOT / listed
            if absolute.is_relative_to(historical_run):
                relative = absolute.relative_to(historical_run)
            elif not listed.is_absolute():
                relative = listed
            else:
                continue
            if (len(relative.parts) < 3 or '..' in relative.parts or
                relative.parts[0].lower() not in ('datatable', 'spriteimage') or
                relative.parts[1].lower() != locale):
                continue
            if expected.setdefault(relative, item['sha256']) != item['sha256']:
                raise ValueError(f'Conflicting Taiwan resource receipt: {relative}')
        if len(expected) != 52:
            raise ValueError(f'Expected 52 locale-specific Taiwan inputs in the receipt, found {len(expected)}')

    for name, digest in SUPPLEMENTAL_SPRITES[locale].items():
        relative = Path('SpriteImage') / locale / name
        if expected.setdefault(relative, digest) != digest:
            raise ValueError(f'Conflicting pinned sprite: {relative}')
    for relative, digest in expected.items():
        path = (client / relative).resolve(strict=True)
        if not path.is_relative_to(client) or sha(path) != digest:
            raise ValueError(f'Changed stock locale input: {relative}')
    return client, expected


def neutralb_npc_inputs(client):
    manifest = json.loads((ROOT / 'inventory/client455-live-resource-inputs.json').read_text(encoding='utf-8'))
    selected = {name.casefold() for name in NEUTRALB_NPC_INPUTS}
    expected = {}
    for row in manifest['inputs']:
        relative = Path(row['relative'])
        if relative.as_posix().casefold() not in selected:
            continue
        path = (client / relative).resolve(strict=True)
        if (not path.is_relative_to(client) or path != Path(row['original']).resolve(strict=True)
                or sha(path) != row['sha256'] or path.stat().st_size != row['bytes']):
            raise ValueError(f'Changed NeutralB NPC input: {relative}')
        if relative in expected and expected[relative] != row['sha256']:
            raise ValueError(f'Conflicting NeutralB NPC input: {relative}')
        expected[relative] = row['sha256']
    if {path.as_posix().casefold() for path in expected} != selected:
        raise ValueError('Missing pinned NeutralB NPC resource dependency')
    return expected


def set_locale(config_file, locale):
    value, _ = LOCALES[locale]
    original = config_file.read_bytes()
    lines = original.splitlines(keepends=True)
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    setup_at = None
    in_setup = found = False
    for index, line in enumerate(lines):
        content = line.rstrip(b'\r\n')
        header = content.removeprefix(b'\xef\xbb\xbf') if index == 0 else content
        section = re.match(rb'^[ \t]*\[([^\]]+)\]', header)
        if section:
            in_setup = section[1].lower() == b'setup'
            if in_setup and setup_at is None:
                setup_at = index
            continue
        if in_setup:
            language = re.fullmatch(rb'([ \t]*language[ \t]*=[ \t]*)([^;]*?)([ \t]*(?:;.*)?)',
                                    content, re.IGNORECASE)
            if language:
                lines[index] = language[1] + value + language[3] + line[len(content):]
                found = True
    if not found:
        setting = b'Language=' + value + newline
        if setup_at is None:
            if lines and not lines[-1].endswith((b'\r', b'\n')):
                lines[-1] += newline
            lines.extend((b'[Setup]' + newline, setting))
        else:
            if not lines[setup_at].endswith((b'\r', b'\n')):
                lines[setup_at] += newline
            lines.insert(setup_at + 1, setting)

    updated = b''.join(lines)
    if updated != original:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=config_file.parent, prefix='R3Engine.ini.', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(updated)
            os.replace(temporary, config_file)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def populate(run, source, active, inputs, audio=False):
    linked = copied = 0
    run.mkdir(exist_ok=True, parents=True)
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
        existing_settings = config_file.exists()
        original = (config_file if existing_settings else source / config_file.name).read_bytes()
        client = Path(json.loads((ROOT / 'config/paths.json').read_text())['client_455'])
        copy_lobby_audio(client, run)
        configured = original.replace(b'Sound=FALSE', b'Sound=TRUE').replace(b'Music=FALSE', b'Music=TRUE')
        if not existing_settings:
            newline = b'\r\n' if b'\r\n' in configured else b'\n'
            configured += b'SoundVol=0.65' + newline + b'MusicVol=0.45' + newline
        if not existing_settings or configured != original:
            config_file.write_bytes(configured)
    config = config_file.read_bytes().splitlines()
    if not {b'ScreenXSize=1920', b'ScreenYSize=1080', b'bFullScreen=FALSE'}.issubset(config):
        raise ValueError('Expected a 1920×1080 windowed configuration')
    return {'sha256': active['sha256'], 'entry_rva': active['entry_rva'], 'architecture': active['architecture'],
            'staged_executable': (run / 'RF_Online.bin').relative_to(ROOT).as_posix(),
            'linked_assets': linked, 'copied_input_bytes': copied}


def test_session(credentials_base64, nation=7):
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
    return marshal_v4x(account, identifier, key, nation=nation)


def game_window(pid, full_hd=True):
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
                if not full_hd or (bounds.right, bounds.bottom) == (1920, 1080):
                    found.append(hwnd)
        return True

    user32.EnumWindows(inspect, 0)
    return found[0] if found else None


@contextmanager
def launch_lock(run):
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.ReleaseMutex.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    scope = hashlib.sha256(os.path.normcase(str(run.resolve())).encode('utf-8')).hexdigest()[:16]
    ctypes.set_last_error(0)
    handle = kernel.CreateMutexW(None, True, 'Local\\RFOnline455Preview-' + scope)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    existing = ctypes.get_last_error() == 183  # ERROR_ALREADY_EXISTS
    try:
        if existing:
            raise RuntimeError('Another test client launcher is active')
        yield
    finally:
        if not existing:
            kernel.ReleaseMutex(handle)
        kernel.CloseHandle(handle)


def owned_process_running(pid, executable):
    if not isinstance(pid, int) or pid <= 0:
        return False
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                ctypes.POINTER(wintypes.DWORD))
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = kernel.OpenProcess(0x00101000, False, pid)  # SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return False
    try:
        if kernel.WaitForSingleObject(handle, 0) != 258:  # WAIT_TIMEOUT, still running
            return False
        path = ctypes.create_unicode_buffer(32768)
        length = wintypes.DWORD(len(path))
        if not kernel.QueryFullProcessImageNameW(handle, 0, path, ctypes.byref(length)):
            return False
        return os.path.normcase(path.value) == os.path.normcase(str(executable.resolve()))
    finally:
        kernel.CloseHandle(handle)


def remove_private_handoff(path, identity):
    if identity is None:
        return
    try:
        if os.path.samestat(identity, path.stat()):
            path.unlink()
    except FileNotFoundError:
        pass


def create_private_handoff(path, payload):
    identity = None
    written = False
    try:
        with path.open('xb') as stream:
            identity = os.fstat(stream.fileno())
            stream.write(payload)
        written = True
        return identity
    finally:
        if not written:
            remove_private_handoff(path, identity)


def recorded_pid(trace):
    try:
        with trace.open('rb') as stream:
            first = stream.readline(4096)
    except (FileNotFoundError, PermissionError):
        return None
    if not first.endswith(b'\n'):
        return None
    event = json.loads(first)
    if event.get('kind') == 'create_error':
        return None
    pid = event.get('pid')
    if event.get('kind') != 'created' or not isinstance(pid, int) or pid <= 0:
        raise ValueError('Unexpected crash recorder creation event')
    return pid


def recorded_outcome(trace):
    outcome = {}
    if trace.is_file():
        with trace.open('rb') as stream:
            for line in stream:
                if not line.endswith(b'\n'):
                    break
                event = json.loads(line)
                if event.get('kind') == 'exit':
                    outcome['client_exit'] = event['code']
                elif event.get('kind') == 'exception' and event.get('first_chance') == 0:
                    outcome['fatal_exception'] = event['code']
    return outcome


def record_crash(run, evidence, receipt, handoff, payload, env):
    identity = create_private_handoff(handoff, payload)
    del payload
    try:
        CRASH_TRACE.parent.mkdir(exist_ok=True, parents=True)
        CRASH_TRACE.unlink(missing_ok=True)
        env['RF455_OBSERVE_PROTOCOL'] = '1'
        recorder = subprocess.Popen(
            [str(CRASH_RECORDER), str(ROOT / evidence['staged_executable']), str(CRASH_TRACE), '--record-crash'],
            cwd=run, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
        evidence['recorder_pid'] = recorder.pid
        evidence['crash_trace'] = CRASH_TRACE.relative_to(ROOT).as_posix()
        print(f'Crash trace: {CRASH_TRACE}', flush=True)
        receipt.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')

        deadline = time.monotonic() + 45
        warned = False
        pid = None
        while True:
            if pid is None:
                pid = recorded_pid(CRASH_TRACE)
                if pid:
                    evidence['pid'] = pid
                    receipt.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
            if pid and game_window(pid):
                evidence['client_size'] = (1920, 1080)
                remove_private_handoff(handoff, identity)
                identity = None
                evidence['private_handoff_removed'] = not handoff.exists()
                receipt.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
                print('Full HD client ready. Play normally, then close the client when finished.', flush=True)
                result = recorder.wait()
                break
            if pid and identity is not None and game_window(pid, full_hd=False):
                remove_private_handoff(handoff, identity)
                identity = None
            result = recorder.poll()
            if result is not None:
                # The child may have written its creation event just before exiting.
                if pid is None and (pid := recorded_pid(CRASH_TRACE)):
                    evidence['pid'] = pid
                break
            if not warned and time.monotonic() >= deadline:
                warned = True
                print('Full HD window not confirmed after 45 seconds. Recording remains active.', flush=True)
            time.sleep(0.1)

        evidence['recorder_exit'] = result
        evidence.update(recorded_outcome(CRASH_TRACE))
        if result:
            raise RuntimeError(f'Test client recorder exited with code {result:#010x}. Trace: {CRASH_TRACE}')
        if 'client_exit' not in evidence:
            raise RuntimeError(f'The recorder did not observe the client exit. Trace: {CRASH_TRACE}')
        failure = evidence.get('fatal_exception')
        if not failure and int(evidence['client_exit'], 16) != 0:
            failure = evidence['client_exit']
        if failure:
            raise RuntimeError(f'Test client stopped with code {failure}. Trace: {CRASH_TRACE}')
        print(f'Client closed. Trace saved to {CRASH_TRACE}', flush=True)
    finally:
        remove_private_handoff(handoff, identity)
        evidence['private_handoff_removed'] = not handoff.exists()
        receipt.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true', help='Wait for startup screenshots, then close this run')
    parser.add_argument('--audio', action='store_true', help='Enable sound and music in the test copy')
    parser.add_argument('--flight', action='store_true', help='Verify the flight to character selection')
    parser.add_argument('--all-slots', action='store_true', help='Capture all three real selection cameras; no character mutation')
    parser.add_argument('--measure-seconds',type=int,default=0,help='Keep main menu open for 0..30 seconds before the verified flight; collect GPU/FPS samples')
    parser.add_argument('--driver-name-check',action='store_true',help='Diagnostic A/B: run the identical binary as RF_Online.exe in the same runtime')
    parser.add_argument('--natural', action='store_true', help='Let the intro finish before checking for the menu')
    parser.add_argument('--credentials-base64', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--current-build', action='store_true', help='Use current own binary with verified Russian resource inputs for manual testing')
    parser.add_argument('--locale', choices=LOCALES, default='ru-ru', help='Client resource locale (default: ru-ru)')
    parser.add_argument('--enhanced-graphics', '--enhanced-lobby', dest='enhanced_graphics', action='store_true', help='Enable integrated lobby and actor lighting in the full playable client')
    parser.add_argument('--check-inputs', action='store_true', help='Validate launch inputs without logging in or launching the game')
    parser.add_argument('--record-crash', action='store_true', help='Keep a passive crash trace until the manually played client exits')
    parser.add_argument('--capture-frame', action='store_true',
                        help='Allow one on-demand world frame at a time in the recorded test runtime')
    args = parser.parse_args()
    if args.natural and not args.verify:
        parser.error('--natural requires --verify')
    if args.flight and not (args.audio and args.verify and not args.natural):
        parser.error('--flight requires --audio --verify without --natural')
    if args.all_slots and not args.flight:parser.error('--all-slots requires --flight')
    if not 0<=args.measure_seconds<=30 or (args.measure_seconds and not args.flight):parser.error('--measure-seconds requires --flight and 0..30')
    if args.driver_name_check and not (args.current_build and args.verify and args.measure_seconds):parser.error('--driver-name-check requires current build and measured verification')
    if args.record_crash and (args.verify or args.check_inputs):
        parser.error('--record-crash requires a manual launch')
    if args.capture_frame and not args.record_crash:
        parser.error('--capture-frame requires --record-crash')
    if args.record_crash and not CRASH_RECORDER.is_file():
        raise FileNotFoundError(f'Missing crash recorder: {CRASH_RECORDER}')
    parent, source, active, inputs = stage(args.current_build or args.check_inputs)
    client, localized = locale_inputs(args.locale)
    resources = neutralb_npc_inputs(client)
    if args.check_inputs:
        print(json.dumps({'status': 'PASS', 'scope': 'Launch inputs only; no server login or game run',
                          'locale': args.locale, 'inputs': len(inputs.keys() | localized.keys() | resources.keys()),
                          'locale_additions': len(localized), 'neutralb_npc_inputs': len(resources),
                          'build': active['sha256']}))
        return
    with launch_lock(parent):
        launch(args, parent, source, active, inputs, client, localized, resources)


def launch(args, run, source, active, inputs, client, localized, resources):
    previous = run / ('manual-launch.json' if args.verify else 'interactive-launch.json')
    handoff = run / 'System/DefaultSet.tmp'
    for receipt in (run / 'manual-launch.json', run / 'interactive-launch.json'):
        if receipt.is_file():
            prior = json.loads(receipt.read_text(encoding='utf-8'))
            executable = ROOT / prior.get('staged_executable', run / 'RF_Online.bin')
            if (owned_process_running(prior.get('pid'), executable) or
                owned_process_running(prior.get('recorder_pid'), CRASH_RECORDER)):
                raise RuntimeError('The preceding test client is still open')
    if handoff.exists():
        raise RuntimeError('A launcher handoff already exists in the test runtime')
    evidence = populate(run, source, active, inputs, audio=args.audio)
    for relative, digest in localized.items():
        stage_asset(client / relative, run / relative, expected=digest)
    for relative, digest in resources.items():
        stage_asset(client / relative, run / relative, expected=digest)
    evidence['neutralb_npc_inputs'] = {path.as_posix(): digest for path, digest in resources.items()}
    evidence['locale'] = args.locale
    evidence['orbit_assets'] = stage_orbit_assets(run)
    evidence['material_assets'] = stage_material_assets(run)
    if args.driver_name_check:
        alternate=run/'RF_Online.exe'
        if alternate.exists():raise ValueError('Driver-name diagnostic target already exists; inspect before replacing it')
        shutil.copyfile(ROOT/evidence['staged_executable'],alternate)
        if sha(alternate)!=evidence['sha256']:raise ValueError('Driver-name A/B binary mismatch')
        evidence['staged_executable']=alternate.relative_to(ROOT).as_posix()
        evidence['driver_name_check']=True
    if args.enhanced_graphics:
        config_file = run / 'R3Engine.ini'
        lines = config_file.read_text(encoding='ascii').splitlines()
        lines = [line for line in lines if not line.partition('=')[0].strip().lower() in ('lobbypost', 'enhancedactorlighting')]
        section = next((i for i, line in enumerate(lines) if line.strip().lower() == '[renderstate]'), None)
        if section is None:
            raise ValueError('RenderState section is required for enhanced lobby')
        lines.insert(section + 1, 'LobbyPost=1')
        lines.insert(section + 2, 'EnhancedActorLighting=1')
        config_file.write_text('\n'.join(lines) + '\n', encoding='ascii')
        evidence['enhanced_graphics'] = True
    set_locale(run / 'R3Engine.ini', args.locale)
    payload = test_session(args.credentials_base64, LOCALES[args.locale][1])
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith('RF455_')}
    if args.record_crash:
        if args.capture_frame:
            for name in ('world-frame.request', 'world-frame.png'):
                (run / name).unlink(missing_ok=True)
            env['RF455_CAPTURE_FRAME_REQUEST'] = '1'
        record_crash(run, evidence, previous, handoff, payload, env)
        return
    if args.verify:
        env.update(RF455_CAPTURE_TITLE='1', RF455_CAPTURE_LOBBY_CAMERA='1')
    if args.all_slots:env.update(RF455_LOBBY_INSPECT_SLOTS='1',RF455_LOBBY_DIAGNOSTICS='1')
    if args.measure_seconds:env['RF455_LOBBY_DIAGNOSTICS']='1'
    captures = ['title-logo.png', 'title-prologue.png', 'lobby-camera-menu.png']
    if args.flight:
        captures += ['lobby-camera-flight.png', 'lobby-camera-selection.png']
    if args.all_slots:captures += [f'lobby-slot-{i}.png' for i in range(3)]
    preserved = run / 'natural-startup'
    if args.natural:
        preserved.mkdir(exist_ok=True)
        for frame in [*captures, 'title-logo-source.png', 'manual-launch.json']:
            existing = run / frame
            archive = preserved / ('previous-' + frame)
            if existing.is_file() and not archive.exists():
                shutil.copyfile(existing, archive)
    if args.verify:
        for frame in [*captures, 'title-logo-source.png','lobby-diagnostics.json','lobby-visual.json']:
            (run / frame).unlink(missing_ok=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.PostMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.SetForegroundWindow.argtypes = (wintypes.HWND,)
    tick_ms = ctypes.windll.kernel32.GetTickCount64
    tick_ms.restype = ctypes.c_uint64
    game = None
    audio_meter = None
    complete = False
    identity = None
    started_launch = False
    try:
        identity = create_private_handoff(handoff, payload)
        started_launch = True
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
        deadline = started + (360 if args.natural else 120 if args.all_slots else 45 + args.measure_seconds)
        evidence['captures'] = {}
        evidence['capture_seconds'] = {}
        evidence['started_tick_ms'] = tick_ms()
        evidence['natural_mode'] = args.natural
        evidence['performance_samples']=[];last_measurement=0
        while time.monotonic() < deadline:
            if game.poll() is not None:
                raise RuntimeError(f'Test client exited during startup ({game.returncode})')
            if hwnd := game_window(game.pid):
                evidence['client_size'] = (1920, 1080)
                # WinMain reads the launcher handoff before creating the window.
                remove_private_handoff(handoff, identity)
                identity = None
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
                            if args.measure_seconds:
                                evidence['foreground_requested'] = bool(user32.SetForegroundWindow(hwnd))
                        if frame == 'lobby-camera-selection.png':
                            evidence['selection_tick_ms'] = tick_ms()
                        print(f'{frame} at {evidence["capture_seconds"][frame]} s', flush=True)
                    except OSError:
                        continue
                if args.flight and evidence.get('menu_tick_ms') and not evidence.get('start_tick_ms'):
                    if tick_ms() - evidence['menu_tick_ms'] >= max(2200,args.measure_seconds*1000):
                        if not user32.PostMessageW(hwnd, 0x0100, 0x0d, 1):
                            raise RuntimeError('Could not start the flight from menu')
                        user32.PostMessageW(hwnd, 0x0101, 0x0d, 0xc0000001)
                        evidence['start_tick_ms'] = tick_ms()
                if args.measure_seconds and time.monotonic()-last_measurement>=1:
                    last_measurement=time.monotonic()
                    try:
                        sample=json.loads((run/'lobby-diagnostics.json').read_text())
                        sample['elapsed_seconds']=round(time.monotonic()-started,2)
                        sample['foreground'] = user32.GetForegroundWindow() == hwnd
                        visual=json.loads((run/'lobby-visual.json').read_text())
                        sample['camera_view']=visual.get('camera_view',[])
                        sample['stage']='selection' if evidence.get('selection_tick_ms') else 'flight' if evidence.get('start_tick_ms') else 'menu' if evidence.get('menu_tick_ms') else 'startup'
                        evidence['performance_samples'].append(sample)
                    except (OSError,ValueError):pass
                if len(evidence['captures']) == len(captures):
                    if audio_meter:
                        time.sleep(2.0)
                    break
            time.sleep(0.1)
        else:
            raise RuntimeError('Startup did not produce the expected Full HD window or frames')
        complete = True
    finally:
        remove_private_handoff(handoff, identity)
        evidence['private_handoff_removed'] = not handoff.exists()
        evidence['reached_lobby'] = complete if args.verify else None
        if game and (args.verify or not complete) and game.poll() is None:
            game.terminate()
            game.wait(timeout=10)
        if args.driver_name_check and alternate.is_file() and sha(alternate)==evidence['sha256']:
            alternate.unlink()
        if audio_meter and audio_meter.poll() is None:
            audio_meter.terminate()
            audio_meter.wait(timeout=5)
        if started_launch and args.natural:
            for frame in evidence.get('captures', {}):
                shutil.copyfile(run / frame, preserved / frame)
                prior = preserved / ('previous-' + frame)
                if prior.is_file():
                    shutil.copyfile(prior, run / frame)
            (preserved / 'manual-launch.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
            prior = preserved / 'previous-manual-launch.json'
            if prior.is_file():
                previous.write_bytes(prior.read_bytes())
        elif started_launch:
            previous.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    summary=dict(evidence);summary.pop('performance_samples',None)
    summary['performance_sample_count']=len(evidence.get('performance_samples',[]))
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
