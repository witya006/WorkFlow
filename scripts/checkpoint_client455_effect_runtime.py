"""Verify actual aiming cue GPU frames/lifecycle; keep full nuclear/client open."""
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
    ref=load('client455-effect-runtime-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_effect_runtime.py') and (ref['functions'],ref['instructions'])==(16,2546) and ref['target_R3T_release_warning_confirmed'],'Reference provenance')
    check(ref['master_start_prior_reference']);check(ref['raw_evidence']);check(ref['legacy_texture_source']);pins=json.loads((WS/'config/client-target.json').read_text())
    for pin,folder,key in zip(ref['references'],['current','reference-backup'],['behavior_reference','secondary_reference']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(data)['architecture']=='x86' and pin['image_base']=='0x400000' and len(pin['ranges'])==16,'Pinned input')
        for row in pin['ranges']+pin['globals']+[pin['additional_master_range']]:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'] and ref['references'][0]['globals']==ref['references'][1]['globals'],'Reference equivalence')
    session=WS/'artifacts/client455-progress/effect-runtime106-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'IDA cleanup')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and link['client_objects']==182,'Ordinary link')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['effect_runtime_port_sha256']==sha(WS/'scripts/client455_effect_runtime_port.py') and not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'],'Current preparation/build')
    require(len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==59,'Facade coverage')
    check(dict(file=build['log'],sha256=build['log_sha256']));check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    sources=[record(WS/'scripts/native'/name) for name in ['client455_effect_disappear.inc','client455_effect_schedule.inc','client455_effect_passes.inc']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared input drift')
    manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/addcodebyjang/effectcore.h','source/addcodebyjang/effectcore.cpp']:
        rows=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    mapping=(WS/link['map']['file']).read_text();retained={}
    for symbol in ['FrameMoveMagicEffects@@','FrameMoveAllEffectsList@@','RenderAllEffectsList@@','RenderAlphaEffects455@@','SetDisapearTimeEffect@@','DeleteMagicList@@YAXKH@Z']:
        match=re.search(re.escape(symbol)+r'[^\r\n]*\seffectcore.obj\s*$',mapping,re.M);require(match,'Ordinary retained '+symbol);retained[symbol]=match.group(0).strip()
    require('R3Engine455Startup:effectcore.obj' not in mapping,'Legacy engine effectcore selected')
    run=checked_native('client455-effect-runtime-native',link_hash)
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_effect_runtime.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-effect-runtime-reference.json') and run['source']['sha256']==sha(WS/'scripts/native/client455_effect_runtime_probe.cpp'),'Native provenance')
    check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    resources=load('client455-effect-resources-reference');actual={Path(row['file']).name.lower():row['sha256'] for row in run['inputs']}
    for row in resources['inputs']:check(row);require(actual.get(Path(row['file']).name.lower())==row['sha256'],'Actual resources')
    result=run['native'];require(result['master_capacity']==256 and result['master_overflow_eviction'],'Master boundary');require(tuple(result[key] for key in ['checks','warnings','real_RPK_cue_tracks','real_models','particle_recipes','ordinary_FrameMove_ticks','dynamic_light_ticks','GPU_frames','effect_capacity'])==(573,6,6,6,5,90,90,4,512),'Native domain')
    require(result['particle_pixels']>20 and result['cleared_pixels']==0 and 0<result['cancellation_drain_ticks']<360 and result['memory_before']==result['memory_after'] and result['retained_global_texture_cache_bytes']==9728,'Actual render/cancel/memory')
    for key in ['ordinary_effect_cancellation','overflow_eviction','quality_owner','negative_disappear_releases','explicit_global_texture_table_teardown','all_lab_allocations_released']:require(result[key],'Native '+key)
    for key in ['full_dynamic_light_compositing','full_world_pass_order','full_nuclear_owner','full_effect_runtime','full_client']:require(not result[key],'Unjustified acceptance '+key)
    visual=load('client455-effect-runtime-visual-review');require(visual['reviewed'] and visual['reviewed_frames']==4 and visual['frames']==run['frames'] and visual['native_sha256']==sha(WS/'inventory/client455-effect-runtime-native.json') and visual['script_sha256']==sha(WS/'scripts/review_client455_effect_runtime.py'),'Actual effect review');check(visual['sheet'])
    for row in run['frames']:check(row);check(row['preview'])
    require(len({row['sha256'] for row in run['frames']})==4,'Distinct actual frames')
    for name,count in [('magic',36),('effect-resources',66),('player-status',58),('tagged-audio',157)]:require(checked_native(f'client455-{name}-native',link_hash)['native']['checks']==count,'Regression '+name)
    hover=checked_native('client455-board-hover-native',link_hash);require(hover['native']['all_owners_released'] and hover['native']['sprite_allocator_balanced'],'Hover regression')
    baseline=WS/'artifacts/client455-progress/client455-board-hover-native-before106.json';before={Path(row['file']).name:row for row in json.loads(baseline.read_text())['frames']};require(len(before)==len(hover['frames'])==6,'Frame coverage')
    for row in hover['frames']:check(row);check(row['preview']);check(before[Path(row['file']).name]);require(row['sha256']==before[Path(row['file']).name]['sha256'],'Changed hover pixels')
    review=load('client455-board-hover-visual-review');require(review['reviewed'] and review['reviewed_frames']==6 and review['frames']==hover['frames'] and review['native_sha256']==sha(WS/'inventory/client455-board-hover-native.json'),'Viewed hover');check(review['sheet'])
    checked_native('client455-account-native',link_hash);require(checked_native('client455-hotbar-native',link_hash)['native']['actual_packets']==7,'Hotbar regression')
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not row['natural_exit'] and row['native']['registered']==17 for row in storage['runs']),'Storage regression')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own PE Create1')
    ready=[row['value'] for row in ui['nation_paths'] if row.get('value','').startswith('RF455 TaggedAudio:ready:7969:')];require(len(ready)==1,'Actual ordinary audio provider');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Engine unchanged');check(engine['baseline_library'])
    fresh=['effect-runtime-reference','effect-runtime-native','effect-runtime-visual-review','effect-resources-native','magic-native','player-status-native','tagged-audio-native','board-hover-native','board-hover-visual-review','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native','account-native','hotbar-native','storage-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),session=record(session),sources=sources,generated_providers=providers,retained=retained,normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},CPU_checks=573,master_capacity=256,all256_master_survivors_checked=True,actual_effect_GPU_frames=4,byte_equal_hover_GPU_frames=6,viewed_GPU_frames=10,cancellation_drain_ticks=result['cancellation_drain_ticks'],effect_capacity=512,target_R3T_release_warning_confirmed=True,explicit_global_texture_table_teardown=True,baseline=record(baseline),previous105_checkpoint=record(WS/'artifacts/client455-progress/client455-effect-resources-checkpoint-before106.json'),previous105_runtime_gate='HISTORICAL',ordinary_audio_provider=ready[0],derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,other32_GUI_frames_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-effect-runtime-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:actual6trackAiming/4viewedGPU/cancelDrains/512eviction/targetR3Twarning;fullnuclear/world/M9OPEN')


if __name__=='__main__':main()
