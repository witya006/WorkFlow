"""Accept typed ordinary wrappers/null-icon ownership without closing gameplay."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def main():
    ref=load('client455-item-object-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_item_object.py') and len(ref['assembly'])==14 and ref['actual_instructions']==444,'Reference source/coverage')
    for row in ref['raw_evidence']+ref['inputs']+ref['fixtures']:check(row)
    for name,field in [('resource-object','base_reference_sha256'),('item-payloads','payload_reference_sha256'),('skill-force-items','SF_reference_sha256')]:
        require(ref[field]==sha(WS/f'inventory/client455-{name}-reference.json'),'Changed reference chain')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==21,'Changed reference identity')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Function/EH drift')
    session_path=WS/'artifacts/client455-progress/item-object091-session.json';session=json.loads(session_path.read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'IDA cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Ordinary link')
    link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['item_object_port_sha256']==sha(WS/'scripts/client455_item_object_port.py'),'Migration source drift')
    names=['client455_client_items.h','client455_item_object.h','client455_board_object.inc','client455_item_object.cpp','client455_item_ownership.h','client455_item_ownership.cpp','client455_skill_force_items.h','client455_skill_force_items.cpp','client455_item_payloads.h','client455_item_payloads.cpp','client455_hotbar_bridge.inc']
    sources=[record(WS/'scripts/native'/name) for name in names]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    manifest=json.loads((WS/prep['manifest']).read_text());check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));selected=[]
    for suffix in ['source/item/citemdata.h','source/item/citemdata.cpp','source/mainapp.h','source/gameobject/board/common/clinkboard.cpp','generated/client455_item_object.cpp','generated/client455_item_ownership.cpp','generated/client455_skill_force_items.cpp','generated/client455_item_payloads.cpp']:
        rows=[r for r in manifest if r['file'].endswith('/'+suffix)];require(len(rows)==1,'Prepared provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    native=load('client455-item-object-native');require(native['normal_link_sha256']==link_hash and native['script_sha256']==sha(WS/'scripts/probe_client455_item_object.py') and
        native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and native['reference_sha256']==sha(WS/'inventory/client455-item-object-reference.json'),'Native provenance')
    require([r['name'] for r in native['runs']]==['item-object','item-object-data','item-object-sf'],'Native coverage')
    fixture_hashes={Path(r['file']).name:r['sha256'] for r in ref['inputs']+ref['fixtures']}
    for run in native['runs']:
        for key in ['source','exe','map','console','output']:check(run[key])
        for row in run['inputs']:check(row)
        require({Path(r['file']).name:r['sha256'] for r in run['inputs']}==fixture_hashes and run['natural_exit']==0 and run['architecture']=='x86' and run['native']['status']=='PASS' and
                run['native']==json.loads((WS/run['output']['file']).read_text()),'Native execution/input provenance')
        mapping=(WS/run['map']['file']).read_text()
        factory='createSkillForce@RF455SourceItemManager' if run['name']=='item-object-sf' else 'createPayload@RF455SourceItemManager'
        for symbol in [factory,'RF455_ReleaseBoardItemReference']:
            require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:',mapping),'Actual production provider missing '+symbol)
    owner=native['runs'][0]['native'];require(owner['CItemObject_size']==592 and owner['CBoardObject_size']==620 and owner['whole_record_oracles']==2 and
        owner['real_SF_owners']==1447 and owner['real_other_owners']==566 and owner['cloned_wrappers']==2013 and owner['Quest_name_refusals']==9 and owner['signed_BYTE_cases']==7,'Typed source coverage')
    require(owner['actual_game_global_manager'] and owner['actual_source_pack_removal'] and owner['primary_empty_retired_guard'] and owner['ordinary_hotbar_metadata'],'Concrete owner branch')
    for field in ['icon_provider','normal_bootstrap_load','full_Linker_ownership','full_client']:require(not owner[field],'Unjustified full-game acceptance')
    require(native['runs'][1]['native']['fresh_payloads']==575 and native['runs'][2]['native']['real_SF_payloads']==1447,'Production data/SF regression')
    mapping=(WS/native['runs'][0]['map']['file']).read_text()
    for symbol in ['SetItem455@CItemObject','Clear@CItemObject','Clone@CBoardObject','RF455_GameItems']:
        require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_item_object.obj',mapping),'Typed provider '+symbol)
    fresh_names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native']
    fresh={name:sha(WS/'inventory'/(name+'.json')) for name in fresh_names}
    for name in ['client455-hotbar-native','client455-account-native']:
        report=load(name);require(report['normal_link_sha256']==link_hash and report['natural_exit']==0 and report['native']['status']=='PASS','Affected ordinary regression')
        for field in ['exe','map','output']:check(report[field])
        require(report['native']==json.loads((WS/report['output']['file']).read_text()),'Affected result drift')
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and all(r['natural_exit']==0 and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for run in storage['runs']:
        for key in ['exe','fixture','console']:check(run[key])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and
        not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and
        any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact new PE Create')
    check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Engine unexpectedly changed')
    report=dict(status='PARTIAL',scope='Actual ordinary typed item592/board620/shared payload manager and source pack lifetime/null-icon domain;full gameplay owners still open',
        script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-item-object-reference.json'),native_sha256=sha(WS/'inventory/client455-item-object-native.json'),
        session=record(session_path),sources=sources,generated_providers=selected,normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence=fresh,
        selected_functions=21,assembly_instructions=444,real_typed_owners=2013,whole_record_oracles=2,Quest_name_refusals=9,
        production_payload575_SF1447_regression='PASS_BOUNDED',engine_unchanged_sha256=engine['library_sha256'],
        previous090gate='historical after new normal link/reports;its static base reference/oracles retained',
        unchanged_GPU_audio_159k_suites_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-object-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:ordinary592/620/2013owners/actualmanager-pack/metadata/production575-1447/exactPECreate1 PASS;icon-bootstrap-game/M9 OPEN')
if __name__=='__main__':main()
