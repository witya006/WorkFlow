"""Corroborate a live UI failure using own code/vtable and sequential source."""
import json,re,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,require,check

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def own_symbols(link):
    symbols=[]
    for line in (WS/link['map']['file']).read_text().splitlines():
        match=re.match(r'^\s+[\da-fA-F]+:[\da-fA-F]+\s+(\S+)\s+([\da-fA-F]{8})\b',line)
        if match:symbols.append((int(match[2],16)-0x400000,match[1]))
    return symbols
def corroborate_next_window(link,live,klass,before,after):
    require(live['first_login_frame_captured'] and live['login_render_returned_after_capture'] and live['live_server']['private_handoff_removed'],'Current pre-Enter frame andhandoff cleanup')
    for key in ['events','captured_frame','capture_metadata']:check(live[key])
    require(any(x.get('own_child_validated') and x.get('sent') for x in live['selection_input']),'Addressed own Enter')
    for value in ['RF455 Protocol:tx:1:14:1','RF455 Protocol:rx:1:15:22','RF455 Protocol:select-result:0:0:0']:require(value in live['protocol_observations'],'Actual live selection '+value)
    fatal=[x for x in live['exceptions'] if not x.get('first_chance')];require(len(fatal)==1 and fatal[0]['code']=='0xc0000005','Actual next failure')
    symbols=own_symbols(link)
    def resolve(address):
        start,name=max((a,n) for a,n in symbols if a<=address);return dict(rva=hex(address),symbol=name,offset=hex(address-start))
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    context=next(x for x in events if x['kind']=='fatal_context');require(context.get('readable_stack_words',0)>0 and context['own_stack_rva_candidates'],'Readable actual stack evidence')
    resolved=[resolve(int(fatal[0]['rva'],16))]+[dict(resolve(int(x['rva'],16)),stack_offset=x['stack_offset']) for x in context['own_stack_rva_candidates'][:18]]
    for name in ['SetSprite','Init']:require(any(name+'@'+klass in x['symbol'] for x in resolved),'Actual next window '+name)
    candidates=[x for x in resolved if 'Create_UI@CGP_MainGame' in x['symbol']];require(candidates,'Actual Create_UI caller candidate')
    tables=[(a,n) for a,n in symbols if n=='??_7'+klass+'@@6BCGUIContainer@@@'];require(len(tables)==1,'Own next-window primary vtable')
    raw=(WS/link['executable']['file']).read_bytes();target=struct.unpack('<I',read_va(raw,0x400000+tables[0][0]+0x6c,4))[0]-0x400000
    require('Init@'+klass in resolve(target)['symbol'] and resolve(target)['offset']=='0x0','Actual next-window Init slot')
    calls=[]
    for row in candidates:
        ret=int(row['rva'],16);instruction=read_va(raw,0x400000+ret-3,3)
        if instruction==b'\xff\x50\x6c':calls.append(dict(return_rva=hex(ret),instruction_rva=hex(ret-3),bytes=instruction.hex(),vtable_rva=hex(tables[0][0]),slot_offset='0x6c',callee=resolve(target)))
    require(calls,'Caller instruction corroborated by vtable andfatal inner methods')
    source=WS/'work/client455-port/normal/source/gameprogress/cgp_maingame.cpp';body=source.read_bytes();require(body.index(before.encode())<body.index(after.encode()),'Sequential completed window thenfailing window source')
    return dict(kind='UNHANDLED_AFTER_SUCCESSFUL_SELECTION',own_rva=fatal[0]['rva'],code=fatal[0]['code'],resolved_stack_candidates=resolved,stack_is_candidate_scan_not_unwind=True,verified_own_virtual_calls=calls,cause='Next old'+klass+'::SetSprite/Init;prior windowInit returned on the sequential MainGame::Create_UI path',whole_client_run_succeeded=False),record(source)
