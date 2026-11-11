"""Pin 455 monster animation keys and verify a bounded ordinary-client frame sequence."""

import collections
import itertools
import json
import struct
from pathlib import Path

from audit_client455_language import decode
from audit_client455_resource_catalog import catalog, cstring
from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/monster189'
RAW = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
BASE = 0x400000
MONSTER_VTABLE = 0xaaa504
SLOTS = {24: 0x459dd0, 28: 0x459e00, 336: 0x45a1e0, 340: 0x45a330,
         344: 0x45a390, 368: 0x458630}
CALLS = {0x45a37b: 0x43e510, 0x459ddf: 0x4574a0, 0x459e13: 0x457910,
         0x45797e: 0x923a40, 0x457994: 0x43cde0, 0x457590: 0x43cde0}
EXPECTED = {
    0: 'YOUNGFLEM_PEACESTAND_01_00.ANI', 0x10: 'YOUNGFLEM_PEACEWALK_01_00.ANI',
    0x1000: 'WING_PEACESTAND_01_00.ANI', 0x1010: 'WING_PEACEWALK_01_00.ANI',
}


def verify_catalog():
    original = read('resource-catalog-reference')['catalog']
    source = Path(original['original'])
    require(sha(source) == original['sha256'], 'Pinned Resource.edf')
    table = catalog(decode(source.read_bytes()))[1][2]
    names = {}
    for start in range(0, len(table['raw']), table['stride']):
        row = table['raw'][start:start + table['stride']]
        names[struct.unpack_from('<I', row)[0]] = cstring(row, 136, 64)
    require(all(names.get(key, '').upper() == name for key, name in EXPECTED.items())
            and not {0x100, 0x110}.intersection(names), 'Catalog selects both real models at 455 keys')
    staged = read('live-resource-inputs')
    rows = {entry['key']: entry['relative'] for entry in staged['selected_monster_animations']}
    require(all(Path(rows[key]).name.upper() == name for key, name in EXPECTED.items()),
            'Selected animations are staged from the catalog')
    return original['sha256'], names


def verify_reference():
    proof = verify_regions(RAW)
    session = json.loads(RAW.read_text())
    require(session['closed']['success'] and session['closed']['saved'], 'Closed own reference session')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for offset, target in SLOTS.items():
            require(read_va(binary, MONSTER_VTABLE + offset, 4) == struct.pack('<I', target),
                    f'Monster vtable slot {offset}')
        for site, target in CALLS.items():
            branch = read_va(binary, site, 5)
            require(branch[0] == 0xe8 and site + 5 + struct.unpack_from('<i', branch, 1)[0] == target,
                    f'Monster direct CALL at RVA {site - BASE:#x}')
        for site, shift in ((0x45a35d, 12), (0x45a369, 4), (0x45a3c0, 12), (0x45a406, 4)):
            require(read_va(binary, site, 3) == bytes((0xc1, 0xe0, shift)), 'Monster animation key shift')
    catalog_sha, names = verify_catalog()
    save('monster-animation-reference', dict(
        **proof, raw=record(RAW), scope='Normal monster animation key and selected draw/animation virtual paths.',
        mesh_key_shift=12, type_shift=4, catalog_sha256=catalog_sha,
        catalog_examples={hex(key): names[key] for key in EXPECTED},
        vtable_rva=hex(MONSTER_VTABLE - BASE), vtable_slots={k: hex(v - BASE) for k, v in SLOTS.items()}))
    return names


def observe_live(report, link, names, *, expect_screen_clip):
    live = json.loads(report.read_text())
    expected_link = json.loads(link.read_text())['executable']
    require(live['normal_link_sha256'] == sha(link) and live['executable'] == expected_link
            and sha(WS / live['staged_executable']) == expected_link['sha256'], 'Exact own world PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and live['live_server']['private_handoff_removed']
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events),
            'Clean ordinary monster run')
    debug = [row['value'] for row in events if row['kind'] == 'debug_string']
    lookup_prefix = 'RF455 Protocol:monster-animation-key:'
    lookups = collections.Counter(tuple(map(int, value[len(lookup_prefix):].split(':')))
                                 for value in debug if value.startswith(lookup_prefix))
    require(lookups[1, 0, 0x1000] > 0 and lookups[1, 1, 0x1010] > 0,
            'Production manager returned Wing stand and walk animations')
    require('RF455 Protocol:monster-move:1:0:14' in debug and
            any(value.startswith('RF455 Protocol:town-state:') for value in debug), 'Existing world routes still used')
    frame_prefix = 'RF455 MonsterFrame:'
    frames = []
    for value in debug:
        if not value.startswith(frame_prefix):
            continue
        index, elapsed, serial, mesh, animation, frame, result, size, *position = value[len(frame_prefix):].split(':')
        require(int(index) == len(frames) and result == '0' and size == '640x500'
                and int(animation) >> 12 == int(mesh) and int(animation) in names, 'Exact animation capture')
        if expect_screen_clip:
            x, y = map(float, position)
            require(-0.8 < x < 0.8 and -0.38 < y < 0.55, 'Capture inside screen bounds')
        image = live['monster_frames'][len(frames)]
        check(image)
        require(image['file'].endswith(f'/world-monster-{index}.png'), 'Frame ordering')
        frames.append(dict(image, elapsed_ms=int(elapsed), actor=int(serial), mesh=int(mesh),
                           animation=int(animation), animation_file=names[int(animation)], bone_frame=int(frame),
                           screen_clip=list(map(float, position))))
    require(len(frames) == len(live['monster_frames']) <= 3
            and len({frame['actor'] for frame in frames}) <= 1
            and all(after['elapsed_ms'] >= before['elapsed_ms'] + 150
                    for before, after in itertools.pairwise(frames)), 'Bounded same-actor sequence')
    advancing = any(a['animation'] == b['animation'] and a['bone_frame'] != b['bone_frame']
                    and a['sha256'] != b['sha256'] for a, b in itertools.combinations(frames, 2))
    return dict(executable=expected_link, frames=frames, advancing_animation=advancing,
                wing_stand_lookups=lookups[1, 0, 0x1000], wing_walk_lookups=lookups[1, 1, 0x1010])


def main():
    catalog_names = verify_reference()
    link = read('normal-link')
    digest = sha(path('normal-link'))
    first_report = PRIVATE / 'first-live.json'
    first_link = PRIVATE / 'first-link.json'
    baseline = observe_live(first_report, first_link, catalog_names, expect_screen_clip=False)
    require(baseline['advancing_animation'], 'Baseline animation advances across distinct backbuffer frames')
    observed = observe_live(LIVE, path('normal-link'), catalog_names, expect_screen_clip=True)
    symbols = ('?GetAnimationData_Normal@CMonster@@', '?GetAnimationData_Force@CMonster@@')
    own = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(symbols)}
    require(len(own) == len(symbols), 'Linked ordinary monster animation routes')
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'live-resource-inputs',
             'monster-animation-reference')
    fresh = {name: record(path(name)) for name in names}
    fresh.update({'monster-animation-live': record(LIVE), 'monster-animation-raw': record(RAW),
                  'baseline-monster-animation-live': record(first_report), 'baseline-link': record(first_link)})
    sources = ('scripts/client455_character_tables_port.py', 'scripts/client455_world_update_port.py',
               'scripts/native/client455_protocol_observation.h', 'scripts/native/client455_live_world_observation.inc',
               'scripts/probe_client455_device_startup.py', 'scripts/probe_client455_live_launcher.py',
               'scripts/prepare_client455_live_resources.py')
    save('monster-animation-checkpoint', dict(
        status='PARTIAL_LIVE_MONSTER_ANIMATION', scope='Production 455 monster keys on NeutralB and advancing animation in the baseline run.',
        normal_executable=link['executable'], normal_link_sha256=digest, own_symbols=own,
        fresh_evidence=fresh, runtime_login_report=record(LIVE), script=record(Path(__file__)),
        sources=[record(WS / source) for source in sources], baseline_capture=baseline,
        current_capture=observed, full_455_animation_match=False,
        server_modified=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
