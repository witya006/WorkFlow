"""Verify full selected shader-owner bodies against both pinned455 binaries."""
import json,hashlib
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from checkpoint_client455_rvp_effects import require,sha,check,load
from client455_normal_link_evidence import validate_normal_link


def contracts(raw):
    selected=set(raw['selected']);require(len(selected)==15,'15 selected complete shader-owner functions')
    asm={x['addr']:x for x in raw['assembly']};cfg={x['addr']:x['result']['result'][0] for x in raw['cfg']};require(selected==set(asm)==set(cfg),'Selected full assembly/CFG sets')
    spans=[];instructions=0
    for at in sorted(selected):
        a,g=asm[at],cfg[at];lines=a['lines'];addresses={int(x['addr'],16) for x in lines};pages=a['pages'];total=pages[0]['total_instructions']
        require(len(lines)==len(addresses)==total==sum(x['instruction_count'] for x in pages) and all(len(x['asm']['lines'])==x['instruction_count']<=100 for x in pages) and pages[-1]['cursor']['done'],'Complete paged assembly '+at)
        instructions+=total
        if at=='0x8c94a0':
            tail=a['tail_query']['result'][0];require(tail['cursor']['done'] and not tail['truncated'] and tail['count']==len(tail['matches'])==19,'Noncontiguous lower splat-cleanup chunk')
            extra={int(x['addr'],16) for x in tail['matches']};require(not addresses&extra,'Distinct lower chunk');addresses|=extra;instructions+=19
        require(g['cursor']['done'] and g['count']==g['total_blocks']==len(g['blocks']) and all(int(x['start'],16) in addresses for x in g['blocks'] if x['size']>0),'All positive CFG starts '+at)
        p=next(x for x in raw['functions'] if x['addr']==at)['pages'];require(sum(x['line_count'] for x in p)==p[0]['total_lines'] and p[-1]['cursor']['done'],'Complete pseudocode '+at)
        merged=[]
        for block in sorted((x for x in g['blocks'] if x['size']>0),key=lambda x:int(x['start'],16)):
            lo,hi=int(block['start'],16),int(block['end'],16)
            if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
            else:merged.append([lo,hi])
        spans.extend((at,lo,hi-lo) for lo,hi in merged)
    require(instructions==1592,'1592 selected instructions including19 lower-chunk instructions')
    return spans,instructions


def main():
    file=WS/'artifacts/client455-progress/special-shader134-reference.json';sessionfile=WS/'artifacts/client455-progress/special-shader134-session.json';raw=json.loads(file.read_text());spans,instructions=contracts(raw)
    session=json.loads(sessionfile.read_text());require(session['saved']['ok'] and session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA session saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned x86 client455')
        rows=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(at-0x400000),bytes=n,sha256=hashlib.sha256(read_va(data,at,n)).hexdigest()) for owner,at,n in spans]
        if refs:require(rows==refs[0]['ranges'],'Every selected complete body range agrees between both455')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=rows))
    before=WS/'artifacts/client455-progress/before134';manifest=json.loads((before/'manifest.json').read_text());require(len(manifest)==40,'Exact133 runtime/evidence snapshot')
    for row in manifest:check(row)
    old= json.loads((before/'inventory/client455-startup-engine-build.json').read_text());engine=load('client455-startup-engine-build')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current engine generator')
    for name,value in engine['special_shader_owner'].items():require(value==sha(WS/'scripts/native'/name),'Current registry source')
    for key in ['camera_header_overlay','particle_header_overlay','vertex_header_overlay','material_header_overlay']:
        check(engine[key]);require(engine[key]['sha256']==old[key]['sha256'],'Shared consumer headers unchanged134')
    a,b=archive_objects(before/old['library'],True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(b)==67,'Same67 engine objects')
    changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload'];(same if x==y else stamp if len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:] else changed).append(name)
    require(len(changed)==1 and Path(changed[0]).name.lower()=='r3d3d8.obj','Only actual device/shader-owner object payload changed')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and any(x['sha256']==engine['library_sha256'] for x in link['libraries']),'Actual new owner linked into full own PE')
    mapping=(WS/link['map']['file']).read_text();require('RF455_LoadSpecialShaderBinary' in mapping and 'RF455_ReleaseSpecialShaders' in mapping,'Actual owner retained in ordinary executable')
    inputs=load('client455-special-shaders-inputs')
    for row in inputs['inputs']:check(row)
    for row in inputs['programs']:check(row['encrypted']);check(row['decoded'])
    out=dict(status='CONFIRMED_SELECTED',scope='Binary special-material shader registry/real sources/ordinary device restore-invalidate;full draw pending',script=record(Path(__file__)),raw=record(file),session=record(sessionfile),references=refs,full_assembly=15,instructions=instructions,verified_ranges=len(spans),CFG_complete=True,noncontiguous_lower_chunk_instructions=19,
             inputs=record(WS/'inventory/client455-special-shaders-inputs.json'),engine=record(WS/engine['library']),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),normal_executable=link['executable'],snapshot=record(before/'manifest.json'),changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,shared_headers_changed=False,
             gaps=['Special-material DrawOneMatGroup dispatcher8C94A0 and constants consumer8C9230 are identified but not yet migrated. PS18.zw fields are loaded by133 but not yet submitted through the ordinary special draw pipeline',
                   'Init.r3s fallback904B60 is only partially decompiled and is not implemented;missing binary list emits explicit diagnostic. No claim of full special-loader equivalence',
                   'Actual init.r3o has0FX/0serialized objects. Positive FX/failure/caps/OOM/overflow/invalid indices/truncated files and all numeric conversions remain unverified;known original failure resource quirks are preserved',
                   'The three restore cycles invoke actual resource callbacks on the same live device;actual D3D9 Reset/lost-device/mode-switch behavior is not certified',
                   'All7GPU material layers,light-object owner/state,constant-register unused lanes and full material/world/client-acceptance gaps remain open'],
             input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-special-shaders-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=15,instructions=instructions,ranges=len(spans),changed_members=changed,own_executable=link['executable'])))


if __name__=='__main__':main()
