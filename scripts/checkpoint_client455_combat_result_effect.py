"""Validate the monster result path through the ordinary effect queue, atlas and sound."""

import json
import struct
from pathlib import Path

from PIL import Image

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_monster_force_result import verify_live
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import require, sha
from client455_asset_staging import stage_asset
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_runtime_inputs import copy_tagged_sound_providers
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS, pe


PRIVATE = WS / 'artifacts/client455-progress/block197'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
ATLAS = 'Effect/effectfont.dds'
BLOCK_SOUNDS = ('Snd/Critical/block_00.wav', 'Snd/Critical/block_01.wav')
INPUTS = {
    ATLAS: 'db8d1c5f1b14e812563c21e206e71f58987fa697f150e24dc1733edb447cf7a8',
    'Snd/WaveList.spt': 'ecc7c9baac15fba51e4338c9d45a48394126741de4b95472a0b11e787e629f8a',
    'mss32.dll': '441b290e7dc6334eb5023cd9b7937739298fdd66c104d4c96e5edcf642ae912d',
    BLOCK_SOUNDS[0]: '7086a2e58039330fbd61a0481963e7afbf99379f97b54dc1d82df1bc3e3169ff',
    BLOCK_SOUNDS[1]: '54bbbb39c2d032f54bf09e309575cca9ef3ba62cbef87780a6ce2b66c139ca3b',
}


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {0x7f0efd: 0x7ec840, 0x7f0ea7: 0x7ec7e0, 0x7ec86c: 0x7dbd50,
             0x7ec8ae: 0x7e6ed0, 0x7e74ea: 0x7e50c0, 0x7e8d01: 0x4172a0,
             0x412c82: 0x417270}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed combat display call at ' + hex(site))
        require(read_va(binary, 0xaedefc, 6) == b'BLOCK\0', 'Confirmed atlas token')
        require(read_va(binary, 0xaaa540, 4) == struct.pack('<I', 0x7ce670), 'Monster object flag query')
    glyph = raw['details']['0x7e50c0']['code']
    require(all(token in glyph for token in ('0.17578125', '0.1953125', 'a3 * 90.0', 'a3 * 32.0')),
            'Confirmed block atlas rectangle')
    save('combat-result-effect-reference', dict(
        **proof, raw=record(REFERENCE), scope='Monster BLOCK and MISS atlas, time, sound and visibility.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        block_rect=[100, 96, 90, 32], atlas_size=[512, 256], block_sound_ids=[277093, 277094],
        lifetime=0.9, fade_start=0.45, elevation=5, cull_flags=['0x1000', '0x20000']))


def stage_inputs(run):
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    inputs = copy_tagged_sound_providers(run)
    for relative, digest in INPUTS.items():
        source, dest = client / relative, run / relative
        stage_asset(source, dest, digest)
        inputs.append(dict(**record(dest), original=str(source)))
    manifest = (run / 'Snd/WaveList.spt').read_bytes()
    for wave_id, relative in zip((277093, 277094), BLOCK_SOUNDS):
        rows = [line.split() for line in manifest.splitlines() if line.startswith(str(wave_id).encode() + b'\t')]
        require(rows == [[str(wave_id).encode(), b'.\\' + relative.replace('/', '\\').encode()]], 'Actual block sound manifest')
    config = run / 'R3Engine.ini'
    config.write_text('[Sound]\nSound=TRUE\nMusic=FALSE\n[Path]\nSoundPath=.\\Snd\\\n', encoding='ascii')
    return inputs + [record(config)]


def inspect_frames(run, native):
    frames = []
    for word in ('block', 'miss'):
        raw = run / (word + '.bgra')
        body = raw.read_bytes()
        require(len(body) == 640 * 480 * 4, 'Full Direct3D frame')
        frame = Image.frombytes('RGB', (640, 480), body, 'raw', 'BGRX')
        rgb = frame.tobytes()
        changed = [pixel for pixel in zip(rgb[::3], rgb[1::3], rgb[2::3]) if pixel != (16, 32, 48)]
        blue = sum(b > r + 32 and b > g + 32 for r, g, b in changed)
        warm = sum(r > b + 32 for r, g, b in changed)
        require(len(changed) == native[word + '_pixels'] and (blue if word == 'block' else warm) > 100,
                'Different rendered combat word and expected atlas colors')
        preview = PRIVATE / (word + '.png')
        frame.save(preview)
        frames.append(dict(word=word, raw=record(raw), preview=record(preview), blue=blue, warm=warm))
    return frames


def verify_component():
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('combat-result-effect', source)
    inputs = stage_inputs(exe.parent)
    files, _, clips = resource_inputs(exe.parent)
    native, console = run_fixture(exe, files, ['--block-render'], 'combat-result-effect')
    require(native['status'] == 'PASS' and native['real_block_sample'] and
            native['expired_pixels'] == native['clipped_pixels'] == 0, 'Combat render and sound')
    impact, impact_console = run_fixture(exe, files, ['--impact-effect'], 'force-impact')
    require(impact == read('monster-force-impact-checkpoint')['native'], 'Positive damage regression')
    return dict(native=native, console=console, frames=inspect_frames(exe.parent, native), inputs=inputs, real_clips=clips,
                regression=dict(impact=impact, console=impact_console), source=record(source),
                probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']})


def main():
    verify_reference()
    component = verify_component()
    link = read('normal-link')
    live = verify_live(link, LIVE)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'combat-result-effect-reference',
             'skill-force-items-reference', 'tagged-audio-reference', 'live-resource-inputs', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['combat-result-effect-live'] = record(LIVE)
    owners = ('?FrameMoveEffect@@', '?ExtractEffectInfo@CAllEffectInfo@@',
              '?EFUtil_RenderStringMoveOut@@', '?RF455_PlayActorEffectSound@@')
    symbols = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(owners)}
    require(len(symbols) == len(owners), 'Ordinary queue, atlas and audio owners linked')
    sources = ('scripts/client455_combat_result_effect_port.py', 'scripts/native/client455_combat_result_effect_probe.inc',
               'scripts/native/client455_equipment_effects.h', 'scripts/native/client455_player_owner.cpp')
    save('combat-result-effect-checkpoint', dict(
        **component, status='PARTIAL_COMPONENT_COMBAT_RESULT_RENDER',
        scope='Monster Force BLOCK and MISS render with the original atlas and BLOCK uses a real muted Miles sample.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live, script=record(Path(__file__)),
        sources=[record(WS / name) for name in sources], own_symbols=symbols, M6='OPEN', M9='OPEN'))
    print(json.dumps(component['native']))


if __name__ == '__main__':
    main()
