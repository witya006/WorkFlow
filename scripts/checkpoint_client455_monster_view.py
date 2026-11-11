"""Verify a clear ordinary-client frame series after the NeutralB camera drag."""

import json
import math
from pathlib import Path

from PIL import Image

from checkpoint_client455_monster_animation import observe_live, verify_catalog
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import require, sha
from checkpoint_client455_world_observation import sample_values
from client455_ui_checkpoint import record
from compare_client_binaries import WS


LIVE = WS / 'artifacts/client455-progress/monster190/live.json'


def main():
    _, names = verify_catalog()
    link = read('normal-link')
    observation = observe_live(LIVE, path('normal-link'), names, expect_screen_clip=True)
    frames = observation['frames']
    require(len(frames) == 3 and observation['advancing_animation'], 'Three frames of one advancing clip')
    require({frame['animation'] for frame in frames} == {0}
            and frames[0]['elapsed_ms'] >= 1200, 'Youngflem stand series after the drag')
    require(all(a['bone_frame'] < b['bone_frame'] for a, b in zip(frames, frames[1:])),
            'Standing clip advances in all three samples')
    for frame in frames:
        with Image.open(WS / frame['file']) as png:
            require(png.format == 'PNG' and png.size == (640, 500), 'Full frame from the normal renderer')

    live = json.loads(LIVE.read_text())
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [event['value'] for event in events if event['kind'] == 'debug_string']
    accepted = messages.index('RF455 Protocol:position-mode:0:0:0')
    require(messages.index('RF455 Protocol:map-bsp:0:1:0') < accepted, 'Actual NeutralB world')
    steps = messages[accepted + 1:]
    drag = [list(map(int, value.split(':')[2:])) for value in steps
            if value.startswith('RF455 Protocol:camera-mouse:')]
    require(drag == [[1, 420, 0], [2, 420, 4], [3, 280, 4], [4, 280, 32]],
            'One short right drag through the ordinary mouse handler')
    samples = [sample_values(value) for value in steps if value.startswith('RF455 WorldSample:')]
    require(len(samples) == 6 and [row['index'] for row in samples] == list(range(6)),
            'Complete bounded world sample sequence')
    before, after = samples[:2]
    initial, yaw, distance = before['yaw_pitch_distance']
    expected = initial + (280 - 420) * (640 / 1024) * 0.4 / 2
    require(all(math.isclose(row['yaw_pitch_distance'][0], expected, abs_tol=1e-4)
                and row['yaw_pitch_distance'][1:] == [yaw, distance] for row in samples[1:])
            and after['elapsed_ms'] < frames[0]['elapsed_ms'], 'New elevation persists through capture')

    fresh = {name: record(path(name)) for name in (
        'normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
        'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'live-resource-inputs',
        'monster-animation-reference')}
    fresh['monster-view-live'] = record(LIVE)
    sources = ('native/client455_camera_mouse_observation.inc', 'native/client455_live_world_observation.inc',
               'client455_camera_input_port.py', 'client455_world_update_port.py',
               'checkpoint_client455_monster_animation.py')
    save('monster-view-checkpoint', dict(
        status='PARTIAL_LIVE_MONSTER_STAND_FRAMES',
        scope='Visible Youngflem standing animation on NeutralB after one bounded camera drag.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        fresh_evidence=fresh, runtime_login_report=record(LIVE), script=record(Path(__file__)),
        sources=[record(WS / 'scripts' / name) for name in sources], camera_elevation=[initial, expected],
        frames=frames, wing_stand_lookups=observation['wing_stand_lookups'],
        wing_walk_lookups=observation['wing_walk_lookups'], full_455_animation_match=False,
        M6='OPEN', M9='OPEN'))
    print(f'PASS: elevation {initial:g} -> {expected:g}, standing clip ticks '
          f'{[frame["bone_frame"] for frame in frames]}')


if __name__ == '__main__':
    main()
