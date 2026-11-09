"""Pin the light transform chain and exact linked x87 bodies in the own PE."""
import hashlib,json,re,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va,FUNCTIONS
from checkpoint_client455_rvp_effects import load,require,sha,check
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def ranges(raw):
    result=[]
    def add(addr,size,cfg,assembly,count,pages=None):
        lines=assembly['lines'];addresses={int(x['addr'],16) for x in lines}
        require(len(lines)==len(addresses)==count and all(int(b['start'],16) in addresses for b in cfg['blocks'] if b['size']>0)
                and cfg['count']==cfg['total_blocks']==len(cfg['blocks']) and cfg['cursor']['done'],'All instructions and CFG blocks '+addr)
        if pages:require(all(p['instruction_count']==len(p['asm']['lines'])<=100 for p in pages) and sum(p['instruction_count'] for p in pages)==count and pages[-1]['cursor']['done'],'Bounded full assembly pages')
        spans=[(int(addr,16),int(addr,16)+size)]+[(int(b['start'],16),int(b['end'],16)) for b in cfg['blocks'] if b['size']>0];merged=[]
        for lo,hi in sorted(spans):
            if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
            else:merged.append([lo,hi])
        result.extend((addr,lo,hi-lo) for lo,hi in merged)
    bounds={x['query']:x['fn'] for x in raw['bounds']['result']}
    for a in raw['assembly']:
        cfg=next(x for x in raw['cfg'] if x['addr']==a['addr']);add(a['addr'],int(bounds[a['addr']]['size'],16),cfg,a,a['total_instructions'],a['pages'])
    for q in raw['queries']:
        addr=q.get('addr','0x874514');asm=q['asm'];bound=q['bounds']['result'][0]['fn'];cfg=q['cfg']['result'][0]
        require(asm['cursor']['done'] and asm['instruction_count']<=100,'Bounded complete CRT context')
        add(addr,int(bound['size'],16),cfg,asm['asm'],asm['total_instructions'])
    return result


def symbols(mapping):
    return {m[1]:int(m[2],16) for line in mapping.splitlines() if (m:=re.match(r'^\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\b',line))}


def linked(raw,mapping,reference,require_owner=True):
    names=symbols(mapping);out=[]
    for name,va,size in FUNCTIONS+[('_RF455_NormalizeLightVector',0x51d5d0,0x88)]:
        at=names[name];expected=bytearray(read_va(reference,va,size));actual=read_va(raw,at,size);relocated=[]
        if name=='_RF455_MatrixInvert':
            epsilon=names['_RF455_AffineEpsilon'];require(read_va(raw,epsilon,4)==struct.pack('<f',.001),'Actual linked epsilon')
            expected[0x21:0x25]=struct.pack('<I',epsilon);relocated.append(dict(offset='0x21',kind='absolute epsilon',target_rva=hex(epsilon-0x400000)))
        elif name=='_RF455_NormalizeLightVector':
            require(actual[0x39]==expected[0x39]==0xe8,'Normalizer sqrt wrapper CALL')
            target=at+0x3e+struct.unpack_from('<i',actual,0x3a)[0];require(target==names['_RF455_LightSqrt'],'Selected own sqrt policy backend')
            expected[0x3a:0x3e]=actual[0x3a:0x3e];relocated.append(dict(offset='0x3a',kind='relative CALL to selected finite sqrt policy',target_rva=hex(target-0x400000)))
        require(actual==expected,'Exact linked function body except verified relocation '+name)
        out.append(dict(name=name,rva=hex(at-0x400000),reference_rva=hex(va-0x400000),bytes=size,sha256=hashlib.sha256(actual).hexdigest(),relocated=relocated))
    if require_owner:require('_RF455_BuildLightDirection' in names,'Ordinary linked light owner')
    return out


def main():
    file=WS/'artifacts/client455-progress/light-direction131-reference.json';session_file=WS/'artifacts/client455-progress/light-direction131-session.json';raw=json.loads(file.read_text());session=json.loads(session_file.read_text());spans=ranges(raw)
    require(len(raw['selected'])==5 and sum(x['total_instructions'] for x in raw['assembly'])==315
            and sum(x['asm']['total_instructions'] for x in raw['queries'])==96,'5primary315 plus5CRT96 instructions')
    require(all(sum(x['line_count'] for x in f['pages'])==f['pages'][0]['total_lines'] and f['pages'][-1]['cursor']['done'] for f in raw['functions']),'Primary complete decompilation')
    require(session['saved']['ok'] and session['closed']['saved'] and session['closed']['success'] and session['after']['count']==0,'Owned session saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 reference')
        rows=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(lo-0x400000),bytes=size,sha256=hashlib.sha256(read_va(data,lo,size)).hexdigest()) for owner,lo,size in spans]
        if refs:require(rows==refs[0]['ranges'],'Both455 pinned bodies and shared CRT tails equal')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=rows))
    engine=load('client455-startup-engine-build');old=json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before131.json').read_text());before=WS/'artifacts/client455-progress/engine-before131.lib'
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and sha(before)==old['library_sha256'],'Current engine and exact130 backup')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    for key in ['camera_header_overlay','vertex_header_overlay','particle_header_overlay','core_header_overlay','level_header_overlay']:
        check(engine[key]);require(engine[key]['sha256']==old[key]['sha256'],'Shared headers unchanged;no182 rebuild required')
    a,b=archive_objects(before,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(b)==67,'Same67 engine objects')
    changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload'];(same if x==y else stamp if len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:] else changed).append(name)
    require(len(changed)==1 and 'renderentity' in changed[0].lower(),'Only real entity lighting payload changed')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact current normal link');data=(WS/link['executable']['file']).read_bytes();mapping=(WS/link['map']['file']).read_text();reference=(WS/'work/client-reference/current/RF_Online.bin').read_bytes();bodies=linked(data,mapping,reference)
    math=load('client455-light-direction-math');cpu_bodies=linked((WS/math['exe']['file']).read_bytes(),(WS/math['map']['file']).read_text(),reference,False)
    sources=[record(WS/'scripts/native'/name) for name in ['client455_light_direction.h','client455_light_direction.inc','client455_entity_lighting.inc']]
    require(engine['light_direction']=={Path(x['file']).name:x['sha256'] for x in sources[:2]} and engine['lighting_consumers']['client455_entity_lighting.inc']==sources[-1]['sha256'],'Current connected source')
    previous=json.loads((WS/'artifacts/client455-progress/client455-lighting-consumers-checkpoint-before131.json').read_text())
    gaps=[x for x in previous['gaps'] if not x.startswith('Target lit transform uses')]
    gaps+=['Inverse/transform and normalizer bodies are instruction-identical except selected sqrt CALL. Finite masked12PC/RC values verified;old CRT matherr/errno/precision-error dispatch,unmasked exceptions and complete NaN/Inf/status-flag parity remain open',
           'Actual caller ignores failed affine inverse and then consumes unspecified stack data;no deterministic fallback added. Failed caller output is not accepted',
           'Earlier130 described Vector3fTransform as legacy;the source already used the exact455x87 wrapper.131 reuses that backend and replaces the D3DX inverse and separate entity normalizer']
    out=dict(status='CONFIRMED_SELECTED',script=record(Path(__file__)),scope='Exact light affine inverse/transform and normalizer body with selected finite CRT sqrt rounding policy;actual LitGrass consumers',raw=record(file),session=record(session_file),
             full_assembly=10,primary_functions=5,primary_instructions=315,CRT_context_instructions=96,verified_ranges=len(spans),CFG_complete=True,CRT_decompilation_complete=False,references=refs,sources=sources,engine=record(WS/engine['library']),old_engine=record(before),
             changed_members=changed,timestamp_only_members=stamp,unchanged_members=same,shared_headers_changed=False,normal_executable=link['executable'],normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),linked_bodies=bodies,CPU_linked_bodies=cpu_bodies,
             previous130_gate=record(WS/'artifacts/client455-progress/client455-lighting-consumers-checkpoint-before131.json'),gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-light-direction-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=10,instructions=411,ranges=len(spans),changed=len(changed),same=len(same),stamp=len(stamp),linked_bodies=len(bodies))))


if __name__=='__main__':main()
