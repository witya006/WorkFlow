"""Select missing resource dependencies from an OWN live-run diagnostic."""
import argparse,json,re,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_language import decode
from audit_client455_resource_catalog import catalog,cstring,sha
from audit_client455_legacy_models import expected as legacy_model
from mesh08 import decode as mesh08


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--events',required=True)
    parser.add_argument('--monster-animation-mesh',action='append',type=int,default=[])
    parser.add_argument('--resource', action='append', default=[],
                        help='Resolve only the selected paths observed in this run')
    args=parser.parse_args()
    events=(WS/args.events).resolve()
    if not events.is_relative_to((WS/'work/m9').resolve()) or events.name!='debug-events.jsonl':raise ValueError('Expected owned live-run events')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']).resolve()
    requested=set()
    for line in events.read_text().splitlines():
        event=json.loads(line)
        if event.get('kind')!='debug_string':continue
        text=event.get('value','')
        match=re.search(r'(?:FileName = |ImportMeshData\( )([^\r\n]*?\.(?:bn|ani|msh))(?= \[| \))',text,re.IGNORECASE)
        if match:requested.add(match[1].replace('\\','/').removeprefix('./'))
    if args.resource:
        selected = {name.casefold() for name in args.resource}
        requested = {name for name in requested if name.casefold() in selected}
        if {name.casefold() for name in requested} != selected:
            raise ValueError('Selected resource must be present in owned diagnostics')
    inputs={};directories={};members=[];missing=[];observations=[];previous={}
    def add(path):
        path=path.resolve()
        if not path.is_relative_to(client) or not path.is_file():raise ValueError('Invalid original resource dependency')
        relative=path.relative_to(client).as_posix()
        inputs[relative.casefold()]=dict(original=str(path),relative=relative,sha256=sha(path),bytes=path.stat().st_size)
    manifest=WS/'inventory/client455-live-resource-inputs.json'
    if manifest.exists():
        previous=json.loads(manifest.read_text())
        for row in previous['inputs']:
            path=Path(row['original'])
            if sha(path)!=row['sha256']:raise ValueError('Changed earlier live resource dependency')
            add(path)
        members+=previous['members']
        observations+=previous.get('observations',[previous['observation']])
    def resolve(relative):
        path=(client/relative).resolve()
        if not path.is_relative_to(client):raise ValueError('Resource path escaped client')
        if path.is_file():add(path);return path.read_bytes()
        directory=path.parent
        if directory not in directories:
            info=directory/'RFSINFO.DAT';names=info.read_text(encoding='ascii').split() if info.is_file() else []
            if not names:
                for i in range(1024):
                    candidate=directory/f'DATA{i}.RFS'
                    if not candidate.is_file():break
                    names.append(candidate.name)
            table={}
            for name in names:
                archive=(directory/name).resolve()
                if not archive.is_relative_to(client):raise ValueError('Archive index escaped client')
                if not archive.is_file():continue
                with archive.open('rb') as stream:
                    header=stream.read(4)
                    if len(header)!=4:raise ValueError('Short RFS header')
                    count=struct.unpack('<I',header)[0];length=archive.stat().st_size
                    if count>(length-4)//64:raise ValueError('Invalid RFS count')
                    for _ in range(count):
                        row=stream.read(64)
                        if len(row)!=64 or b'\0' not in row[:56]:raise ValueError('Invalid RFS member')
                        offset,size=struct.unpack_from('<II',row,56)
                        if offset+size>length:raise ValueError('Invalid RFS member range')
                        table.setdefault(row[:56].split(b'\0')[0].lower(),(archive,offset,size))
            directories[directory]=(info,table)
        info,table=directories[directory];entry=table.get(path.name.encode('ascii').lower())
        if not entry:missing.append(relative);return None
        archive,offset,size=entry;add(archive)
        if info.is_file():add(info)
        with archive.open('rb') as stream:stream.seek(offset);data=stream.read(size)
        if len(data)!=size:raise ValueError('Short RFS member data')
        members.append(dict(relative=relative,archive=archive.relative_to(client).as_posix(),offset=offset,bytes=size));return data
    resource=client/'DataTable/Resource.edf';add(resource);mesh_rows={}
    groups=catalog(decode(resource.read_bytes()))
    animation_rows=previous.get('selected_monster_animations', []) if manifest.exists() else []
    table=groups[1][2]
    for i in range(table['count']):
        start=i*table['stride']
        row=table['raw'][start:start+table['stride']]
        key=struct.unpack_from('<I',row)[0]
        if key>>12 not in args.monster_animation_mesh:
            continue
        name=(cstring(row,8,128)+cstring(row,136,64)).replace('\\','/').removeprefix('./')
        selection = dict(mesh=key>>12,key=key,relative=name)
        if selection not in animation_rows:animation_rows.append(selection)
        requested.add(name)
    for tables in groups:
        table=tables[1]
        for i in range(table['count']):
            row=table['raw'][i*328:(i+1)*328]
            name=(cstring(row,8,128)+cstring(row,136,64)).replace('\\','/').removeprefix('./')
            mesh_rows.setdefault(name.casefold(),row)
    for name in sorted(requested):
        data=resolve(name)
        if data is None or not name.lower().endswith('.msh'):continue
        row=mesh_rows.get(name.casefold())
        if row is None:raise ValueError('Observed mesh absent from Resource.edf')
        heads=[part.header for part in mesh08(data).parts] if data.startswith(b'MESH08') else [head for head,_ in legacy_model(data)[1]]
        texture_root=cstring(row,200,128).replace('\\','/').removeprefix('./')
        for head in heads:
            for at in [398,498]:
                texture=head[at:at+100].split(b'\0')[0].decode('ascii').replace('\\','/').rsplit('/',1)[-1]
                if texture:
                    relative=f'{texture_root.rstrip("/")}/{texture}'
                    if resolve(relative) is None:
                        fallback=str(Path(relative).with_suffix('.rft')).replace('\\','/')
                        if resolve(fallback) is not None:missing.remove(relative)
    observation=dict(file=events.relative_to(WS).as_posix(),sha256=sha(events))
    if observation not in observations:observations.append(observation)
    if args.resource:
        resolved = {name.casefold() for name in requested} - {name.casefold() for name in missing}
        missing += [name for name in previous.get('missing', []) if name.casefold() not in resolved]
        requested.update(previous.get('requested', []))
    report=dict(scope='Resource dependencies requested by owned live runs;not complete client assets or455equivalence',
        script=dict(file=Path(__file__).relative_to(WS).as_posix(),sha256=sha(Path(__file__))),
        observation=observation,observations=observations,requested=sorted(requested),
        inputs=sorted(inputs.values(),key=lambda row:row['relative'].casefold()),members=members,missing=sorted(set(missing)),
        selected_monster_animations=animation_rows,
        input_exe_executed=False,server_modified=False)
    (WS/'inventory/client455-live-resource-inputs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(requested=len(requested),input_files=len(inputs),input_bytes=sum(row['bytes'] for row in inputs.values()),missing=len(report['missing']))))


if __name__=='__main__':main()
