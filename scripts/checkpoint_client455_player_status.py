"""Verify status/ordinary-avatar progress without accepting nuclear/full client."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-player-status-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_player_status.py') and (ref['functions'],ref['instructions'])==(17,2036),'Reference provenance')
    check(ref['raw_evidence']);check(ref['exploration'])
    pins=json.loads((WS/'config/client-target.json').read_text())
    for pin,folder,key in zip(ref['references'],['current','reference-backup'],['behavior_reference','secondary_reference']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(data)['architecture']=='x86','Input identity')
        require(len(pin['ranges'])==17,'Selected ranges')
        for row in pin['ranges']+[pin['diagnostic_range']]:
            require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Reference equivalence')
    session=WS/'artifacts/client455-progress/player-status102-session.json';state=json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'Owned IDA cleanup')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS' and link['client_objects']==182,'Full ordinary link')
    prep,build,consumers=load('client455-normal-preparation'),load('client455-normal-build'),load('client455-normal-consumers')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['player_status_port_sha256']==sha(WS/'scripts/client455_player_status_port.py'),'Preparation source')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and consumers['normal_build_sha256']==sha(WS/'inventory/client455-normal-build.json') and consumers['native']['status']=='PASS','Current build/consumers')
    require(len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==57,'Facade count')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_player_status.h','client455_board_hover.cpp','client455_board_hover.h']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared input drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/character/player/cplayer.h','source/character/player/cplayer.cpp','include/client455_player_status.h','generated/client455_board_hover.cpp']:
        selected=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(selected)==1,'Provider '+suffix)
        for row in selected:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=selected
    mapping=(WS/link['map']['file']).read_text();retained={}
    for symbol,provider in [('SetServerStatusFlag@CPlayer@@QAEX_K@Z','cplayer.obj'),('SetTypedHover455@CBoardManager','RFClient455Facade:client455_board_hover.obj')]:
        match=re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(provider),mapping);require(match,'Ordinary retained provider '+symbol);retained[symbol]=match.group(0)
    run=checked_native('client455-player-status-native',link_hash)
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_player_status.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-player-status-reference.json'),'Native provenance')
    for row in [run['source'],run['console']]:check(row)
    require(run['source']['sha256']==sha(WS/'scripts/native/client455_player_status_probe.cpp'),'Native source')
    result=run['native'];require((result['checks'],result['flag_subtypes'],result['DWORD_lowBYTE_cases'])==(58,8,12),'Selected native domain')
    for key in ['actual_avatar','ordinary_64bit_status_setter','unknown_state_refusal','stale_no_subtype','actual_hover_and_screen','nuclear_refusal_before_mutation']:require(result[key],'Native '+key)
    for key in ['full_nuclear_owner','full_status_sideeffects','full_455_wire_receivers','full_client']:require(not result[key],'Unjustified acceptance '+key)
    hover=checked_native('client455-board-hover-native',link_hash)
    require(hover['script_sha256']==sha(WS/'scripts/probe_client455_board_hover.py') and hover['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and hover['reference_sha256']==sha(WS/'inventory/client455-board-hover-reference.json'),'Hover provenance')
    check(hover['source']);check(hover['console'])
    for row in hover['inputs']:check(row)
    require(hover['native']['actual_live_ordinary_avatar'] and hover['native']['actual_avatar_null_fastpath_checked'] and not hover['native']['live_avatar_cancellation'],'Actual hover avatar domain')
    require(hover['native']['GPU_frames']==len(hover['frames'])==6 and hover['native']['all_owners_released'] and hover['native']['sprite_allocator_balanced'],'Hover lifecycle/frames')
    baseline_path=WS/'artifacts/client455-progress/client455-board-hover-native-before102.json';baseline=json.loads(baseline_path.read_text())
    prior_visual_path=WS/'artifacts/client455-progress/client455-board-hover-visual-review-before102.json';prior_visual=json.loads(prior_visual_path.read_text())
    require(prior_visual['native_sha256']==sha(baseline_path) and prior_visual['frames']==baseline['frames'] and prior_visual['reviewed'],'101 reviewed baseline')
    before={Path(row['file']).name:row for row in baseline['frames']};require(len(before)==6,'Baseline coverage')
    for row in hover['frames']:
        old=before[Path(row['file']).name];check(old);check(row);check(row['preview']);require(row['sha256']==old['sha256'],'Changed hover pixels')
    review=load('client455-board-hover-visual-review')
    require(review['native_sha256']==sha(WS/'inventory/client455-board-hover-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_board_hover.py') and review['frames']==hover['frames'] and review['reviewed'] and review['reviewed_frames']==6,'Fresh visual review');check(review['sheet'])
    checked_native('client455-account-native',link_hash);checked_native('client455-hotbar-native',link_hash)
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not row['natural_exit'] and row['native']['registered']==17 for row in storage['runs']),'Storage regression')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own PE Create1')
    check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Engine unchanged');check(engine['baseline_library'])
    fresh=['player-status-reference','player-status-native','board-hover-native','board-hover-visual-review','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native','account-native','hotbar-native','storage-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),sources=sources,providers=providers,retained=retained,session=record(session),normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},
                CPU_checks=58,flag_subtypes=8,DWORD_lowBYTE_cases=12,selected_functions=17,instructions=2036,equal_ranges=17,extra_equal_diagnostic_ranges=1,
                actual_hover_avatar='Nonnull ordinary Avatar/status0;true nuclear predicate remains explicitrefusal',viewed_GPU_frames=6,byte_equal_hover_frames=6,baseline=record(baseline_path),baseline_visual=record(prior_visual_path),
                previous101_checkpoint=record(WS/'artifacts/client455-progress/client455-board-hover-checkpoint-before102.json'),previous101_runtime_gate='HISTORICAL',previous101_other32_GPU_frames_rerun=False,
                derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-status-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:58CPU/ordinaryAvatarHover/6viewedByteEqualGPU/17ranges+diagnostic/currentPECreate1;nuclearowner/fullstatus/wirereceivers/M9OPEN')


if __name__=='__main__':main()
