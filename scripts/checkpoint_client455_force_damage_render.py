"""Validate the ordinary Force damage text, Prism Beam resource and sound path."""

import hashlib
import json
import re
import struct
from pathlib import Path

from PIL import Image

from build_client455_x87_math import read_va
from checkpoint_client455_combat_result_effect import stage_inputs
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_monster_force_result import verify_live
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_asset_staging import stage_asset
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS, pe
from rpk455 import Rpk


PRIVATE = WS / 'artifacts/client455-progress/damage198'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
FORCE_INPUTS = {
    'Effect/EffectEntity23.rpk': '2e95d388dc5ed07c13170a6761cd4490b5345c14c215c872222fe09e40f5d642',
    'Snd/Force/PrismBeam/PrismBeam_02.WAV': '5de7f72727b56a79d36f66713ee0c4e4a288e23abb3e0f57c0c682b45fe82938',
    'Effect/EffectEntityList.spt': '87b5a829c4114bc913d1fbef431cebe5de37c332ddd59e919dddb7bc3b178759',
    'Effect/MagicSptList.spt': '71ee31d6993c3735ee68c7fddf759687e86445388e8d18ea9014d1ca31cfb650',
}
PRISM = b'force\\prismbeam\\d\\pri_d01.spt'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {0x7ef83c: 0x7dca10, 0x7ef862: 0x7e6ed0, 0x7ef8b8: 0x8b4cd0,
             0x7ef8ec: 0x7dbd50, 0x7ef913: 0x7f0560, 0x7ef940: 0x7f0560,
             0x7dca73: 0x43bfb0, 0x7d36f0: 0x43bfe0, 0x7f0583: 0x7d8ff0}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed Force renderer call at ' + hex(site))
        require(read_va(binary, 0xaed82c, 8) == b'damage2\0', 'Confirmed damage dummy name')
    words = read('combat-result-effect-reference')
    check(words['raw'])
    glyph = json.loads((WS / words['raw']['file']).read_text())['details']['0x7e50c0']['code']
    require('a4 % 2' in glyph and '(a4 >> 1)' in glyph, '455 numeric atlas layout')
    body = raw['details']['0x7ef770']['code']
    require('Buffer, 2, -1, 1.0, 1.0' in body and '0xB00FFFFF | 0x4F200000' in body,
            '455 Force numeric style and magic mask')
    save('force-damage-render-reference', dict(
        **proof, raw=record(REFERENCE), scope='Force damage renderer, position and Prism Beam effect dispatch.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        text_style=2, atlas_bank=0, atlas_row=1, damage_dummy=dict(name='damage2', reference_slot=8, source_slot=6),
        text_reference=record(path('combat-result-effect-reference')), prism_magic_id='0x4f22000e', prism_sound=9324))


def stage_force_inputs(run):
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    inputs = stage_inputs(run)
    for relative, digest in FORCE_INPUTS.items():
        source, dest = client / relative, run / relative
        stage_asset(source, dest, digest)
        inputs.append(dict(**record(dest), original=str(source)))
    archive = Rpk((run / 'Effect/EffectEntity23.rpk').read_bytes())
    script = archive.read(PRISM)
    magic_manifest = (run / 'Effect/MagicSptList.spt').read_bytes()
    magic_path = re.findall(rb'^0x4f22000e\s+(\S+)', magic_manifest, re.I | re.M)
    require(len(magic_path) == 1 and magic_path[0].lower().lstrip(b'\\') == PRISM, 'Actual Prism Beam script key')
    entity_manifest = (run / 'Effect/EffectEntityList.spt').read_bytes()
    ids = [int(value) for value in re.findall(rb'entity_id\s+(\d+)', script)]
    require(ids == [821, 822, 823] and re.search(rb'create_type\s+2', script), 'Actual Prism Beam tracks')
    for ident in ids:
        keys = re.findall(rb'^' + str(ident).encode() + rb'\s+(\S+)', entity_manifest, re.M)
        require(len(keys) == 1 and keys[0].lower().removeprefix(b'.\\effect\\') in archive.files,
                'Actual Prism Beam track asset')
    sounds = (run / 'Snd/WaveList.spt').read_bytes()
    require(re.search(rb'^9324\s+\.\\Snd\\Force\\PrismBeam\\PrismBeam_02\.WAV\b', sounds, re.M),
            'Actual Prism Beam sound key')
    return inputs, dict(member=PRISM.decode(), sha256=hashlib.sha256(script).hexdigest(), tracks=ids)


def inspect_damage_frames(run, native):
    frames = []
    for index, name in enumerate(('damage-first', 'damage-final')):
        raw = run / (name + '.bgra')
        body = raw.read_bytes()
        require(len(body) == 640 * 480 * 4, 'Complete damage frame')
        frame = Image.frombytes('RGB', (640, 480), body, 'raw', 'BGRX')
        rgb = frame.tobytes()
        changed = [pixel for pixel in zip(rgb[::3], rgb[1::3], rgb[2::3]) if pixel != (16, 32, 48)]
        blue = sum(b > r + 32 and b > g + 32 for r, g, b in changed)
        require(len(changed) == native['pixels'][index] and blue > 500, '455 blue atlas digits')
        preview = PRIVATE / (name + '.png')
        frame.save(preview)
        frames.append(dict(amount=native['damage'][index], raw=record(raw), preview=record(preview), blue=blue))
    require(frames[0]['raw']['sha256'] != frames[1]['raw']['sha256'], 'Two different damage frames')
    return frames


def verify_component():
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('force-damage-render', source)
    inputs, prism = stage_force_inputs(exe.parent)
    files, _, clips = resource_inputs(exe.parent)
    native, console = run_fixture(exe, files, ['--damage-render'], 'force-damage-render')
    require(native['status'] == 'PASS' and sum(native['damage']) == 70000 and native['tracks'] == [3, 3] and
            native['magic_id'] == '0x4f22000e' and native['sound_id'] == 9324 and native['expired_pixels'] == 0,
            'Force render, particle activation, expiry and sound')
    block, block_console = run_fixture(exe, files, ['--block-render'], 'block-render')
    require(block == read('combat-result-effect-checkpoint')['native'], 'BLOCK and MISS regression')
    return dict(native=native, console=console, frames=inspect_damage_frames(exe.parent, native),
                inputs=inputs, prism=prism, real_clips=clips, source=record(source),
                regression=dict(block=block, console=block_console),
                probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']})


def main():
    verify_reference()
    component = verify_component()
    link = read('normal-link')
    live = verify_live(link, LIVE)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'force-damage-render-reference',
             'skill-force-items-reference', 'tagged-audio-reference', 'live-resource-inputs', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['force-damage-render-live'] = record(LIVE)
    owners = ('?EFUtil_RenderStringMoveOut@@', '?ExtractEffectInfo@CAllEffectInfo@@',
              '?EFUTIL_GetPosType@@', '?RF455_PlayActorEffectSound@@')
    symbols = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(owners)}
    require(len(symbols) == len(owners), 'Ordinary Force renderer and position/audio owners linked')
    sources = ('scripts/client455_combat_result_effect_port.py', 'scripts/native/client455_combat_result_effect_probe.inc',
               'scripts/native/client455_effect_positions.h')
    save('force-damage-render-checkpoint', dict(
        **component, status='PARTIAL_COMPONENT_FORCE_DAMAGE_RENDER',
        scope='Ordinary Force hit renders damage numbers and activates stock Prism Beam tracks and audio.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live, script=record(Path(__file__)),
        sources=[record(WS / name) for name in sources], own_symbols=symbols, M6='OPEN', M9='OPEN'))
    print(json.dumps(component['native']))


if __name__ == '__main__':
    main()
