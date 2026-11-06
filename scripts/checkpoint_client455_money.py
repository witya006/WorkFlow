"""Validate the bounded money restoration without accepting Tutorial or M9."""
import hashlib
import json
import re
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    link = load('client455-normal-link')
    require(validate_normal_link(link) == 'PASS', 'Current normal link')
    link_hash = sha(WS / 'inventory/client455-normal-link.json')
    engine_hash = sha(WS / 'inventory/client455-startup-engine-build.json')
    prep = load('client455-normal-preparation')
    require(prep['script_sha256'] == sha(WS / 'scripts/prepare_client455_normal.py'), 'Preparation drift')
    for name in ['client455_money.h', 'client455_money.cpp',
                 'client455_inventory_money.inc', 'client455_inventory_gold.inc']:
        require(prep['record_inputs'][name] == sha(WS / 'scripts/native' / name), 'Changed money source ' + name)
    check(dict(file=prep['manifest'], sha256=prep['manifest_sha256']))
    manifest = json.loads((WS / prep['manifest']).read_text())
    expected = {
        'source/character/avatar/cavatar.h',
        'source/character/avatar/cavatar_etc.cpp',
        'source/userinterface/gamewindow/guiinventorywindow.h',
        'source/userinterface/gamewindow/guiinventorywindow.cpp',
        'include/client455_money.h', 'generated/client455_money.cpp',
    }
    selected = [row for row in manifest if any(row['file'].endswith('/' + name) for name in expected)]
    require(len(selected) == len(expected), 'Missing money source/ABI manifest')
    for row in selected:
        check(row)
        check(dict(file=row['input'], sha256=row['input_sha256']))

    reference = load('client455-money-reference')
    require(reference['script_sha256'] == sha(WS / 'scripts/audit_client455_money.py'), 'Static audit drift')
    for row in reference['raw_evidence']:
        check(row)
    require(len(reference['references'][0]['ranges']) == 21 and
            len(reference['assemblies']) == 10 and
            sum(row['instructions'] for row in reference['assemblies']) == 382,
            'Money/Tutorial reference coverage')
    pins = json.loads((WS / 'config/client-target.json').read_text())
    for folder, key, pin in zip(['current', 'reference-backup'],
                                ['behavior_reference', 'secondary_reference'],
                                reference['references']):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        require(sha(path) == pin['sha256'] == pins[key]['sha256'], 'Changed reference pin')
        require(pin['architecture'] == 'x86' and pin['image_base'] == '0x400000', 'Reference architecture')
        for row in pin['ranges']:
            digest = hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest()
            require(digest == row['sha256'], 'Changed selected reference body')
        require(read_va(raw, 0xaa9f24, 2) == b',\0', 'Grouping separator')

    money = load('client455-money-native')
    require(money['normal_link_sha256'] == link_hash and money['engine_report_sha256'] == engine_hash,
            'Stale money execution')
    require(money['script_sha256'] == sha(WS / 'scripts/probe_client455_money.py') and
            money['builder_sha256'] == sha(WS / 'scripts/client455_own_probe.py'), 'Probe drift')
    check(money['source'])
    require([run['nation'] for run in money['runs']] == ['Korea', 'Russia'], 'Locale coverage')
    for run in money['runs']:
        for key in ['exe', 'map', 'output', 'console', 'trace']:
            check(run[key])
        for row in run['inputs'] + run['frames']:
            check(row)
            if 'original' in row:
                require(sha(Path(row['original'])) == row['sha256'], 'Changed original money input')
        require(pe((WS / run['exe']['file']).read_bytes())['architecture'] == 'x86', 'Probe architecture')
        native = run['native']
        require(run['exit'] == 0 and native == json.loads((WS / run['output']['file']).read_text()) and
                native['status'] == 'PASS', 'Money native execution')
        require(native['cases'] == 92 and native['rounding_modes'] == 4 and
                native['frames'] == len(run['frames']) == 3 and native['colored_pixels'] > 0,
                'Money numeric/GPU coverage')
        for key in ['real_Avatar_inventory_chain', 'signed64_storage',
                    'wider_title_alignment', 'shared_text_buffer']:
            require(native[key], 'Missing actual money contract ' + key)
        require(not native['full_inventory_currency_network'] and not native['actual_Tutorial_stage'],
                'Unjustified full currency/Tutorial claim')

    actor = load('client455-rvp-actor-native')
    require(actor['normal_link_sha256'] == link_hash and actor['engine_report_sha256'] == engine_hash,
            'Stale actor regression')
    require(actor['script_sha256'] == sha(WS / 'scripts/probe_client455_rvp_actor.py') and
            actor['builder_sha256'] == sha(WS / 'scripts/client455_own_probe.py') and
            actor['runtime_inputs_sha256'] == sha(WS / 'scripts/client455_runtime_inputs.py'), 'Actor probe drift')
    for key in ['source', 'exe', 'map', 'output', 'console', 'trace']:
        check(actor[key])
    for row in actor['inputs'] + actor['frames']:
        check(row)
    a = actor['native']
    require(actor['natural_exit'] == 0 and actor['inputs_unchanged'] and
            a == json.loads((WS / actor['output']['file']).read_text()) and a['status'] == 'PASS', 'Actor execution')
    require(a['actors'] == 12 and a['stock_ticks'] == 269 and a['actor_draws'] == 185 and
            a['particle_draws'] == 148 and a['entity_draws'] == 6 and a['isolated_entity_pixels'] > 0 and
            a['distinct_pose_ticks'] == 9 and a['restored_parts'] == 459 and not a['warnings'] and
            a['memory_before'] == a['memory_after'], 'Actor/FX regression')
    for name, count, native_name, script in [
        ('client455-money-visual', 6, 'client455-money-native', 'review_client455_money.py'),
        ('client455-rvp-actor-visual', 9, 'client455-rvp-actor-native', 'review_client455_rvp_actor.py'),
    ]:
        visual = load(name)
        require(visual['manually_reviewed'] and len(visual['frames']) == count and
                visual['native_sha256'] == sha(WS / 'inventory' / (native_name + '.json')) and
                visual['script_sha256'] == sha(WS / 'scripts' / script), 'Stale/missing visual review')
        check(visual['sheet'])
        for row in visual['frames']:
            check(row)
            require(sha(WS / row['preview']) == row['preview_sha256'], 'Changed frame preview')

    account = load('client455-account-native')
    require(account['normal_link_sha256'] == link_hash and account['natural_exit'] == 0 and
            account['script_sha256'] == sha(WS / 'scripts/probe_client455_account.py') and
            account['builder_sha256'] == sha(WS / 'scripts/client455_own_probe.py') and
            account['source_sha256'] == sha(WS / account['source']), 'Stale account regression')
    for name, digest in account['sources'].items():
        require(sha(WS / 'scripts/native' / name) == digest, 'Account source drift')
    for key in ['exe', 'map', 'output']:
        check(account[key])
    for row in account['inputs']:
        check(row)
    n = account['native']
    require(n == json.loads((WS / account['output']['file']).read_text()) and n['status'] == 'PASS' and
            n['actual_Avatar_stage_skip'] and n['actual_MainApp_Create_gate'] and
            n['actual_login_Tutorial_transform'] and n['actual_account_send_receive'] and
            not n['full_fourstage_factory'] and not n['authentication_performed'], 'Account regression scope')

    early = load('client455-startup-native')
    ui = load('client455-ui-startup-native')
    require(early['normal_link_sha256'] == link_hash and early['normal_winmain_executed'] and
            early['transport_connected'] and not early['debugger_exit'], 'Fresh early startup')
    require(ui['normal_link_sha256'] == link_hash and ui['engine_build_sha256'] == engine_hash and
            ui['early_startup_sha256'] == sha(WS / 'inventory/client455-startup-native.json') and
            ui['completed_existing_client_create'] and ui['markers'][-1]['eax'] == 1 and
            not ui['debugger_exit'], 'Fresh exact PE/Create1')
    for body in [early, ui]:
        check(body['events'])
        require(sha(WS / body['staged_executable']) == link['executable']['sha256'], 'Staged PE differs')
    require(not load('client455-startup-audit')['unresolved_provider_modules'], 'Missing DLL provider')
    engine = load('client455-startup-engine-build')
    require(engine['library_sha256'] ==
            '9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769' and
            load('client455-startup-contracts-native')['build_sha256'] == engine_hash,
            '082 engine/contract evidence no longer reusable')
    check(dict(file=engine['library'], sha256=engine['library_sha256']))
    mapping = (WS / link['map']['file']).read_text()
    for symbol, unit in [
        # MSVC inlines FormatMoney into the naturally retained shared-buffer API.
        ('RF455_GetMoneyText', 'RFClient455Facade:client455_money'),
        ('?SetDalant@CAvatar@@QAEX_J@Z', 'cavatar_etc'),
        ('?SetGold@CAvatar@@QAEX_J@Z', 'cavatar_etc'),
        ('?SetOwnDalant@CGUIInventoryWindow@@QAEX_J@Z', 'guiinventorywindow'),
        ('?SetOwnGold@CGUIInventoryWindow@@QAEX_J@Z', 'guiinventorywindow'),
    ]:
        require(re.search(re.escape(symbol) + r'[^\r\n]*' + re.escape(unit) + r'.obj', mapping),
                'Missing ordinary 64-bit provider ' + symbol)

    report = dict(
        status='PARTIAL', Avatar_inventory_signed64='PASS_BOUNDED', money_cases=184,
        rounding_modes=4, money_GPU_frames=6, fresh_actor_GPU_frames=9,
        exactPE_Create1='PASS', account_regression='PASS_BOUNDED',
        normal_link_sha256=link_hash, engine_report_sha256=engine_hash,
        reused_082_engine_contracts=True, three_map_audio_suites_rerun=False,
        evidence_sha256={name: sha(WS / 'inventory' / (name + '.json')) for name in [
            'client455-money-reference', 'client455-money-native', 'client455-money-visual',
            'client455-rvp-actor-native', 'client455-rvp-actor-visual', 'client455-account-native',
            'client455-startup-native', 'client455-ui-startup-native']},
        script_sha256=sha(Path(__file__)),
        helper_sha256=sha(WS / 'scripts/checkpoint_client455_rvp_effects.py'),
        gaps=reference['gaps'], actual_Tutorial_stage=False,
        full_currency_protocol=False, input_exe_executed=False, server_modified=False,
        M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN',
    )
    (WS / 'inventory/client455-money-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL:actual Avatar/inventory signed64;184cases/6money+9actorGPU;fresh account/PE/Create1;M9 OPEN')


if __name__ == '__main__':
    main()
