"""Verify the selected aiming core and current integration, leaving full455 open."""
import hashlib
import json
import re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    ref=load('client455-nuclear-aiming-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_nuclear_aiming.py') and (ref['functions'],ref['instructions'])==(19,1670),'Selected reference provenance')
    for row in [ref['raw_evidence'],ref['effect_input_reference'],ref['audio_input_reference']]+ref['inputs']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for pin,folder,key in zip(ref['references'],['current','reference-backup'],['behavior_reference','secondary_reference']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';data=binary.read_bytes()
        require(sha(binary)==pin['sha256']==pins[key]['sha256'] and pe(data)['architecture']=='x86' and pin['image_base']=='0x400000','Pinned x86 input')
        require(len(pin['ranges'])==19 and len(pin['pick_slots'])==2,'Selected coverage')
        for row in pin['ranges']+pin['pick_slots']:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Reference bytes drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'] and ref['references'][0]['pick_slots']==ref['references'][1]['pick_slots'],'Reference equivalence')
    session=WS/'artifacts/client455-progress/nuclear107-session.json';state=json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'Owned IDA cleanup')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS' and link['client_objects']==182,'Ordinary executable')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['nuclear_aiming_port_sha256']==sha(WS/'scripts/client455_nuclear_aiming_port.py'),'Port provenance')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'],'Current build')
    require(len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==60,'Facade coverage')
    check(dict(file=build['log'],sha256=build['log_sha256']));check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    sources=[record(WS/'scripts/native'/name) for name in ['client455_nuclear_aiming.h','client455_nuclear_aiming.cpp','client455_magic_move.inc','client455_board_hover.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared input drift')
    manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/mainapp.h','source/mainapp.cpp','source/addcodebyjang/foreffect.cpp','source/addcodebyjang/effectcore.cpp','generated/client455_nuclear_aiming.cpp']:
        rows=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    source=WS/'work/client455-port/normal/source'
    require(b'RF455NuclearAiming m_nuclearAiming455;' in (source/'mainapp.h').read_bytes(),'Actual MainApp member')
    require(b'RF455_NuclearAiming().FrameMove();' in (source/'addcodebyjang/foreffect.cpp').read_bytes(),'Ordinary frame hook')
    require(b'm_nuclearAiming455.Clear();' in (source/'mainapp.cpp').read_bytes(),'Ordinary teardown hook')
    mapping=(WS/link['map']['file']).read_text();retained={}
    for symbol,owner in [('FrameMove@RF455NuclearAiming','RFClient455Facade:client455_nuclear_aiming.obj'),('Clear@RF455NuclearAiming','RFClient455Facade:client455_nuclear_aiming.obj'),('MovePosMagicEffect@@','effectcore.obj')]:
        match=re.search(re.escape(symbol)+r'[^\r\n]*\s'+re.escape(owner)+r'\s*$',mapping,re.M);require(match,'Retained ordinary provider '+symbol);retained[symbol]=match.group(0).strip()
    run=checked_native('client455-nuclear-aiming-native',link_hash)
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_aiming.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py') and run['source']['sha256']==sha(WS/'scripts/native/client455_nuclear_aiming_probe.cpp') and run['reference_sha256']==sha(WS/'inventory/client455-nuclear-aiming-reference.json'),'Native provenance')
    check(run['world_input_manifest']);check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    require(run['inputs_unchanged'],'Fixture input integrity')
    result=run['native'];require(result['checks']==29 and result['warnings']==7 and result['owner_bytes']==20 and result['real_effect_children']==6 and 0<result['drain_ticks']<300 and result['memory_before']==result['memory_after'],'Native selected domain')
    for key in ['actual_MainApp_owner','real_world_cursor','real_Miles_radar','track_offsets_preserved','repeated_pending_retains','pending_zero_retains_visual_and_sound','clear_stops_with_handle','missing_effect_sound_quirk','scoped_memory_balanced','muted_lab']:require(result[key],'Native '+key)
    for key in ['C1A_message','full_nuclear_owner','full_world_frame_order','full_client']:require(not result[key],'Unjustified acceptance '+key)
    for name,count in [('magic',36),('effect-resources',66),('player-status',62),('tagged-audio',157),('effect-runtime',573)]:require(checked_native(f'client455-{name}-native',link_hash)['native']['checks']==count,'Regression '+name)
    status=load('client455-player-status-native')['native'];require(status['pending_zero_allows_hover_clear'] and status['nuclear_refusal_before_mutation'],'Real pending0/synthetic pending1 disclosure')
    gpu=load('client455-effect-runtime-native');hover=checked_native('client455-board-hover-native',link_hash)
    for name,report,count in [('effect-runtime',gpu,4),('board-hover',hover,6)]:
        review=load(f'client455-{name}-visual-review');require(review['reviewed'] and review['reviewed_frames']==count and review['frames']==report['frames'] and review['native_sha256']==sha(WS/f'inventory/client455-{name}-native.json'),'Viewed '+name);check(review['sheet'])
        for row in report['frames']:check(row);check(row['preview'])
    baseline=WS/'artifacts/client455-progress/client455-board-hover-native-before107.json';before={Path(row['file']).name:row for row in json.loads(baseline.read_text())['frames']}
    require(len(before)==len(hover['frames'])==6,'Hover frame coverage')
    for row in hover['frames']:check(before[Path(row['file']).name]);require(row['sha256']==before[Path(row['file']).name]['sha256'],'Changed hover pixels')
    require(hover['native']['all_owners_released'] and hover['native']['sprite_allocator_balanced'],'Hover ownership')
    checked_native('client455-account-native',link_hash);require(checked_native('client455-hotbar-native',link_hash)['native']['actual_packets']==7,'Hotbar regression')
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not row['natural_exit'] and row['native']['registered']==17 for row in storage['runs']),'Storage regression')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own executable Create1')
    ready=[row['value'] for row in ui['nation_paths'] if row.get('value','').startswith('RF455 TaggedAudio:ready:7969:')];require(len(ready)==1,'Actual ordinary audio provider');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Unchanged engine');check(engine['baseline_library'])
    fresh=['nuclear-aiming-reference','nuclear-aiming-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native','magic-native','effect-resources-native','effect-runtime-native','effect-runtime-visual-review','player-status-native','tagged-audio-native','board-hover-native','board-hover-visual-review','account-native','hotbar-native','storage-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),session=record(session),sources=sources,generated_providers=providers,retained=retained,normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},nuclear_core_checks=29,real_BSP_cursor=True,real_Miles_radar=True,actual_MainApp_owner=True,pending_zero_hover_allowed=True,pending_one_hover_explicit_refusal=True,viewed_GPU_frames=10,byte_equal_hover_GPU_frames=6,baseline=record(baseline),previous106_checkpoint=record(WS/'artifacts/client455-progress/client455-effect-runtime-checkpoint-before107.json'),previous106_runtime_gate='HISTORICAL',ordinary_audio_provider=ready[0],derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,other32_GUI_frames_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-aiming-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:MainApp aiming20/realBSPcursor/6moving children/Miles/pending0hover;C1A/fullnuclear/M9OPEN')


if __name__=='__main__':main()
