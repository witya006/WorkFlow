"""Pin system-message routes/caller ordering and actual login sink before integration."""
import hashlib,json,re,struct
from pathlib import Path
from audit_client455_tutorial_integration import record,require,rtti,vptr_store
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,sha
from compare_client_binaries import WS,pe


def main():
    source=WS/'artifacts/client455-progress/dispatch110-reference.json'
    state=WS/'artifacts/client455-progress/dispatch110-session.json'
    raw=json.loads(source.read_text());session=json.loads(state.read_text())
    selected=raw['selected'];code={row['addr']:row for row in raw['functions'] if row['addr'] in selected}
    assembly={row['addr']:row for row in raw['assembly']};bounds={row['query']:row['fn'] for row in raw['ranges']['result']}
    require(len(selected)==len(set(selected))==len(code)==len(assembly)==len(bounds)==22,'Selected function coverage')
    require(sum(row['instruction_count'] for row in assembly.values())==1254,'Instruction coverage')
    for addr in selected:
        body,asm,fn=code[addr],assembly[addr],bounds[addr]
        require(fn and fn['addr']==addr and not body.get('error') and not body['truncated'] and body['cursor']['done'],'Complete pseudocode')
        require(asm['cursor']['done'] and asm['instruction_count']==asm['total_instructions']==len(asm['asm']['lines']),'Complete assembly')
        begin,end=int(addr,16),int(addr,16)+int(fn['size'],16)
        # IDA includes three discontiguous EH cleanup/handler chunks in this
        # constructor's listing. Pin their real bytes separately, not as body.
        require(all(begin<=int(row['addr'],16)<end or (addr=='0x53b860' and 0xa2b110<=int(row['addr'],16)<0xa2b13e) for row in asm['asm']['lines']),'Instruction boundaries')
    require(session['analysis_database']=='79b91993' and session['after_first_close']['count']==0,'Analysis session cleanup')
    require(session['closed']['success'] and session['closed']['saved'] and session['closed']['session_id']==session['reopened']['session']['session_id'] and session['after']['count']==0,'Persisted recovery save/close')
    calls=[(0x5e47cb,0x875203),(0x5e47e3,0x53f780),(0x5e4825,0x45b220),(0x5e482c,0x45b1a0),(0x5e4835,0x5e4a60),
           (0x5e4a82,0x58f370),(0x5e4a98,0x540400),(0x5e4b28,0x745b80),(0x5e4b85,0x745b80),(0x540425,0x5e5920),
           (0x53b8b5,0x53b9b0),(0x53ce6c,0x7b24b0),(0x53ceb1,0x8c6020),(0x4fe057,0x52ab50),(0x4fe066,0x6023b0),
           (0x4fe06c,0x5e47a0),(0x5c5ac5,0x4fe610),(0x5c5ad4,0x6023b0),(0x5c5ada,0x5e47a0),(0x5c5aeb,0x4fd640),
           (0x5c5aff,0x52ac00),(0x52ab67,0x8728b0),(0x52ab74,0x52ac40)]
    refs=[];pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=path.read_bytes()
        require(sha(path)==pins[key]['sha256'] and pe(image)['architecture']=='x86' and pe(image)['image_base']==0x400000,'Pinned x86 reference')
        ranges=[dict(rva=hex(int(addr,16)-0x400000),bytes=int(bounds[addr]['size'],16),sha256=hashlib.sha256(read_va(image,int(addr,16),int(bounds[addr]['size'],16))).hexdigest()) for addr in selected]
        for at,target in calls:
            data=read_va(image,at,5);require(data[0]==0xe8 and at+5+struct.unpack('<i',data[1:])[0]==target,'Decoded relative call '+hex(at))
        tail=read_va(image,0xa2b110,0x2e);jump=read_va(image,0xa2b139,5)
        require(jump[0]==0xe9 and 0xa2b139+5+struct.unpack('<i',jump[1:])[0]==0x871f63,'Constructor EH tail end')
        tails=[dict(owner_rva='0x13b860',rva='0x62b110',bytes=46,sha256=hashlib.sha256(tail).hexdigest())]
        vtable,store=vptr_store(image,0x53b89d);identity=rtti(image,vtable)
        require(identity['class_name']=='CGP_LogIn' and struct.unpack('<I',read_va(image,vtable+32,4))[0]==0x53cb40,'Actual login owner/render identity')
        literal=read_va(image,0xad8244,5);require(literal==b'[%d]\0','Sequence header format')
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,tails=tails,login_identity=identity,constructor_vptr_store=store,
                 sequence_format=dict(rva='0x6d8244',bytes=5,sha256=hashlib.sha256(literal).hexdigest()),decoded_calls=[dict(rva=hex(at-0x400000),target_rva=hex(target-0x400000)) for at,target in calls])
        require(not refs or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in refs[0].items() if k!='sha256'},'Selected equivalence')
        refs.append(row)
    dispatcher=code['0x5e4a60']['code'];require('a1 == 9' in dispatcher and 'v3 = 25' in dispatcher and 'if ( a2 )' in dispatcher and 'v3 = a2' in dispatcher,'MainGame style rules')
    require('sub_745B80(&byte_1028630, &Str, 2, 3)' in dispatcher,'Tutorial ignores caller category/style')
    require(raw['ce7immediate']['result'][0]['matches']==['0x5c5aca'] and raw['ce7immediate']['result'][0]['cursor']['done'],'Unique selected CE7 immediate')
    for row in raw['counterrefs']['result']:
        require(not row['more'] and len(row['xrefs'])==3 and all(x['fn']['addr']=='0x5e4a60' for x in row['xrefs']),'Independent process counters')
    normal=WS/'work/client455-port/normal/source'
    paths=['global.cpp','mainapp.cpp','mainapp.h','gameprogress/cgp_login.h','gameprogress/cgp_login.cpp','gameobject/board/common/cboardmanager.cpp']
    observed={relative:(normal/relative).read_bytes() for relative in paths}
    require(b'vsprintf( l_pDisplayString' in observed['global.cpp'] and b'CGUIChatWindow::FS_SYSTEM' in observed['global.cpp'],'Legacy formatted path still present')
    require(b'#define GPI_MAIN_GAME\t\t0x2' in observed['mainapp.h'] and b'new CGP_MainGame' in observed['mainapp.cpp'] and b'new CGP_Tutorial' not in observed['mainapp.cpp'],'Factory remains legacy three-stage')
    require(re.search(rb'void\s+CBoardManager::SetRequestProcessState\b',observed[paths[-1]]) and re.search(rb'm_bIsRequestProcessTime\s*=\s*0;',observed[paths[-1]]),'Existing selected request-clear source')
    link=load('client455-normal-link');gate=load('client455-chat-checkpoint')
    require(gate['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json') and gate['normal_executable']==link['executable'],'Unchanged runtime109 link')
    check(link['executable']);engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==gate['derived_engine_unchanged'],'Unchanged engine')
    report=dict(status='AUDIT_OPEN',scope='Complete selected dispatch/caller/login-message contracts; no source/runtime restoration claimed',script_sha256=sha(Path(__file__)),raw=record(source),session=record(state),selected_functions=22,full_assembly_functions=22,instructions=1254,references=refs,
        source_observations=[record(normal/path) for path in paths]+[record(WS/'scripts/native/client455_avatar_stage.cpp')],
        current_runtime_gate=dict(**record(WS/'inventory/client455-chat-checkpoint.json'),work=109,executable=link['executable']),
        confirmed=['System formatter:stage not0/1/2 emits centerFFCC1F00 then common dispatch; title suppresses center and chat',
        'MainGame3 uses separate process DWORD sequence,style2/category caller;category9 chooses25;nonzero style overrides; Tutorial2 has separate counter and forcesstyle2/category3',
        'Login1 updates real CGP_LogIn message256 at+372 through currentstage pointer; null clears; bounded copy zeroes256 and copies min(strlen+1,255)',
        'Login Render draws nonempty message after UI,centered using screen width and real text width,screenheight-30,colorFFFFA670,flags32,scale1',
        'Adjacent secondary message256 at+632 has an actual target quirk:null secondary setter clears primary+372',
        'Hover C1A:statuspredicate+pending then Clear(position/effect/sound/pending),localized message/common dispatch,then item mutation',
        'Arm CE7:clear request-process state,message/common dispatch,then start only ifpending0; repeated arm still outputs message',
        'Legacy source formatted output remains oldchat-only and DWORD overload no-op; actual factory MainGame2 differs from target3; existing bridge maps2to3'],
        next_work=111,next_action='Implement common dispatch in ordinary source with actual login/4pane/center sinks and C1A/CE7 producers; verify actual stage mapping/counters/sideeffects/order,not a message journal',
        gaps=['No runtime integration from this audit; live pending1 hover/CE7 caller remains open',
              'Full Tutorial/four-stage factory and login/auth/UI flow remain open; selected sink is not whole stage acceptance',
              'Formatted buffer size/unsafe overflow/null/CRTstartup/concurrency/privateABI and all previous client-acceptance gaps remain open'],
        runtime_changed=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-message-dispatch-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('AUDIT_OPEN:22functions/22fullasm/1254instructions,22bodies+1EHregion equalbothpins;23relativecalls/actualLoginRTTI;runtime109 unchanged;next111 source integration')


if __name__=='__main__':main()
