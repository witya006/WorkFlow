"""Run actual CEntity/material lighting paths with stock geometry and shaders."""
import argparse,json,math,struct
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,require,sha
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario
from probe_client455_sky_fade import bits,number


def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]


def normal_oracle(run,native):
    row=next(x for x in native['inputs'] if x['file'].lower().endswith('/bd_grass01/bd_grass01.r3e'));check(row)
    data=(WS/row['file']).read_bytes();require(struct.unpack_from('<II',data)==(113,0),'Actual113 entity input')
    require((run/'entity-resolved.r3e').read_bytes()==data,'Resource owner resolves the exact pinned model')
    meta=next(json.loads(x) for x in (run/'lighting-consumers.jsonl').read_text().splitlines() if json.loads(x)['kind']=='vertices')
    require(meta['cw']&0xf00==0,'Selected PC24 nearest/even geometry domain')
    directory=struct.unpack_from('<20I',data,8);chunks=[];offset=88
    for size in directory[1::2]:chunks.append(data[offset:offset+size]);offset+=size
    require(offset==len(data),'Complete real entity streams')
    faces=list(struct.iter_unpack('<HI',chunks[4]));face_ids=[x[0] for x in struct.iter_unpack('<H',chunks[5])];vertex_ids=[x[0] for x in struct.iter_unpack('<H',chunks[6])]
    groups=list(struct.iter_unpack('<HIhH6h',chunks[7]));ids=[];group_faces=[]
    for count,start,*_ in groups:
        selected=[faces[face_ids[start+i]] for i in range(count)];group_faces.append(selected)
        for corners,begin in selected:ids.extend(vertex_ids[begin:begin+corners])
    raw=(run/'entity-vertices.bin').read_bytes();require(len(raw)==len(ids)*36,'All expanded GPU vertices captured')
    vertices=list(struct.iter_unpack('<6fI2f',raw));positions={}
    for index,v in zip(ids,vertices):
        if index in positions:require(positions[index]==v[:3],'Repeated source positions unchanged')
        positions[index]=v[:3]
    #Geometry/topology oracle uses captured positions,independent cross products
    #and stock face indices. It does not prove the inherited decompressor/CRT.
    accumulated={i:[0.,0.,0.] for i in positions};cursor=0;maximum_error=0.;bit_mismatches=0
    def normalize(v):
        square=f32(f32(f32(v[0]*v[0])+f32(v[1]*v[1]))+f32(v[2]*v[2]));length=f32(math.sqrt(square))
        return [f32(x/length) for x in v]
    for selected in group_faces:
        for corners,begin in selected:
            a,b,c=[positions[vertex_ids[begin+i]] for i in range(3)]
            u=[f32(y-x) for x,y in zip(a,b)];v=[f32(y-x) for x,y in zip(a,c)]
            face=normalize([f32(f32(u[1]*v[2])-f32(u[2]*v[1])),f32(f32(u[2]*v[0])-f32(u[0]*v[2])),f32(f32(u[0]*v[1])-f32(u[1]*v[0]))])
            for index in vertex_ids[begin:begin+corners]:accumulated[index]=[f32(a+b) for a,b in zip(accumulated[index],face)]
        for corners,begin in selected:
            for index in vertex_ids[begin:begin+corners]:
                v=accumulated[index]
                if v==[0.,0.,0.]:v=[0.,1.,0.]
                accumulated[index]=normalize(v)
                actual=vertices[cursor][3:6];expected=accumulated[index];error=max(abs(a-b) for a,b in zip(actual,expected));maximum_error=max(error,maximum_error)
                require(all(math.isfinite(x) for x in actual) and error==0,'Actual expanded normal matches selected reference arithmetic '+str((cursor,index,actual,expected,error)))
                bit_mismatches+=sum(bits(a)!=bits(b) for a,b in zip(actual,expected))
                cursor+=1
    require(cursor==5328,'Selected actual grass geometry coverage')
    return dict(vertices=cursor,groups=len(groups),stride=36,maximum_normal_error=maximum_error,normal_values_exact=True,normal_bit_mismatches=bit_mismatches,precision_bits=24,
                positions_from_native_capture=True,full_decompressor_FP_equivalence=False)


def verify(run,native):
    rows=[json.loads(x) for x in (run/'lighting-consumers.jsonl').read_text().splitlines()]
    materials=[x for x in rows if x['kind']=='material'];require(len(materials)==8,'Eight actual pre/after material cases')
    for row in materials:
        active=bool(row['cap'] and row['bump'])
        require(row['pre_op']==(22 if active else 2) and row['pre_alpha']==(0 if active else 1)
                and row['post_op']==4 and row['post_arg2']==0
                and row['post_factor']==(row['tint'] if active else 0x12345678),'Capability-gated bump and exact cleanup/tint bind')
    bump=[x for x in rows if x['kind']=='bump'];require(len(bump)==3,'Three selected bump animation times')
    for row in bump:
        angle=f32(float(number(row['time']))*2);c=f32(math.cos(angle));s=f32(math.sin(angle));scale=f32(.01)
        require(row['values']==list(map(bits,[f32(c*scale),f32(s*-scale),f32(s*scale),f32(c*scale)])),'Bump factor uses twice process time')
    frames=[x for x in rows if x['kind']=='frame'];require(len(frames)==5,'Five actual entity draw paths')
    for row in frames:
        require(row['draws']>0 and row['pixels']>100 and row['stride']==36,'Real visible model with455 vertex stride')
        require(row['color_op']==(4 if row['flags']&0x40 else 5),'Lit paths use MODULATE,other paths MODULATE2X')
        if row['id']<3:require(row['post']==[1,0,0 if row['flags']&0x40 else 1,1,0],'Reference post-state leaves lighting enabled,clears colorvertex and preserves diffuse source')
        base=0xff4080c0;tint=row['sky_tint'];modulated=base if row['id']==0 else (base&0xff000000)|sum(((((base>>s)&255)*((tint>>s)&255))>>8)<<s for s in [0,8,16])
        require(row['expected_tint']==modulated,'Independent integer sky modulation')
        if row['id']<2:require(row['actual_factor']==modulated and row['shader_bytes']==0,'Ordinary map-color path binds actual modulated texture factor')
        if row['id']==2:
            rgb=[(modulated>>s)&255 for s in [16,8,0]];expected=[bits(min(1.,f32(f32(c/255)+k))) for c,k in zip(rgb,[.25,f32(.2),f32(.2)])]+[bits(f32(192/255))]
            expected+=[bits(min(1.,f32(f32(c/412)+f32(.1)))) for c in rgb]+[bits(1)]
            require(row['material'][:8]==expected and row['actual_factor']==0x12345678,'Lit fixed path takes priority and builds actual D3D material')
        if row['id']>=3:
            name='grass1.vso' if row['id']==3 else 'LitGrass1.vso';actual=run/f'draw-shader-{row["id"]}.bin';original=run/'System/Shader'/name
            require(actual.read_bytes()==original.read_bytes() and len(actual.read_bytes())==row['shader_bytes'],'Byte-identical pinned shader actually bound at indexed submission')
    require(frames[4]['constants'][8:16]==frames[2]['material'][:8],'Actual lit shader diffuse/ambient constants match restored fixed light')
    geometry=normal_oracle(run,native)
    return dict(material_cases=8,bump_times=3,actual_entity_paths=5,GPU_frames=5,geometry=geometry,
                actual_Grass1_shader=True,actual_LitGrass1_shader=True,full_lighting=False,all_CRT_FP_inputs=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing',action='store_true');args=parser.parse_args();file=WS/'inventory/client455-lighting-consumers-native.json'
    r=json.loads(file.read_text()) if args.verify_existing else scenario('client455_lighting_consumers_probe.cpp','lighting-consumers','client455-lighting-consumers-native','client455-sky-lighting-inputs',
               ['System/Shader/grass1.vso','System/Shader/LitGrass1.vso'])
    run=(WS/r['exe']['file']).parent
    require(r['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current normal libraries')
    r.update(status='PASS_SELECTED',scope='Actual CEntity normal36/map tint/lit fixed/Grass1/LitGrass1 and material bump cleanup in full-object own-client lab;full lighting remains open',
             included_source=record(WS/'scripts/native/client455_sky_material_probe.cpp'),world_source=record(WS/'scripts/native/client455_world_probe.cpp'),
             driver_script=record(Path(__file__)),trace=record(run/'lighting-consumers.jsonl'),vertices=record(run/'entity-vertices.bin'),
             resolved_input=record(run/'entity-resolved.r3e'),normal_diagnostic=record(run/'normal-diagnostic.jsonl'),
             captured_shaders=[record(run/f'draw-shader-{i}.bin') for i in [3,4]],verdict=verify(run,r))
    file.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
