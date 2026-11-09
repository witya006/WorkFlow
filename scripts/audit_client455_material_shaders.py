"""Pin the actual BSP material route and particle-owned shader light chain."""
import copy,hashlib,json
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_item_payloads import record
from audit_client455_lighting_consumers import contracts
from audit_client455_texture_lifetime import archive_objects
from checkpoint_client455_rvp_effects import require,sha,check,load
from client455_normal_link_evidence import validate_normal_link

def main():
    file=WS/'artifacts/client455-progress/material-shader135-reference.json';sessionfile=WS/'artifacts/client455-progress/material-shader135-session.json';raw=json.loads(file.read_text());normalized=copy.deepcopy(raw)
    for row in normalized['assembly']:row['total_instructions']=row['pages'][0]['total_instructions']
    normalized['cfg']=[{**row['result']['result'][0],'addr':row['addr']} for row in raw['cfg']];spans,count=contracts(normalized);require(len(raw['selected'])==12 and count==2063,'12 full particle-light/splat functions,2063 instructions')
    session=json.loads(sessionfile.read_text());require(session['saved']['ok'] and session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned455 x86 client')
        rows=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(at-0x400000),bytes=n,sha256=hashlib.sha256(read_va(data,at,n)).hexdigest()) for owner,at,n in spans]
        if refs:require(rows==refs[0]['ranges'],'Both pinned versions agree on complete selected functions')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=rows))
    inherited=[]
    for name,owner in [('client455-material-layout-reference','0x8c9230'),('client455-special-shaders-reference','0x8c94a0')]:
        ref=load(name);check(ref['raw']);check(ref['session']);inherited.append(dict(reference=record(WS/f'inventory/{name}.json'),owner=owner,raw=ref['raw'],session=ref['session']))
    before=WS/'artifacts/client455-progress/before135';manifest=json.loads((before/'manifest.json').read_text());require(len(manifest)==49,'Exact134 runtime snapshot')
    for row in manifest:check(row)
    engine=load('client455-startup-engine-build');old=json.loads((before/'inventory/client455-startup-engine-build.json').read_text());require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current engine generator')
    for row in engine['base_sources']+engine['derived_sources']+[engine['material_shader_port_script']]:check(row)
    for name,value in engine['material_shader_draw'].items():require(value==sha(WS/'scripts/native'/name),'Exact material/light source inputs')
    for key in ['camera_header_overlay','particle_header_overlay','vertex_header_overlay','material_header_overlay']:
        check(engine[key]);require(engine[key]['sha256']==old[key]['sha256'],'Shared declarations unchanged135')
    a,b=archive_objects(before/old['library'],True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(b)==67,'Same67 engine units');changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload'];(same if x==y else stamp if len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:] else changed).append(name)
    require({Path(x).name.lower() for x in changed}=={'r3render.obj','r3particle.obj','renderparticle.obj'},'Exactly the real material/particle loader/render owners changed')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and any(x['sha256']==engine['library_sha256'] for x in link['libraries']),'Actual new engine in own full PE')
    mapping=(WS/link['map']['file']).read_text();require(all(x in mapping for x in ['RF455_GetShaderLight','RF455_UpdateParticleShaderLight','RF455_GetMaterialShaderSelection','DrawOneMatGroup']),'Ordinary owner symbols retained')
    out=dict(status='CONFIRMED_SELECTED',scope='Ordinary BSP special material dispatch/PS18/particle light producer and selected fixed splat passes',script=record(Path(__file__)),contract_verifier=record(WS/'scripts/audit_client455_lighting_consumers.py'),raw=record(file),session=record(sessionfile),references=refs,full_assembly=12,instructions=count,verified_ranges=len(spans),CFG_complete=True,inherited_dispatch_proofs=inherited,
             engine=record(WS/engine['library']),normal_executable=link['executable'],normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),snapshot=record(before/'manifest.json'),changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,shared_headers_changed=False,
             gaps=['PS6 reads four floats starting at color+20 in a32-byte light allocation;its fourth lane lies outside the object and is not certified. No fabricated alpha value is introduced',
                   'The supplied Fraction/Plazma programs do not consume PS18. Actual GPU register delivery is proven;all consumers of the new specular fields/full appearance are not certified',
                   'VS12/13 and PS16 were explicit lab initial states and remain untouched by the restored consumer. Their complete ordinary producers,other shader objects/unused lanes are open',
                   'Init.r3s fallback,positive FX/caps/errors/OOM/overflow/bad indices/truncated input and device Reset/lost-device remain open. Selected splat3-layer cases do not cover all combinations',
                   'Global particle light owner is restored;the separate per-BSP light list and its producers/positive object-light routing remain open. Full particle advanced providers other than [light] remain rejected',
                   'Full world/stages/Login/auth/protocol/Character/gameplay and every remaining client-acceptance requirement are still open'],
             input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-material-shaders-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=12,instructions=count,ranges=len(spans),changed=changed,executable=link['executable'])))
if __name__=='__main__':main()
