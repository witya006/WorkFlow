"""Validate selected real magic parsing/cache work; full effect acceptance stays open."""
import hashlib
import json
import re
from pathlib import Path

from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    ref = load('client455-magic-reference')
    require(ref['script_sha256'] == sha(WS/'scripts/audit_client455_magic.py')
            and ref['rpk_reader_sha256'] == sha(WS/'scripts/rpk455.py')
            and (ref['functions'], ref['instructions']) == (19, 2988), 'Reference provenance')
    check(ref['raw_evidence'])
    pins = json.loads((WS/'config/client-target.json').read_text())
    for pin, folder, key in zip(ref['references'], ['current', 'reference-backup'],
                                ['behavior_reference', 'secondary_reference']):
        path = WS/f'work/client-reference/{folder}/RF_Online.bin'
        data = path.read_bytes()
        require(sha(path) == pin['sha256'] == pins[key]['sha256']
                and pe(data)['architecture'] == 'x86' and pin['image_base'] == '0x400000'
                and len(pin['ranges']) == 19, 'Pinned input')
        for row in pin['ranges'] + [pin['array_initializer']]:
            require(hashlib.sha256(read_va(data, 0x400000+int(row['rva'], 16),
                                          row['bytes'])).hexdigest() == row['sha256'], 'Range drift')
    require(ref['references'][0]['ranges'] == ref['references'][1]['ranges']
            and ref['references'][0]['array_initializer'] == ref['references'][1]['array_initializer'],
            'Reference equivalence')
    for row in ref['inputs'] + [ref['cue']]:
        check(row)
    require(ref['cue']['tracks'] == 6 and ref['cue']['sha256'] ==
            '7459ef920bf277c92041c57d2dbe1876641d740bded34325bf8268de14b52b84', 'Real cue')
    session = WS/'artifacts/client455-progress/magic104-session.json'
    state = json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],
            'Owned IDA cleanup')

    link = load('client455-normal-link')
    link_hash = sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link) == 'PASS' and link['client_objects'] == 182, 'Ordinary link')
    prep, build = load('client455-normal-preparation'), load('client455-normal-build')
    require(prep['script_sha256'] == sha(WS/'scripts/prepare_client455_normal.py')
            and prep['magic_port_sha256'] == sha(WS/'scripts/client455_magic_port.py'),
            'Current preparation')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects'] == 20
            and build['source_manifest_sha256'] == prep['manifest_sha256']
            and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj'))) == 59,
            'Build coverage')
    check(dict(file=build['log'], sha256=build['log_sha256']))
    sources = [record(WS/'scripts/native'/name) for name in
               ['client455_magic_control.h', 'client455_magic_control.cpp', 'client455_magic_parser_extra.inc']]
    for row in sources:
        require(prep['record_inputs'][Path(row['file']).name] == row['sha256'], 'Prepared input drift')
    check(dict(file=prep['manifest'], sha256=prep['manifest_sha256']))
    manifest = json.loads((WS/prep['manifest']).read_text())
    providers = []
    for suffix in ['source/global.h', 'source/global.cpp', 'source/addcodebyjang/cmagicscript.h',
                   'source/addcodebyjang/cmagicscript.cpp', 'source/addcodebyjang/effectcore.cpp',
                   'generated/client455_magic_control.cpp']:
        selected = [row for row in manifest if row['file'].lower().endswith('/'+suffix)]
        require(len(selected) == 1, 'Generated provider '+suffix)
        for row in selected:
            check(row)
            check(dict(file=row['input'], sha256=row['input_sha256']))
        providers += selected
    mapping = (WS/link['map']['file']).read_text()
    retained = {}
    for symbol, owner in [('CreateMagicTrack@CProcessMagic', 'cmagicscript.obj'),
                          ('GetEntityIDs@CProcessMagic', 'cmagicscript.obj'),
                          ('??0EffectInfo@@QAE@XZ', 'global.obj'),
                          ('StartMagicEffect@@YAKQAMMKPAXK@Z', 'effectcore.obj'),
                          ('GetRealID@@YAKK@Z', 'effectentitylist.obj'),
                          ('Add455@RF455MagicControl', 'RFClient455Facade:client455_magic_control.obj')]:
        match = re.search(re.escape(symbol)+r'[^\r\n]*\s'+re.escape(owner)+r'\s*$', mapping, re.M)
        require(match, 'Ordinary retained '+symbol)
        retained[symbol] = match.group(0).strip()

    run = checked_native('client455-magic-native', link_hash)
    require(run['script_sha256'] == sha(WS/'scripts/probe_client455_magic.py')
            and run['builder_sha256'] == sha(WS/'scripts/client455_own_probe.py')
            and run['reference_sha256'] == sha(WS/'inventory/client455-magic-reference.json'),
            'Native provenance')
    check(run['source'])
    check(run['console'])
    require(run['source']['sha256'] == sha(WS/'scripts/native/client455_magic_probe.cpp'), 'Native source')
    for row in run['inputs']:
        check(row)
    actual = {Path(row['file']).name.lower(): row['sha256'] for row in run['inputs']}
    require(all(actual.get(Path(row['file']).name.lower()) == row['sha256'] for row in ref['inputs']),
            'Actual staged dependencies')
    result = run['native']
    require(tuple(result[key] for key in ['checks', 'process_bytes', 'runtime_bytes', 'track_bytes',
                                        'maximum_tracks', 'real_RPK_cue_tracks']) == (36, 3004, 456, 46, 64, 6),
            'Native domain')
    for key in ['packed_tracks_equal', 'actual_entity_mapping', 'ordinary_cache_start_disappear',
                'selector_boundaries_and_NaN', 'control_nodes_and_multi', 'all_allocations_released']:
        require(result[key], 'Native '+key)
    for key in ['full_effect_rendering', 'full_nuclear_aiming', 'full_client']:
        require(not result[key], 'Unjustified acceptance '+key)

    status = checked_native('client455-player-status-native', link_hash)
    require(status['native']['checks'] == 58 and status['native']['nuclear_refusal_before_mutation'],
            'Status regression')
    audio = checked_native('client455-tagged-audio-native', link_hash)
    require(audio['native']['checks'] == 157 and audio['native']['actual_MainApp_owner']
            and audio['native']['real_Miles_provider_listener_samples'], 'Audio regression')
    hover = checked_native('client455-board-hover-native', link_hash)
    require(hover['native']['actual_live_ordinary_avatar'] and hover['native']['all_owners_released']
            and hover['native']['sprite_allocator_balanced'], 'Hover regression')
    baseline_path = WS/'artifacts/client455-progress/client455-board-hover-native-before104.json'
    before = {Path(row['file']).name: row for row in json.loads(baseline_path.read_text())['frames']}
    require(len(hover['frames']) == len(before) == 6, 'Frame coverage')
    for row in hover['frames']:
        prior = before[Path(row['file']).name]
        check(prior)
        check(row)
        check(row['preview'])
        require(row['sha256'] == prior['sha256'], 'Changed prior pixels')
    review = load('client455-board-hover-visual-review')
    require(review['reviewed'] and review['reviewed_frames'] == 6 and review['frames'] == hover['frames']
            and review['native_sha256'] == sha(WS/'inventory/client455-board-hover-native.json'), 'Viewed frames')
    check(review['sheet'])
    checked_native('client455-account-native', link_hash)
    hotbar = checked_native('client455-hotbar-native', link_hash)
    require(hotbar['native']['actual_packets'] == 7, 'Hotbar regression')
    storage = load('client455-storage-native')
    require(storage['normal_link_sha256'] == link_hash and len(storage['runs']) == 3
            and all(not row['natural_exit'] and row['native']['registered'] == 17 for row in storage['runs']),
            'Storage regression')
    early, ui = load('client455-startup-native'), load('client455-ui-startup-native')
    require(early['normal_link_sha256'] == ui['normal_link_sha256'] == link_hash
            and early['sound_return'] == 1 and not early['debugger_exit'] and not ui['debugger_exit']
            and ui['completed_existing_client_create']
            and any(row['name'] == 'after_client_create' and row['eax'] == 1 for row in ui['markers'])
            and all(row['first_chance'] == 1 for row in ui['exceptions']), 'Exact own PE Create1')
    ready = [row['value'] for row in ui['nation_paths'] if row.get('value', '').startswith('RF455 TaggedAudio:ready:7969:')]
    require(len(ready) == 1, 'Actual ordinary audio provider')
    check(early['events'])
    check(ui['events'])
    engine = load('client455-startup-engine-build')
    require(sha(WS/engine['library']) == engine['library_sha256'] ==
            '546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a', 'Engine unchanged')
    check(engine['baseline_library'])
    fresh = ['magic-reference', 'magic-native', 'player-status-native', 'tagged-audio-native',
             'board-hover-native', 'board-hover-visual-review', 'normal-preparation', 'normal-build',
             'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-native',
             'ui-startup-native', 'account-native', 'hotbar-native', 'storage-native']
    report = dict(status='PARTIAL', scope=ref['scope'], script_sha256=sha(Path(__file__)), session=record(session),
                  sources=sources, generated_providers=providers, retained=retained, normal_link_sha256=link_hash,
                  normal_executable=link['executable'], fresh_evidence={name: record(WS/f'inventory/client455-{name}.json') for name in fresh},
                  CPU_checks=36, real_RPK_cue_tracks=6, process_bytes=3004, runtime_bytes=456, maximum_tracks=64,
                  viewed_GPU_frames=6, byte_equal_hover_frames=6, baseline=record(baseline_path),
                  previous103_checkpoint=record(WS/'artifacts/client455-progress/client455-tagged-audio-checkpoint-before104.json'),
                  previous103_runtime_gate='HISTORICAL', ordinary_audio_provider=ready[0],
                  derived_engine_unchanged=engine['library_sha256'], unchanged_bulk_suites_rerun=False,
                  other32_GUI_frames_rerun=False, gaps=ref['gaps'], input_exe_executed=False,
                  server_modified=False, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-magic-checkpoint.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PARTIAL:36CPU/real6trackRPKcue/magic64/process3004/runtime456/cache;6viewedByteEqualGPU;fullFX/nuclear/M9OPEN')


if __name__ == '__main__':
    main()
