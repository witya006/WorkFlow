"""Pin seven runtime layers and their separate serialized representation."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_lighting_consumers import contracts
from audit_client455_light_direction import linked
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    file=WS/'artifacts/client455-progress/material-layout133-reference.json';session_file=WS/'artifacts/client455-progress/material-layout133-session.json';raw=json.loads(file.read_text());spans,count=contracts(raw)
    require(len(raw['selected'])==5 and count==1438,'5full functions/1438instructions');session=json.loads(session_file.read_text());require(session['saved']['ok'] and session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA saved/closed')
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned455 client')
        rows=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(at-0x400000),bytes=n,sha256=hashlib.sha256(read_va(data,at,n)).hexdigest()) for owner,at,n in spans]
        limit=read_va(data,0x90a627,32);require(struct.pack('<I',2048) in limit,'Additional main material count guard context2048')
        if refs:require(rows==refs[0]['ranges'] and limit.hex()==refs[0]['material_limit_context']['hex'],'Both pinned functions and limit context equal')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=rows,material_limit_context=dict(rva='0x50a627',bytes=32,hex=limit.hex(),full_function_assembly_claimed=False)))
    engine=load('client455-startup-engine-build');old=json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before133.json').read_text());before=WS/'artifacts/client455-progress/engine-before133.lib'
    require(engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py') and sha(before)==old['library_sha256'],'Current engine/exact132 backup')
    for row in engine['base_sources']+engine['derived_sources']+[engine['material_header_overlay'],engine['material_port_script']]:check(row)
    header=engine['material_header_overlay'];require(header['original_sha256']==sha(WS/'artifacts/client455-progress/legacy-material-header-before133.h'),'Legacy material header not edited')
    for key in ['camera_header_overlay','particle_header_overlay']:check(engine[key]);require(engine[key]['sha256']!=old[key]['sha256'],'Shared consumers receive new material declaration')
    require(engine['vertex_header_overlay']['sha256']==old['vertex_header_overlay']['sha256'],'36byte vertex layout retained')
    build=load('client455-normal-build');prep=load('client455-normal-preparation');require(not build['build_exit'] and build['objects']==182 and build['canonical_kernel_objects']==20 and prep['camera_header_overlay']['sha256']==engine['camera_header_overlay']['sha256'],'Full182/20 rebuild with actual changed shared header')
    a,b=archive_objects(before,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(b)==67,'Same67engine units');changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload'];(same if x==y else stamp if len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:] else changed).append(name)
    require(any(Path(x).name.lower()=='r3material.obj' for x in changed),'Actual loader payload changed')
    source=next(x for x in engine['derived_sources'] if x['file'].endswith('/r3material.cpp'));text=(WS/source['file']).read_bytes();require(b'fread(&mat[i].m_Layer[j],46,1,fp);' in text and b'specular_flikering_scale' in text and b'specular_flikering_speed' in text and b'shader_object' in text and b'light_object' in text,'Actual serialized prefix and confirmed text writers')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current own full PE');bodies=linked((WS/link['executable']['file']).read_bytes(),(WS/link['map']['file']).read_text(),(WS/'work/client-reference/current/RF_Online.bin').read_bytes())
    previous=WS/'artifacts/client455-progress/client455-entity-owner-checkpoint-before133.json';old_gate=json.loads(previous.read_text());gaps=[x for x in old_gate['gaps'] if not x.startswith('Source material records are332')]
    gaps+=['Runtime seven54-byte layers/material526 and46-byte binary prefix restored. Special material shader8C9230 reads specular fields into PS18.zw;its full special shader owner/draw pipeline is not yet ported',
           'Main text material guard2048 is pinned by partial context;full main text parser assembly beyond prior evidence,all CRT numeric conversions,reload/invalid indices/truncation/OOM and complete material/render behavior remain open']
    out=dict(status='CONFIRMED_SELECTED',script=record(Path(__file__)),scope='Runtime material526/seven54-byte layers with46-byte serialized prefix and actual text metadata writers',raw=record(file),session=record(session_file),full_assembly=5,instructions=count,verified_ranges=len(spans),CFG_complete=True,references=refs,
             material_header=header,port_script=engine['material_port_script'],generated_source=source,engine=record(WS/engine['library']),old_engine=record(before),changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,shared_headers_changed=True,client_objects=182,kernel_objects=20,
             normal_executable=link['executable'],normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),retained_light_math=bodies,previous132_gate=record(previous),gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-material-layout-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=5,instructions=count,ranges=len(spans),changed=len(changed),same=len(same),stamp=len(stamp),runtime_material=526,runtime_layer=54,layers=7)))


if __name__=='__main__':main()
