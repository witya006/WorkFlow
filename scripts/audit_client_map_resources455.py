"""Pin map containers and resolve weather dependencies without running game code."""
import hashlib
import json
import struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from map455 import MapFile, inspect_r3t
from rpk455 import Rpk


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455'])
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    functions=[('rpk_open_index',0x8e6c50,0x109),('rpk_path_component',0x8e6da0,0x89),
               ('rpk_name_match',0x8e6e30,0x3e),('rpk_lookup_offset',0x8e6e70,0x125),
               ('rpk_fopen',0x8e70d0,0x55),('rpk_directory_scan',0x8e71c0,0x27d),
               ('rpk_group_lookup',0x8e74b0,0x59),('archive_aware_fopen',0x8e7680,0x37),
               ('bsp_load',0x8fdea0,0x60d),('ebp_load',0x8ff280,0x456),
               ('particle_spt_load',0x8db5b0,0x1553),('dds_header_xor',0x8f1810,0x4c),
               ('entity_geometry_load',0x8e0a20,0xe3d),('r3t_load',0x8f33b0,0x139),
               ('dds_from_file',0x8f1860,0xf1)]
    binary=[];baseline=None;header_mask=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(data)!=target[key]['sha256']:raise ValueError('Pinned map-analysis PE changed')
        bodies=[read_va(data,va,size) for _,va,size in functions]
        if baseline is not None and bodies!=baseline:raise ValueError('Map function bodies differ between references')
        baseline=bodies
        mask=read_va(data,0xbf7f00,128)
        if header_mask is not None and mask!=header_mask:raise ValueError('DDS header masks differ')
        header_mask=mask
        checks=[(0x8fdf33,bytes.fromhex('68ac020000'),'BSP header684'),
                (0x8fdf41,bytes.fromhex('833f27'),'BSP version39'),
                (0x8ff2b5,bytes.fromhex('6884010000'),'EBP header388'),
                (0x8ff2c3,bytes.fromhex('833f14'),'EBP version20'),
                (0x8e6d37,bytes.fromhex('c1e106'),'RPK node64'),
                (0x8e7102,bytes.fromhex('8b9710010000'),'RPK payload base at owner+272'),
                (0x8db650,bytes.fromhex('bf88daae00'),'case-sensitive end token before Particle header'),
                (0x8db741,bytes.fromhex('bf88daae00'),'case-sensitive end token before lowercasing body token'),
                (0x8db753,bytes.fromhex('0f8429130000'),'body end goes to finalization before next archive entry')]
        for va,wanted,_ in checks:
            if read_va(data,va,len(wanted))!=wanted:raise ValueError(f'Instruction changed:{va:x}')
        binary.append({'input':folder,'sha256':sha(data),'architecture':'x86','image_base':'0x400000',
                       'functions':[{'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':sha(body)}
                                    for (name,va,size),body in zip(functions,bodies)],
                       'dds_header_mask':{'va':'0xbf7f00','rva':'0x7f7f00','size':128,'sha256':sha(mask)},
                       'instructions':[{'va':hex(va),'rva':hex(va-0x400000),'bytes':b.hex(),'meaning':meaning} for va,b,meaning in checks]})
    archives=[];providers={};size_mismatches=0;entries=0
    for path in sorted((root/'Map/Entity').glob('*.rpk')):
        data=path.read_bytes();rpk=Rpk(data)
        if rpk.to_bytes()!=data:raise ValueError('RPK round trip changed bytes')
        relative=path.relative_to(root).as_posix()
        archives.append({'path':relative,'size':len(data),'sha256':sha(data),'nodes':len(rpk.nodes),
                         'files':len(rpk.files),'declared_size_mismatches':len(rpk.size_mismatches),'round_trip':True})
        entries+=len(rpk.files);size_mismatches+=len(rpk.size_mismatches)
        for key,i in rpk.files.items():
            full=b'map\\entity\\'+key
            providers.setdefault(full,[]).append((path,rpk,i,key))
    maps=[]
    for path in sorted((root/'Map').rglob('*')):
        kind=path.suffix[1:].lower()
        if kind not in ('bsp','ebp') or not path.is_file():continue
        data=path.read_bytes();parsed=MapFile(data,kind)
        if parsed.to_bytes()!=data:raise ValueError('Map round trip changed bytes')
        end=parsed.sequential_end()
        if end>len(data):raise ValueError('Sequential map reads would exceed input')
        maps.append({'path':path.relative_to(root).as_posix(),'kind':kind,'size':len(data),'sha256':sha(data),
                     'version':39 if kind=='bsp' else 20,'round_trip':True,'lumps':parsed.summary(),
                     'declared_overlaps':parsed.declared_overlaps,'sequential_offset_mismatches':parsed.sequential_offset_mismatches(),
                     'sequential_end':end,'unconsumed_bytes':len(data)-end})
    references={};r3x=[]
    for path in sorted((root/'Map').rglob('*.r3x')):
        data=path.read_bytes();body=(data[4:1036]+bytes(1032))[:1032]
        if len(data)<4 or struct.unpack_from('<I',data)[0]!=0x3f8ccccd:raise ValueError('Unexpected R3X version')
        rel=path.relative_to(root).as_posix()
        r3x.append({'path':rel,'size':len(data),'sha256':sha(data)})
        if struct.unpack_from('<I',body)[0]&0x20:
            for slot,(name_at,id_at) in enumerate([(256,384),(392,520)]):
                id=struct.unpack_from('<I',body,id_at)[0]
                if id:
                    name=body[name_at:name_at+128].split(b'\0')[0]
                    references.setdefault(name,[]).append({'r3x':rel,'slot':slot,'id':id})
    selected={};missing=[];weather=[]
    stage=WS/'work/map-resource-audit/selected'
    def resolve(name):
        key=name.lower().replace(b'/',b'\\').removeprefix(b'.\\')
        if key in selected:return selected[key]
        if any(part in (b'',b'.',b'..') for part in key.split(b'\\')) or b':' in key:
            raise ValueError('Unsafe dependency path')
        choices=providers.get(key,[])
        loose=root.joinpath(*[p.decode('ascii') for p in key.split(b'\\')])
        candidates=[]
        for path,rpk,i,inner in choices:
            raw=rpk.read(inner)
            candidates.append((raw,{'archive':path.relative_to(root).as_posix(),'node':i,
                                    'absolute_archive_offset':rpk.base+rpk.offsets[i],
                                    'declared_size':rpk.nodes[i].declared_size,'inferred_extent':rpk.extents[i]}))
        if loose.is_file():candidates.append((loose.read_bytes(),{'loose':loose.relative_to(root).as_posix()}))
        if not candidates:return None
        if len({sha(raw) for raw,_ in candidates})!=1:raise ValueError('Ambiguous resource content; runtime ordering required')
        raw=candidates[0][0];dest=stage.joinpath(*[p.decode('ascii') for p in key.split(b'\\')])
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and dest.read_bytes()!=raw:raise ValueError('Selected resource snapshot changed')
        if not dest.exists():dest.write_bytes(raw)
        record={'path':key.decode('ascii').replace('\\','/'),'size':len(raw),'sha256':sha(raw),
                'providers':[meta for _,meta in candidates],'staged':dest.relative_to(WS).as_posix()}
        selected[key]=record
        if key.endswith(b'.r3e'):
            parsed=MapFile(raw,'r3e')
            if parsed.to_bytes()!=raw:raise ValueError('R3E round trip changed bytes')
            record['geometry']={'version':113,'lumps':parsed.summary(),'sequential_offset_mismatches':parsed.sequential_offset_mismatches()}
        elif key.endswith(b'.r3t'):record['textures']=inspect_r3t(raw,header_mask)
        return record
    for name,uses in references.items():
        resolved=resolve(name)
        item={'name':name.decode('ascii'),'uses':uses,'resolved':resolved is not None,'dependencies':[]}
        weather.append(item)
        if not resolved:
            missing.append({'name':name.decode('ascii'),'uses':uses});continue
        raw=(WS/resolved['staged']).read_bytes();tokens=raw.split()
        try:start=tokens.index(b'[Particle]')+1
        except ValueError:raise ValueError('Weather input lacks Particle marker')
        # Match raw whitespace tokens, not line/comment grammar invented for SPT.
        # Dependency discovery only; numeric rand syntax is left to real loader.
        for i in range(start,len(tokens)):
            token=tokens[i]
            if token==b'end':break
            if token.lower()==b'entity_file':
                if i+1==len(tokens):raise ValueError('Missing entity_file operand')
                entity=tokens[i+1];base=entity.rsplit(b'.',1)[0]
                for suffix in (b'.r3e',b'.r3m',b'.r3t'):
                    dep=resolve(base+suffix)
                    item['dependencies'].append({'name':(base+suffix).decode('ascii'),'resolved':dep is not None})
                    if dep is None:missing.append({'name':(base+suffix).decode('ascii'),'from':name.decode('ascii')})
    # Search remaining archive indexes for missing weather directory components.
    # Hash only header+tables here: unrelated payloads are not used as evidence.
    searches=[]
    if missing:
        components={item['name'].encode('ascii').lower().split(b'\\')[-3] for item in missing}
        for path in sorted(root.rglob('*.rpk')):
            with path.open('rb') as stream:
                head=stream.read(8)
                if len(head)!=8 or struct.unpack_from('<I',head)[0]!=0x3f800000:raise ValueError('Unsupported RPK in missing-resource search')
                count=struct.unpack_from('<I',head,4)[0]
                table=stream.read(72*count)
                if len(table)!=72*count:raise ValueError('Truncated RPK search table')
            searches.append({'path':path.relative_to(root).as_posix(),'size':path.stat().st_size,
                             'header_tables_sha256':sha(head+table),
                             'directory_component_hits':[c.decode('ascii') for c in sorted(components) if c in table.lower()]})
    report={'schema':1,'scope':'Map containers and six unique active weather references from65 loose R3X; not a complete client resource manifest or runtime proof',
            'tool_sha256':{f'scripts/{name}':sha((WS/'scripts'/name).read_bytes()) for name in
                           ['rpk455.py','map455.py','audit_client_map_resources455.py','test_map455.py']},
            'binary_evidence':binary,'archives':archives,'archive_file_entries':entries,
            'archive_declared_size_mismatches':size_mismatches,'map_containers':maps,'r3x':r3x,
            'weather':weather,'selected_assets':list(selected.values()),'missing':missing,
            'other_archive_index_search':searches,
            'identified_source_gaps':['Legacy source has no archive-aware fopen/group support.',
                                      'Legacy particle SPT parser scans to EOF and does not stop on case-sensitive end;455 stops before lowercasing. This matters for FILE positioned inside RPK.',
                                      'Full particle455 added options and curves remain outside this resource audit.'],
            'limits':['RPK tooling reads next-offset/EOF extents; metadata sizes are preserved even when wrong.',
                      'BSP/EBP tool validates ranges/record strides and retains raw offsets; sequential game reads can differ.',
                      'Staged assets are unmodified; no actual game loader, GPU, collision or network executed.',
                      'No claim that all maps or all particle options/material/texture behavior match455.']}
    out=WS/'inventory/client455-map-resources.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(archives)} RPK/{entries} files, {len(maps)} BSP/EBP round trips, {len(selected)} staged weather assets. Missing references: {len(missing)}.')


if __name__=='__main__':main()
