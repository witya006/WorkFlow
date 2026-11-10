"""Pin equipment animation/fade and its actual resource inputs."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record,sha
from audit_client455_language import decode
from audit_client455_item_payloads import item_tables
from audit_client455_resource_catalog import catalog,cstring
from audit_client455_legacy_models import expected as legacy_model
from mesh08 import decode as mesh08
from client455_reference_regions import verify_regions
from client455_resource_inputs import ResourceInputs
from ani455 import decode as decode_ani

def main():
    raw=WS/'artifacts/client455-progress/equipment-providers146-reference/session.json';proof=verify_regions(raw)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=ResourceInputs(client)
    base=json.loads((WS/'inventory/client455-equipment-reference.json').read_text())
    for entry in base['inputs']:inputs.add(Path(entry['original']))
    items,_,_=item_tables(decode((client/'DataTable/Item.edf').read_bytes()));groups=catalog(decode((client/'DataTable/Resource.edf').read_bytes()))
    meshes={};animations={}
    for group,tables in enumerate(groups):
        for i in range(tables[1]['count']):
            row=tables[1]['raw'][328*i:328*(i+1)];meshes.setdefault((5 if group==0 else group,struct.unpack_from('<I',row)[0]),row)
    table=groups[5][2]
    for i in range(table['count']):
        row=table['raw'][244*i:244*(i+1)];animations[struct.unpack_from('<I',row)[0]]=row
    cases=[];loaded_models={};needed_ani={};textures=set()
    requests=[(8,0,race,mode) for race in range(5) for mode in range(6)]
    requests += [(27,0,4,mode) for mode in range(6)]+[(46,0,race,mode) for race in range(4) for mode in range(6)]
    requests += [(6,1820,0,mode) for mode in range(4)]+[(1,0,0,1)]
    for kind,index,race,mode in requests:
        item=items[kind];row=item['data'][index*item['stride']:(index+1)*item['stride']];mesh=struct.unpack_from('<I',row,72)[0]
        adjusted=(mesh&0xff0fffff)|(race<<20) if ((mesh>>16)&15) in [0,8] and ((mesh>>20)&255)!=10 and ((mesh>>8)&255)!=7 else mesh
        selected=((adjusted<<4)|mode)&0xffffffff;effective=mode
        if selected not in animations and mode:effective=0;selected=(adjusted<<4)&0xffffffff
        found=selected in animations
        ani_maximum=0;ani_tracks=0
        if found:
            ani=animations[selected];relative=(cstring(ani,8,128)+cstring(ani,136,64)).replace('\\','/').removeprefix('./')
            data=inputs.read(client/relative);assert data is not None,relative;needed_ani[selected]=relative
            parsed=decode_ani(data);ani_maximum=parsed.maximum;ani_tracks=len(parsed.tracks)
        resource=meshes[(5,adjusted)]
        relative=(cstring(resource,8,128)+cstring(resource,136,64)).replace('\\','/').removeprefix('./')
        if relative not in loaded_models:
            model=inputs.read(client/relative);assert model is not None,relative
            headers=[part.header for part in mesh08(model).parts] if model.startswith(b'MESH08') else [header for header,_ in legacy_model(model)[1]]
            loaded_models[relative]=len(headers)
            directory=cstring(resource,200,128).replace('\\','/').removeprefix('./')
            for header in headers:
                for offset in [398,498]:
                    #Exporter directories may contain Korean ANSI bytes. The
                    #runtime discards that byte prefix before resolving the
                    #resource-directory basename;do not recode the prefix.
                    name=header[offset:offset+100].split(b'\0')[0].replace(b'\\',b'/').rsplit(b'/',1)[-1].decode('ascii')
                    if name:textures.add((directory,name))
        cases.append(dict(type=kind,index=index,race=race,mode=mode,effective=effective,animation_id=selected,found=found,mesh_parts=loaded_models[relative],ani_maximum=ani_maximum,ani_tracks=ani_tracks))
    fallbacks=[]
    for directory,name in textures:
        path=client/directory/name
        if inputs.read(path) is None:
            alternate=path.with_suffix('.rft');assert inputs.read(alternate) is not None,alternate
            inputs.missing.discard(path.resolve().relative_to(client.resolve()).as_posix());fallbacks.append(dict(requested=path.relative_to(client).as_posix(),resolved=alternate.relative_to(client).as_posix()))
    assert not inputs.missing,inputs.missing
    target=WS/'artifacts/client455-equipment-providers';target.mkdir(exist_ok=True);expected=target/'expected.bin'
    expected.write_bytes(b'EA46'+struct.pack('<I',len(cases))+b''.join(struct.pack('<10I',c['type'],c['index'],c['race'],c['mode'],c['effective'],c['animation_id'],c['found'],c['mesh_parts'],c['ani_maximum'],c['ani_tracks']) for c in cases))
    sources=[WS/'scripts/native'/name for name in ['client455_player_equipment.h','client455_normal_item_copy.h','client455_equipment_providers_probe.cpp']]
    report=dict(status='PARTIAL_COMPONENT_STATIC',scope='Equipment animation selection/fallback/state and fade;full production item effects/conditions/appearance still open',**proof,raw=record(raw),
        decoder_script=record(WS/'scripts/decode_client455_cfg.py'),regions_script=record(WS/'scripts/client455_reference_regions.py'),resource_script=record(WS/'scripts/client455_resource_inputs.py'),script=record(Path(__file__)),
        sources=[record(p) for p in sources],inputs=list(inputs.inputs.values()),cases=cases,selected_animations=needed_ani,selected_models=loaded_models,texture_fallbacks=fallbacks,missing=[],resolved_members=inputs.members,expected=record(expected),
        ordinary_runtime_changed=False,production_controller_connected=False,full_item_animation_effects=False,full_condition_effects=False,full_player_appearance_or_draw=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-providers-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=proof['full_functions'],instructions=proof['full_instructions'],blocks=proof['positive_cfg_blocks'],cases=len(cases),real_animations=len(needed_ani),models=len(loaded_models),inputs=len(inputs.inputs),missing=0)))
if __name__=='__main__':main()
