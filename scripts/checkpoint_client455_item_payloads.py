"""Accept bounded source item factories/readers;keep ordinary-game acceptance open."""
import hashlib
import json
import re
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    reference=load('client455-item-payloads-reference');sf=load('client455-skill-force-items-reference')
    for name,report in [('item-payloads',reference),('skill-force-items',sf)]:
        require(report['script_sha256']==sha(WS/f'scripts/audit_client455_{name.replace("-","_")}.py') and
                report['edf_helper_sha256']==sha(WS/'scripts/audit_client455_language.py'),'Stale reference source')
        for row in report['raw_evidence']+report['inputs']+report.get('fixtures',report.get('golden',[])):check(row)
        for row in report['inputs']:require(sha(Path(row['original']))==row['original_sha256'],'Changed original EDF')
    require(reference['previous_SF_reference_sha256']==sha(WS/'inventory/client455-skill-force-items-reference.json'),'Changed SF reference chain')
    require(len(reference['assembly'])==19 and reference['actual_instructions']==1796 and
            reference['item_rows']==76049 and reference['quest_rows']==2895 and reference['animus_level_rows']==648,'Reference coverage')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();index=0 if folder=='current' else 1
        require(sha(path)==pins[key]['sha256'] and pe(raw)['architecture']=='x86','Changed x86 pin')
        for report,expected in [(reference,50),(sf,35)]:
            pin=report['references'][index];require(pin['sha256']==sha(path) and len(pin['ranges'])==expected,'Reference identity/count')
            for row in pin['ranges']+pin['external_assembly_windows']:
                require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed range/EH window')
        flag=reference['references'][index]['Taiwan_item_flag'];slot=read_va(raw,0x400000+int(flag['slot_rva'],16),4)
        require(slot.hex()==flag['slot_bytes'] and int.from_bytes(slot,'little')==0x82c490 and flag['value']==1,'Installed profile branch')
    require([(r['locale'],r['descriptions'],r['dungeons'],r['tail']) for r in reference['locales']]==
            [('zh-tw',68084,100,0),('ko-kr',63821,100,0),('ru-ru',52255,0,11185)],'Real ND corpus drift')
    session_path=WS/'artifacts/client455-progress/item-payloads089-session.json';session=json.loads(session_path.read_text())
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'IDA cleanup')
    native=load('client455-item-payloads-native')
    require(native['script_sha256']==sha(WS/'scripts/probe_client455_item_payloads.py') and
            native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and
            native['reference_sha256']==sha(WS/'inventory/client455-item-payloads-reference.json') and
            native['SF_reference_sha256']==sha(WS/'inventory/client455-skill-force-items-reference.json') and
            native['edf_source_sha256']==sha(WS/'scripts/native/client455_language.cpp'),'Native provenance')
    for row in native['sources']+native['objects']+[native['build_log'],native['edf_dependency']]:check(row)
    require(sha(WS/native['library'])==native['library_sha256'],'Changed source library')
    expected_modes=[('item-payloads','standalone'),('item-payloads','full_object'),('item-payloads-sf','standalone'),('item-payloads-sf','full_object')]
    require([(r['probe'],r['mode']) for r in native['runs']]==expected_modes,'Native coverage')
    fixture_rows=reference['inputs']+reference['fixtures']+sf['inputs']+sf['golden']
    fixture_hashes={Path(r['file']).name:r['sha256'] for r in fixture_rows}
    require(len(fixture_hashes)==len(fixture_rows),'Fixture basename collision')
    for run in native['runs']:
        for key in ['exe','map','console','output']:check(run[key])
        for row in run['inputs']:check(row)
        require({Path(r['file']).name:r['sha256'] for r in run['inputs']}==fixture_hashes,'Fixture copy drift')
        require(run['natural_exit']==0 and run['architecture']=='x86' and pe((WS/run['exe']['file']).read_bytes())['architecture']=='x86' and
                run['native']==json.loads((WS/run['output']['file']).read_text()) and run['native']['status']=='PASS','Native execution')
        mapping=(WS/run['map']['file']).read_text()
        symbols=['RF455_ReleaseBoardItemReference','erase@RF455SourceItemManager','createSkillForce@RF455SourceItemManager']
        if run['probe']=='item-payloads':symbols+=['createPayload@RF455SourceItemManager','loadItemEdf@RF455ItemDataStore',
            'localizeItemEdf@RF455ItemDataStore','loadQuestEdf@RF455ItemDataStore','loadCharacterEdf@RF455ItemDataStore','animusLevel@RF455ItemDataStore']
        for symbol in symbols:require(re.search(re.escape(symbol)+r'[^\r\n]*RF455ItemPayloads:',mapping),'Missing exact source provider '+symbol)
        require(re.search('RF455_DecodeEdf'+r'[^\r\n]*RFClient455Facade:client455_language.obj',mapping),'Existing EDF decoder provider missing')
    item=native['runs'][0]['native'];regression=native['runs'][2]['native']
    require(item==native['runs'][1]['native'] and regression==native['runs'][3]['native'],'Standalone/full-object divergence')
    for field,expected in [('real_item_rows',76049),('real_item_tables',47),('real_quest_frames',12),('real_character_frames',7),
                           ('real_quest_rows',2895),('fresh_factory_cases',reference['factory_cases']),('fresh_payloads',575),
                           ('cloned_wrappers',575),('bounded_unsafe_cases',0),('Animus_level_cases',99),('NDItem_locales',3)]:
        require(item[field]==expected,'Missing item branch '+field)
    require(item['concrete_primary_manager'] and item['whole_table_byte_oracles'] and item['source_SF_dispatch'],'Missing concrete runtime')
    for field in ['ordinary_game_binding','Quest_sentence_expansion','full_payload_gameplay','full_client']:require(not item[field],'Unjustified scope')
    require(regression['real_SF_payloads']==1447 and regression['cloned_wrappers']==1447 and not regression['recording_host'] and
            regression['actual_last_owner_erase'] and not regression['ordinary_Linker_bound'],'Existing SF runtime regression')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Ordinary client drift')
    link_hash=sha(WS/'inventory/client455-normal-link.json');ordinary=load('client455-hotbar-checkpoint')
    require(native['normal_link_sha256']==ordinary['normal_link_sha256']==link_hash and
            link['executable']['sha256']=='82625b3ef5c237900146f65531a701a3451d3dbec292a65eef2ed5ece83df6f8' and
            not native['normal_client_relinked'] and not native['ordinary_Linker_changed'],'Ordinary086 unexpectedly changed')
    for name,digest in ordinary['fresh_evidence'].items():require(sha(WS/'inventory'/(name+'.json'))==digest,'Changed086 gate evidence')
    report=dict(status='PARTIAL_SOURCE_RUNTIME',scope='Real Item47/Quest12/Character7 readers and five fresh payload states with concrete manager/087clone-release;ordinary086 current',
        script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-item-payloads-reference.json'),
        native_sha256=sha(WS/'inventory/client455-item-payloads-native.json'),session=dict(file=session_path.relative_to(WS).as_posix(),sha256=sha(session_path)),
        source_sha256={Path(r['file']).name:r['sha256'] for r in native['sources'] if r['file'].startswith('scripts/native/')},
        selected_functions=50,assembly_instructions=1796,real_item_rows=76049,fresh_factory_cases=575,cloned_wrappers=575,Animus_level_cases=99,
        standalone_and_full_object='PASS_BOUNDED',SF1447_regression_same_new_library='PASS_BOUNDED',NDItem_profiles=['zh-tw','ko-kr','ru-ru'],
        ordinary_runtime_gate='inventory/client455-hotbar-checkpoint.json',ordinary_runtime_gate_sha256=sha(WS/'inventory/client455-hotbar-checkpoint.json'),
        normal_link_sha256=link_hash,normal_client_relinked=False,ordinary_Linker_changed=False,
        previous088_runtime_gate='historical source hashes after shared header change;static reference retained;new-library SF regression accepted here',
        unchanged_GPU_startup_suites_rerun=False,gaps=reference['gaps']+[
            'All previous storage/oldbelt/36 board factory classes/Tutorial/fourstage/Login/auth/gameplay/M6F/M7/M9 requirements remain mandatory'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-payloads-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_SOURCE_RUNTIME:76049 item rows/575 fresh factory-owned lifetimes/99 Animus XP cases/3 NDItem profiles;SF1447 regression;ordinary086/M9 OPEN')


if __name__=='__main__':main()
