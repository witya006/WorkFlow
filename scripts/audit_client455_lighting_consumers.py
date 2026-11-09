"""Pin actual455 lighting consumers,vertex layout and typed material mapping."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def contracts(raw):
    selected=set(raw['selected']);asm={x['addr']:x for x in raw['assembly']};cfg={x['addr']:x for x in raw['cfg']}
    require(selected==set(asm)==set(cfg),'Selected complete assembly/CFG sets')
    bounds={x['query']:x['fn'] for x in raw['bounds']['result']};spans=[]
    for at in sorted(selected):
        a,g=asm[at],cfg[at];addresses={int(x['addr'],16) for x in a['lines']}
        require(len(a['lines'])==len(addresses)==a['total_instructions']==sum(x['instruction_count'] for x in a['pages'])
                and all(x['instruction_count']==len(x['asm']['lines'])<=100 for x in a['pages']) and a['pages'][-1]['cursor']['done']
                and g['count']==g['total_blocks']==len(g['blocks']) and g['cursor']['done']
                and all(int(x['start'],16) in addresses for x in g['blocks'] if x['size']>0),'All instructions and positive CFG starts '+at)
        p=next(x for x in raw['functions'] if x['addr'].lower()==at)['pages']
        require(sum(x['line_count'] for x in p)==p[0]['total_lines'] and p[-1]['cursor']['done'],'Full selected decompilation '+at)
        ranges=[(int(at,16),int(at,16)+int(bounds[at]['size'],16))]+[(int(x['start'],16),int(x['end'],16)) for x in g['blocks'] if x['size']>0];merged=[]
        for lo,hi in sorted(ranges):
            if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
            else:merged.append([lo,hi])
        spans.extend((at,lo,hi-lo) for lo,hi in merged)
    return spans,sum(x['total_instructions'] for x in asm.values())


def main():
    files=[WS/'artifacts/client455-progress'/name for name in ['lighting-consumers130-reference.json','lighting-consumers130-material-reference.json']]
    raws=[json.loads(x.read_text()) for x in files];spans=[];instructions=0
    for raw in raws:
        ranges,count=contracts(raw);spans.extend(ranges);instructions+=count
    require(len(raws[0]['selected'])==16 and len(raws[1]['selected'])==1 and instructions==3450,'17 full functions/3450instructions')
    sessions=[WS/'artifacts/client455-progress'/name for name in ['lighting-consumers130-session.json','lighting-consumers130-material-session.json']]
    transform_file=WS/'artifacts/client455-progress/lighting-consumers130-transform-context.json'
    transform_session=WS/'artifacts/client455-progress/lighting-consumers130-transform-session.json'
    transform=json.loads(transform_file.read_text());sessions.append(transform_session)
    for file in sessions:
        s=json.loads(file.read_text());require(s['saved']['ok'] and s['closed']['success'] and s['after']['count']==0,'Owned IDA saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    declaration=b''.join(struct.pack('<HHBBBB',*x) for x in [(0,0,2,0,0,0),(0,12,2,0,3,0),(0,24,4,0,10,0),(0,28,1,0,5,0),(255,0,17,0,0,0)])
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();image=pe(data)
        require(sha(path)==pins[key]['sha256'] and image['architecture']=='x86' and image['image_base']==0x400000,'Pinned455 binary')
        ranges=[dict(owner_rva=hex(int(at,16)-0x400000),rva=hex(lo-0x400000),bytes=size,sha256=hashlib.sha256(read_va(data,lo,size)).hexdigest()) for at,lo,size in spans]
        require(read_va(data,0xbf7878,40)==declaration and struct.unpack('<f',read_va(data,0xbf7378,4))[0]==412,'Pinned normal36 declaration and ambient divisor412')
        constants=[dict(rva=hex(at-0x400000),bytes=n,hex=read_va(data,at,n).hex()) for at,n in [(0xbf7878,40),(0xbf7378,4)]]
        if refs:require(ranges==refs[0]['ranges'] and constants==refs[0]['constants'],'Both455 ranges and constants equal')
        contexts=[dict(rva=hex(int(x['fn']['addr'],16)-0x400000),bytes=int(x['fn']['size'],16),sha256=hashlib.sha256(read_va(data,int(x['fn']['addr'],16),int(x['fn']['size'],16))).hexdigest()) for x in transform['bounds']['result']]
        if refs:require(contexts==refs[0]['transform_context_bytes'],'Selected transform context bytes equal both455')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges,constants=constants,transform_context_bytes=contexts,transform_full_assembly_claimed=False))
    shader=next(x for x in raws[0]['assembly'] if x['addr']=='0x8da0c0');require(shader['disasm_query_addr']=='0x8d9f50' and any(int(x['addr'],16)==0x8d9f50 for x in shader['lines']),'Lower shader loader chunk included')
    engine=load('client455-startup-engine-build');require(engine['objects']==67 and len(engine['derived_sources'])==21 and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current67engine/21derived')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    for field in ['vertex_header_overlay','camera_header_overlay','particle_header_overlay','level_header_overlay']:check(engine[field])
    sources=[record(WS/'scripts/native'/name) for name in ['client455_entity_lighting.h','client455_entity_lighting.inc','client455_entity_normals.h','client455_lit_grass.inc']]
    require(engine['lighting_consumers']=={Path(x['file']).name:x['sha256'] for x in sources},'Current connected implementations');check(engine['lighting_port_script'])
    oldreport=json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before130.json').read_text());old=WS/'artifacts/client455-progress/engine-before130.lib'
    require(sha(old)==oldreport['library_sha256'] and engine['camera_header_overlay']['sha256']!=oldreport['camera_header_overlay']['sha256'],'Exact129 backup and changed shared vertex declarations')
    before,after=archive_objects(old,True),archive_objects(WS/engine['library'],True);require(set(before)==set(after) and len(before)==67,'Same67engine members')
    changed=[];same=[];stamp=[]
    for name in before:
        a,b=before[name]['payload'],after[name]['payload'];(same if a==b else stamp if len(a)==len(b) and a[:4]+a[8:]==b[:4]+b[8:] else changed).append(name)
    build=load('client455-normal-build');require(not build['build_exit'] and build['objects']==182 and build['canonical_kernel_objects']==20,'Full shared-header182/20 rebuild')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current real normal link')
    mapping=(WS/link['map']['file']).read_text(errors='replace');required=['RF455_SetLitGrass','RF455_SetLightingCaps','RF455_HasBumpEnvironment','DrawEntityVS@CEntity','DrawEntity@CEntity']
    require(all(x in mapping for x in required),'Ordinary PE retains real consumers')
    gaps=['Selected finite PC24 geometry and lighting are covered;full GetNormal/decompressor/CRT/FP/RC/NaN/Inf/status flags remain open',
          'Source material records are332/46bytes with4 slots;target runtime records526/54bytes read46 serialized bytes per layer. Extra runtime fields and broader layer capacity remain open',
          'LitGrass reads19.xyz and21/22 only;original3-register stack overreads leave other lanes unspecified. Source uses deterministic unused lanes;complete state-consumer analysis remains open',
          'Legacy Grass loader/caps failure paths and full shader lifecycle/device reset/OOM remain open',
          'Target lit transform uses affine inverse8BFBC0 with0.001 guards,transform8C0980 and normalization51D5D0→41DB70→41DB90. Source currently uses D3DX inverse/legacy transform/x87 sqrt on selected affine input;exact guard/determinant/normalizer parity remains open',
          'Actual CEntity methods are connected;game producers of flag40 and broader shader selection,full map visibility/entity ownership/world/camera/alpha/material acceptance,INS/Planet/lensflare/localfog and remaining client acceptance remain open']
    out=dict(status='CONFIRMED_SELECTED',scope='Ordinary entity sky modulation,normal36 geometry,lit fixed/Grass paths and capability-gated bump material pre/after consumers',script_sha256=sha(Path(__file__)),
             raw=[record(x) for x in files],sessions=[record(x) for x in sessions],transform_context=record(transform_file),full_assembly=17,instructions=instructions,verified_ranges=len(spans),CFG_complete=True,references=refs,
             sources=sources,port_script=engine['lighting_port_script'],vertex_header=engine['vertex_header_overlay'],engine=record(WS/engine['library']),old_engine=record(old),
             changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,shared_headers_changed=True,client_objects=182,kernel_objects=20,ordinary_symbols_retained=required,
             gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-lighting-consumers-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],functions=17,instructions=instructions,ranges=len(spans),changed=len(changed),same=len(same),timestamp_only=len(stamp))))


if __name__=='__main__':main()
