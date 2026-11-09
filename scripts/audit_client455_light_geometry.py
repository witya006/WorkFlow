"""Pin selected light geometry/matrix contracts and the derived engine changes."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_texture_lifetime import archive_objects
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import load,require,sha,check
from compare_client_binaries import WS,pe
from audit_goal_checkpoint import runtime_sections


def main():
    raw_file=WS/'artifacts/client455-progress/light-geometry121-reference.json';raw=json.loads(raw_file.read_text());session_file=WS/'artifacts/client455-progress/light-geometry121-session.json';session=json.loads(session_file.read_text())
    selected=set(raw['selected']);bounds={x['query']:x['fn'] for x in raw['bounds']['result']};assembly={x['addr']:dict(pages=x['pages'],lines=[line for page in x['pages'] for line in page['asm']['lines']],total_instructions=x['coverage']['total']) for x in raw['assembly']}
    require(len(selected)==7 and set(bounds)==set(assembly)==selected,'Selected new geometry support')
    for addr in selected:
        rows=[x for x in raw['functions'] if x['addr']==addr];x=rows[-1]
        if 'pages' in x:require(sum(p['line_count'] for p in x['pages'])==x['pages'][0]['total_lines'] and x['pages'][-1]['cursor']['done'],'Complete new pcode pages')
        else:require(x['line_count']==x['total_lines'] and not x['truncated'] and x['cursor']['done'],'Complete new pcode')
    cache_file=WS/'artifacts/client455-progress/world-frame120-reference.json';cache=json.loads(cache_file.read_text());prior=json.loads((WS/'artifacts/client455-progress/client455-world-frame-reference-before121.json').read_text());require(prior['raw']['sha256']==sha(cache_file),'Exact cached120 evidence')
    cached=['0x8fe980','0x8fec90','0x8f66b0','0x8f67d0','0x8c4ec0']
    for addr in cached:
        assembly[addr]=next(x for x in cache['assembly'] if x['addr']==addr);bounds[addr]=next(x['fn'] for x in cache['extra_bounds']['result'] if x['query']==addr)
        x=next(x for x in cache['functions'] if x['addr']==addr)
        tail=[x]
        if addr in ['0x8fe980','0x8fec90']:tail+=[next(x for x in cache['extra_tails'] if x['addr']==addr)]
        elif addr=='0x8c4ec0':tail+=[cache['declaration_page'],cache['declaration_tail']]
        require(sum(x['line_count'] for x in tail)==tail[0]['total_lines'] and tail[-1]['cursor']['done'],'Complete cached selected pcode')
    for x in assembly.values():
        require(len(x['lines'])==x['total_instructions']==sum(p['instruction_count'] for p in x['pages']) and len({r['addr'] for r in x['lines']})==len(x['lines']) and x['pages'][-1]['cursor']['done'],'Full unique assembly')
        require(all(len(p['asm']['lines'])==p['instruction_count']<=120 for p in x['pages']),'Bounded MCP pages')
    require(sum(assembly[x]['total_instructions'] for x in selected)==712,'New instruction total')
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(image)['architecture']=='x86','Pinned x86 client')
        ranges=[dict(rva=hex(int(at,16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(image,int(at,16),int(fn['size'],16))).hexdigest()) for at,fn in sorted(bounds.items())];calls=[]
        for fn in assembly.values():
            for line in fn['lines']:
                if not line['instruction'].startswith('call ') or not line.get('refs'):continue
                at=int(line['addr'],16);b=read_va(image,at,5)
                if b[0]!=0xe8:continue
                dest=int(line['refs'][0]['addr'],16);require(at+5+struct.unpack('<i',b[1:])[0]==dest,'Decoded direct call');calls.append(dict(rva=hex(at-0x400000),target_rva=hex(dest-0x400000)))
        require(sum(x['target_rva']=='0x4fdca0' for x in calls)==2,'Two inspected owners call matrix setter')
        require(sum(x['target_rva']=='0x4c0030' for x in calls)==2,'Both BSP matrices initialize to identity')
        row=dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,decoded_calls=calls);require(not references or {k:v for k,v in row.items() if k!='sha256'}=={k:v for k,v in references[0].items() if k!='sha256'},'Both selected455 references equal');references.append(row)
    engine=load('client455-startup-engine-build');require(engine['objects']==67 and len(engine['derived_sources'])==14 and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current derived engine')
    for row in engine['base_sources']+engine['derived_sources']+[engine['baseline_library'],engine['bsp_header_overlay'],engine['camera_header_overlay'],engine['particle_header_overlay']]:check(row)
    for name,digest in engine['bsp_light'].items():require(sha(WS/'scripts/native'/name)==digest,'Exact BSP light sources')
    old=WS/'artifacts/client455-progress/engine-before121.lib';require(sha(old)=='7c828f7767bfa5a36ce0d8df2f2f133fc91a235284115c49c75e496a289252e9','Exact120 engine')
    a,b=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(a)==67,'Same67 engine members');code=[];stamp=[];same=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload']
        if x==y:same.append(name)
        elif len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:]:stamp.append(name)
        else:code.append(name)
    runtime_changed=[name for name in a if runtime_sections(a[name]['payload'])!=runtime_sections(b[name]['payload'])]
    gaps=['Full placed BSP/ILevel/INS/Empty transform writers and inverse-matrix consumers are not ported;the source-owned128-byte extension is not target private-layout parity','Finite fixture geometry and actual Bellato lighting do not prove all leaf recursion/oblique planes/invalid IDs/NaN/FP modes/CRT/concurrency or unsafe target domains','Selected declaration create/release is verified;full lost-device/reset/recreate/failure/OOM/error paths and renderer pipeline remain open','Full world/Character/input/stages/auth/protocol/gameplay and all other client-acceptance gaps remain;M6/M6F/M7/M9 OPEN']
    result=dict(status='CONFIRMED_SELECTED',scope='Selected regular/magic BSP light geometry guards,deduplication,batches,owned world/inverse matrices and explicit declaration;full renderer remains open',script_sha256=sha(Path(__file__)),raw=record(raw_file),session=record(session_file),cached_raw=record(cache_file),cached_reference=record(WS/'artifacts/client455-progress/client455-world-frame-reference-before121.json'),new_full_assembly=7,new_instructions=712,full_assembly=len(assembly),instructions=sum(x['total_instructions'] for x in assembly.values()),references=references,engine=record(WS/engine['library']),old_engine=record(old),code_changed_members=code,timestamp_only_members=stamp,unchanged_members=same,sources=[record(WS/'scripts/native'/x) for x in engine['bsp_light']],header_overlay=engine['bsp_header_overlay'],matrix_contract=dict(target_world_offset=372,target_inverse_offset=436,copy_bytes_each=64,source_layout_equivalence=False),gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    result['payload_changed_members']=result.pop('code_changed_members');result['runtime_section_or_relocation_changed_members']=runtime_changed
    (WS/'inventory/client455-light-geometry-reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(asm=len(assembly),instructions=result['instructions'],runtime_sections_or_relocations=runtime_changed,other_payload_changes=len(code),stamp=len(stamp),same=len(same))))


if __name__=='__main__':main()
