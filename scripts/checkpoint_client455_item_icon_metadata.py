"""Check physical metadata/inventory core without claiming full item-board integration."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def checked_native(name,link_hash):
    report=load(name);require(report['normal_link_sha256']==link_hash and report['natural_exit']==0 and report['native']['status']=='PASS','Current native '+name)
    for key in ['exe','map','output']:check(report[key])
    require(report['native']==json.loads((WS/report['output']['file']).read_text()),'Result drift');return report

def main():
    ref=load('client455-item-icon-metadata-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_item_icon_metadata.py') and len(ref['assembly'])==22 and ref['actual_instructions']==1138 and len(ref['decoded_offsets'])==15,'Static coverage/provenance')
    for row in ref['raw_evidence']+ref['inputs']+ref['fixtures']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==28,'Reference identity')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Static range drift')
    session=WS/'artifacts/client455-progress/item-metadata094-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'IDA cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['item_metadata_port_sha256']==sha(WS/'scripts/client455_item_metadata_port.py'),'Migration provenance')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_item_icon_metadata.h','client455_item_icon_metadata.cpp','client455_item_payloads.h','client455_item_atlas.cpp','client455_item_icon.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/userinterface/gamewindow/guiinventorywindow.h','source/userinterface/gamewindow/guiinventorywindow.cpp','generated/client455_item_icon_metadata.cpp']:
        rows=[r for r in manifest if r['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Prepared provider missing '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    inventory_source=(WS/next(r['file'] for r in selected if r['file'].lower().endswith('/guiinventorywindow.cpp'))).read_bytes();require(b'return TakeInItemFields455(slot,itemID,spriteID,quantity,required,_GetAvatarRace());' in inventory_source,'Ordinary inventory caller not connected')
    normal_map=(WS/link['map']['file']).read_text();require(re.search(r'TakeInItemFields455@CGUIInventoryBoard[^\r\n]*RFClient455Facade:client455_item_icon_metadata.obj',normal_map),'Inventory core absent from normal PE')
    run=checked_native('client455-item-icon-metadata-native',link_hash);require(run['script_sha256']==sha(WS/'scripts/probe_client455_item_icon_metadata.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-item-icon-metadata-reference.json') and run['architecture']=='x86','Native provenance');check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    wanted={Path(r['file']).name:r['sha256'] for r in ref['inputs']+ref['fixtures']};actual={Path(r['file']).name:r['sha256'] for r in run['inputs']};require(all(actual.get(k)==v for k,v in wanted.items()),'Native inputs/oracle mismatch')
    result=run['native'];require(result['real_metadata_cases']==566 and result['Quest_refusals']==9 and result['SF_refusal'] and result['bounded_cases']==0 and result['race_level_cases']==520 and result['actual_inventory_icon_owners']==16 and result['GPU_frames']==3,'Metadata/owner coverage')
    for key in ['actual_game_data_manager','actual_pack_clones','BYTE_quantity_and_sticky_FF','invalid_ID_detaches','all_payload_owners_released','sprite_allocator_balanced']:require(result[key],'Missing actual contract '+key)
    for key in ['ordinary_CItemBoard_Add','full_inventory','full_client']:require(not result[key],'Unjustified fullgame completion')
    mapping=(WS/run['map']['file']).read_text()
    for symbol in ['RF455_ReadBasicIconMetadata','RF455_IconUsable455','TakeInItem455@CGUIInventoryBoard','TakeInItemFields455@CGUIInventoryBoard']:require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_item_icon_metadata.obj',mapping),'Production provider '+symbol)
    review=load('client455-item-icon-metadata-visual-review');require(review['native_sha256']==sha(WS/'inventory/client455-item-icon-metadata-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_item_icon_metadata.py') and review['reviewed'] and review['reviewed_frames']==3 and review['frames']==run['frames'],'Visual review provenance');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    frames={Path(r['file']).name:WS/r['file'] for r in run['frames']};require(frames['metadata-real-items.bgra'].read_bytes()!=frames['metadata-updated-item.bgra'].read_bytes(),'Update made no visible difference')
    checked_native('client455-hotbar-native',link_hash);checked_native('client455-account-native',link_hash);storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not r['natural_exit'] and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for case in storage['runs']:
        for key in ['exe','fixture','console']:check(case[key])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact current PE Create');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Engine drift')
    fresh_names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native','client455-item-icon-metadata-visual-review']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-item-icon-metadata-reference.json'),native_sha256=sha(WS/'inventory/client455-item-icon-metadata-native.json'),sources=sources,generated_providers=selected,session=record(session),normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:sha(WS/f'inventory/{name}.json') for name in fresh_names},
        selected_ranges=28,assembly_instructions=1138,decoded_offsets=15,real_metadata_cases=566,Quest_refusals=9,race_level_cases=520,actual_inventory_icon_owners=16,viewed_GPU_frames=3,ordinary_inventory_fields_core_retained=True,
        normal_basic_metadata_reader_retained='RF455_ReadBasicIconMetadata' in normal_map,full_payload_to_board_event_binding=False,previous093gate='historical runtime after new source/link/reports;static atlas evidence retained',unchanged_world_audio_159k_093atlas_092icon_2013owner_1447SF_suites_rerun=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-icon-metadata-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:566realmetadata/520race-level/16realinventoryicons/3viewedGPU/ordinaryfields-core/exactPECreate1;fullboard-events-game-M9OPEN')
if __name__=='__main__':main()
