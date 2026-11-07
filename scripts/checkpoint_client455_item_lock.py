"""Validate the selected lock child and keep full drag/game acceptance open."""
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
    ref=load('client455-item-lock-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_item_lock.py')
            and (ref['functions'],ref['instructions'])==(17,1610),'Reference provenance')
    for row in ref['raw_evidence']+ref['inputs']:
        check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86'
                and len(pin['ranges'])==17,'Pinned reference')
        for row in pin['ranges']:
            require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Selected pins differ')
    glyph=next(row for row in ref['inputs'] if row.get('target_id')==52)
    require(glyph['original_size']==[8,12] and glyph['texture_size']==[8,16]
            and glyph['actions']==glyph['total_frames']==1 and sha(Path(glyph['original']))==glyph['sha256'],'Actual lock glyph')
    session=WS/'artifacts/client455-progress/item-lock100-session.json';state=json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'IDA cleanup')

    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Ordinary link')
    prep=load('client455-normal-preparation');build=load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py')
            and prep['item_icon_port_sha256']==sha(WS/'scripts/client455_item_icon_port.py')
            and not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20,'Prepared build')
    require(len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==56,'Facade count')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_item_icon.cpp','client455_item_icon_members.inc',
              'client455_item_atlas.cpp','client455_item_object.cpp','client455_board_object.inc','client455_linker_owners.cpp']]
    for row in sources:
        require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared provider drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    mapping=(WS/link['map']['file']).read_text();retained={}
    for symbol,provider in [('SetLock455@CGUIItem','client455_item_icon.obj'),('BindLock455@CGUIItem','client455_item_icon.obj'),
                            ('RefreshLock455@CBoardObject','client455_item_object.obj')]:
        match=re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:'+re.escape(provider),mapping)
        require(match,'Ordinary provider missing '+symbol);retained[symbol]=match.group(0)
    engine=load('client455-startup-engine-build')
    require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Unchanged derived engine')
    check(engine['baseline_library'])

    run=checked_native('client455-item-lock-native',link_hash)
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_item_lock.py')
            and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py')
            and run['reference_sha256']==sha(WS/'inventory/client455-item-lock-reference.json') and run['architecture']=='x86','Native provenance')
    for row in [run['source'],run['console']]+run['inputs']:
        check(row)
    wanted={Path(row['file']).name:row['sha256'] for row in ref['inputs']}
    actual={Path(row['file']).name:row['sha256'] for row in run['inputs']}
    require(all(actual.get(name)==digest for name,digest in wanted.items()),'Native inputs')
    result=run['native']
    require((result['direct_BYTE_cases'],result['wrapper_flag21_cases'],result['geometry_cases'],result['GPU_frames'])==(256,256,18,6),'Selected coverage')
    for key in ['actual_EDF_inventory_owner','actual_Linker_Add_Remove','copy_descriptor_rawShow','empty_preserves_lock',
                'clipped_route_lock_unclipped','all_owners_released','sprite_allocator_balanced']:
        require(result[key],'Missing actual route '+key)
    require(not result['full_drag_handlers'] and not result['full_client'],'Unjustified full acceptance')
    review=load('client455-item-lock-visual-review')
    require(review['native_sha256']==sha(WS/'inventory/client455-item-lock-native.json')
            and review['script_sha256']==sha(WS/'scripts/review_client455_item_lock.py')
            and review['reviewed'] and review['reviewed_frames']==6 and review['frames']==run['frames'],'Lock visual review')
    check(review['sheet'])
    for row in run['frames']:
        check(row);check(row['preview'])

    prior_path=WS/'artifacts/client455-progress/client455-ready-cooldown-checkpoint-before100.json'
    prior=json.loads(prior_path.read_text());regressions=[];inherited=0
    for name,count in [('ready-cooldown',6),('linker-window',8),('linker-owners',3),
                       ('item-icon-metadata',3),('gui-timer',6),('item-icon',9)]:
        current=checked_native('client455-'+name+'-native',link_hash)
        require(current['script_sha256']==sha(WS/f'scripts/probe_client455_{name.replace("-","_")}.py'),'Regression runner provenance')
        baseline_path=WS/f'artifacts/client455-progress/client455-{name}-native-before100.json'
        baseline=json.loads(baseline_path.read_text())
        visual=load('client455-'+name+'-visual-review')
        require(visual['reviewed'] and visual['reviewed_frames']==count,'Baseline review '+name);check(visual['sheet'])
        if name in ['ready-cooldown','item-icon']:
            require(visual['native_sha256']==sha(baseline_path) and visual['frames']==baseline['frames'],'Direct baseline review '+name)
        else:
            chain=next(row for row in prior['regressions'] if row['name']=='client455-'+name)
            require(chain['current']['sha256']==sha(baseline_path)
                    and chain['inherited_review']['sha256']==sha(WS/f'inventory/client455-{name}-visual-review.json'),'099 visual inheritance '+name)
            check(chain['baseline']);old=json.loads((WS/chain['baseline']['file']).read_text())
            require(visual['native_sha256']==chain['baseline']['sha256'] and visual['frames']==old['frames'],'098 reviewed source '+name)
        old_frames={Path(row['file']).name:row for row in baseline['frames']}
        require(len(current['frames'])==len(old_frames)==count,'Frame coverage '+name)
        for row in current['frames']:
            before=old_frames[Path(row['file']).name];check(before);check(row);check(row['preview'])
            require(row['sha256']==before['sha256'],'Changed prior pixels '+row['file'])
        inherited+=count
        regressions.append(dict(name=name,baseline=record(baseline_path),
                                current=record(WS/f'inventory/client455-{name}-native.json'),
                                inherited_review=record(WS/f'inventory/client455-{name}-visual-review.json'),byte_equal_frames=count))
    require(inherited==35,'Regression domain')
    owners=load('client455-linker-owners-native')['native']
    require(owners['owned_clones']==50 and owners['explicit_missing_provider_refusals']==3,'Flag21 refusal removed;other3retained')
    checked_native('client455-hotbar-native',link_hash);checked_native('client455-account-native',link_hash)
    storage=load('client455-storage-native')
    require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3
            and all(not row['natural_exit'] and row['native']['registered']==17 for row in storage['runs']),'Storage regression')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1
            and not ui['debugger_exit'] and ui['completed_existing_client_create']
            and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers'])
            and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own PE Create1')
    check(early['events']);check(ui['events'])
    fresh=['normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native',
           'ui-startup-native','hotbar-native','storage-native','account-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),
                reference=record(WS/'inventory/client455-item-lock-reference.json'),native=record(WS/'inventory/client455-item-lock-native.json'),
                visual=record(WS/'inventory/client455-item-lock-visual-review.json'),session=record(session),sources=sources,retained=retained,
                resource_staging_helper=record(WS/'scripts/client455_runtime_inputs.py'),normal_link_sha256=link_hash,normal_executable=link['executable'],
                fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},
                previous099_checkpoint=record(prior_path),regressions=regressions,new_viewed_GPU_frames=6,inherited_byte_equal_reviewed_frames=35,
                direct_BYTE_cases=256,wrapper_flag21_cases=256,geometry_cases=18,selected_ranges=17,instructions=1610,
                derived_engine_unchanged=engine['library_sha256'],previous099gate='Historical runtime after client source/link changed;static proofs and35reviewed frames retained',
                gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-lock-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:flag21/256raw-256normalized/18geometry/6newviewedGPU/35byte-equalreviewedframes/ordinaryLinker/currentPECreate1;drag-handlers/fullgame/M9OPEN')


if __name__=='__main__':main()
