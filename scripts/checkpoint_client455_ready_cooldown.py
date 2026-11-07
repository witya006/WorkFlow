"""Check the selected ready/cooldown port, without accepting full client gameplay."""
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
    ref = load('client455-ready-cooldown-reference')
    base = load('client455-linker-cooldown-reference')
    require(ref['script_sha256'] == sha(WS/'scripts/audit_client455_ready_cooldown.py')
            and ref['base_reference_sha256'] == sha(WS/'inventory/client455-linker-cooldown-reference.json'),
            'Reference provenance')
    require(base['status'] == 'STATIC_ONLY_NOT_IMPLEMENTED' and base['assembly_instructions'] == 5906
            and (ref['state_cases'], ref['grid_cases'], ref['additional_instructions']) == (132, 48, 248),
            'Selected reference domain')
    for row in base['raw_evidence'] + [base['session']] + ref['raw_evidence'] + ref['inputs'] + ref['fixtures']:
        check(row)
    pins = json.loads((WS/'config/client-target.json').read_text())
    for index, (folder, key) in enumerate([('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]):
        path = WS/f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        require(sha(path) == pins[key]['sha256'] == ref['references'][index]['sha256']
                == base['references'][index]['sha256'] and pe(raw)['architecture'] == 'x86', 'Pinned binary')
        for manifest, count in [(base, 82), (ref, 12)]:
            ranges = manifest['references'][index]['ranges']
            require(len(ranges) == count, 'Range coverage')
            for row in ranges:
                require(hashlib.sha256(read_va(raw, 0x400000+int(row['rva'], 16), row['bytes'])).hexdigest()
                        == row['sha256'], 'Selected binary range drift')
    for manifest in [base, ref]:
        require(manifest['references'][0]['ranges'] == manifest['references'][1]['ranges'], 'Selected pins differ')
    session = WS/'artifacts/client455-progress/ready-cooldown099-session.json'
    state = json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'], 'IDA cleanup')

    link = load('client455-normal-link')
    require(validate_normal_link(link) == 'PASS' and link['client_objects'] == 182
            and not link['unique_unresolved'], 'Ordinary client link')
    link_hash = sha(WS/'inventory/client455-normal-link.json')
    build = load('client455-normal-build')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects'] == 20, 'Client build')
    facade_objects = list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj'))
    require(len(facade_objects) == 56, 'Facade object coverage')
    prep = load('client455-normal-preparation')
    require(prep['script_sha256'] == sha(WS/'scripts/prepare_client455_normal.py')
            and prep['linker_cooldown_port_sha256'] == sha(WS/'scripts/client455_linker_cooldown_port.py')
            and prep['gui_timer_port_sha256'] == sha(WS/'scripts/client455_gui_timer_port.py'), 'Port provenance')
    sources = [record(WS/'scripts/native'/name) for name in [
        'client455_gui_animation.h', 'client455_gui_animation.cpp',
        'client455_linker_cooldown.h', 'client455_linker_cooldown.cpp',
        'client455_item_icon_members.inc', 'client455_item_icon.cpp',
        'client455_item_atlas.cpp', 'client455_linker_owners.cpp']]
    for row in sources:
        require(prep['record_inputs'][Path(row['file']).name] == row['sha256'], 'Prepared source drift')
    check(dict(file=prep['manifest'], sha256=prep['manifest_sha256']))
    manifest = json.loads((WS/prep['manifest']).read_text())
    providers = []
    for suffix in ['gameobject/board/common/clinkboard.h', 'gameobject/board/common/clinkboard.cpp',
                   'gameobject/board/common/cboard.h', 'userinterface/guicontroller/guiitem.h',
                   'userinterface/guicontroller/guiitem.cpp', 'generated/client455_gui_animation.cpp',
                   'generated/client455_linker_cooldown.cpp']:
        selected = [row for row in manifest if row['file'].lower().endswith('/'+suffix)]
        require(len(selected) == 1, 'Prepared provider missing '+suffix)
        for row in selected:
            check(row)
            check(dict(file=row['input'], sha256=row['input_sha256']))
        providers += selected
    mapping = (WS/link['map']['file']).read_text()
    retained = {}
    for symbol, provider in [('BeginTypedDelay455@CLinkBoard', 'client455_linker_cooldown.obj'),
                             ('ProcessCooldowns455@CLinkBoard', 'client455_linker_cooldown.obj'),
                             ('FindOriginalTyped455@CLinkBoard', 'client455_linker_cooldown.obj'),
                             ('Update@RF455GuiAnimation', 'client455_gui_animation.obj'),
                             ('Draw@RF455GuiAnimation', 'client455_gui_animation.obj')]:
        match = re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:'+re.escape(provider), mapping)
        require(match, 'Ordinary PE provider missing '+symbol)
        retained[symbol] = match.group(0)

    engine = load('client455-startup-engine-build')
    require(not engine['build_exit'] and engine['objects'] == 67
            and engine['script_sha256'] == sha(WS/'scripts/build_client455_engine_startup.py'), 'Derived engine provenance')
    check(dict(file=engine['library'], sha256=engine['library_sha256']))
    check(engine['baseline_library'])
    require(engine['baseline_library']['sha256'] == 'fba3d77db954750118dbfb5dbb66e5606c3c79398ebe8d502b5fb61d7cad7369',
            'Preserved engine033 library')
    for row in engine['base_sources']:
        check(row)
    for key in ['sprite_header_overlay', 'camera_header_overlay']:
        row = engine[key]
        check(row)
        check(dict(file=row['original'], sha256=row['original_sha256']))
    require(prep['camera_header_overlay'] == engine['camera_header_overlay'], 'Shared forced declaration')
    camera = (WS/engine['camera_header_overlay']['file']).read_text()
    require(camera.index('port_std.hpp') < camera.index('2dsprite455.h'), 'WinSock-safe declaration order')
    sprite = (WS/engine['sprite_header_overlay']['file']).read_bytes()
    require(b'void* GetFrameTexture455()const' in sprite, 'Own nonvirtual texture accessor')

    run = checked_native('client455-ready-cooldown-native', link_hash)
    require(run['script_sha256'] == sha(WS/'scripts/probe_client455_ready_cooldown.py')
            and run['builder_sha256'] == sha(WS/'scripts/client455_own_probe.py')
            and run['reference_sha256'] == sha(WS/'inventory/client455-ready-cooldown-reference.json')
            and run['architecture'] == 'x86', 'Native provenance')
    for row in [run['source'], run['console']] + run['inputs']:
        check(row)
    wanted = {Path(row['file']).name: row['sha256'] for row in ref['inputs']+ref['fixtures']}
    actual = {Path(row['file']).name: row['sha256'] for row in run['inputs']}
    require(all(actual.get(name) == digest for name, digest in wanted.items()), 'Native input fixtures')
    result = run['native']
    require((result['state_cases'], result['grid_cases'], result['GPU_frames']) == (132, 48, 6), 'Native domain')
    for key in ['ordinary_copy_reset_center', 'actual_global_original_lookup', 'ordinary_BeginDelay_FrameMove_Remove',
                'occupied_cache_preserved', 'hidden_expiry', 'pending_erase_quirk', 'actual_SF_group_source_fanout',
                'SF_CPU_icons_synthetic', 'actual_mode3_state', 'all_owners_released', 'sprite_allocator_balanced']:
        require(result[key], 'Selected actual route missing '+key)
    require(not result['full_gameplay_handlers'] and not result['full_client'], 'Unjustified acceptance')
    review = load('client455-ready-cooldown-visual-review')
    require(review['native_sha256'] == sha(WS/'inventory/client455-ready-cooldown-native.json')
            and review['script_sha256'] == sha(WS/'scripts/review_client455_ready_cooldown.py')
            and review['reviewed'] and review['reviewed_frames'] == 6 and review['frames'] == run['frames'], 'Ready visual review')
    check(review['sheet'])
    for row in run['frames']:
        check(row)
        check(row['preview'])

    regressions = []
    for name, baseline_name, count in [
        ('client455-linker-window', 'window097', 8), ('client455-linker-owners', 'owners096', 3),
        ('client455-item-icon-metadata', 'metadata094', 3), ('client455-gui-timer', 'timer098', 6)]:
        current = checked_native(name+'-native', link_hash)
        baseline_path = WS/f'artifacts/client455-progress/{baseline_name}-before099.json'
        baseline = json.loads(baseline_path.read_text())
        visual = load(name+'-visual-review')
        require(visual['reviewed'] and visual['reviewed_frames'] == count and visual['frames'] == baseline['frames']
                and visual['native_sha256'] == sha(baseline_path), 'Inherited reviewed baseline '+name)
        check(visual['sheet'])
        old_frames = {Path(row['file']).name: row for row in baseline['frames']}
        require(len(current['frames']) == len(old_frames) == count, 'Regression frame coverage '+name)
        for row in current['frames']:
            old = old_frames[Path(row['file']).name]
            check(row)
            check(row['preview'])
            check(old)
            require(row['sha256'] == old['sha256'], 'Changed previously reviewed pixels '+row['file'])
        regressions.append(dict(name=name, baseline=record(baseline_path),
                                inherited_review=record(WS/f'inventory/{name}-visual-review.json'),
                                current=record(WS/f'inventory/{name}-native.json'), byte_equal_frames=count))
    checked_native('client455-hotbar-native', link_hash)
    checked_native('client455-account-native', link_hash)
    storage = load('client455-storage-native')
    require(storage['normal_link_sha256'] == link_hash and len(storage['runs']) == 3
            and all(not row['natural_exit'] and row['native']['registered'] == 17 for row in storage['runs']), 'Storage regression')
    for row in storage['runs']:
        for key in ['exe', 'fixture', 'console']:
            check(row[key])
    early, ui = load('client455-startup-native'), load('client455-ui-startup-native')
    contracts = load('client455-startup-contracts-native')
    require(early['normal_link_sha256'] == ui['normal_link_sha256'] == link_hash
            and contracts['build_sha256'] == ui['engine_build_sha256'] == sha(WS/'inventory/client455-startup-engine-build.json')
            and not early['debugger_exit'] and early['sound_return'] == 1 and not ui['debugger_exit']
            and ui['completed_existing_client_create'] and any(row['name'] == 'after_client_create' and row['eax'] == 1 for row in ui['markers'])
            and all(row['first_chance'] == 1 for row in ui['exceptions']), 'Current own PE Create1')
    check(early['events'])
    check(ui['events'])

    fresh = ['normal-preparation', 'normal-build', 'normal-consumers', 'normal-link', 'startup-engine-build',
             'own-entry', 'startup-audit', 'startup-contracts-native', 'startup-native', 'ui-startup-native',
             'hotbar-native', 'storage-native', 'account-native']
    report = dict(status='PARTIAL', scope=ref['scope'], script_sha256=sha(Path(__file__)),
                  reference=record(WS/'inventory/client455-ready-cooldown-reference.json'),
                  static_base=record(WS/'inventory/client455-linker-cooldown-reference.json'),
                  native=record(WS/'inventory/client455-ready-cooldown-native.json'),
                  visual=record(WS/'inventory/client455-ready-cooldown-visual-review.json'),
                  sources=sources, generated_providers=providers, retained=retained, session=record(session),
                  normal_link_sha256=link_hash, normal_executable=link['executable'],
                  fresh_evidence={name: record(WS/f'inventory/client455-{name}.json') for name in fresh},
                  derived_engine_sha256=engine['library_sha256'], baseline033=engine['baseline_library'],
                  state_cases=132, grid_cases=48, new_viewed_GPU_frames=6,
                  inherited_byte_equal_reviewed_frames=20, regressions=regressions,
                  selected_base_ranges=82, additional_ranges=12, additional_instructions=248,
                  previous098gate='Historical runtime after source/link/derived engine changed; static proofs and20byte-equal frames retained',
                  old082_derived_library_snapshot_retained=False,
                  unchanged_world_audio_159k_093atlas_092icon_2013owner_1447SF_095manual_suites_rerun=False,
                  gaps=ref['gaps'], input_exe_executed=False, server_modified=False,
                  M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-ready-cooldown-checkpoint.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PARTIAL:132states/48grids/realready6GPU/ordinarycooldown/20byte-equalreviewedframes/currentPECreate1;fullhandlers/game/M9OPEN')


if __name__ == '__main__':
    main()
