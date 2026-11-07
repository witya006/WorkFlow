"""Validate actual Linker ownership;keep full window/callback/game acceptance open."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_item_icon_metadata import checked_native
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def frame_hashes(report):return {Path(r['file']).name:r['sha256'] for r in report['frames']}

def main():
    ref=load('client455-linker-owners-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_linker_owners.py') and len(ref['assembly'])==21 and ref['actual_instructions']==1105,'Static coverage/provenance')
    for row in ref['raw_evidence']+ref['inputs']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==21,'Reference identity')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Static range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Pin mismatch')
    session=WS/'artifacts/client455-progress/linker-owners096-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'IDA cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['linker_owners_port_sha256']==sha(WS/'scripts/client455_linker_owners_port.py'),'Migration provenance')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_linker_owners.h','client455_linker_owners.cpp','client455_item_icon_members.inc']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/gameobject/board/common/clinkboard.h','source/gameobject/board/common/clinkboard.cpp','source/userinterface/gamewindow/guiforcebeltwindow.h','generated/client455_linker_owners.cpp']:
        rows=[r for r in manifest if r['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Prepared owner missing '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    normal_map=(WS/link['map']['file']).read_text()
    for symbol,provider in [('AddTypedObject455@CLinkBoard','client455_linker_owners.obj'),('RemoveTypedObject455@CLinkBoard','client455_linker_owners.obj'),('registerIcon@RF455IconLinks','client455_icon_links.obj'),('unregisterIcon@RF455IconLinks','client455_icon_links.obj')]:require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:'+re.escape(provider),normal_map),'Actual normal provider missing '+symbol)
    run=checked_native('client455-linker-owners-native',link_hash);require(run['script_sha256']==sha(WS/'scripts/probe_client455_linker_owners.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-linker-owners-reference.json') and run['architecture']=='x86','Native provenance');check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    wanted={Path(r['file']).name:r['sha256'] for r in ref['inputs']};actual={Path(r['file']).name:r['sha256'] for r in run['inputs']};require(all(actual.get(k)==v for k,v in wanted.items()),'Real data mismatch')
    result=run['native'];require(result['owned_clones']==50 and result['banks']==5 and result['slots_per_bank']==10 and result['fresh_null_callback_cases']==3 and result['explicit_missing_provider_refusals']==4 and result['GPU_frames']==3,'Owner coverage')
    for key in ['ordinary_CLinkBoard_Add_Remove_Clear','original_release_retains_copies','occupied_clone_released','actual_window_icon_owner','registered_quantity_usable','local_reset_after_unregister','all_owners_released','sprite_allocator_balanced','SF_Animus_icons_synthetic']:require(result[key],'Actual contract missing '+key)
    for key in ['full_Linker_window','live_source_board_callbacks','Macro_registration','full_client']:require(not result[key],'Unjustified game completion')
    review=load('client455-linker-owners-visual-review');require(review['native_sha256']==sha(WS/'inventory/client455-linker-owners-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_linker_owners.py') and review['reviewed'] and review['reviewed_frames']==3 and review['frames']==run['frames'],'Visual provenance');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    require(len(set(frame_hashes(run).values()))==3,'No visible update/removal')
    inherited=[]
    for name,old_path,review_name in [('client455-icon-links-native','icon-links095-before096.json','client455-icon-links-visual-review'),('client455-item-icon-metadata-native','item-metadata094-before095.json','client455-item-icon-metadata-visual-review')]:
        current=checked_native(name,link_hash);baseline=WS/'artifacts/client455-progress'/old_path;old=json.loads(baseline.read_text());old_review=load(review_name)
        require(old_review['native_sha256']==sha(baseline) and old_review['reviewed'] and old_review['reviewed_frames']==3 and old['frames']==old_review['frames'],'Previous visual baseline');check(old_review['sheet'])
        require(frame_hashes(current)==frame_hashes(old) and len(current['frames'])==3 and current['native']==old['native'],'Inventory/icon registry regression')
        require(current['source']['sha256']==old['source']['sha256'] and current['script_sha256']==old['script_sha256'],'Regression driver/source drift')
        for row in current['frames']:check(row);check(row['preview'])
        inherited.append(dict(current=name,baseline=record(baseline),visual=record(WS/f'inventory/{review_name}.json'),raw_frames_byte_equal=True))
    checked_native('client455-hotbar-native',link_hash);checked_native('client455-account-native',link_hash);storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not r['natural_exit'] and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for case in storage['runs']:
        for key in ['exe','fixture','console']:check(case[key])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact PE Create');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Engine drift')
    fresh_names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native','client455-item-icon-metadata-native','client455-icon-links-native','client455-linker-owners-visual-review']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-linker-owners-reference.json'),native_sha256=sha(WS/'inventory/client455-linker-owners-native.json'),sources=sources,generated_providers=selected,session=record(session),normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:sha(WS/f'inventory/{name}.json') for name in fresh_names},
        selected_ranges=21,assembly_instructions=1105,owned_clones=50,fresh_null_callback_cases=3,SF_Animus_icons_synthetic=True,explicit_missing_provider_refusals=4,viewed_GPU_frames=3,normal_registration_retained=True,ordinary_CLinkBoard_binding=True,full_Linker_window=False,inherited_visual_evidence=inherited,
        previous095gate='historical runtime after source/link/reports changed;static registry proofs retained',unchanged_world_audio_159k_093atlas_092icon_2013owner_1447SF_suites_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-linker-owners-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:ordinaryLinker50ownedclones/registration/remove-clear/original-release/3viewedGPU/6oldframes-equal/exactPECreate1;fullwindow-callbacks-Macro-game-M9OPEN')
if __name__=='__main__':main()
