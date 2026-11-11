"""Verify the passive NeutralB samples and backbuffer captures from the own PE."""
import json
import math
import struct

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


def sample_values(value):
    index, elapsed, action, enabled, avatar, anchor, view = value.split(':')[1:]

    def vector(text):
        values = list(map(float, text.split(',')))
        require(len(values) == 3 and all(map(math.isfinite, values)), 'Invalid world sample vector')
        return values

    require(enabled in ('0', '1'), 'Invalid input flag')
    return dict(index=int(index), elapsed_ms=int(elapsed), avatar_action=int(action),
                input_enabled=enabled == '1', avatar_position=vector(avatar),
                camera_anchor=vector(anchor), yaw_pitch_distance=vector(view))


def main():
    raw = WS / 'artifacts/client455-progress/client455-world-observation-live-taiwan-native.json'
    live = json.loads(raw.read_text())
    link = read('normal-link')
    staged = WS / live['staged_executable']
    link_sha = sha(path('normal-link'))
    require(link_sha == live['normal_link_sha256'] and link['executable'] == live['executable']
            and sha(staged) == link['executable']['sha256'],
            'Live samples must use the current own PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [row['value'] for row in events if row['kind'] == 'debug_string']
    markers = ['RF455 Protocol:map-bsp:0:1:0', 'RF455 Protocol:avatar-ready:0:0:0',
               'RF455 Protocol:tx:3:1:1', 'RF455 Protocol:rx:3:2:1', 'RF455 Protocol:position-mode:0:0:0']
    positions = [messages.index(marker) for marker in markers]
    require(positions == sorted(positions), 'Wrong order of initial NeutralB events')
    remaining = messages[positions[-1] + 1:]
    samples = [sample_values(value) for value in remaining if value.startswith('RF455 WorldSample:')]
    require([sample['index'] for sample in samples] == [0, 1, 2]
            and all(sample['elapsed_ms'] >= delay for sample, delay in zip(samples, (0, 1000, 3000))),
            'Missing passive samples after start-position acknowledgement')
    require(len(live['world_frames']) == 2, 'Expected early and settled captures')
    frames = []
    for index, frame in zip((0, 2), live['world_frames']):
        check(frame)
        data = (WS / frame['file']).read_bytes()
        require(data[:16] == b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR', 'Invalid PNG header')
        width, height = struct.unpack_from('>II', data, 16)
        require(f'RF455 WorldCapture:{index}:0:{width}x{height}' in remaining, 'Missing GPU capture evidence')
        frames.append(dict(frame, sample_index=index, width=width, height=height))
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and any(row['kind'] == 'selection_observation_end' for row in events)
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events)
            and live['live_server']['private_handoff_removed'], 'Live observation did not end cleanly')
    packets = [value.removeprefix('RF455 Protocol:rx:') for value in remaining
               if value.startswith('RF455 Protocol:rx:')]
    selected_symbols = ('?Render@CGP_MainGame@@', '?DrawMapRender@CLevel@@',
                        '?InputProcess_Mouse@CGP_MainGame@@', '?InputProcess_Keyboard@CInputProcessMgr@@')
    symbols = {symbol: hex(rva) for rva, symbol in own_symbols(link) if symbol.startswith(selected_symbols)}
    require(len(symbols) == len(selected_symbols), 'Expected own render and input RVAs')
    evidence = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
                'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in evidence}
    fresh['world-observation-native'] = record(raw)
    save('world-observation-checkpoint', dict(
        status='PASS_PASSIVE_OBSERVATION', normal_executable=link['executable'],
        normal_link_sha256=link_sha, source_report=record(raw), own_symbols=symbols,
        fresh_evidence=fresh,
        script=record(WS / 'scripts/checkpoint_client455_world_observation.py'),
        sources=[record(WS / 'scripts' / filename) for filename in
                 ('client455_initial_download_port.py', 'native/client455_live_world_observation.inc',
                  'native/client455_protocol_observation.h', 'probe_client455_device_startup.py',
                  'probe_client455_live_launcher.py')],
        start_mode=0, map='NeutralB', subsequent_packets=len(packets),
        received_3_16=sum(value.startswith('3:16:') for value in packets),
        samples=samples, frames=frames, movement_input_sent=False, movement_verified=False,
        camera_input_verified=False, world_visual_acceptance=False, M6='OPEN', M9='OPEN'))
    print(f'PASS: {len(samples)} passive samples, {len(frames)} frames, {len(packets)} subsequent replies')


if __name__ == '__main__':
    main()
