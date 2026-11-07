"""Check canonical455 board identities and bounded source consumers, not full items."""
import hashlib
import json
import re
from pathlib import Path

from audit_client455_tutorial_integration import rtti, vptr_store
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current normal link')
    link_hash=sha(WS/'inventory/client455-normal-link.json')
    prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and
            prep['record_inputs']['client455_storage.h']==sha(WS/'scripts/native/client455_storage.h'),'Stale preparation/storage header')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    manifest=json.loads((WS/prep['manifest']).read_text())
    expected=['network/protocol/characterdb.h','define.h','gameobject/board/common/cboardmanager.h',
              'gameobject/board/common/cboardmanager.cpp','gameobject/board/itemboard/citemboard.cpp']
    selected=[]
    for suffix in expected:
        found=[row for row in manifest if row['file'].endswith('/source/'+suffix)]
        require(len(found)==1,'Missing generated storage consumer '+suffix);selected+=found
    selected+=[row for row in manifest if row['file'].endswith('/include/client455_storage.h')]
    require(len(selected)==6,'Missing copied storage header')
    for row in selected:
        check(row);check(dict(file=row['input'],sha256=row['input_sha256']))

    static_path=WS/'artifacts/client455-progress/storage085-reference.json'
    static=json.loads(static_path.read_text());assembly=static['physical_guard_assembly']
    require(len(static['functions'])==10 and all(not r['truncated'] and r['line_count']==r['total_lines'] for r in static['functions']), 'Incomplete selected pseudocode')
    require(len(assembly['asm']['lines'])==assembly['total_instructions']==25 and
            len({r['addr'] for r in assembly['asm']['lines']})==25,'Incomplete physical-item guard assembly')
    session_path=WS/'artifacts/client455-progress/storage085-session.json';session=json.loads(session_path.read_text())
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA session not saved/closed')
    target=load('client455-tutorial-integration')
    require(target['script_sha256']==sha(WS/'scripts/audit_client455_tutorial_integration.py'),'Changed084 RTTI helper')
    for row in target['raw_evidence']:check(row)
    references=[];pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,old in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],target['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pins[key]['sha256']==old['sha256'],'Changed binary pin')
        for row in old['ranges']:
            require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Changed084 body')
        selected_ranges=[]
        for row in static['ranges']['result']:
            require(not row['error'],'Missing085 function')
            address,size=int(row['fn']['addr'],16),int(row['fn']['size'],16)
            selected_ranges.append(dict(rva=hex(address-0x400000),bytes=size,
                                        sha256=hashlib.sha256(read_va(raw,address,size)).hexdigest()))
        require(not references or references[0]['ranges']==selected_ranges,'085 bodies differ between pins')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=selected_ranges))
        for row in target['target_boards']:
            vtable,instruction=vptr_store(raw,0x400000+int(row['store_rva'],16))
            require(instruction==row['store_bytes'] and rtti(raw,vtable)['class_name']==row['class_name'],'Changed target primary-vptr/RTTI identity')
    expected_classes={row['class_name']:row['id'] for row in target['target_boards']}

    native=load('client455-storage-native')
    require(native['normal_link_sha256']==link_hash and native['architecture']=='x86' and
            native['script_sha256']==sha(WS/'scripts/probe_client455_storage.py') and
            native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Stale storage execution')
    for key in ['source','exe','map']:check(native[key])
    require(pe((WS/native['exe']['file']).read_bytes())['architecture']=='x86' and len(native['runs'])==3,'Storage probe scope')
    first=native['runs'][0]['native']
    for run in native['runs']:
        for key in ['exe','fixture','console']:check(run[key])
        require(run['natural_exit']==0 and run['native']==first and
                json.loads((WS/run['console']['file']).read_text())==first,'Storage execution differs/failed')
        fixture=[tuple(map(int,line.split())) for line in (WS/run['fixture']['file']).read_text().splitlines()]
        require(fixture==[(i,int(i in {0,1,5})) for i in range(256)],'Independent reference guard fixture changed')
    require(first['status']=='PASS' and first['registry_limit']==56 and first['registered']==17 and
            first['physical_codes_checked']==256 and first['public_present']==18 and
            first['source_storage_ids']==list(range(7)) and first['legacy_belt_invalid']==255,'Identity coverage')
    require(first['actual_Force_Animus_packs'] and first['legacy_belt_rejected'] and first['Trunk_missing'] and
            not first['full_factory'] and not first['full_item_protocol'] and not first['actual_Tutorial'],'Unjustified full acceptance')
    names=[]
    for row in first['boards']:
        name=row['class'].removeprefix('class ')
        require(expected_classes.get(name)==row['id'],'Source class registered at wrong455 ID')
        names.append(name)
    require(len(set(names))==17 and 'CBeltBoard' not in names,'Retired legacy class retained in factory')

    account=load('client455-account-native')
    require(account['normal_link_sha256']==link_hash and account['natural_exit']==0 and
            account['script_sha256']==sha(WS/'scripts/probe_client455_account.py') and
            account['source_sha256']==sha(WS/account['source']),'Stale account regression')
    for key in ['exe','map','output']:check(account[key])
    for row in account['inputs']:check(row)
    a=account['native']
    require(a==json.loads((WS/account['output']['file']).read_text()) and a['status']=='PASS' and
            a['actual_account_send_receive'] and a['actual_Avatar_stage_skip'] and a['actual_MainApp_Create_gate'] and
            a['actual_login_Tutorial_transform'] and not a['authentication_performed'],'Affected account regression')
    early=load('client455-startup-native');ui=load('client455-ui-startup-native')
    require(early['normal_link_sha256']==link_hash and early['normal_winmain_executed'] and
            early['transport_connected'] and not early['debugger_exit'],'Fresh early startup')
    require(ui['normal_link_sha256']==link_hash and ui['completed_existing_client_create'] and
            ui['markers'][-1]['eax']==1 and not ui['debugger_exit'] and
            ui['early_startup_sha256']==sha(WS/'inventory/client455-startup-native.json'),'Fresh exact PE/Create1')
    for report in [early,ui]:
        check(report['events'])
        require(sha(WS/report['staged_executable'])==link['executable']['sha256'],'Staged PE differs')
    require(not load('client455-startup-audit')['unresolved_provider_modules'],'Unresolved runtime provider')
    engine=load('client455-startup-engine-build')
    require(engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769' and
            load('client455-startup-contracts-native')['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Unchanged engine evidence drift')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    mapping=(WS/link['map']['file']).read_text()
    for method in ['?Create@CBoardManager@@QAEXXZ','?GetBoard@CBoardManager@@QAEPAVCBaseBoard@@E@Z',
                   '?ReturnItemToItemBoard@CBoardManager@@QAEHEEEPAVCBoardItem@@@Z']:
        require(re.search(re.escape(method)+r'[^\r\n]*cboardmanager.obj',mapping),'Ordinary provider missing '+method)
    retired=[]
    source_root=WS/'work/client455-port/normal/source'
    for path in source_root.rglob('*'):
        if path.suffix.lower() not in ['.cpp','.h']:continue
        for number,line in enumerate(path.read_bytes().splitlines(),1):
            if b'_GetBeltBoard(' in line:retired.append(dict(file=path.relative_to(WS).as_posix(),line=number))
    require(retired,'Unrecovered legacy callers unexpectedly disappeared')
    report=dict(status='PARTIAL',scope='Canonical registry/storage IDs and physical-item eligibility;not full storage/protocol/Tutorial',
                reference_functions=references,physical_guard_actual_asm=25,
                raw_evidence=[dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in [static_path,session_path]],
                target_registry_reference_sha256=sha(WS/'inventory/client455-tutorial-integration.json'),
                script_sha256=sha(Path(__file__)),RTTI_helper_sha256=sha(WS/'scripts/audit_client455_tutorial_integration.py'),
                normal_link_sha256=link_hash,engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),
                generated_sources=selected,native_runs=3,registered_target_identities=17,
                source_Force_id=3,source_Animus_id=4,public_registry_limit=56,legacy_belt_invalid=255,
                remaining_target_registry_classes=[name for name in expected_classes if name not in names],
                unrecovered_retired_belt_callers=retired,
                fresh_evidence={name:sha(WS/'inventory'/(name+'.json')) for name in ['client455-storage-native','client455-account-native',
                    'client455-startup-native','client455-ui-startup-native']},
                exactPE_Create1='PASS_BOUNDED',unchanged_engine_contracts_reused=True,
                actor_money_maps_audio_GPU_suites_rerun=False,
                gaps=['36 target registry classes,including Trunk5,are not registered;17 same-named classes do not establish complete behavior',
                      'Legacy _GetBeltBoard paths explicitly refuse;old MainGame.Create_Board and old BeltList download still need real455 replacements',
                      'Physical eligibility0/1/5 is verified;full ReturnItem effects/trade/trunk/hotbar/item packet layouts and producers/consumers remain open',
                      'Legacy inventory/equip trade lookup remains bounded;not a new455trade implementation',
                      'Actual Tutorial/sharedUI/Avatar/QBI/follow/localhandlers/fourstage/Login/auth/gameplay and all earlier acceptance gaps remain open',
                      'Existing Create1 stops before the complete game loop;observed first-chance exceptions do not establish failure-domain parity'],
                input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-storage-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:actual17 canonical identities/Force3/Animus4/physical0-1-5;3runs/account/exactPE/Create1;full items/Tutorial/M9 OPEN')


if __name__=='__main__':main()
