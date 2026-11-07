"""Accept the concrete SF source runtime while ordinary game owners stay open."""
import hashlib
import json
import re
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    reference=load('client455-skill-force-items-reference')
    require(reference['script_sha256']==sha(WS/'scripts/audit_client455_skill_force_items.py') and
            reference['edf_helper_sha256']==sha(WS/'scripts/audit_client455_language.py'),'Stale SF reference')
    require(reference['previous_ownership_reference_sha256']==sha(WS/'inventory/client455-item-ownership-reference.json'),
            'Changed087 base ownership evidence')
    for row in reference['raw_evidence']+reference['inputs']+reference['golden']:check(row)
    for row in reference['inputs']:require(sha(Path(row['original']))==row['original_sha256'],'Changed source EDF')
    for row in reference['candidates']:require(sha(Path(row['original']))==row['sha256'],'Changed candidate EDF')
    require(reference['real_records']==1447 and len(reference['assembly'])==16 and reference['actual_instructions']==1224,'Reference coverage')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pins[key]['sha256']==pin['sha256'] and pe(raw)['architecture']=='x86','Changed pin')
        require(len(pin['ranges'])==35 and pin['external_assembly_windows'],'Reference functions/EH tails')
        for row in pin['ranges']+pin['external_assembly_windows']:
            require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed function/tail window')
    expected_counts={'base.edf':[88,84,504,60,711],'zh-tw.edf':[88,84,504,60,711],
                     'ko-kr.edf':[88,84,504,60,640],'ru-ru.edf':[88,77,504,39,446]}
    require({Path(r['file']).name:[t['count'] for t in r['tables']] for r in reference['inputs']}==expected_counts,
            'Real compatibility evidence drift')
    require({r['locale']:r['failed_table'] for r in reference['golden']}=={'zh-tw':None,'ko-kr':4,'ru-ru':1},'Mismatch positions')
    session_path=WS/'artifacts/client455-progress/skill-force088-session.json';session=json.loads(session_path.read_text())
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'IDA session cleanup')
    native=load('client455-skill-force-items-native')
    require(native['script_sha256']==sha(WS/'scripts/probe_client455_skill_force_items.py') and
            native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and
            native['reference_sha256']==sha(WS/'inventory/client455-skill-force-items-reference.json') and
            native['edf_source_sha256']==sha(WS/'scripts/native/client455_language.cpp'),'Native source provenance')
    for row in native['sources']+native['objects']+[native['build_log'],native['edf_dependency']]:check(row)
    require(sha(WS/native['library'])==native['library_sha256'],'Changed concrete source library')
    require([r['mode'] for r in native['runs']]==['standalone','full_object'],'Native modes')
    first=native['runs'][0]['native']
    fixture_hashes={Path(r['file']).name:r['sha256'] for r in reference['inputs']+reference['golden']}
    for run in native['runs']:
        for key in ['exe','map','console','output']:check(run[key])
        for row in run['inputs']:check(row)
        require({Path(r['file']).name:r['sha256'] for r in run['inputs']}==fixture_hashes,'Fixture copy drift')
        require(run['natural_exit']==0 and run['architecture']=='x86' and
                pe((WS/run['exe']['file']).read_bytes())['architecture']=='x86' and
                run['native']==first==json.loads((WS/run['output']['file']).read_text()),'Source runtime execution')
        mapping=(WS/run['map']['file']).read_text()
        for symbol in ['createSkillForce@RF455SourceItemManager','localizeEdf@RF455SkillForceData',
                       'erase@RF455SourceItemManager','RF455_ReleaseBoardItemReference']:
            require(re.search(re.escape(symbol)+r'[^\r\n]*RF455SkillForceItems:',mapping),'Separate source provider missing '+symbol)
        require(re.search('RF455_DecodeEdf'+r'[^\r\n]*RFClient455Facade:client455_language.obj',mapping),'Existing EDF decoder not retained')
    require(first['status']=='PASS' and first['real_tables']==5 and first['real_SF_payloads']==1447 and
            first['cloned_wrappers']==1447 and first['source_factory_selector']==1,'Actual source runtime coverage')
    for key in ['concrete_primary_manager','real_table_borrowing','prefix_localization_writes',
                'actual_last_owner_erase','duplicate_factory_requests']:require(first[key],'Missing concrete branch '+key)
    require(not first['recording_host'] and not first['all_payload_factories'] and
            not first['ordinary_Linker_bound'] and not first['actual_Tutorial'],'Unjustified acceptance scope')
    require(first['matching_localization']=='zh-tw' and first['Korea_count_mismatch_table']==4 and
            first['Russia_count_mismatch_table']==1,'Real supplied mismatch branch')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    profile_path=client/'R3Engine.ini'
    language=[line for line in profile_path.read_bytes().splitlines() if re.match(rb'^Language\s*=',line)]
    require(len(language)==1,'Installed resource profile setting missing/ambiguous')
    setting=language[0].split(b'=',1)[1].strip().decode('ascii')
    nation=load('client455-nation-paths-reference')
    row=next((r for r in nation['references'][0]['rows'] if r['setting']==setting),None)
    require(row and setting=='Taiwan' and row['id']==8 and row['folder']==first['matching_localization'],
            'The passing source test no longer matches the installed profile')
    installed_profile=dict(original=str(profile_path),setting=setting,nation_id=row['id'],folder=row['folder'],
        setting_line_sha256=hashlib.sha256(language[0]).hexdigest(),
        nation_mapping_sha256=sha(WS/'inventory/client455-nation-paths-reference.json'),
        original_configuration_changed=False,normal_WinMain_profile_executed_in_this_probe=False)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Normal client drift')
    link_hash=sha(WS/'inventory/client455-normal-link.json');ordinary=load('client455-hotbar-checkpoint')
    require(native['normal_link_sha256']==ordinary['normal_link_sha256']==link_hash and
            link['executable']['sha256']=='82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8' and
            not native['normal_client_relinked'] and not native['ordinary_Linker_changed'],'Ordinary086 unexpectedly changed')
    for name,digest in ordinary['fresh_evidence'].items():require(sha(WS/'inventory'/(name+'.json'))==digest,'Changed086 acceptance report')
    taiwan=load('client455-startup-taiwan-native')
    require(taiwan['normal_link_sha256']==link_hash and taiwan['script_sha256']==sha(WS/'scripts/probe_client455_startup.py') and
            taiwan['nation']=='Taiwan' and not taiwan['debugger_exit'] and taiwan['normal_winmain_executed'] and
            taiwan['transport_connected'] and taiwan['sound_return']==1 and not taiwan['graphics_window_created'],
            'New primary-profile early startup failed/stale')
    check(taiwan['events']);check(taiwan['debugger'])
    for row in taiwan['lab_inputs']:check(row)
    require(sha(WS/taiwan['staged_executable'])==link['executable']['sha256'] and
            any(r['value'].startswith('RF455 NDLanguage:950:') for r in taiwan['language_debug']) and
            all(r['matches_audited_provider'] for r in taiwan['loaded_provider_checks']),'Taiwan language/provider evidence')
    report=dict(status='PARTIAL_SOURCE_RUNTIME',scope='Concrete selector1 SF payload/data/manager and087owned-wrapper kernels on real files;ordinary086 remains current',
        reference_sha256=sha(WS/'inventory/client455-skill-force-items-reference.json'),
        native_sha256=sha(WS/'inventory/client455-skill-force-items-native.json'),
        session=dict(file=session_path.relative_to(WS).as_posix(),sha256=sha(session_path)),script_sha256=sha(Path(__file__)),
        source_sha256={Path(r['file']).name:r['sha256'] for r in native['sources'] if r['file'].startswith('scripts/native/')},
        selected_functions=35,assembly_instructions=1224,real_SF_records=1447,cloned_wrappers=1447,
        recording_host=False,concrete_primary_manager=True,standalone_and_full_object='PASS_BOUNDED',
        input_localization_mismatch={'ko-kr':4,'ru-ru':1},count_compatible_test_locale='zh-tw',
        installed_resource_profile=installed_profile,
        new_Taiwan_early_startup_sha256=sha(WS/'inventory/client455-startup-taiwan-native.json'),
        new_Taiwan_early_startup='PASS_BOUNDED_CRT_WINMAIN_LANGUAGE950_TCP_SOUND',
        normal_link_sha256=link_hash,ordinary_runtime_gate='inventory/client455-hotbar-checkpoint.json',
        ordinary_runtime_gate_sha256=sha(WS/'inventory/client455-hotbar-checkpoint.json'),
        normal_client_relinked=False,ordinary_Linker_changed=False,unchanged_GPU_startup_suites_rerun=False,
        gaps=reference['gaps']+['Count compatibility alone is not a full locale/version/game acceptance claim',
            'Source SF160 data record is not the complete private C++ ABI or all SF gameplay/XP/cooldown/UI methods',
            'All prior item/storage/GUI/Tutorial/fourstage/Login/auth/gameplay and M6F/M7/M9 requirements remain mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-skill-force-items-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_SOURCE_RUNTIME:1447realSF/create/ownedclone/concretemanager/last-owner erase;zh-tw pass/ko-ru mismatch preserved;ordinary086/M9OPEN')


if __name__=='__main__':main()
