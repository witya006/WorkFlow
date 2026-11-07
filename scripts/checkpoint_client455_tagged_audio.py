"""Validate the real tagged-audio dependency; keep nuclear/full acceptance open."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-tagged-audio-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_tagged_audio.py') and (ref['functions'],ref['instructions'])==(18,1520),'Reference provenance');check(ref['raw_evidence'])
    pins=json.loads((WS/'config/client-target.json').read_text())
    for pin,folder,key in zip(ref['references'],['current','reference-backup'],['behavior_reference','secondary_reference']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(data)['architecture']=='x86' and len(pin['ranges'])==18,'Pinned input')
        for row in pin['ranges']:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Reference equivalence')
    for row in ref['inputs']:check(row)
    session=WS/'artifacts/client455-progress/tagged-audio103-session.json';state=json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'Owned IDA cleanup')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and link['client_objects']==182,'Ordinary link')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['tagged_audio_port_sha256']==sha(WS/'scripts/client455_tagged_audio_port.py'),'Current preparation')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==58,'Build coverage')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_tagged_audio.h','client455_tagged_audio.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared input drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/mainapp.h','source/mainapp.cpp','generated/client455_tagged_audio.cpp']:
        selected=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(selected)==1,'Generated provider '+suffix)
        for row in selected:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=selected
    mapping=(WS/link['map']['file']).read_text();retained={}
    for symbol in ['Open@RF455TaggedAudio','Close@RF455TaggedAudio','RF455_PrepareTaggedAudio']:
        match=re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_tagged_audio.obj',mapping);require(match,'Ordinary retained '+symbol);retained[symbol]=match.group(0)
    run=checked_native('client455-tagged-audio-native',link_hash)
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_tagged_audio.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-tagged-audio-reference.json') and run['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py'),'Native provenance')
    check(run['source']);check(run['console']);require(run['source']['sha256']==sha(WS/'scripts/native/client455_tagged_audio_probe.cpp'),'Native source')
    for row in run['inputs']:check(row)
    wanted={Path(row['file']).name.lower():row['sha256'] for row in ref['inputs']};actual={Path(row['file']).name.lower():row['sha256'] for row in run['inputs']}
    require(all(actual.get(name)==digest for name,digest in wanted.items()),'Actual staged dependencies')
    result=run['native'];require((result['checks'],result['channels'],result['cache_capacity'],result['manifest_records'])==(157,30,64,7969),'Native domain')
    for key in ['real_Miles_provider_listener_samples','actual_MainApp_owner','real_radar_WAV','muted_lab','duplicate_and_stale_tags','targeted_stop','relative_3D_position','LRU_reuse']:require(result[key],'Native '+key)
    for key in ['full_nuclear_aiming','full_audio_parity','audible_output_capture','full_client']:require(not result[key],'Unjustified acceptance '+key)
    status=checked_native('client455-player-status-native',link_hash);require(status['native']['checks']==58 and status['native']['nuclear_refusal_before_mutation'],'Status regression')
    hover=checked_native('client455-board-hover-native',link_hash);require(hover['native']['actual_live_ordinary_avatar'] and hover['native']['all_owners_released'] and hover['native']['sprite_allocator_balanced'],'Hover regression')
    baseline_path=WS/'artifacts/client455-progress/client455-board-hover-native-before103.json';baseline=json.loads(baseline_path.read_text());before={Path(row['file']).name:row for row in baseline['frames']}
    require(len(hover['frames'])==len(before)==6,'Frame coverage')
    for row in hover['frames']:
        prior=before[Path(row['file']).name];check(prior);check(row);check(row['preview']);require(row['sha256']==prior['sha256'],'Changed prior pixels')
    review=load('client455-board-hover-visual-review');require(review['reviewed'] and review['reviewed_frames']==6 and review['frames']==hover['frames'] and review['native_sha256']==sha(WS/'inventory/client455-board-hover-native.json'),'Viewed frames');check(review['sheet'])
    checked_native('client455-account-native',link_hash);checked_native('client455-hotbar-native',link_hash)
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not row['natural_exit'] and row['native']['registered']==17 for row in storage['runs']),'Storage regression')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own PE Create1')
    ready=[row['value'] for row in ui['nation_paths'] if row.get('value','').startswith('RF455 TaggedAudio:ready:7969:')];require(len(ready)==1,'Actual ordinary provider initialized');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Engine unchanged');check(engine['baseline_library'])
    fresh=['tagged-audio-reference','tagged-audio-native','player-status-native','board-hover-native','board-hover-visual-review','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native','account-native','hotbar-native','storage-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),session=record(session),sources=sources,generated_providers=providers,retained=retained,normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},CPU_checks=157,real_Miles=True,ordinary_provider=ready[0],channels=30,cache_capacity=64,viewed_GPU_frames=6,byte_equal_hover_frames=6,baseline=record(baseline_path),previous102_checkpoint=record(WS/'artifacts/client455-progress/client455-player-status-checkpoint-before103.json'),previous102_runtime_gate='HISTORICAL',derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,other32_GUI_frames_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-tagged-audio-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:157CPU/realMiles/30channels/64LRU/ordinaryCreate3D/6viewedByteEqualGPU;nuclear/effect/fullsound/M9OPEN')


if __name__=='__main__':main()
