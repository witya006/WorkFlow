"""Bind the localized key path and live forward-input observation to pinned binaries."""
import hashlib
import json
import math
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from checkpoint_client455_world_observation import sample_values
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress'
BASE = 0x400000


def verify_reference(raw_path):
    raw = json.loads(raw_path.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session must close')
    pins = read('avatar-world-reference')['references']
    for pin in pins:
        check(pin)
    binaries = [(WS / pin['file']).read_bytes() for pin in pins]
    bounds = {row['query']: row['fn'] for row in raw['bounds']['result']}
    regions = []
    for body in raw['disassembly']:
        fn = bounds[body['addr']]
        address, size = int(fn['addr'], 16), int(fn['size'], 16)
        require(body['cursor']['done'] and body['instruction_count'] == body['total_instructions']
                and len(body['asm']['lines']) == body['total_instructions'], 'Incomplete IDA body')
        a, b = [read_va(binary, address, size) for binary in binaries]
        require(a == b and len(a) == size, 'Pinned reference function differs')
        regions.append(dict(rva=hex(address - BASE), bytes=size, instructions=body['total_instructions'],
                            sha256=hashlib.sha256(a).hexdigest()))
    require(len(regions) == 5, 'Expected localized paths and selector evidence')
    return [dict(file=p['file'], sha256=p['sha256'], architecture=p['architecture'],
                 image_base=p['image_base']) for p in pins], regions


def main():
    live_path = PRIVATE / 'client455-world-walk-live-taiwan-native.json'
    live = json.loads(live_path.read_text())
    link = read('normal-link')
    digest = sha(path('normal-link'))
    require(digest == live['normal_link_sha256'] and live['executable'] == link['executable']
            and sha(WS / live['staged_executable']) == link['executable']['sha256'], 'Exact live own PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [event['value'] for event in events if event['kind'] == 'debug_string']
    keymap = next(row for row in live['inputs'] if row['file'].lower().endswith('/zh-tw/keymap.dat'))
    check(keymap)
    require(sha(Path(keymap['original'])) == keymap['sha256'], 'Pinned localized KeyMap.dat')
    key_record = messages.index('RF455 Protocol:keymap:24:38:0')
    accepted = messages.index('RF455 Protocol:position-mode:0:0:0')
    require(key_record < accepted and messages.index('RF455 Protocol:map-bsp:0:1:0') < accepted,
            'Ordinary localized keymap and NeutralB before accepted position')
    steps = messages[accepted + 1:]
    down = next(v for v in steps if v.startswith('RF455 Protocol:walk-key-down:38:') and v.endswith(':1'))
    up = next(v for v in steps if v.startswith('RF455 Protocol:walk-key-up:38:') and v.endswith(':0'))
    require(steps.index(down) < steps.index('RF455 Protocol:move-queued:4:1:12') < steps.index(up)
            and 'RF455 Protocol:move-queued:4:12:6' in steps[steps.index(up) + 1:]
            and not any('walk-key-restore-failed' in v for v in steps), 'Move and stop queued after scoped input')
    samples = [sample_values(value) for value in steps if value.startswith('RF455 WorldSample:')]
    require([s['index'] for s in samples] == list(range(6)) and all(s['input_enabled'] for s in samples)
            and all(s['elapsed_ms'] >= t for s, t in zip(samples, (0, 1000, 3000, 4500, 6500, 8500))),
            'Expected world observations including two post-stop samples')
    start, held, *_, settled, final = samples
    displacement = math.dist(start['avatar_position'], final['avatar_position'])
    require(math.dist(start['avatar_position'], held['avatar_position']) > 2 and displacement > 2
            and settled['avatar_position'] == final['avatar_position']
            and start['avatar_action'] == settled['avatar_action'] == final['avatar_action']
            and held['avatar_action'] != start['avatar_action']
            and all(s['camera_anchor'] == s['avatar_position'] for s in samples),
            'Observed displacement, follow anchor and two stable late samples')
    require(len(live['world_frames']) == 2, 'Expected two rendered frames')
    for frame in live['world_frames']:
        check(frame)
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events)
            and live['live_server']['private_handoff_removed'], 'Own run stopped cleanly')
    raw_reference = PRIVATE / 'walk183-keymap-reference.json'
    pins, regions = verify_reference(raw_reference)
    evidence = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
                'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in evidence}
    fresh['world-walk-native'] = record(live_path)
    fresh['keymap-reference-raw'] = record(raw_reference)
    symbols = ('?LoadData@CInputProcessMgr@@', '?InputProcess_Keyboard@CInputProcessMgr@@',
               '?RequestMoveByKeyboard@CAvatar@@', '?PositionMsg_MoveRequest_clzo@CNetworkMgr@@')
    mapped = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(symbols)}
    require(len(mapped) == len(symbols), 'Expected four linked keyboard and movement methods')
    scope = ('Ordinary NeutralB avatar advances after scoped Win32 forward input, queues move and '
             'stop messages, then reaches a stable position while the camera anchor follows.')
    save('world-walk-checkpoint', dict(
        status='PASS_LIVE_FORWARD_MOVEMENT_AND_SETTLING', normal_executable=link['executable'],
        scope=scope, normal_link_sha256=digest, fresh_evidence=fresh, script=record(Path(__file__)),
        runtime_login_report=record(live_path),
        sources=[record(WS / 'scripts' / name) for name in
                 ('client455_initial_download_port.py', 'native/client455_protocol_observation.h',
                  'native/client455_walk_observation.inc', 'native/client455_live_world_observation.inc',
                  'probe_client455_device_startup.py', 'probe_client455_live_launcher.py')],
        references=pins, reference_regions=regions, keymap=keymap, own_symbols=mapped,
        samples=samples, forward_key='VK_UP', input_source='own game thread Win32 keyboard table',
        displacement=displacement, key_down=down, key_up=up, frames=live['world_frames'],
        movement_enqueued=sum(v == 'RF455 Protocol:move-queued:4:1:12' for v in steps),
        stop_enqueued=sum(v == 'RF455 Protocol:move-queued:4:12:6' for v in steps),
        matched_server_ack=False, physical_keyboard_verified=False, camera_rotation_verified=False,
        alternate_keymap_mode_verified=False, M6='OPEN', M9='OPEN'))
    print(f'PASS: live forward displacement {displacement:.2f}, two stable post-stop samples')


if __name__ == '__main__':
    main()
