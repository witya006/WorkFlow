"""Pin the aiming member20, pending quirks, cursor and child-movement contracts."""
import hashlib,json
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe


def main():
    path=WS/'artifacts/client455-progress/nuclear107-reference.json';raw=json.loads(path.read_text());functions=[row['fn'] for row in raw['ranges']['result']]
    require(len(functions)==19 and all(functions) and all(row['cursor']['done'] for row in raw['functions']+raw['assembly']),'Complete selected functions')
    require(sum(row['instruction_count'] for row in raw['assembly'])==1670,'Instruction coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';data=binary.read_bytes();require(sha(binary)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned input')
        ranges=[dict(rva=hex(int(fn['addr'],16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(fn['addr'],16),int(fn['size'],16))).hexdigest()) for fn in functions]
        slots=[dict(rva=hex(addr-0x400000),bytes=4,sha256=hashlib.sha256(read_va(data,addr,4)).hexdigest()) for addr in [0xb38504,0xaecb5c]]
        require(read_va(data,0xb38504,4)==bytes.fromhex('f07d8e00') and read_va(data,0xaecb5c,4)==bytes.fromhex('f07e7c00'),'Actual level/dummy pick slots')
        references.append(dict(sha256=sha(binary),architecture='x86',image_base='0x400000',ranges=ranges,pick_slots=slots))
    require(references[0]['ranges']==references[1]['ranges'] and references[0]['pick_slots']==references[1]['pick_slots'],'Reference equivalence')
    resources=json.loads((WS/'inventory/client455-effect-resources-reference.json').read_text());audio=json.loads((WS/'inventory/client455-tagged-audio-reference.json').read_text())
    report=dict(status='CONFIRMED_SELECTED',scope='MainApp-owned equivalent of inline aiming20, ordinary frame hook, real cursor/effect/audio core and pending0 hover path; full nuclear command/C1A/notification lifecycle still open',script_sha256=sha(Path(__file__)),raw_evidence=record(path),references=references,functions=19,instructions=1670,effect_input_reference=record(WS/'inventory/client455-effect-resources-reference.json'),audio_input_reference=record(WS/'inventory/client455-tagged-audio-reference.json'),inputs=resources['inputs']+audio['inputs'],
                contracts=['Inline aiming member20:handleDWORD0,pendingDWORD4,command position3floats8; ctorzeros20, destructor empty; Clear zeroescommand position,stopsvisual,thenpending0',
                           'SetPending only calls SetVisualState when oldpending==0, then stores fullDWORD input. Pending1to0 retains visual/audio; repeated1 doesnot restart',
                           'SetVisualState1 first expires oldhandle,queries live cursor,starts null-character cue1358041136,always plays Radar277034 loop1/tag1,forces actual dynamic-light limit3',
                           'Non1 visual state stops effect/audio only when handle!=0. Missing effect can stillplay sound; Clear withhandle0 leaves itplaying',
                           'SetPosition copies threefloats independently; visual cursor neverupdates this commandposition. Frame requires bothhandle andpending',
                           'Real CLevel vtable slot28 resolves to8E7DF0, dummy resolves to7C7EF0. Real wrapper subtracts viewport offsets andinvokes BSP pick; ortho/null dummy domains remainopen',
                           'MovePosMagicEffect sets old/new yaw,rotates eachtrack localoffset,add/moves/subtracts it using NowMagicListPtr,leaves master base matrix unchanged',
                           'Hover target cancels/messages only for actualavatar predicate AND pending!=0; pending0 path nowallowed, pending1 stillrefuses beforemutation untilC1A provider'],
                gaps=['Localized C1A/CE7 output and full notification/chat dispatch notrestored; pending1 hover cancellation stays explicitrefusal',
                      'Nuclear command/response/list12 container handlers,final position commit,otherinput cancels andcomplete gameframe order remainunported',
                      'Own core lives in CMainApp instead of recreating the whole32byte targetcontainer; selected state/layout proved,fullprivateABI notaccepted',
                      'Loaded perspective BSP path accepted only; target orthographic projection/menu dummy/OOM/null/uninitialized/FP domains notrestored andownadapter explicitlyrefuses them',
                      'MainApp Destroy explicitlyclears core beforeaudioClose; fulltarget shutdown order andallprevious effect/world/audio/client acceptance gaps remainmandatory'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-aiming-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('19functions/1670asm/19equalranges/2pickslots;C1A/fullnuclear remainopen')


if __name__=='__main__':main()
