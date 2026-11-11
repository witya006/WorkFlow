"""Verify ordinary right-drag bounds and live world camera output."""
import json
import math
import struct
from pathlib import Path

from PIL import Image, ImageChops

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from checkpoint_client455_world_observation import sample_values
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress'
REFERENCE = PRIVATE / 'camera184-reference.json'


def reference():
    proof = verify_regions(REFERENCE)
    constants = {0xab0d80: ('<f', 89.0), 0xab0d88: ('<d', 89.0),
                 0xab0d90: ('<f', -89.0), 0xab0d98: ('<d', -89.0),
                 0xab0d70: ('<f', -35.0)}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for address, (fmt, value) in constants.items():
            require(read_va(binary, address, struct.calcsize(fmt)) == struct.pack(fmt, value),
                    'Camera bounds changed at RVA ' + hex(address - 0x400000))
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session must close')
    return dict(**proof, raw=record(REFERENCE), right_drag_bounds=[-89, 89],
                non_fps_free_target_lower_bound=-35, full_mouse_behavior_verified=False)


def main():
    live_path = PRIVATE / 'client455-world-camera-live-taiwan-native.json'
    live = json.loads(live_path.read_text())
    link = read('normal-link')
    digest = sha(path('normal-link'))
    require(digest == live['normal_link_sha256'] and live['executable'] == link['executable']
            and sha(WS / live['staged_executable']) == link['executable']['sha256'], 'Exact live own PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [event['value'] for event in events if event['kind'] == 'debug_string']
    accepted = messages.index('RF455 Protocol:position-mode:0:0:0')
    require(messages.index('RF455 Protocol:map-bsp:0:1:0') < accepted, 'Actual NeutralB BSP')
    steps = messages[accepted + 1:]
    drags = [list(map(int, event.split(':')[2:])) for event in steps
             if event.startswith('RF455 Protocol:camera-mouse:')]
    require(drags == [[gesture * 4 + stage, y, buttons] for gesture in range(3)
                      for stage, y, buttons in ((1, 420, 0), (2, 420, 4), (3, 74, 4), (4, 74, 32))],
            'Expected three full right drags')
    samples = [sample_values(value) for value in steps if value.startswith('RF455 WorldSample:')]
    require([s['index'] for s in samples] == [0, 1, 2] and all(s['input_enabled'] for s in samples)
            and all(s['elapsed_ms'] >= t for s, t in zip(samples, (0, 1800, 3400))),
            'Expected before, middle, and after camera samples')
    start, middle, end = samples
    require(all(s['avatar_position'] == start['avatar_position'] and s['camera_anchor'] == start['camera_anchor']
                and s['yaw_pitch_distance'][1:] == start['yaw_pitch_distance'][1:] for s in samples),
            'Only camera elevation should change')
    vertical = [s['yaw_pitch_distance'][0] for s in samples]
    expected = max(-89.0, start['yaw_pitch_distance'][0] + 3 * (74 - 420) * (640 / 1024) * 0.4 / 2)
    require(vertical[0] > vertical[1] > vertical[2] and math.isclose(vertical[2], expected, abs_tol=1e-4)
            and vertical[2] == -89.0, 'Live right drag must reach the confirmed lower bound')
    require(len(live['world_frames']) == 2, 'Expected pre- and post-drag frames')
    images = []
    for index, frame in zip((0, 2), live['world_frames']):
        check(frame)
        with Image.open(WS / frame['file']) as png:
            require(png.size == (640, 500) and f'RF455 WorldCapture:{index}:0:640x500' in steps,
                    'Expected comparable frames from D3D')
            images.append(png.convert('RGB').crop((32, 90, 460, 190)))
    changed = sum(pixel != (0, 0, 0) for pixel in ImageChops.difference(*images).get_flattened_data())
    require(changed > 30000, 'Camera change must be visible outside the HUD')
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and any(row['kind'] == 'selection_observation_end' for row in events)
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events)
            and live['live_server']['private_handoff_removed'], 'Own run stopped cleanly')
    save('world-camera-reference', reference())
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'world-camera-reference')
    fresh = {name: record(path(name)) for name in names}
    fresh['world-camera-native'] = record(live_path)
    fresh['world-camera-reference-raw'] = record(REFERENCE)
    mapped = {name: hex(rva) for rva, name in own_symbols(link)
              if name.startswith(('?InputProcess_Mouse@CGP_MainGame@@', '?Render@CCamera@@'))}
    require(len(mapped) == 2, 'Linked own camera methods')
    save('world-camera-checkpoint', dict(
        status='PASS_LIVE_RIGHT_DRAG_ELEVATION', normal_executable=link['executable'], normal_link_sha256=digest,
        scope='Ordinary NeutralB right drags lower the camera elevation parameter to the 455 clamp and change the rendered scene.',
        fresh_evidence=fresh, runtime_login_report=record(live_path), script=record(Path(__file__)),
        sources=[record(WS / 'scripts' / name) for name in
                 ('client455_camera_input_port.py', 'native/client455_camera_mouse_observation.inc',
                  'native/client455_protocol_observation.h', 'native/client455_live_world_observation.inc',
                  'probe_client455_device_startup.py', 'probe_client455_live_launcher.py')],
        own_symbols=mapped, samples=samples, right_drag_phases=drags, frames=live['world_frames'],
        changed_region_pixels=changed, physical_mouse_verified=False, horizontal_rotation_verified=False,
        full_camera_behavior_verified=False, M6='OPEN', M9='OPEN'))
    print(f'PASS: camera elevation {vertical}, {changed} changed pixels in the compared region')


if __name__ == '__main__':
    main()
