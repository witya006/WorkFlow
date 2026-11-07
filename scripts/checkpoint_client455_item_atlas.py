"""Verify production atlas selection while keeping fullclient acceptance open."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def native(name,link_hash):
    report=load(name);require(report['normal_link_sha256']==link_hash and report['natural_exit']==0 and report['native']['status']=='PASS','Current native execution '+name)
    for key in ['exe','map','output']:check(report[key])
    require(report['native']==json.loads((WS/report['output']['file']).read_text()),'Native result drift');return report

def main():
    ref=load('client455-item-atlas-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_item_atlas.py') and len(ref['assembly'])==17 and ref['actual_instructions']==1001 and len(ref['decoded_byte_stores'])==47 and ref['atlas_cases']==880,'Static coverage/provenance')
    for row in ref['raw_evidence']+ref['inputs']+ref['fixtures']+[ref['regression_baseline']]:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(binary)['architecture']=='x86' and len(pin['ranges'])==18,'Changed reference pin')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(binary,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Static range drift')
    session=WS/'artifacts/client455-progress/item-atlas093-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'IDA cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['item_icon_port_sha256']==sha(WS/'scripts/client455_item_icon_port.py'),'Port preparation drift')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_item_atlas.h','client455_item_atlas.cpp','client455_item_icon.h','client455_item_icon.cpp','client455_item_icon_members.inc','client455_target_sprites.inc']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/userinterface/guicontroller/guiitem.h','source/userinterface/guicontroller/guiitem.cpp','source/userinterface/spritemgr.h','generated/client455_item_atlas.cpp']:
        rows=[r for r in manifest if r['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Missing prepared provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    run=native('client455-item-atlas-native',link_hash);require(run['script_sha256']==sha(WS/'scripts/probe_client455_item_atlas.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-item-atlas-reference.json') and run['architecture']=='x86','Atlas native provenance');check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    wanted={Path(r['file']).name:r['sha256'] for r in ref['inputs']+ref['fixtures']};actual={Path(r['file']).name:r['sha256'] for r in run['inputs']};require(all(actual.get(k)==v for k,v in wanted.items()),'Native oracle/input mismatch')
    result=run['native'];require(result['atlas_cases']==880 and result['callback_failures']==563 and result['unsigned_WORD_row_wrap_cases']==2 and result['actual_manager_callback_fallback'] and result['actual_GUIItem_SetSprite'] and result['automatic_sample_icons']==16 and result['GPU_frames']==4 and result['sprite_allocator_balanced'],'Atlas runtime coverage')
    for key in ['payload_metadata_binding','full_GUIItem_children','full_client']:require(not result[key],'Overstated completion')
    mapping=(WS/run['map']['file']).read_text()
    for symbol in ['RF455_ItemSpriteSearch455','RF455_UnitPartsSearch455','GetTargetSpriteInfo455@CSpriteMgr','SetTypedSprite455@CGUIItem']:require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_item_atlas.obj',mapping),'Missing production provider '+symbol)
    review=load('client455-item-atlas-visual-review');require(review['native_sha256']==sha(WS/'inventory/client455-item-atlas-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_item_atlas.py') and review['reviewed'] and review['reviewed_frames']==4 and review['frames']==run['frames'],'Visual review provenance');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    icons=native('client455-item-icon-native',link_hash);require(icons['script_sha256']==sha(WS/'scripts/probe_client455_item_icon.py') and icons['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Icon regression provenance');check(icons['source'])
    for row in icons['inputs']:check(row)
    for row in icons['frames']:check(row);check(row['preview'])
    old={Path(r['file']).name:r['sha256'] for r in ref['regression_frames']};new={Path(r['file']).name:r['sha256'] for r in icons['frames']};require(old==new and len(old)==9,'Previously viewed092frames changed')
    owners=load('client455-item-object-native');require(owners['normal_link_sha256']==link_hash and owners['script_sha256']==sha(WS/'scripts/probe_client455_item_object.py') and len(owners['runs'])==3,'Owner regression provenance')
    for case in owners['runs']:
        require(case['natural_exit']==0 and case['native']['status']=='PASS' and case['native']==json.loads((WS/case['output']['file']).read_text()),'Owner/data/SF runtime')
        for key in ['source','exe','map','output','console']:check(case[key])
        for row in case['inputs']:check(row)
    require(owners['runs'][0]['native']['cloned_wrappers']==2013 and owners['runs'][1]['native']['fresh_payloads']==575 and owners['runs'][2]['native']['real_SF_payloads']==1447,'Owner/data/SF coverage')
    native('client455-hotbar-native',link_hash);native('client455-account-native',link_hash);storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not r['natural_exit'] and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for case in storage['runs']:
        for key in ['exe','fixture','console']:check(case[key])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact own PE Create');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Unexpected engine change')
    fresh_names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native','client455-item-object-native','client455-item-icon-native','client455-item-atlas-visual-review']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-item-atlas-reference.json'),native_sha256=sha(WS/'inventory/client455-item-atlas-native.json'),session=record(session),sources=sources,generated_providers=selected,
        normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:sha(WS/f'inventory/{name}.json') for name in fresh_names},selected_ranges=18,assembly_instructions=1001,decoded_stores=47,atlas_cases=880,viewed_GPU_frames=4,unchanged092_GPU_frame_hashes=9,
        production_owner2013_data575_SF1447='PASS_BOUNDED',previous092gate='historical runtime after newsource/link/reports;staticreferences and priorvisualframebaseline retained',unchanged_world_audio_159k_suites_rerun=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-atlas-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:880atlas cases/actualautomaticGUIItem/4viewedGPU/9unchangedframes/owners-data-SF/exactPECreate1;payloadbinding-fullgame-M9OPEN')
if __name__=='__main__':main()
