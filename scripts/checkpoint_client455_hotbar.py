"""Verify ordinary455 hotbar delta-save evidence;full Linker/game remain open."""
import hashlib
import json
import re
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def main():
    link=load('client455-normal-link')
    require(validate_normal_link(link)=='PASS','Current normal link')
    link_hash=sha(WS/'inventory/client455-normal-link.json')
    prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py'),'Stale preparation')
    names=['client455_hotbar.h','client455_hotbar.cpp','client455_hotbar_bridge.inc']
    for name in names:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Changed hotbar production source '+name)
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    manifest=json.loads((WS/prep['manifest']).read_text())
    suffixes=['source/gameobject/board/common/clinkboard.h','source/gameobject/board/common/clinkboard.cpp',
              'source/userinterface/gamewindow/guiforcebeltwindow.h','source/userinterface/gamewindow/guiforcebeltwindow.cpp',
              'include/client455_hotbar.h','generated/client455_hotbar.cpp']
    selected=[]
    for suffix in suffixes:
        matches=[r for r in manifest if r['file'].endswith('/'+suffix)]
        require(len(matches)==1,'Missing generated provider '+suffix)
        for row in matches:
            check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=matches

    root=WS/'artifacts/client455-progress'
    raw_paths=[root/('hotbar086-'+suffix+'.json') for suffix in ['reference','asm','session']]
    reference,assembly,session=[json.loads(path.read_text()) for path in raw_paths]
    require(len(reference['functions'])==45 and all(not r['truncated'] and r['line_count']==r['total_lines']
            for r in reference['functions']),'Incomplete selected pseudocode')
    require(len(reference['ranges']['result'])==45 and not any(r['error'] for r in reference['ranges']['result']),
            'Missing function ranges')
    expected_asm={'0x5003C0':72,'0x58BB90':144,'0x5004E0':41,'0x58BE20':26,'0x58A6C0':22,
                  '0x57EAC0':28,'0x501750':176,'0x669410':33,'0x669190':98}
    require({r['addr'] for r in assembly}==set(expected_asm),'Missing assembly functions')
    ranges={r['fn']['addr'].lower():r['fn'] for r in reference['ranges']['result']}
    for body in assembly:
        lines=[line for page in body['pages'] for line in page['asm']['lines']]
        start=int(body['addr'],16);size=int(ranges[body['addr'].lower()]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==expected_asm[body['addr']] and
                body['pages'][0]['total_instructions']==len(lines),'Incomplete/duplicate assembly '+body['addr'])
        require(all(start<=int(line['addr'],16)<start+size for line in lines),'Assembly outside function')
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,
            'Owned IDA session not saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pins[key]['sha256'] and pe(raw)['architecture']=='x86','Changed binary pin')
        selected_ranges=[]
        for row in reference['ranges']['result']:
            fn=row['fn'];address,size=int(fn['addr'],16),int(fn['size'],16)
            selected_ranges.append(dict(rva=hex(address-0x400000),bytes=size,
                sha256=hashlib.sha256(read_va(raw,address,size)).hexdigest()))
        require(not references or references[0]['ranges']==selected_ranges,'Selected functions differ between pins')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=selected_ranges))

    native=load('client455-hotbar-native')
    require(native['normal_link_sha256']==link_hash and native['natural_exit']==0 and
            native['script_sha256']==sha(WS/'scripts/probe_client455_hotbar.py') and
            native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Stale hotbar execution')
    for name in ['source','exe','map','console','output','packets']:check(native[name])
    n=native['native']
    require(n==json.loads((WS/native['output']['file']).read_text()) and n['status']=='PASS' and
            pe((WS/native['exe']['file']).read_bytes())['architecture']=='x86','Native output/architecture')
    require(n['real_source_banks']==5 and n['slots_per_bank']==10 and n['actual_packets']==7 and
            n['maximum_payload']==202 and n['actual_group']==13 and n['actual_opcode']==17,'Hotbar coverage')
    for key in ['actual_send_ring_AES','actual_metadata_bridge','drag_suppression','failure_commits_cache',
                'ordinary_FrameMove','raw_bank_flag_packing']:require(n[key],'Missing actual branch '+key)
    require(not n['full_Linker_UI_ownership'] and not n['actual_Tutorial'],'Unjustified full acceptance')
    # Independent hand-reviewed wire fixtures from target58BB90/57EAC0. These
    # are decoded frames including WORD total size and group13/op17,not ciphertext.
    packets=[bytes.fromhex(line) for line in (WS/native['packets']['file']).read_text().splitlines()]
    fixed=['06000d11f800','12000d11f803000421432701563431031200','06000d11aa00',
           '0a000d11aa0100ffffff','0a000d11aa012a167956',None,'0a000d11aa0131044523']
    require(len(packets)==7,'Packet trace length')
    for packet,expected in zip(packets,fixed):
        require(int.from_bytes(packet[:2],'little')==len(packet) and packet[2:4]==bytes([13,17]),'Wire frame')
        if expected is not None:require(packet==bytes.fromhex(expected),'Independent fixed packet mismatch')
    full=packets[5]
    require(len(full)==206 and full[4:6]==bytes([0xaa,50]),'Maximum payload framing')
    for i in range(50):
        record=full[6+4*i:10+4*i]
        require(record[:2]==bytes([i,4]) and int.from_bytes(record[2:],'little')==10000+i,'Maximum packet record')

    storage=load('client455-storage-native')
    require(storage['normal_link_sha256']==link_hash and storage['architecture']=='x86' and
            storage['script_sha256']==sha(WS/'scripts/probe_client455_storage.py') and
            storage['builder_sha256']==native['builder_sha256'],'Stale storage regression')
    for name in ['source','exe','map']:check(storage[name])
    require(len(storage['runs'])==3,'Storage runs')
    for run in storage['runs']:
        for name in ['exe','fixture','console']:check(run[name])
        require(run['natural_exit']==0 and run['native']==storage['runs'][0]['native'] and
                json.loads((WS/run['console']['file']).read_text())==run['native'],'Storage regression')
        s=run['native']
        require(s['status']=='PASS' and s['registered']==17 and s['registry_limit']==56 and
                s['actual_Force_Animus_packs'] and s['legacy_belt_rejected'] and
                s['Trunk_missing'] and not s['full_factory'],'Storage scope drift')
    account=load('client455-account-native')
    require(account['normal_link_sha256']==link_hash and account['natural_exit']==0 and
            account['script_sha256']==sha(WS/'scripts/probe_client455_account.py') and
            account['source_sha256']==sha(WS/account['source']),'Stale account regression')
    for key in ['exe','map','output']:check(account[key])
    for row in account['inputs']:check(row)
    a=account['native']
    require(a==json.loads((WS/account['output']['file']).read_text()) and a['status']=='PASS' and
            a['actual_account_send_receive'] and a['actual_Avatar_stage_skip'] and
            a['actual_MainApp_Create_gate'] and a['actual_login_Tutorial_transform'] and
            not a['authentication_performed'],'Affected account regression')
    early=load('client455-startup-native');ui=load('client455-ui-startup-native')
    require(early['normal_link_sha256']==link_hash and early['normal_winmain_executed'] and
            early['transport_connected'] and not early['debugger_exit'],'Fresh early startup')
    require(ui['normal_link_sha256']==link_hash and ui['completed_existing_client_create'] and
            ui['markers'][-1]['eax']==1 and not ui['debugger_exit'] and
            ui['early_startup_sha256']==sha(WS/'inventory/client455-startup-native.json'),'Fresh exact PE/Create1')
    for body in [early,ui]:
        check(body['events']);require(sha(WS/body['staged_executable'])==link['executable']['sha256'],'Staged PE differs')
    require(not load('client455-startup-audit')['unresolved_provider_modules'],'Unresolved startup provider')
    engine=load('client455-startup-engine-build')
    require(engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769' and
            load('client455-startup-contracts-native')['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),
            'Unchanged engine evidence drift')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    mapping=(WS/link['map']['file']).read_text()
    for symbol,unit in [('?FrameMove@CLinkBoard@@UAEXXZ','clinkboard'),
                        ('?CaptureHotbar455@CLinkBoard@@','clinkboard'),
                        ('?RF455_EncodeHotbarReference@@','RFClient455Facade:client455_hotbar'),
                        ('?prepare@RF455HotbarDelta@@','RFClient455Facade:client455_hotbar')]:
        require(re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(unit)+r'.obj',mapping),'Ordinary provider missing '+symbol)
    gaps=[
        'Legacy borrowed source objects/8-slot CGUIForceBeltWindow are not target owned620-byte wrappers/5x10 CGUILinkWindow;clone/refcount/GUI/input/cooldowns/deferred icons remain required',
        'Window-state fields initialize from actual source view Init,but bank widgets/event side effects and complete persistence restore/download are not ported',
        'Physical/SF/Animus source metadata are bound;Gesture/Macro tags are only pure encoding until their real providers are restored',
        'Old MainGame.Create_Board/BeltList still explicitly refuse retired belt;36 factory classes includingTrunk5 and full item/DB/trade/return protocol remain open',
        'Actual Tutorial/sharedUI/Avatar/QBI/follow/localhandlers/fourstage/Login/auth/gameplay and all earlier acceptance gaps remain mandatory',
        'Existing PE Create1 stops before the complete game loop;first-chance exceptions/OOM/concurrent changes are not failure-domain parity or full455acceptance']
    report=dict(status='PARTIAL',scope='Ordinary source Linker50-key delta-save and periodic branch;not fullLinker/UI/ownership/Tutorial',
        reference_functions=references,assembly_instructions=640,assembly_counts=expected_asm,
        raw_evidence=[dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in raw_paths],
        script_sha256=sha(Path(__file__)),normal_link_sha256=link_hash,
        generated_sources=selected,production_sources={name:sha(WS/'scripts/native'/name) for name in names},
        engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),
        fresh_evidence={name:sha(WS/'inventory'/(name+'.json')) for name in ['client455-hotbar-native',
            'client455-storage-native','client455-account-native','client455-startup-native','client455-ui-startup-native']},
        actual_packets=7,group=13,opcode=17,maximum_payload=202,cache_before_transport_failure=True,
        actual_send_ring_AES=True,ordinary_FrameMove='PASS_BOUNDED',exactPE_Create1='PASS_BOUNDED',
        unchanged_engine_contracts_reused=True,actor_money_maps_audio_GPU_suites_rerun=False,
        gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-hotbar-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:ordinaryLinker delta-save/7actualpackets/50slots/FrameMove;storage/account/exactPE/Create1;fullLinker/Tutorial/M9 OPEN')


if __name__=='__main__':main()
