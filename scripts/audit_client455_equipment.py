"""Pin typed equipment creation and collect only its actual resource dependencies."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_language import decode
from audit_client455_item_payloads import item_tables
from audit_client455_resource_catalog import catalog,cstring,sha,record
from audit_client455_legacy_models import expected as legacy_model
from mesh08 import decode as mesh08
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def plan(kind,index,mesh):
    race=index>>28;group=6 if race==14 else 5;table_type=46 if kind==9 else kind
    user=(mesh>>20)&255;category=(mesh>>16)&15;part=(mesh>>8)&255
    if race not in [14,15] and category in [0,8] and user!=10 and part!=7:mesh=(mesh&0xff0fffff)|(race<<20)
    if table_type in [8,46]:group=5
    return [table_type,race,group,mesh,index&0xfffffff]

def main():
    raw_file=WS/'artifacts/client455-progress/equipment145-reference/session.json';raw=json.loads(raw_file.read_text());functions=[]
    for entry in raw['ranges']['result']:
        addr=int(entry['fn']['addr'],16);pages=raw['asm'][entry['query']];assert pages[-1]['cursor']['done']
        lines=[line for p in pages for line in p['asm']['lines']];starts={int(line['addr'],16) for line in lines}
        assert len(starts)==len(lines)==pages[0]['total_instructions'] and all(len(p['asm']['lines'])<=100 for p in pages)
        cfg=next(r for r in raw['cfg']['result'] if int(r['addr'],16)==addr);assert cfg['cursor']['done'] and cfg['count']==cfg['total_blocks']
        blocks=[b for b in cfg['blocks'] if b['size']>0];assert all(int(b['start'],16) in starts for b in blocks)
        assert all(any(int(b['start'],16)<=a<int(b['end'],16) for b in blocks) for a in starts)
        regions=[]
        for b in sorted(blocks,key=lambda b:int(b['start'],16)):
            first,last=int(b['start'],16),int(b['end'],16)
            if regions and regions[-1][1]==first:regions[-1][1]=last
            else:regions.append([first,last])
        functions.append(dict(rva=hex(addr-0x400000),instructions=len(lines),positive_cfg_blocks=len(blocks),regions=[dict(rva=hex(a-0x400000),bytes=b-a) for a,b in regions]))
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();assert sha(path)==pins[key]['sha256'] and pe(binary)['architecture']=='x86'
        assert read_va(binary,0xbcb160,20).startswith(b'.?AVCEquipObject@@\0')
        assert struct.unpack('<I',read_va(binary,0xaa8f60,4))[0]==0xb7a3ac and struct.unpack('<I',read_va(binary,0xb7a3b8,4))[0]==0xbcb158
        assert struct.unpack('<I',read_va(binary,0xaa8f64+140,4))[0]==0x46db70
        refs.append(dict(**record(path),architecture='x86',image_base='0x400000',functions=[dict(f,regions=[dict(r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in f['regions']]) for f in functions],
            equipment_rtti=[dict(rva=hex(a-0x400000),bytes=n,sha256=hashlib.sha256(read_va(binary,a,n)).hexdigest()) for a,n in [(0xbcb158,28),(0xb7a3ac,20),(0xaa8f60,184)]]))
    assert refs[0]['functions']==refs[1]['functions'] and refs[0]['equipment_rtti']==refs[1]['equipment_rtti'] and len(functions)==18
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);root=WS/'artifacts/client455-equipment';root.mkdir(exist_ok=True)
    item_file=client/'DataTable/Item.edf';resource_file=client/'DataTable/Resource.edf';rows,_,_=item_tables(decode(item_file.read_bytes()));groups=catalog(decode(resource_file.read_bytes()))
    inputs={};archives={};resolved=[];missing=set()
    def add(path):
        path=path.resolve();assert path.is_relative_to(client.resolve()) and path.is_file()
        inputs[path.relative_to(client).as_posix()]=dict(original=str(path),relative=path.relative_to(client).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
    def resolve(path):
        path=path.resolve()
        if not path.is_relative_to(client.resolve()):raise ValueError('Resource path outside client: '+str(path))
        if path.is_file():add(path);return path.read_bytes()
        directory=path.parent
        if directory not in archives:
            info=directory/'RFSINFO.DAT';names=info.read_text(encoding='ascii').split() if info.is_file() else []
            if not names:
                for i in range(1024):
                    candidate=directory/f'DATA{i}.RFS'
                    if not candidate.is_file():break
                    names.append(candidate.name)
            table={}
            for name in names:
                archive=(directory/name).resolve();assert archive.is_relative_to(client.resolve())
                if not archive.is_file():continue
                with archive.open('rb') as f:
                    count=struct.unpack('<I',f.read(4))[0];assert count<=(archive.stat().st_size-4)//64
                    for _ in range(count):
                        row=f.read(64);assert len(row)==64 and b'\0' in row[:56]
                        offset,size=struct.unpack_from('<II',row,56);assert offset+size<=archive.stat().st_size
                        table.setdefault(row[:56].split(b'\0')[0].lower(),(archive,offset,size))
            archives[directory]=(info,table)
        info,table=archives[directory];entry=table.get(path.name.encode('ascii').lower())
        if not entry:missing.add(path.relative_to(client).as_posix());return None
        archive,offset,size=entry;add(archive)
        if info.is_file():add(info)
        with archive.open('rb') as f:f.seek(offset);data=f.read(size)
        assert len(data)==size;resolved.append(dict(file=path.relative_to(client).as_posix(),archive=archive.relative_to(client).as_posix(),offset=offset,bytes=size));return data
    for p in [item_file,resource_file,client/'DataTable/ko-kr/NDItem.edf']:add(p)
    #Catalog loading needs its declared bones and box files. Reuse the frozen
    #real input manifest;extra mesh/texture inputs are selected below.
    catalog_ref=json.loads((WS/'inventory/client455-resource-catalog-reference.json').read_text())
    for item in catalog_ref['inputs']:add(Path(item['original']))
    lookup={}
    for group,tables in enumerate(groups):
        t=tables[1]
        for i in range(t['count']):
            r=t['raw'][328*i:328*(i+1)];lookup.setdefault((5 if group==0 else group,struct.unpack_from('<I',r)[0]),r)
    selected=[];textures=set();texture_fallbacks=[]
    for part,index in [(p,16*r) for r in range(5) for p in range(6)]+[(6,0),(7,0)]:
        table=rows[part];r=table['data'][index*table['stride']:(index+1)*table['stride']];mesh=struct.unpack_from('<I',r,72)[0];planned=plan(part,index,mesh)
        resource=lookup[(planned[2],planned[3])];relative=(cstring(resource,8,128)+cstring(resource,136,64)).replace('\\','/').removeprefix('./');data=resolve(client/relative);assert data is not None,relative
        if data.startswith(b'MESH08'):heads=[p.header for p in mesh08(data).parts];fmt='MESH08'
        else:heads=[r for r,_ in legacy_model(data)[1]];fmt='legacy'
        for h in heads:
            for at in [398,498]:
                name=h[at:at+100].split(b'\0')[0].decode('ascii')
                #The material loader drops the exporter path and uses the
                #Resource.edf texture directory. Never access its old D: path.
                directory=cstring(resource,200,128).replace('\\','/').removeprefix('./')
                if name:textures.add((directory,name.replace('\\','/').rsplit('/',1)[-1]))
        selected.append(dict(part=part,index=index,raw_mesh=mesh,plan=planned,resource=relative,format=fmt,parts=len(heads)))
    for directory,name in sorted(textures):
        path=client/directory/name
        if resolve(path) is None:
            alternate=path.with_suffix('.rft')
            if resolve(alternate) is not None:
                missing.discard(path.resolve().relative_to(client.resolve()).as_posix())
                texture_fallbacks.append(dict(requested=path.relative_to(client).as_posix(),resolved=alternate.relative_to(client).as_posix()))
    plans=[]
    for kind,index,mesh in [(0,0,0x50100),(6,0,0xa10300),(7,0,0x900700)]+[(kind,(race<<28)|123,mesh) for kind in [1,8,9] for race in [0,4,14,15] for mesh in [0x700200,0x780001,0xa10300,0x900700]]:
        plans.append([kind,index,mesh]+plan(kind,index,mesh))
    expected=b'EQ45'+struct.pack('<I',len(plans))+b''.join(struct.pack('<8I',*p) for p in plans)+struct.pack('<I',len(selected))
    for case in selected:expected+=struct.pack('<7I',case['part'],case['index'],case['raw_mesh'],*case['plan'][1:4],case['parts'])
    texture_names=sorted({name for _,name in textures});expected+=struct.pack('<I',len(texture_names))
    for name in texture_names:
        encoded=name.encode('ascii');expected+=struct.pack('<I',len(encoded))+encoded
    fixture=root/'expected.bin';fixture.write_bytes(expected)
    out=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Typed CEquipObject creation/resource binding and ordinary Avatar default slots;full player equipment/appearance/render still open',references=refs,raw=record(raw_file),full_functions=18,
        full_instructions=sum(f['instructions'] for f in functions),positive_cfg_blocks=sum(f['positive_cfg_blocks'] for f in functions),equipment_rtti=True,inputs=list(inputs.values()),selected=selected,plan_cases=len(plans),textures=sorted(textures),texture_names=texture_names,texture_fallbacks=texture_fallbacks,missing=sorted(missing),resolved_archive_members=resolved,expected=record(fixture),
        sources=[record(WS/'scripts/native'/name) for name in ['client455_equipment_object.h','client455_equipment_object.cpp','client455_registered_characters.inc']]+[record(WS/'scripts/client455_equipment_port.py')],script=record(Path(__file__)),snapshot=record(WS/'artifacts/client455-progress/before145/manifest.json'),
        gaps=['Full CPlayerProc creation/effect/weapon/rematch/fade/animation/draw consumers remain unported','Legacy GetDefaultItem/UnsetDefaultItem/copy overload and remaining gameplay item consumers remain open;ordinary registered receiver uses new typed getter','This is not complete private644byte CEquipObject ABI/constructor or full failure/concurrency equivalence','Full appearance/selection/bootstrap/world/gameplay/M9 open'],input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-reference.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(functions=18,instructions=out['full_instructions'],cfg=out['positive_cfg_blocks'],selected=len(selected),plans=len(plans),textures=len(textures),missing=sorted(missing),inputs=len(inputs),input_bytes=sum(r['bytes'] for r in inputs.values()))))
if __name__=='__main__':main()
