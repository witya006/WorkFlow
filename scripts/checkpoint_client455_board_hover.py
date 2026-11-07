"""Validate typed hover ownership without accepting live gameplay/operationqueue."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-board-hover-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_board_hover.py') and (ref['functions'],ref['instructions'])==(23,1156),'Static provenance')
    for row in ref['raw_evidence']+ref['inputs']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==23,'Pinned client')
        for row in pin['ranges']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Selected pins differ')
    session=WS/'artifacts/client455-progress/board-hover101-session.json';state=json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'IDA cleanup')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Ordinary link')
    prep=load('client455-normal-preparation');build=load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['board_hover_port_sha256']==sha(WS/'scripts/client455_board_hover_port.py')
            and not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20,'Prepared build')
    require(len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==57,'Facade count')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_board_hover.h','client455_board_hover.cpp','client455_board_object.inc','client455_item_object.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/gameobject/board/common/cboardmanager.h','source/gameobject/board/common/cboardmanager.cpp',
                   'source/userinterface/guicontroller/guiscreen.h','source/userinterface/guicontroller/guiscreen.cpp','generated/client455_board_hover.cpp']:
        selected=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(selected)==1,'Prepared provider '+suffix)
        for row in selected:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=selected
    mapping=(WS/link['map']['file']).read_text();retained={}
    for symbol,provider in [('SetTypedHover455@CBoardManager','client455_board_hover.obj'),('HoverObject455@CBoardManager','client455_board_hover.obj'),
                            ('AddTypedBoardObject455@CBoardManager','client455_board_hover.obj'),('AddTypedHoverIcon455@CGUIScreen','client455_board_hover.obj'),
                            ('RemoveTypedHoverIcon455@CGUIScreen','client455_board_hover.obj'),('Copy455@CBoardObject','client455_item_object.obj')]:
        match=re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:'+re.escape(provider),mapping);require(match,'Ordinary provider '+symbol);retained[symbol]=match.group(0)
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Unchanged engine');check(engine['baseline_library'])
    run=checked_native('client455-board-hover-native',link_hash)
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_board_hover.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py')
            and run['reference_sha256']==sha(WS/'inventory/client455-board-hover-reference.json') and run['architecture']=='x86','Native provenance')
    for row in [run['source'],run['console']]+run['inputs']:check(row)
    wanted={Path(row['file']).name:row['sha256'] for row in ref['inputs']};actual={Path(row['file']).name:row['sha256'] for row in run['inputs']}
    require(all(actual.get(name)==digest for name,digest in wanted.items()),'Actual input staging')
    result=run['native'];require((result['forward_board_BYTE_cases'],result['item_kind_size_cases'],result['mixed_legacy_refusals'],result['GPU_frames'])==(256,5,2,6),'Native selected domain')
    for key in ['copy620','actual_EDF_owner','ordinary_SetHover_ClearOperation_ReturnHover','dual_backups_operation_fallback','replacement_release_order',
                'screen_notifications_cursor_tooltip','ordinary_FrameMove_hover_update','raw_lock_flag21','AddObject_false_after_success','rawslot_not_equipalias',
                'nonphysical_CPU_icons_synthetic','empty_wrapper_size_case','Quest_name_refusal','emptyID0_negativehalf','actual_avatar_null','all_owners_released','sprite_allocator_balanced']:
        require(result[key],'Actual integration '+key)
    for key in ['live_avatar_cancellation','full_operation_queue','full_three_layer_tooltips','full_gameplay_handlers','full_client']:require(not result[key],'Unjustified acceptance '+key)
    review=load('client455-board-hover-visual-review')
    require(review['native_sha256']==sha(WS/'inventory/client455-board-hover-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_board_hover.py')
            and review['reviewed'] and review['reviewed_frames']==6 and review['frames']==run['frames'],'Hover visual review');check(review['sheet'])
    for row in run['frames']:check(row);check(row['preview'])
    prior_path=WS/'artifacts/client455-progress/client455-item-lock-checkpoint-before101.json';prior=json.loads(prior_path.read_text());regressions=[];inherited=0
    for name,count in [('item-lock',6),('ready-cooldown',6),('gui-timer',6),('linker-window',8),('linker-owners',3),('item-icon-metadata',3)]:
        current=checked_native('client455-'+name+'-native',link_hash);baseline_path=WS/f'artifacts/client455-progress/client455-{name}-native-before101.json';baseline=json.loads(baseline_path.read_text())
        visual=load('client455-'+name+'-visual-review');require(visual['reviewed'] and visual['reviewed_frames']==count,'Inherited review '+name);check(visual['sheet'])
        if name=='item-lock':require(visual['native_sha256']==sha(baseline_path) and visual['frames']==baseline['frames'],'Direct100 visual baseline')
        else:
            chain=next(row for row in prior['regressions'] if row['name']==name)
            require(chain['current']['sha256']==sha(baseline_path) and chain['inherited_review']['sha256']==sha(WS/f'inventory/client455-{name}-visual-review.json'),'100 inherited review chain '+name)
        before={Path(row['file']).name:row for row in baseline['frames']};require(len(current['frames'])==len(before)==count,'Regression coverage '+name)
        for row in current['frames']:
            old=before[Path(row['file']).name];check(old);check(row);check(row['preview']);require(row['sha256']==old['sha256'],'Changed prior pixels '+row['file'])
        inherited+=count;regressions.append(dict(name=name,baseline=record(baseline_path),current=record(WS/f'inventory/client455-{name}-native.json'),inherited_review=record(WS/f'inventory/client455-{name}-visual-review.json'),byte_equal_frames=count))
    require(inherited==32,'Regression frame domain')
    checked_native('client455-hotbar-native',link_hash);checked_native('client455-account-native',link_hash)
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not row['natural_exit'] and row['native']['registered']==17 for row in storage['runs']),'Storage regression')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit']
            and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Current own PE Create1')
    check(early['events']);check(ui['events'])
    fresh=['normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native','hotbar-native','storage-native','account-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference=record(WS/'inventory/client455-board-hover-reference.json'),
                native=record(WS/'inventory/client455-board-hover-native.json'),visual=record(WS/'inventory/client455-board-hover-visual-review.json'),session=record(session),sources=sources,
                generated_providers=providers,retained=retained,normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},
                previous100_checkpoint=record(prior_path),regressions=regressions,new_viewed_GPU_frames=6,inherited_byte_equal_reviewed_frames=32,selected_ranges=23,instructions=1156,
                actual_forwarding_destination='CLinkBoard;otherexistingtypedboardproviders stillrefuse',native_avatar_branch='actualnull;liveavatarrefusesuntilstate/cancelowners migrated',
                nonphysical_CPU_icons_synthetic=True,Quest_sentence_provider_still_refuses=True,derived_engine_unchanged=engine['library_sha256'],
                previous100gate='Historical runtime after client/link/manager declarations changed;static proofs and32reviewed frames retained',
                unchanged_world_audio_159k_093atlas_092icon_2013owner_1447SF_095manual_suites_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-board-hover-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:Copy620/dualbackups/actualscreen/ReturnHover/5kinds/6newviewedGPU/32byte-equalreviewedframes/currentPECreate1;liveavatar/fullqueue/handlers/M9OPEN')


if __name__=='__main__':main()
