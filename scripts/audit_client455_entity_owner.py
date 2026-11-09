"""Pin EBP map lighting producer and its ordinary source integration."""
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
from inventory_client455_entity_flags import entities
from prepare_client455_normal import section


def main():
    file=WS/'artifacts/client455-progress/entity-owner132-reference.json';session_file=WS/'artifacts/client455-progress/entity-owner132-session.json';raw=json.loads(file.read_text());spans,count=contracts(raw);require(count==1665 and len(raw['selected'])==5,'Complete5functions1665instructions')
    session=json.loads(session_file.read_text());require(session['saved']['ok'] and session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned session saved/closed')
    reused=record(WS/raw['reused_load_evidence']['file']);pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned455 client')
        rows=[dict(owner_rva=hex(int(owner,16)-0x400000),rva=hex(at-0x400000),bytes=n,sha256=hashlib.sha256(read_va(data,at,n)).hexdigest()) for owner,at,n in spans]
        require(read_va(data,0x8f9690,5)==bytes.fromhex('f644034840') and read_va(data,0x8f969d,5)==bytes.fromhex('834c0e6840'),'Actual packed record test and entity flag OR instructions')
        if refs:require(rows==refs[0]['ranges'],'Both pinned clients equal')
        refs.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=rows))
    inputs=load('client455-entity-flags-inputs');require(inputs['script']['sha256']==sha(WS/'scripts/inventory_client455_entity_flags.py'),'Current independent input parser')
    for row in inputs['maps']:
        require(sha(Path(row['file']))==row['sha256'],'Original EBP unchanged');parsed=entities(Path(row['file']).read_bytes());require(len(parsed)==row['entries'] and [x for x in parsed if not x['particle'] and x['flag']&0x40]==row['lit_entries'],'Reproduced actual flags')
    engine=load('client455-startup-engine-build');old=json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before132.json').read_text());before=WS/'artifacts/client455-progress/engine-before132.lib';require(sha(before)==old['library_sha256'] and engine['script_sha256']==sha(WS/'scripts/build_client455_engine_startup.py'),'Current engine/exact131 backup')
    for row in engine['base_sources']+engine['derived_sources']:check(row)
    for key in ['camera_header_overlay','vertex_header_overlay','particle_header_overlay','core_header_overlay','level_header_overlay']:check(engine[key]);require(engine[key]['sha256']==old[key]['sha256'],'Shared headers stable')
    a,b=archive_objects(before,True),archive_objects(WS/engine['library'],True);require(set(a)==set(b) and len(b)==67,'Same67engine objects');changed=[];same=[];stamp=[]
    for name in a:
        x,y=a[name]['payload'],b[name]['payload'];(same if x==y else stamp if len(x)==len(y) and x[:4]+x[8:]==y[:4]+y[8:] else changed).append(name)
    require(len(changed)==1 and Path(changed[0]).name.lower()=='bsp.obj','Only BSP payload changed '+str(changed))
    owner=engine['map_entity_owner'];check(owner);source=next(x for x in engine['derived_sources'] if x['file'].endswith('/bsp.cpp'));data=(WS/source['file']).read_bytes();start,end=section(data,b'void CBsp::LoadEntities(',b'void CBsp::LoadEntities(');body=data[start:end];snippet=(WS/owner['file']).read_bytes()
    require(body.count(snippet)==1 and body.index(b'mEntity[i].LoadEntity(name,flag)')<body.index(snippet)<body.index(b'mEntity[i].RestoreTexMem();'),'Only successful nonparticle load transfers bit before texture restore')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current full client link');bodies=linked((WS/link['executable']['file']).read_bytes(),(WS/link['map']['file']).read_text(),(WS/'work/client-reference/current/RF_Online.bin').read_bytes())
    previous=WS/'artifacts/client455-progress/client455-light-direction-checkpoint-before132.json';old_gate=json.loads(previous.read_text());gaps=[x for x in old_gate['gaps'] if not x.startswith('Actual CEntity methods are connected')]
    gaps+=['Map EBP bit40 producer is connected and selected actual NeutralB owners/routes verified;other game/effect/entity flag writers and full visibility/fade/alpha/camera acceptance remain open',
           'Physical93 EBP files include alternate/duplicate maps;1584lit rows/82shader rows are data inventory counts,not unique models or completed gameplay scenarios']
    out=dict(status='CONFIRMED_SELECTED',script=record(Path(__file__)),scope='Ordinary EBP record bit40 to successful CEntity owner and real fixed/LitGrass map routes',raw=record(file),session=record(session_file),reused1025_instruction_body=reused,full_assembly=5,instructions=count,verified_ranges=len(spans),CFG_complete=True,references=refs,
             inputs=record(WS/'inventory/client455-entity-flags-inputs.json'),source=owner,generated_source=source,engine=record(WS/engine['library']),old_engine=record(before),changed_members=changed,unchanged_members=same,timestamp_only_members=stamp,shared_headers_changed=False,
             normal_executable=link['executable'],normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),retained_light_math=bodies,previous131_gate=record(previous),gaps=gaps,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-entity-owner-reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(functions=5,instructions=count,ranges=len(spans),changed=len(changed),same=len(same),stamp=len(stamp),maps=inputs['totals'])))


if __name__=='__main__':main()
