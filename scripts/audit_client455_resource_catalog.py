"""Pin Resource.edf owners and inventory the real catalog needed by selection."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_language import decode
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def record(path):return dict(file=Path(path).relative_to(WS).as_posix(),sha256=sha(path))
def fingerprint(data):
    value=2166136261
    for byte in data:value=((value^byte)*16777619)&0xffffffff
    return value
def catalog(plain):
    at=0;groups=[]
    for group in range(9):
        tables=[]
        for kind,stride in enumerate([260,328,244]):
            if len(plain)-at<4:raise ValueError('Short resource count')
            count=struct.unpack_from('<I',plain,at)[0];at+=4
            if count>(len(plain)-at)//stride:raise ValueError('Short resource rows')
            raw=plain[at:at+count*stride];at+=count*stride;tables.append(dict(count=count,stride=stride,raw=raw))
        groups.append(tables)
    if at!=len(plain):raise ValueError('Unaccounted Resource.edf tail')
    return groups
def cstring(row,at,width):
    value=row[at:at+width];assert b'\0' in value
    return value.split(b'\0',1)[0].decode('ascii')
def main():
    raw_file=WS/'artifacts/client455-progress/resource-catalog141-reference/session.json'
    raw=json.loads(raw_file.read_text());flow={int(row['addr'],16):row for row in raw['cfg']['result']};rows=[]
    for entry in raw['ranges']['result']:
        assert not entry['error'];addr,size=int(entry['fn']['addr'],16),int(entry['fn']['size'],16)
        pages=raw['asm'][entry['fn']['addr']];assert pages[-1]['cursor']['done']
        lines=[line for page in pages for line in page['asm']['lines']]
        assert all(len(page['asm']['lines'])<=100 for page in pages) and len(lines)==pages[0]['total_instructions']
        starts={int(line['addr'],16) for line in lines};assert len(starts)==len(lines)
        cfg=flow[addr];assert cfg['cursor']['done'] and cfg['count']==cfg['total_blocks']
        blocks=[block for block in cfg['blocks'] if block['size']>0]
        assert all(int(b['start'],16)<int(b['end'],16) and int(b['start'],16) in starts for b in blocks)
        assert all(any(int(b['start'],16)<=start<int(b['end'],16) for b in blocks) for start in starts)
        regions=[]
        for block in sorted(blocks,key=lambda b:int(b['start'],16)):
            first,last=int(block['start'],16),int(block['end'],16)
            if regions and regions[-1][1]==first:regions[-1][1]=last
            else:regions.append([first,last])
        # IDA function-size metadata is not a contiguous extent when EH chunks
        # are shared/out of line. Pin every actual CFG region, including tails.
        rows.append(dict(rva=hex(addr-0x400000),declared_bytes=size,instructions=len(lines),positive_cfg_blocks=len(blocks),
                         regions=[dict(rva=hex(a-0x400000),bytes=b-a) for a,b in regions]))
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        assert sha(path)==pins[key]['sha256'] and pe(data)['architecture']=='x86'
        functions=[]
        for row in rows:
            functions.append(dict(row,regions=[dict(region,sha256=hashlib.sha256(read_va(data,0x400000+int(region['rva'],16),region['bytes'])).hexdigest()) for region in row['regions']]))
        references.append(dict(**record(path),architecture='x86',image_base='0x400000',functions=functions))
    assert references[0]['functions']==references[1]['functions'] and len(rows)==7
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);source=client/'DataTable/Resource.edf';plain=decode(source.read_bytes());groups=catalog(plain)
    expected=bytearray();summary=[];inputs={};missing=set();selected_ani=[];archive_cache={};archived=[];skipped_meshes=[]
    bone_ids=[{struct.unpack_from('<I',table[0]['raw'],260*i)[0] for i in range(table[0]['count'])} for table in groups]
    def add(path):
        path=path.resolve();assert path.is_relative_to(client.resolve())
        if path.is_file():inputs[path.relative_to(client).as_posix()]=dict(original=str(path),sha256=sha(path),bytes=path.stat().st_size)
        else:missing.add(path.relative_to(client).as_posix())
        return path.is_file()
    def resolve(path):
        path=path.resolve();assert path.is_relative_to(client.resolve())
        if path.is_file():return add(path)
        directory=path.parent
        if directory not in archive_cache:
            info=directory/'RFSINFO.DAT'
            names=info.read_text(encoding='ascii').split() if info.is_file() else []
            if not names:
                for i in range(1024):
                    candidate=directory/f'DATA{i}.RFS'
                    if not candidate.is_file():break
                    names.append(candidate.name)
            table={}
            for name in names:
                archive=(directory/name).resolve();assert archive.is_relative_to(client.resolve())
                if not archive.is_file():continue
                with archive.open('rb') as stream:
                    count_bytes=stream.read(4);assert len(count_bytes)==4
                    count=struct.unpack('<I',count_bytes)[0];assert count<=(archive.stat().st_size-4)//64
                    for i in range(count):
                        row=stream.read(64);assert len(row)==64 and b'\0' in row[:56]
                        member=row[:56].split(b'\0',1)[0];offset,size=struct.unpack_from('<II',row,56)
                        table.setdefault(member.lower(),(archive,offset,size))
            archive_cache[directory]=(info,table)
        info,table=archive_cache[directory];entry=table.get(path.name.encode('ascii').lower())
        if entry:
            archive,offset,size=entry;assert offset+size<=archive.stat().st_size
            add(archive)
            if info.is_file():add(info)
            archived.append(dict(file=path.relative_to(client).as_posix(),archive=archive.relative_to(client).as_posix(),offset=offset,bytes=size))
            return True
        missing.add(path.relative_to(client).as_posix());return False
    add(source)
    for group,tables in enumerate(groups):
        table_summary=[]
        for kind,table in enumerate(tables):
            raw=table['raw'];mutated=bytearray(raw)
            for i in range(table['count']):
                row=raw[i*table['stride']:(i+1)*table['stride']];path_at,file_at=(4,132) if kind==0 else (8,136)
                name=(cstring(row,path_at,128)+cstring(row,file_at,64)).replace('\\','/')
                relative=name.removeprefix('./');assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
                if kind==1:
                    parent=struct.unpack_from('<I',row,4)[0];owner=group or 5
                    present=(parent==0xfffffffe or (0 if parent==0xffffffff else parent) in bone_ids[0]) if owner==5 else parent in bone_ids[group]
                    if not present:skipped_meshes.append(dict(group=group,index=struct.unpack_from('<I',row,0)[0],parent=parent,file=relative,reason='Declared parent ID absent;target skips before AddMesh'))
                if kind==0:
                    resolve(client/relative)
                    bbox=(cstring(row,4,128)+cstring(row,196,64)).replace('\\','/').removeprefix('./');resolve(client/bbox)
                elif kind==1 and group in [0,5] and struct.unpack_from('<I',row,4)[0]==0xfffffffe:
                    struct.pack_into('<I',mutated,i*328+4,struct.unpack_from('<I',row,0)[0])
                    resolve((client/relative).with_suffix('.BBX'))
                elif kind==2 and not any(item['group']==group for item in selected_ani) and resolve(client/relative):
                    selected_ani.append(dict(group=group,file=relative,index=struct.unpack_from('<I',row,0)[0]))
            digest=fingerprint(mutated);expected+=struct.pack('<II',table['count'],digest)
            table_summary.append(dict(count=table['count'],stride=table['stride'],loaded_fingerprint=hex(digest)))
        summary.append(dict(group=group,tables=table_summary))
    root=WS/'artifacts/client455-resource-catalog';root.mkdir(exist_ok=True)
    player=next(item for item in selected_ani if item['group']==0)
    expected+=struct.pack('<I',player['index']);expected_file=root/'expected.bin';expected_file.write_bytes(expected)
    out=dict(status='STATIC_CONFIRMED_PARTIAL',scope='Ordinary Resource.edf catalog/manager registration/player bone validation/ANI event metadata;not whole bootstrap or selection',
        references=references,raw=record(raw_file),full_functions=len(rows),full_instructions=sum(row['instructions'] for row in rows),positive_cfg_blocks=sum(row['positive_cfg_blocks'] for row in rows),
        catalog=dict(original=str(source),sha256=sha(source),decoded_bytes=len(plain),groups=summary),inputs=list(inputs.values()),selected_animations=selected_ani,
        expected=record(expected_file),expected_skipped_meshes=skipped_meshes,missing_declared_inputs=sorted(missing),resolved_archive_members=archived,sources=[record(WS/'scripts/native/client455_resource_catalog.h'),record(WS/'scripts/client455_resource_catalog_port.py')],
        snapshot=record(WS/'artifacts/client455-progress/before141/manifest.json'),script=record(Path(__file__)),
        gaps=['Full data bootstrap and455class/appearance/item consumers','All error UI/quit policy and unsafe malformed target inputs','Ordinary selection/auth/world/gameplay/full client acceptance'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-resource-catalog-reference.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(functions=len(rows),instructions=out['full_instructions'],cfg=out['positive_cfg_blocks'],groups=9,counts=[[t['count'] for t in g] for g in groups],inputs=len(inputs),missing=len(missing),input_bytes=sum(r['bytes'] for r in inputs.values()))))
if __name__=='__main__':main()
