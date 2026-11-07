"""Accept selected production icon kernels,without claiming full455UI/gameplay."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def main():
    ref=load('client455-item-icon-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_item_icon.py') and len(ref['assembly'])==18 and ref['actual_instructions']==1740,'Static provenance/coverage')
    for row in ref['raw_evidence']+ref['fixtures']+ref['inputs']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==22,'Reference pin')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Function/EH/table drift')
    session=WS/'artifacts/client455-progress/item-icon092-session.json';closed=json.loads(session.read_text());require(closed['closed']['success'] and closed['closed']['saved'] and closed['after']['count']==0,'IDA cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal production link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    prep=load('client455-normal-preparation');require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['item_icon_port_sha256']==sha(WS/'scripts/client455_item_icon_port.py'),'Preparation source drift')
    names=['client455_item_icon.h','client455_item_icon.cpp','client455_item_icon_members.inc','client455_target_sprites.inc','client455_item_object.cpp'];sources=[record(WS/'scripts/native'/name) for name in names]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared input drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/userinterface/guicontroller/guiitem.h','source/userinterface/guicontroller/guiitem.cpp','source/userinterface/spritemgr.h','source/userinterface/spritemgr.cpp','generated/client455_item_icon.cpp','generated/client455_item_object.cpp']:
        rows=[r for r in manifest if r['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Prepared provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    native=load('client455-item-icon-native');require(native['normal_link_sha256']==link_hash and native['script_sha256']==sha(WS/'scripts/probe_client455_item_icon.py') and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and native['reference_sha256']==sha(WS/'inventory/client455-item-icon-reference.json'),'Native provenance')
    for field in ['source','exe','map','console','output']:check(native[field])
    for row in native['inputs']:check(row)
    require(native['natural_exit']==0 and native['architecture']=='x86' and native['native']==json.loads((WS/native['output']['file']).read_text()) and native['native']['status']=='PASS','Native execution')
    result=native['native'];require(result['grade_byte_values']==256 and result['quantity_boundary_cases']==120 and result['signed_width_cases']==8 and result['actual_GPU_frames']==9 and result['actual_board_icon_index'] and result['actual_sprite_ID6_ID8'] and result['grade_border_not_caption'] and result['sprite_allocator_balanced'],'Selected contract coverage')
    for field in ['automatic_item_atlas_factory','full_GUIItem','full_client']:require(not result[field],'Unjustified fullUI acceptance')
    wanted={Path(r['file']).name:r['sha256'] for r in ref['inputs']+ref['fixtures']};actual={Path(r['file']).name:r['sha256'] for r in native['inputs']};require(all(actual.get(k)==v for k,v in wanted.items()),'Selected native inputs differ')
    mapping=(WS/native['map']['file']).read_text()
    for symbol in ['DrawTypedIcon455@CGUIItem','RF455_ItemGradeColor','RefreshIcon455@CBoardObject']:require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:',mapping),'Actual production provider '+symbol)
    review=load('client455-item-icon-visual-review');require(review['native_sha256']==sha(WS/'inventory/client455-item-icon-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_item_icon.py') and review['reviewed'] and review['reviewed_frames']==9 and review['frames']==native['frames'],'Visual review provenance');check(review['sheet'])
    for frame in review['frames']:check(frame);check(frame['preview'])
    parent=(WS/native['exe']['file']).parent
    for a,b,equal in [('full','quantity-hidden',True),('full','no-border',False),('full','unusable',False),('quantity','quantity-hidden',False),('hidden','no-image',True)]:
        require(((parent/f'icons-{a}.bgra').read_bytes()==(parent/f'icons-{b}.bgra').read_bytes())==equal,'Actual frame relation')
    owners=load('client455-item-object-native');require(owners['normal_link_sha256']==link_hash and owners['script_sha256']==sha(WS/'scripts/probe_client455_item_object.py') and owners['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Typed owner regression provenance')
    require(len(owners['runs'])==3,'Owner/data/SF coverage')
    for run in owners['runs']:
        for field in ['source','exe','map','console','output']:check(run[field])
        for row in run['inputs']:check(row)
        require(run['natural_exit']==0 and run['native']['status']=='PASS' and run['native']==json.loads((WS/run['output']['file']).read_text()),'Production owner/data/SF execution')
    owner=owners['runs'][0]['native'];require(owner['cloned_wrappers']==2013 and owner['real_SF_owners']==1447 and owner['real_other_owners']==566 and owner['icon_index_grade_binding'] and not owner['full_icon_provider'] and not owner['normal_bootstrap_load'] and not owner['full_Linker_ownership'],'Owner partial scope')
    require(owners['runs'][1]['native']['fresh_payloads']==575 and owners['runs'][2]['native']['real_SF_payloads']==1447,'Actual production data/SF regression')
    for name in ['client455-hotbar-native','client455-account-native']:
        report=load(name);require(report['normal_link_sha256']==link_hash and report['natural_exit']==0 and report['native']['status']=='PASS','Affected regression')
        for field in ['exe','map','output']:check(report[field])
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and all(r['natural_exit']==0 and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for run in storage['runs']:
        for field in ['exe','fixture','console']:check(run[field])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact own PE Create');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Engine drift')
    fresh_names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native','client455-item-object-native','client455-item-icon-visual-review']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-item-icon-reference.json'),native_sha256=sha(WS/'inventory/client455-item-icon-native.json'),
        session=record(session),sources=sources,generated_providers=selected,normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:sha(WS/f'inventory/{name}.json') for name in fresh_names},
        selected_ranges=22,actual_instructions=1740,grade_values=256,quantity_cases=120,signed_width_cases=8,viewed_GPU_frames=9,production_owner2013_payload575_SF1447_regression='PASS_BOUNDED',
        previous091gate='historical runtime gate after changed normal/report/source;static references and whole-record oracles retained',unchanged_world_audio_159k_suites_rerun=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-icon-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:typed icon index/256grades/120quantities/8widths/9viewedGPU/production2013-575-1447/exactPECreate1;fullUI-game-M9 OPEN')
if __name__=='__main__':main()
