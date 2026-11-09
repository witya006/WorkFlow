"""Predict the real teardown trace from pinned target semantics, then compare."""
import json,re
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS
from texture_release455 import release


def main():
    ref=load('client455-texture-lifetime-reference');native=load('client455-texture-lifetime-native');check(native['trace']);trace=json.loads((WS/native['trace']['file']).read_text());states={x['phase']:x for x in trace['states']}
    require(list(states)==['before_shared','shared_acquired','shared_first_release','shared_other_image','before_cache','after_cache','before_world','after_world','after_engine'],'Complete ordered trace')
    before,acquired,first,other=[states[x] for x in ['before_shared','shared_acquired','shared_first_release','shared_other_image']];index,start=trace['shared_record'],trace['shared_start']
    expected=json.loads(json.dumps(before['rows']));expected[index-1]['same']+=1;require(acquired['rows']==expected and acquired['textures']==before['textures'],'Actual cache hit increments package count without loading/releasing')
    predicted=release(acquired,[start]);require(predicted['rows']==first['rows'] and list(predicted['textures'].values())==first['textures'] and not predicted['warnings'] and predicted['shared']==[start],'First image decrements package shared counter')
    require(other['rows']==before['rows'] and other['textures']==before['textures'],'Other image uses same shared counter and restores initial table state')
    require(states['before_cache']['rows']==before['rows'],'Shared branch exercise restores original records')
    owners=trace['owners'];require(len(owners)==21 and [x['real'] for x in owners]==sorted(x['real'] for x in owners) and all(not x['flags']&8 for x in owners),'All real managed cache owners in target order')
    ids=[x['start']+i for x in owners for i in range(x['count'])];predicted=release(states['before_cache'],ids);after=states['after_cache']
    require(predicted['rows']==after['rows'] and list(predicted['textures'].values())==after['textures'],'All actual post-cache rows/handles/refcounts equal target prediction')
    warnings=trace['warnings'];require(len(warnings)==len(predicted['warnings'])==20 and len(predicted['shared'])==4 and len(predicted['freed'])==20 and len(ids)==24,'24 owner/image releases ->4 shared decrements+20 warnings/COM releases')
    expected_warning=ref['warning_base_hex']+ref['warning_suffix_hex'];require(all(x['phase']=='cache_release' and x['hex']==expected_warning for x in warnings),'Exact target warning bytes and phase')
    require(len(trace['pins'])==20 and len(trace['world_pins'])==132,'Every actual managed texture observed')
    require({x['id'] for x in trace['pins']}==set(predicted['freed']),'Effect pins correspond to actual released slots')
    require({x['id'] for x in trace['world_pins']}=={x['id'] for x in after['textures']},'World pins cover every remaining slot')
    for pin in trace['pins']+trace['world_pins']:require(pin['before_refs']==pin['after_refs']+1 and pin['pin_release_return']==0,'One engine COM release,then last lab pin releases actual object')
    require(len(states['before_cache']['textures'])==152 and len(after['textures'])==132 and not states['after_world']['textures'],'Actual152 ->132 ->0 managed handles')
    require(all(states[x]['records']==states[x]['slots']==1 and not states[x]['record_table'] and not states[x]['surface_table'] for x in ['after_world','after_engine']),'Global table free/count reset')
    require(states['after_world']['dmalloc']==785169 and states['after_engine']['dmalloc']==0,'Recorded scoped tracked allocator tail then0')
    require(trace['warning_callback_target_bytes'] and trace['warning_ignore_flag'] and trace['warning_without_callback_returns'],'Three Warning branches')
    mapping=(WS/native['map']['file']).read_text();entries=sorted((int(va,16)-0x400000,name) for name,va in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\b',mapping,re.M));stack_roles=[]
    for prefix in ['?R3ReleaseTextureMem@@','?ReleaseTexMem@CEntity@@','?ReleaseEffectEntityList@@']:
        matches=[x for x in entries if x[1].startswith(prefix)];require(len(matches)==1,'Own retained stack role '+prefix);begin=matches[0][0];end=min(x[0] for x in entries if x[0]>begin)
        require(all(any(begin<=rva<end for rva in w['own_stack_rvas']) for w in warnings),'Every real warning stack includes '+prefix);stack_roles.append(dict(symbol=matches[0][1],begin_rva=hex(begin),end_rva=hex(end)))
    result=dict(status='PASS',script_sha256=sha(Path(__file__)),oracle=record(WS/'scripts/texture_release455.py'),native_sha256=sha(WS/'inventory/client455-texture-lifetime-native.json'),reference_sha256=sha(WS/'inventory/client455-texture-lifetime-reference.json'),trace=record(WS/native['trace']['file']),owners=21,texture_calls=24,shared_decrements=4,exact_warnings=20,effect_COM_releases=20,world_COM_releases=132,all_last_pins_release_to_zero=True,post_cache_exact=True,stack_roles=stack_roles,tracked_Dmalloc_final=0,full_memory_balance=False,full_device_lifecycle=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-texture-lifetime-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS:21owners/24calls/4shared/20exactwarnings;20FX+132worldCOMreleases,lastpins0;all Warning stacks/source states/bytes match;trackedDmalloc0')


if __name__=='__main__':main()
