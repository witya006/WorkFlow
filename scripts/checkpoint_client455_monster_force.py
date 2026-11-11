"""Verify the monster Force selector against both pins and real Wing clips."""

import json
import struct
import subprocess
from pathlib import Path

from audit_client455_skill_force_items import decode, tables
from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS, pe


REFERENCE = WS / 'artifacts/client455-progress/monster191/reference.json'
LIVE = REFERENCE.with_name('live.json')
CASES = ((0, 7, False), (24, 1, True), (25, 1, False), (25, 0, True))


def verify_reference():
    proof = verify_regions(REFERENCE)
    session = json.loads(REFERENCE.read_text())
    require(session['closed']['success'] and session['closed']['saved'], 'Owned IDA session closed')
    calls = {0x45a3d2: 0x4638f0, 0x45a3e6: 0x463b50, 0x463ba8: 0x463780}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        require(read_va(binary, 0xaaa65c, 4) == struct.pack('<I', 0x45a390), 'Monster Force vtable slot')
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed direct call at ' + hex(site))
    save('monster-force-reference', dict(
        **proof, raw=record(REFERENCE), scope='Monster Force clip selection and active effect accessors.',
        selection_rva='0x5a390', actor_effect_item_offset=812, effect_count=7, effect_offset=144,
        effect_stride=40, attack_categories=[0, 4], first_effect_support_type=4))


def resource_inputs(run):
    data = read('skill-force-items-reference')['inputs']
    edf = [next(item for item in data if Path(item['file']).name == name)
           for name in ('base.edf', 'zh-tw.edf')]
    for item in edf:
        check(item)
    table = tables(decode((WS / edf[0]['file']).read_bytes()))[0][0]
    expected = []
    for index, level, attack in CASES:
        offset = index * table['stride']
        row = table['data'][offset:offset + table['stride']]
        categories = list(row[144:385:40])
        # The two pin branches test different bytes when the first slot is unset.
        kind = row[144 + level] if categories[0] != 255 else 255
        require(struct.unpack_from('<I', row)[0] == index and
                (bool(set(categories) & {0, 4}) and kind != 4) == attack, 'Independent Force row case')
        expected.append(dict(index=index, level=level, first_effect=kind, categories=categories, attack=attack))

    staging = read('live-resource-inputs')
    rows = [next(row for row in staging['selected_monster_animations'] if row['key'] == key)
            for key in (0x10c0, 0x10d0)]
    files = [WS / item['file'] for item in edf]
    extracted = []
    for row in rows:
        member = next(item for item in staging['members'] if item['relative'] == row['relative'])
        source = next(item for item in staging['inputs'] if item['relative'] == member['archive'])
        archive = Path(source['original'])
        require(sha(archive) == source['sha256'], 'Pinned Wing archive')
        body = archive.read_bytes()[member['offset']:member['offset'] + member['bytes']]
        require(len(body) == member['bytes'], 'Wing animation extent')
        clip = run / Path(row['relative']).name
        clip.write_bytes(body)
        files.append(clip)
        extracted.append(dict(**record(clip), key=row['key'], archive_sha256=source['sha256']))
    return files, expected, extracted


def verify_live(link):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable']
            and sha(WS / live['staged_executable']) == link['executable']['sha256'], 'Exact own NeutralB PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and live['live_server']['private_handoff_removed']
            and not any(event['kind'] == 'exception' and not event.get('first_chance') for event in events),
            'Clean own live run')
    debug = [event['value'] for event in events if event['kind'] == 'debug_string']
    require(debug.index('RF455 Protocol:map-bsp:0:1:0') < debug.index('RF455 Protocol:position-mode:0:0:0')
            < debug.index('RF455 WorldCapture:2:0:640x500'), 'Live NeutralB renders after position acceptance')
    require(len(live['world_frames']) == 2, 'Two real world frames')
    for frame in live['world_frames']:
        check(frame)
    return live['world_frames']


def main():
    verify_reference()
    source = WS / 'scripts/native/client455_monster_force_probe.cpp'
    exe = build_full_object_probe('monster-force', source)
    files, cases, clips = resource_inputs(exe.parent)
    result = subprocess.run([str(exe), *(str(file) for file in files)], cwd=exe.parent,
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
    console = exe.parent / 'probe-console.txt'
    console.write_bytes(result.stdout + result.stderr)
    require(result.returncode == 0, 'Monster Force component check: ' + result.stderr.decode(errors='replace'))
    runtime = json.loads(result.stdout)
    require(runtime == dict(status='PASS', selected_cases=5, invalid_type_cases=1, actual_ani_imported=2,
                            attack_key=4288, support_key=4304), 'Unexpected component result')
    link = read('normal-link')
    world_frames = verify_live(link)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'monster-force-reference',
             'skill-force-items-reference', 'live-resource-inputs', 'own-entry', 'startup-audit',
             'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-force-live'] = record(LIVE)
    symbols = {name: hex(rva) for rva, name in own_symbols(link)
               if name.startswith(('?GetAnimationData_Force@CMonster@@', '?usesMonsterAttackClip@RF455SkillForceData@@'))}
    require(len(symbols) == 2, 'Ordinary actor and table selector both linked')
    sources = ('scripts/client455_character_tables_port.py', 'scripts/native/client455_skill_force_items.h',
               'scripts/native/client455_skill_force_items.cpp')
    save('monster-force-checkpoint', dict(
        status='PARTIAL_COMPONENT_MONSTER_FORCE_CLIPS', scope='Ordinary actor selector with real Force data and Wing ANI.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), neutralb_startup_frames=world_frames,
        script=record(Path(__file__)), sources=[record(WS / name) for name in sources] + [record(source)],
        probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']},
        console=record(console), real_clips=clips, cases=cases, native=runtime, own_symbols=symbols,
        live_force_activation=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(runtime))


if __name__ == '__main__':
    main()
