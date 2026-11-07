"""Validate bounded icon-link migration without claiming ordinary board integration."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_item_icon_metadata import checked_native
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def main():
    ref=load('client455-icon-links-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_icon_links.py') and len(ref['assembly'])==22 and ref['actual_instructions']==1154 and ref['key_cases']==160,'Static coverage/provenance')
    for row in ref['raw_evidence']+ref['inputs']+ref['fixtures']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==22,'Reference identity')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Static range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'] and [r['value'] for r in ref['decoded_operands']]==[0xfffffff,0xfffffff,28,60],'Pin/key operand mismatch')
    session=WS/'artifacts/client455-progress/icon-links095-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'IDA cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['icon_links_port_sha256']==sha(WS/'scripts/client455_icon_links_port.py'),'Migration provenance')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_icon_links.h','client455_icon_links.cpp','client455_item_icon_members.inc']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/mainapp.h','source/userinterface/guicontroller/guiitem.h','generated/client455_icon_links.cpp']:
        rows=[r for r in manifest if r['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Prepared provider missing '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    normal_map=(WS/link['map']['file']).read_text();ordinary={}
    for symbol in ['SetNum455@CGUIItem','SetUsable455@CGUIItem','find@RF455IconLinks']:
        match=re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_icon_links.obj',normal_map);require(match,'Typed fanout absent from normal PE '+symbol);ordinary[symbol]=True
    run=checked_native('client455-icon-links-native',link_hash);require(run['script_sha256']==sha(WS/'scripts/probe_client455_icon_links.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-icon-links-reference.json') and run['architecture']=='x86','Native provenance');check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    wanted={Path(r['file']).name:r['sha256'] for r in ref['inputs']+ref['fixtures']};actual={Path(r['file']).name:r['sha256'] for r in run['inputs']};require(all(actual.get(k)==v for k,v in wanted.items()),'Native inputs/oracle mismatch')
    result=run['native'];require(result['key_oracles']==160 and result['unsafe_removal_refusals']==2 and result['registered_real_copies']==2 and result['GPU_frames']==3,'Native domain coverage')
    for key in ['actual_MainApp_registry','duplicate_append_first_remove','empty_buckets_retained','current_identity_lookup','WORD_quantity_rawBYTE_usable','unregistered_original_not_a_member','untyped_legacy_local','real_inventory_original','all_owners_cleared','sprite_allocator_balanced']:require(result[key],'Missing actual contract '+key)
    require(not result['ordinary_Linker_Macro_registration'] and not result['full_client'],'Unjustified game completion')
    mapping=(WS/run['map']['file']).read_text()
    for symbol in ['RF455_IconLinkKey','registerIcon@RF455IconLinks','unregisterIcon@RF455IconLinks','SetNum455@CGUIItem','SetUsable455@CGUIItem']:require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_icon_links.obj',mapping),'Production provider '+symbol)
    review=load('client455-icon-links-visual-review');require(review['native_sha256']==sha(WS/'inventory/client455-icon-links-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_icon_links.py') and review['reviewed'] and review['reviewed_frames']==3 and review['frames']==run['frames'],'Visual review provenance');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    require(len({r['sha256'] for r in run['frames']})==3,'Propagation/detach made no visible difference')
    metadata=checked_native('client455-item-icon-metadata-native',link_hash);baseline=WS/'artifacts/client455-progress/item-metadata094-before095.json';old=json.loads(baseline.read_text());previous_review=load('client455-item-icon-metadata-visual-review')
    require(previous_review['native_sha256']==sha(baseline) and previous_review['reviewed'] and previous_review['reviewed_frames']==3 and old['frames']==previous_review['frames'],'Previous metadata visual provenance');check(previous_review['sheet'])
    before={Path(r['file']).name:r['sha256'] for r in old['frames']};after={Path(r['file']).name:r['sha256'] for r in metadata['frames']};require(len(before)==3 and before==after,'Metadata GPU regression')
    require(metadata['native']==old['native'] and metadata['source']['sha256']==old['source']['sha256'] and metadata['script_sha256']==sha(WS/'scripts/probe_client455_item_icon_metadata.py'),'Metadata regression provenance')
    for row in metadata['frames']:check(row);check(row['preview'])
    checked_native('client455-hotbar-native',link_hash);checked_native('client455-account-native',link_hash);storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not r['natural_exit'] and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for case in storage['runs']:
        for key in ['exe','fixture','console']:check(case[key])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact current PE Create');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Engine drift')
    fresh_names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native','client455-item-icon-metadata-native','client455-icon-links-visual-review']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-icon-links-reference.json'),native_sha256=sha(WS/'inventory/client455-icon-links-native.json'),sources=sources,generated_providers=selected,session=record(session),normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:sha(WS/f'inventory/{name}.json') for name in fresh_names},
        selected_ranges=22,assembly_instructions=1154,key_oracles=160,registered_real_copies=2,viewed_GPU_frames=3,ordinary_fanout_retained=ordinary,normal_registration_retained='registerIcon@RF455IconLinks' in normal_map,
        previous094_metadata_baseline=record(baseline),previous094_visual_review=record(WS/'inventory/client455-item-icon-metadata-visual-review.json'),previous094_frames_byte_equal=True,ordinary_Linker_Macro_registration=False,previous094gate='historical runtime after source/link/reports changed;static metadata proofs and visual evidence retained',unchanged_world_audio_159k_093atlas_092icon_2013owner_1447SF_suites_rerun=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-icon-links-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:160keys/actualMainApp-registry/fanout/removal/3viewedGPU/094frames-equal/exactPECreate1;ordinaryLinker-Macro-registration/fullboard/game/M9OPEN')
if __name__=='__main__':main()
