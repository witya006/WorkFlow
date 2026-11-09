"""Pin center-message lifecycle/dispatch and prove the pending frame-order gap."""
import hashlib
import json
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require, sha
from compare_client_binaries import WS, pe


def main():
    path=WS/'artifacts/client455-progress/messages108-reference.json';raw=json.loads(path.read_text())
    extra_path=WS/'artifacts/client455-progress/messages108-implementation-reference.json';extra=json.loads(extra_path.read_text())
    functions=[row['fn'] for row in raw['ranges']['result']+extra['ranges']['result']];assembly={row['addr']:row for row in raw['assembly']+extra['assembly']}
    code={row['addr']:row for row in raw['functions']+[raw['chat']]+extra['functions']}
    require(len(functions)==25 and len(assembly)==21 and sum(row['instruction_count'] for row in assembly.values())==2914,'Selected coverage')
    for fn in functions:
        require(fn is not None,'Missing function boundary');addr=fn['addr']
        if addr in assembly:require(assembly[addr]['cursor']['done'] and assembly[addr]['instruction_count']==assembly[addr]['total_instructions'],'Complete assembly')
        else:require(code[addr]['cursor']['done'] and not code[addr]['truncated'],'Complete selected pseudocode')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path455=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path455.read_bytes()
        require(sha(path455)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 reference')
        ranges=[dict(rva=hex(int(fn['addr'],16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(fn['addr'],16),int(fn['size'],16))).hexdigest()) for fn in functions]
        refs.append(dict(sha256=sha(path455),architecture='x86',image_base='0x400000',ranges=ranges))
    require(refs[0]['ranges']==refs[1]['ranges'],'Selected reference equivalence')
    def call(caller,target):
        rows=[row for row in assembly[caller]['asm']['lines'] if row['instruction'].startswith('call ') and any(ref['addr']==target for ref in row.get('refs',[]))]
        require(len(rows)==1,'Unambiguous caller edge '+caller+'->'+target)
        return int(rows[0]['addr'],16)
    update=call('0x549f20','0x54d900');effects=call('0x549f20','0x7e1c30')
    aiming=call('0x54a830','0x52ae70');draw=call('0x54a830','0x54dcb0')
    require(update<effects and aiming<draw,'Target update/render ordering')
    render=assembly['0x54a830']['asm']['lines'];ui=[int(render[i+1]['addr'],16) for i,row in enumerate(render[:-1]) if row['instruction']=='mov eax, [edx+28h]' and render[i+1]['instruction']=='call eax']
    require(len(ui)==1 and ui[0]<aiming,'UI virtual Draw precedes aiming container frame')
    session=WS/'artifacts/client455-progress/messages108-session.json';state=json.loads(session.read_text())
    require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'Owned IDA cleanup')
    source=WS/'work/client455-port/normal/source';early=source/'addcodebyjang/foreffect.cpp';late=source/'gameprogress/cgp_maingame.cpp'
    late_text=late.read_bytes();source_timing=b'RF455_NuclearAiming().FrameMove();' not in early.read_bytes() and late_text.count(b'RF455_NuclearAiming().FrameMove();')==1 and late_text.index(b'_GetUIScreen()->Draw();')<late_text.index(b'RF455_NuclearAiming().FrameMove();')
    implementation_session=WS/'artifacts/client455-progress/messages108-implementation-session.json';impl_state=json.loads(implementation_session.read_text());require(impl_state['closed']['success'] and impl_state['closed']['saved'] and not impl_state['after']['count'],'Implementation IDA cleanup')
    report=dict(status='CONFIRMED_SELECTED',scope='Center-message queue/84byte record/lifecycle, medium-font measurement, stage owner and C1A dispatch dependencies; full message runtime requires separate native evidence',script_sha256=sha(Path(__file__)),raw_evidence=record(path),additional_evidence=record(extra_path),session=record(session),implementation_session=record(implementation_session),references=refs,selected_functions=25,complete_assembly_functions=21,instructions=2914,pseudocode_only_functions=4,
                frame_order=dict(center_update_rva=hex(update-0x400000),ordinary_effect_frame_rva=hex(effects-0x400000),UI_draw_rva=hex(ui[0]-0x400000),nuclear_container_frame_rva=hex(aiming-0x400000),center_draw_rva=hex(draw-0x400000)),current_source_timing_matches_target=source_timing,current_sources=[record(early),record(late)],
                facts=['Center owner consists of two list12 members: pending64byte chunks then up to3 active84byte records; constructor/destructor bind/unbind singleton C0BD60',
                       'Text chunks use actual _mbsnbcpy with59byte limit and zeroed60byte buffer; ambient CRT multibyte mode is independent of NDLanguage codepage; immediate short message only when pending queue is empty',
                       'Active record x0/y4/text60@8/colorDWORD68/timeDWORD72/scaleFloat76=1/alphaFloat80=0',
                       'Update promotes at most one queued chunk when active empty, newest age>500ms, or pending queue>5; iterates active newest-to-oldest',
                       'Update uses unbounded float factor loopTime*4.5, newest scale1 and others0.8, line targetY200-index*fontHeight, centering and alpha fade; age>=3600ms fades to0',
                       'Deletes at most one oldest active record per update only if age>3600ms and alpha<=0.01; Draw oldest-to-newest uses font flags80000010 and own scale',
                       '5E47A0 formats buffer then routes stage3/other non0/1/2 into center withcolorFFCC1F00, then common chat/login dispatch5E4A60',
                       'Stage1 uses real login progress message sink; stage3 and stage2 have separate sequence counters; actual chat InsertText745B80 has4panes,14message categories,style18byte records and wrapping dependency746020',
                       'Target MainGame embeds center owner at byte177440,constructor/destructor own its lifetime; message measure8C6380 has a fourth flags argument hidden by old decompiler prototype,80000010 selects actual medium font',
                       'Actual target aiming container Frame runs at end of Render after UI Draw, then center Draw; migrated source timing is separately recorded and full world runtime remains unaccepted'],
                gaps=['Message owner runtime/GPU/stage lifetime and C1A/CE7 caller integration require current native/checkpoint evidence',
                      'Target4pane chat/style records/wrapping and login/Tutorial sinks cannot be replaced by legacy chat-only output',
                      'Full world pipeline/camera/render reset integration requires runtime acceptance beyond the selected late Render source hook',
                      'Command/response producers,list12 nuclear container,final position commit and all previous client-acceptance gaps remain open'],input_exe_executed=False,server_modified=False,runtime_changed=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-system-messages-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('25selected/21fullasm/2914instructions/25equalranges;lateRender source timing='+str(source_timing)+';full message dispatch OPEN')


if __name__=='__main__':main()
