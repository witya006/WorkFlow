"""Resolve actual Chef particle references through the supplied RPK corpus."""
import collections,hashlib,json,re,struct
from pathlib import Path
from audit_client455_effects import decoded
from compare_client_binaries import WS
from rpk455 import Rpk

def sha(raw):return hashlib.sha256(raw).hexdigest()
def ini(path):
    sections={};active=''
    for line in path.read_bytes().splitlines():
        text=line.strip()
        if text.startswith(b'[') and b']' in text:active=text[1:text.index(b']')].decode('ascii').upper();sections.setdefault(active,{})
        elif b'=' in text:
            key,value=text.split(b'=',1);sections.setdefault(active,{})[key.strip().decode('ascii').upper()]=value.split(b';',1)[0].strip().decode('ascii')
    return sections
def main():
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);archives=[];members=collections.defaultdict(list)
    for path in sorted((client/'Chef').glob('*.rpk')):
        raw=path.read_bytes();archive=Rpk(raw);archives.append(dict(file=str(path),sha256=sha(raw),nodes=len(archive.nodes),members=len(archive.files)))
        for key,node in archive.files.items():
            members[key].append((path,archive,node))
    def resolve(name):
        key=name.replace('/','\\').lower().encode('ascii');prefix=b'.\\chef\\'
        if key.startswith(prefix):key=key[len(prefix):]
        found=members.get(key,[])
        if found:
            values=[]
            for path,archive,node in found:
                raw=archive.read(key);values.append((raw,dict(archive=str(path),node=node,offset=archive.base+archive.offsets[node],inferred_bytes=len(raw),declared_size=archive.nodes[node].declared_size,sha256=sha(raw))))
            if len({sha(raw) for raw,_ in values})>1:raise ValueError('Different archive variants need runtime enumeration: '+name)
            return values[0]
        path=client/name
        if path.is_file():
            raw=path.read_bytes();return raw,dict(loose=str(path),bytes=len(raw),sha256=sha(raw))
        return None,None
    definitions=[];stage=WS/'work/client-reference/particle455-inputs';stage.mkdir(parents=True,exist_ok=True)
    for kind in ['particle','entity']:
        table=ini(client/f'Chef/Real/{kind}.ini');maximum=int(table[kind.upper()+'_INFO']['MAX'+kind.upper()]);rows=[]
        for ordinal in range(1,maximum+1):
            section=table.get(kind.upper()+str(ordinal),{});name=section.get(kind.upper(),'NULL');match=re.match(r'[+-]?\d+',section.get('INDEX','0'));index=int(match[0]) if match else 0
            raw,evidence=resolve(name);row=dict(ordinal=ordinal,index=index,path=name,source=section,present=raw is not None,resolution=evidence)
            if raw is not None and kind=='particle':
                target=stage/f'particle_{index:04d}_{ordinal:03d}.spt';target.write_bytes(raw);row['copy']=target.relative_to(WS).as_posix()
                tokens=raw.split(b'\x1a')[0].split();row['tracks']=tokens.count(b'time');row['entity_refs']=[tokens[i+1].decode('ascii',errors='replace') for i,t in enumerate(tokens[:-1]) if t.lower()==b'entity_file']
                row['advanced_tokens']=sorted({t.decode('ascii') for t in tokens if t.lower() in [b'control_node',b'tracelength',b'[light]',b'distort',b'distort_offset',b'azirang_width',b'use_combine_scale']})
            rows.append(row)
        definitions.append(dict(kind=kind,ini=dict(file=str(client/f'Chef/Real/{kind}.ini'),sha256=sha((client/f'Chef/Real/{kind}.ini').read_bytes())),maximum=maximum,rows=rows))
    ids=set()
    for name in ['Patrol_B','Patrol_R','Bfly','accship','trans','trans2']:
        path=client/f'Chef/Eff/Real/{name}.EFF'
        if path.is_file():
            for record in decoded(path.read_bytes()):ids.update(struct.unpack_from('<I',record,at)[0] for at in [96,112,128] if struct.unpack_from('<I',record,at)[0])
    rows=definitions[0]['rows'];selected=[dict(index=r['index'],path=r['path'],present=r['present'],copy=r.get('copy'),advanced_tokens=r.get('advanced_tokens')) for r in rows if r['index'] in ids]
    report=dict(scope='Read-only exact Chef RPK/loose particle definitions;archive duplicate contents must match,not a claim of runtime enumeration policy',
        archives=archives,definitions=definitions,RVP_particle_ids=sorted(ids),RVP_definitions=selected,script_sha256=sha(Path(__file__).read_bytes()),input_exe_executed=False,server_modified=False)
    (WS/'inventory/client455-particle-inputs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(archives=len(archives),counts=[dict(kind=d['kind'],defined=d['maximum'],present=sum(r['present'] for r in d['rows'])) for d in definitions],RVP=selected)))
if __name__=='__main__':main()
