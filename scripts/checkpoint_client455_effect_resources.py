"""Verify ordinary archive ownership and real aiming-resource loading, not full FX."""
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
    ref = load('client455-effect-resources-reference')
    require(ref['script_sha256'] == sha(WS/'scripts/audit_client455_effect_resources.py')
            and ref['rpk_reader_sha256'] == sha(WS/'scripts/rpk455.py')
            and (ref['functions'], ref['instructions']) == (14, 1315), 'Reference provenance')
    check(ref['raw_evidence'])
    pins = json.loads((WS/'config/client-target.json').read_text())
    for pin, folder, key in zip(ref['references'], ['current', 'reference-backup'],
                                ['behavior_reference', 'secondary_reference']):
        path = WS/f'work/client-reference/{folder}/RF_Online.bin'
        data = path.read_bytes()
        require(sha(path) == pin['sha256'] == pins[key]['sha256']
                and pe(data)['architecture'] == 'x86' and pin['image_base'] == '0x400000'
                and len(pin['ranges']) == 14, 'Pinned input')
        for row in pin['ranges'] + [pin['initializer']]:
            require(hashlib.sha256(read_va(data, 0x400000+int(row['rva'], 16),
                                          row['bytes'])).hexdigest() == row['sha256'], 'Range drift')
    require(ref['references'][0]['ranges'] == ref['references'][1]['ranges']
            and ref['references'][0]['initializer'] == ref['references'][1]['initializer'], 'Reference equivalence')
    for row in ref['inputs']:
        check(row)
    require(len(ref['actual_nuclear_members']) == 24, 'Actual dependency closure')
    session = WS/'artifacts/client455-progress/effect105-session.json'
    state = json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'], 'IDA cleanup')

    link = load('client455-normal-link')
    link_hash = sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link) == 'PASS' and link['client_objects'] == 182, 'Ordinary link')
    prep, build = load('client455-normal-preparation'), load('client455-normal-build')
    require(prep['script_sha256'] == sha(WS/'scripts/prepare_client455_normal.py')
            and prep['magic_port_sha256'] == sha(WS/'scripts/client455_magic_port.py')
            and not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects'] == 20
            and build['source_manifest_sha256'] == prep['manifest_sha256']
            and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj'))) == 59,
            'Current preparation/build')
    check(dict(file=build['log'], sha256=build['log_sha256']))
    check(dict(file=prep['manifest'], sha256=prep['manifest_sha256']))
    manifest = json.loads((WS/prep['manifest']).read_text())
    providers = []
    for suffix in ['source/addcodebyjang/effectentitylist.h', 'source/addcodebyjang/effectentitylist.cpp',
                   'source/addcodebyjang/effectcore.cpp']:
        selected = [row for row in manifest if row['file'].lower().endswith('/'+suffix)]
        require(len(selected) == 1, 'Generated provider '+suffix)
        for row in selected:
            check(row)
            check(dict(file=row['input'], sha256=row['input_sha256']))
        providers += selected
    mapping = (WS/link['map']['file']).read_text()
    retained = {}
    for symbol, owner in [('GetEffectResourceGroup455', 'effectentitylist.obj'),
                          ('LoadEffectEntityList@@', 'effectentitylist.obj'),
                          ('ReleaseEffectEntityList@@', 'effectentitylist.obj'),
                          ('GetEntityFromEffectEntityList@@', 'effectentitylist.obj'),
                          ('GetParticleFromEffectEntityList@@', 'effectentitylist.obj'),
                          ('StartMagicEffect@@YAKQAMMKPAXK@Z', 'effectcore.obj')]:
        match = re.search(re.escape(symbol)+r'[^\r\n]*\s'+re.escape(owner)+r'\s*$', mapping, re.M)
        require(match, 'Ordinary retained '+symbol)
        retained[symbol] = match.group(0).strip()

    run = checked_native('client455-effect-resources-native', link_hash)
    require(run['script_sha256'] == sha(WS/'scripts/probe_client455_effect_resources.py')
            and run['builder_sha256'] == sha(WS/'scripts/client455_own_probe.py')
            and run['reference_sha256'] == sha(WS/'inventory/client455-effect-resources-reference.json')
            and run['source']['sha256'] == sha(WS/'scripts/native/client455_effect_resources_probe.cpp'), 'Native provenance')
    check(run['source'])
    check(run['console'])
    for row in run['inputs']:
        check(row)
    actual = {Path(row['file']).name.lower(): row['sha256'] for row in run['inputs']}
    require(all(actual.get(Path(row['file']).name.lower()) == row['sha256'] for row in ref['inputs']), 'Staged real dependencies')
    result = run['native']
    require(tuple(result[key] for key in ['checks', 'warnings', 'real_RPK_cue_tracks', 'real_R3E_models',
                                        'real_particle_recipes', 'real_particle_clones', 'retained_global_texture_cache_bytes'])
            == (66, 6, 6, 6, 5, 10, 9728), 'Native scope')
    for key in ['ordinary_archive_owner', 'ordinary_start_selects_group', 'real_D3D_textures',
                'cache_hit_selection_preserved', 'table_only_reload_balanced', 'static_empty_group_remains_valid',
                'all_allocations_released', 'explicit_global_texture_table_teardown']:
        require(result[key], 'Native '+key)
    require(result['memory_before'] == result['memory_after'], 'Lab memory balance')
    for key in ['GPU_effect_drawn', 'full_effect_runtime', 'full_nuclear_aiming', 'full_client']:
        require(not result[key], 'Unjustified acceptance '+key)
    magic = checked_native('client455-magic-native', link_hash)
    require(magic['native']['checks'] == 36 and magic['native']['real_RPK_cue_tracks'] == 6
            and magic['source']['sha256'] == sha(WS/'scripts/native/client455_magic_probe.cpp'), 'Magic regression')
    status = checked_native('client455-player-status-native', link_hash)
    require(status['native']['checks'] == 58 and status['native']['nuclear_refusal_before_mutation'], 'Status regression')
    audio = checked_native('client455-tagged-audio-native', link_hash)
    require(audio['native']['checks'] == 157 and audio['native']['real_Miles_provider_listener_samples'], 'Audio regression')
    hover = checked_native('client455-board-hover-native', link_hash)
    require(hover['native']['all_owners_released'] and hover['native']['sprite_allocator_balanced'], 'Hover regression')
    baseline_path = WS/'artifacts/client455-progress/client455-board-hover-native-before105.json'
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
    require(checked_native('client455-hotbar-native', link_hash)['native']['actual_packets'] == 7, 'Hotbar regression')
    storage = load('client455-storage-native')
    require(storage['normal_link_sha256'] == link_hash and len(storage['runs']) == 3
            and all(not row['natural_exit'] and row['native']['registered'] == 17 for row in storage['runs']), 'Storage regression')
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
    fresh = ['effect-resources-reference', 'effect-resources-native', 'magic-native', 'player-status-native',
             'tagged-audio-native', 'board-hover-native', 'board-hover-visual-review', 'normal-preparation',
             'normal-build', 'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-native',
             'ui-startup-native', 'account-native', 'hotbar-native', 'storage-native']
    report = dict(status='PARTIAL', scope=ref['scope'], script_sha256=sha(Path(__file__)), session=record(session),
                  generated_providers=providers, retained=retained, normal_link_sha256=link_hash,
                  normal_executable=link['executable'], fresh_evidence={name: record(WS/f'inventory/client455-{name}.json') for name in fresh},
                  CPU_checks=66, real_R3E_models=6, real_particle_recipes=5, real_particle_clones=10,
                  D3D_textures_restored=True, GPU_effect_drawn=False, legacy_R3T_release_warnings=6,
                  explicit_global_texture_table_teardown=True, retained_global_texture_cache_bytes=9728,
                  viewed_GPU_frames=6, byte_equal_hover_frames=6, baseline=record(baseline_path),
                  previous104_checkpoint=record(WS/'artifacts/client455-progress/client455-magic-checkpoint-before105.json'),
                  previous104_runtime_gate='HISTORICAL', ordinary_audio_provider=ready[0],
                  derived_engine_unchanged=engine['library_sha256'], unchanged_bulk_suites_rerun=False,
                  other32_GUI_frames_rerun=False, gaps=ref['gaps'], input_exe_executed=False,
                  server_modified=False, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-effect-resources-checkpoint.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PARTIAL:66CPU/ordinaryEffectArchiveOwner/6realModels/5recipes/10clones/D3Dtextures;6legacyWarnings/fullFX/nuclear/M9OPEN')


if __name__ == '__main__':
    main()
