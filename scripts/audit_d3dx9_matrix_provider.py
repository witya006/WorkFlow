"""Record architecture/hash/export RVAs of the pinned matrix runtime,without loading it."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def main():
    reference=json.loads((WS/'inventory/client455-mesh-runtime-reference.json').read_text(encoding='utf-8'));provider=reference['matrix_provider'];path=Path(provider['path']);data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=provider['sha256']:raise ValueError('Pinned matrix provider changed')
    image=pe(data);base=image['image_base'];header=struct.unpack_from('<I',data,0x3c)[0];rva,size=struct.unpack_from('<II',data,header+24+96)
    directory=struct.unpack('<IIHH7I',read_va(data,base+rva,40));names,functions,ordinals=directory[9],directory[8],directory[10];exports=[]
    for n in range(directory[7]):
        nameRva=struct.unpack('<I',read_va(data,base+names+4*n,4))[0];name=read_va(data,base+nameRva,96).split(b'\0',1)[0].decode('ascii')
        if name not in ['D3DXMatrixInverse','D3DXMatrixMultiply']:continue
        ordinal=struct.unpack('<H',read_va(data,base+ordinals+2*n,2))[0]
        if ordinal>=directory[6]:raise ValueError('Matrix export ordinal outside table')
        entry=struct.unpack('<I',read_va(data,base+functions+4*ordinal,4))[0]
        if rva<=entry<rva+size:raise ValueError('Unexpected forwarded matrix export')
        exports.append({'name':name,'rva':hex(entry),'preferred_va':hex(base+entry)})
    if len(exports)!=2:raise ValueError('Missing matrix exports')
    report={'path':str(path),'sha256':provider['sha256'],'architecture':'x86','preferred_image_base':hex(base),'file_version':provider['file_version'],'exports':exports,'observed_current_host_behavior':{'input_diagonal_bits':['40000000','40000000','40000000','3f800000'],'inverse_diagonal_bits':['3effffff','3effffff','3effffff','3f7fffff'],'scope':'Actual direct export check in14562-case source CPU test;CPU-dispatch-specific observation,not all-hardware certification'},'behavior_evidence':['inventory/client455-mesh-runtime.json','inventory/client455-mesh-runtime-client.json','scripts/native/test_client455_mesh_runtime.cpp'],'limits':['Export-entry RVAs only;internal CPU dispatcher implementations not mapped','No input EXE executed;this audit is static anddoes not load the DLL']}
    (WS/'inventory/client455-d3dx9-provider.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sha256':report['sha256'],'architecture':'x86','exports':exports}))
if __name__=='__main__':main()
