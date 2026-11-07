"""Validate selected typed timer integration; leave full455 acceptance open."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_item_icon_metadata import checked_native
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def main():
    ref=load('client455-gui-timer-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_gui_timer.py') and (ref['assembly_functions'],ref['assembly_instructions'],ref['state_cases'],ref['label_cases'],ref['radial_cases'],ref['radial_triangles'])==(29,2791,175,112,57,171),'Static timer coverage')
    require(ref['decoded_control_word']==0x27f and ref['decoded_pi']==3.1415927410125732421875,'Decoded numeric constants')
    for row in ref['raw_evidence']+ref['inputs']+ref['fixtures']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==32,'Reference identity')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Static range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Selected pins differ')
    session=WS/'artifacts/client455-progress/gui-timer098-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'IDA session cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal client link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['gui_timer_port_sha256']==sha(WS/'scripts/client455_gui_timer_port.py'),'Migration provenance')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_gui_timer.h','client455_gui_timer.cpp','client455_item_icon.cpp','client455_item_icon_members.inc','client455_icon_links.cpp','client455_linker_owners.cpp','client455_linker_window.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/userinterface/guicontroller/guiitem.h','source/userinterface/guicontroller/guiitem.cpp','generated/client455_gui_timer.cpp','generated/client455_item_icon.cpp','generated/client455_icon_links.cpp']:
        rows=[r for r in manifest if r['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Prepared provider missing '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    mapping=(WS/link['map']['file']).read_text();retained={}
    for symbol,provider in [('BeginDelayAnimation455@CGUIItem','client455_icon_links.obj'),('Start455@RF455GuiTimer','client455_gui_timer.obj'),('Update@RF455GuiTimer','client455_gui_timer.obj'),('DrawWithSink455@RF455GuiTimer','client455_gui_timer.obj')]:
        match=re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:'+re.escape(provider),mapping);require(match,'Normal retained timer provider missing '+symbol);retained[symbol]=match.group(0)
    run=checked_native('client455-gui-timer-native',link_hash);require(run['script_sha256']==sha(WS/'scripts/probe_client455_gui_timer.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-gui-timer-reference.json') and run['architecture']=='x86','Native provenance');check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    result=run['native'];require((result['state_cases'],result['label_cases'],result['radial_cases'],result['radial_triangles'],result['GPU_frames'])==(175,112,57,171,6),'Native timer domain')
    for key in ['ctor_partial_writes','ordinary_copy_empty_update','actual_registry_fanout','actual_Linker_timer_query','all_owners_released','sprite_allocator_balanced']:require(result[key],'Native integration missing '+key)
    require(not result['full_client'] and not result['full_gameplay'],'Unjustified gameplay acceptance')
    review=load('client455-gui-timer-visual-review');require(review['native_sha256']==sha(WS/'inventory/client455-gui-timer-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_gui_timer.py') and review['reviewed'] and review['reviewed_frames']==6 and review['frames']==run['frames'],'Timer visual review');check(review['sheet'])
    for row in run['frames']:check(row);check(row['preview'])
    checks={};viewed=6
    for name,count in [('client455-linker-window',8),('client455-linker-owners',3),('client455-item-icon-metadata',3),('client455-item-icon',9)]:
        current=checked_native(name+'-native',link_hash);visual=load(name+'-visual-review');require(visual['native_sha256']==sha(WS/f'inventory/{name}-native.json') and visual['reviewed'] and visual['reviewed_frames']==count and visual['frames']==current['frames'],'Fresh changed dependency visuals '+name);check(visual['sheet']);viewed+=count;checks[name]=sha(WS/f'inventory/{name}-native.json')
        for row in current['frames']:check(row);check(row['preview'])
    window=load('client455-linker-window-native')['native'];require(window['actual_typed_timer_query'] and window['event_cases']==48 and window['actual_owned_icons']==50,'Actual Linker timer query/window regression')
    deltas=[r for group in review['regressions'] for r in group['frames']];require(len(deltas)==23,'Changed layer baseline frame coverage')
    require(sum(r['changed_pixels']>0 for r in deltas)==11 and sum(r['changed_pixels']==0 for r in deltas)==12,'Changed frame order accounting')
    for group in review['regressions']:check(group['baseline'])
    for row in deltas:
        if row['name'].startswith('glyph-') or row['name'] in ['metadata-empty.bgra','icons-clipped.bgra','icons-no-border.bgra','icons-hidden.bgra','icons-no-image.bgra']:require(row['changed_pixels']==0 and row['before']==row['after'],'Untouched glyph/clip/empty regression')
    checked_native('client455-hotbar-native',link_hash);checked_native('client455-account-native',link_hash);storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not r['natural_exit'] and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for case in storage['runs']:
        for key in ['exe','fixture','console']:check(case[key])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact own PE Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Engine drift')
    fresh=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native']+[name+suffix for name in ['client455-linker-window','client455-linker-owners','client455-item-icon-metadata','client455-item-icon'] for suffix in ['-native','-visual-review']]
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-gui-timer-reference.json'),native_sha256=sha(WS/'inventory/client455-gui-timer-native.json'),visual_sha256=sha(WS/'inventory/client455-gui-timer-visual-review.json'),sources=sources,generated_providers=selected,retained=retained,session=record(session),normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:sha(WS/f'inventory/{name}.json') for name in fresh},selected_ranges=32,assembly_instructions=2791,state_cases=175,label_cases=112,radial_cases=57,radial_triangles=171,viewed_GPU_frames=viewed,layer_order_baselines=review['regressions'],stop_fanout_present_in_full_object_probe_but_unused_in_normal_PE=True,previous097gate='historical runtime after source/link/reports changed;static window proofs retained',unchanged_world_audio_159k_093atlas_2013owner_1447SF_095manual_suites_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-gui-timer-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:175states/112labels/57radial-171triangles/ordinarycopy-update-fanout/29viewedGPU/exactPECreate1;fullhandlers-cooldown-game-M9OPEN')
if __name__=='__main__':main()
