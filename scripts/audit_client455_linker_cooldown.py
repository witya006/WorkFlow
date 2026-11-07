"""Pin complete selected Linker virtuals/cache/ready-animation contracts before porting."""
import hashlib,json
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_linker_window import dimensions
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS,pe

def main():
    path=WS/'artifacts/client455-progress/linker-cooldown099-reference.json';raw=json.loads(path.read_text());extra_path=WS/'artifacts/client455-progress/linker-cooldown099-extra.json';extra=json.loads(extra_path.read_text())
    merged=lambda key:{int(row['addr'],16):row for group in [raw,extra] for row in group[key]}
    functions=list(merged('ranges').values());assembly=list(merged('assembly').values());bodies=list(merged('functions').values());require(len(functions)==len(assembly)==len(bodies) and len(functions)==79,'Full selected function set')
    for body in bodies:require(body['code'] and not body['truncated'] and body['cursor']['done'],'Incomplete pseudocode')
    for body in assembly:require(body['cursor']['done'] and body['instruction_count']==body['total_instructions']==len(body['asm']['lines']),'Incomplete selected assembly')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        binary_path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=binary_path.read_bytes();require(sha(binary_path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86','Pinned client identity');ranges=[];tails=[]
        for fn in functions+[dict(addr='0xaae914',size=hex(320)),dict(addr='0xada7d4',size=hex(120)),dict(addr='0xaac13c',size=hex(20))]:
            va,size=int(fn['addr'],16),int(fn['size'],16);ranges.append(dict(rva=hex(va-0x400000),bytes=size,sha256=hashlib.sha256(read_va(binary,va,size)).hexdigest()))
        for fn,body in zip(functions,assembly):
            begin=int(fn['addr'],16);end=begin+int(fn['size'],16)
            for line in body['asm']['lines']:
                addr=int(line['addr'],16)
                if not begin<=addr<end:tails.append(dict(rva=hex(addr-0x400000),bytes=15,sha256=hashlib.sha256(read_va(binary,addr,15)).hexdigest()))
        references.append(dict(sha256=sha(binary_path),architecture='x86',image_base='0x400000',ranges=ranges,external_assembly_windows=tails))
    require(references[0]['ranges']==references[1]['ranges'] and references[0]['external_assembly_windows']==references[1]['external_assembly_windows'],'Selected client contracts differ')
    by_addr={int(row['addr'],16):row for row in assembly}
    def instructions(va):return '\n'.join(row['instruction'] for row in by_addr[va]['asm']['lines'])
    require('add ecx, 1315Ch' in instructions(0x501c30) and 'mov [eax+10h], ecx' in instructions(0x501c30),'Cache owner20-byte record writes')
    require('cmp eax, 32h' in instructions(0x501750) or '32h' in instructions(0x501750),'Fifty cache records')
    require('imul eax, 3BC8h' in instructions(0x5019e0) and 'call sub_60C680' in instructions(0x5019e0),'Bank membership predicate is actual root-list membership')
    require('sub_628AE0' in instructions(0x501750) and 'sub_502C20' in instructions(0x501750),'Ready cue reset/queue on expiration')
    require('call sub_502C50' in instructions(0x501750) and 'call sub_502D30' in instructions(0x501750) and 'call sub_502D30' in instructions(0x5032a0),'Pending erase/postincrement sequence')
    selected_virtuals={row['offset']:int(row['addr'],16) for row in raw['virtuals']};require(selected_virtuals[8]==0x501750 and selected_virtuals[12]==0x501a20 and selected_virtuals[52]==0x500590 and selected_virtuals[64]==0x5007e0,'Actual Linker virtual bindings')
    # Common frame13:0 is not a40-frame SPR action. It is one sheet with8x5
    # cells. Its original height640 differs from padded texture height1024.
    sprite_row=next(row for row in load('client455-linker-window-reference')['inputs'] if row.get('runtime_relative')=='SpriteImage/zh-tw/common.spr');check(sprite_row);frame=dimensions((WS/sprite_row['file']).read_bytes())[(13,0)]
    require(frame[1:]==(1024,640,1024,1024),'Ready-sheet geometry changed')
    facts=[
        dict(rva='0x101c30',contract='Cache admission checks attached bank row OR active bank;not IsShow or pin flags alone. Each free matching slot gets its own clock reading;occupied entries are not restarted.'),
        dict(rva='0x101c30',contract='Match wrapper virtual kind and code,then wrapper index against source item serial+4. Index,server index anddata-code are distinct comparisons.'),
        dict(rva='0x101c30',contract='Raw gate114A070 defaults0;nonzero gate suppresses the entire routine for kind1. Meaning beyond this behavior is not yet named.'),
        dict(rva='0x101750',contract='Expiration uses unsigned DWORD(now-start)+offset>=duration. Even hidden/removed-bank entries expire and are cleared;ready cues are attached only for admitted/current banks.'),
        dict(rva='0x1007e0',contract='Remove clears matching object pointer andstart timestamp only;bank/offset/duration remain. Expiration clears all20 record bytes.'),
        dict(rva='0x1019e0',contract='Calls root CGUIContainer membership test with window+0x150+bank*0x3bc8. Active bank is an explicit separate exception.'),
        dict(rva='0x21af30',contract='Ready child at GUIItem+1040 uses atlas1/action13/frame0,128x128,8columns5rows,FPS34,no loop,initial stopped;blend mode3.'),
        dict(rva='0x228bd0',contract='Animation Update uses source loopSeconds,Show/paused/stopped gates,strict pause elapsed>interval,frame spill then total comparison;one-shot clamps last frame andsets stopped.'),
        dict(rva='0x21b240',contract='Ready cue centered with signed integer (iconSize-cueSize)/2. It is a separate child attached towindow,not the radial timer or always-drawn GUIItem child.'),
        dict(rva='0x4c6f40',contract='Blend mode3 uses SRCALPHA/ONE and modulated texture alpha. Reusing existing alpha-only DrawSpriteUV would produce different output.'),
        dict(rva='0x102190',contract='Original-owner lookup forphysical kind0 checks boards1,0,5;equal lookup502330 checks1,0. SF branches3/7,Animus4,kind6 board22,Macro7 board35.'),
        dict(rva='0x101a20',contract='Window messages use raw455 codes501/502/504/50c/510/512/3327. Legacy global enums must not be silently substituted.')]
    facts.append(dict(rva='0x101953',contract='Erase returns advanced iterator;the outer loop then increments it again unconditionally. Adjacent stopped cues can survive to a later frame;do not replace with a conventional erase-without-increment loop. End/sentinel unsafe domains remain open.'))
    session=WS/'artifacts/client455-progress/linker-cooldown099-session.json';state=json.loads(session.read_text());require(state['closed']['saved'] and state['closed']['success'] and state['after']['count']==0,'IDA session cleanup')
    report=dict(status='STATIC_ONLY_NOT_IMPLEMENTED',scope='Selected full Linker virtual methods,cooldown records,original-owner routes and required ready-animation dependency',script_sha256=sha(Path(__file__)),raw_evidence=[record(path),record(extra_path)],session=record(session),references=references,functions=len(functions),assembly_instructions=sum(row['instruction_count'] for row in assembly),virtuals=raw['virtuals'],ready_sheet=dict(input=sprite_row,action=13,frame=0,original=[1024,640],texture=[1024,1024],columns=8,rows=5,cell=[128,128],fps=34,blend_mode=3),confirmed=facts,
        next_dependency='Implement source-owned CGUIObjectAni-compatible ready child and mode3 draw first;then wire real cache/FrameMove/remove/typedBegin andcompletehandlers. Current production098 remains unchanged.',
        unknowns=['Gate114A070 broadergame meaning','Pending-list end/sentinel/unsafe/OOM/concurrency domains','Remaining live callbacks/lock/SF-Quest/Macro/Vending/fullAdd/bootstrap andallpriorclient gaps'],current_runtime_gate='inventory/client455-gui-timer-checkpoint.json',production_changed=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-linker-cooldown-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],functions=len(functions),instructions=report['assembly_instructions'],ranges=len(references[0]['ranges']),ready_sheet=frame)))
if __name__=='__main__':main()
