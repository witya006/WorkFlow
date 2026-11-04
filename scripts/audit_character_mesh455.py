"""Pin legacy/455 mesh lifecycle and binding differences without executing inputs."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from export_character_analysis import coff_function_records

def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];baseline=None
    sites=[(0x921504,'68ab160000','Mesh storage5803bytes'),(0x92150b,'e8a013f5ff','Clear whole mesh via memset'),
        (0x921519,'810510961801ab160000','Account5803bytes'),(0x93bc5f,'81c2ba020000','Blend loop reference base+698'),
        (0x93bdb4,'899a50ffffff','Blend count at+522'),(0x93be02,'8dba54ffffff','Copy parent pointers to+526'),
        (0x93bb1c,'81c7ab160000','Parent mesh stride5803'),(0x93bb17,'7411','First match exits parent scan'),
        (0x93bb94,'83bd71130000007479','Rematch requires external flag at+5495'),
        (0x93bdc2,'83c040','Inline blend matrices advance64bytes'),(0x93bdf7,'d9508c','Identity first element at loop base+646')]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']:raise ValueError('Pinned Character reference changed')
        bodies=[];functions=[]
        for name,va,size in [('mesh_construct',0x9214e0,0x1c2),('mesh_destroy',0x920fd0,0xd2),('load_real',0x9238a0,0x195),
            ('init_vertex',0x93cd60,0x1083),('find_by_name',0x93ba40,0x57),('bind_parents',0x93bab0,0xbd),('rematch',0x93bb70,0xc1),('bind_blends',0x93bc40,0x1f6)]:
            body=read_va(data,va,size);bodies.append(body);functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and bodies!=baseline:raise ValueError('Character bodies differ between references')
        baseline=bodies;facts=[]
        for va,hexbytes,meaning in sites:
            wanted=bytes.fromhex(hexbytes)
            if read_va(data,va,len(wanted))!=wanted:raise ValueError('Character instruction changed:'+hex(va))
            facts.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':hexbytes,'meaning':meaning})
        references.append({'sha256':digest,'architecture':'x86','image_base':'0x400000','functions':functions,'instructions':facts})
    legacy=[]
    inputs=json.loads((WS/'inventory/character-codeview.json').read_text(encoding='utf-8'))['objects']
    for index,names in [(7,['?InitVertex@@YAXPAVObjectData@@PAVCHARACTEROBJECT@@1PAVTextureManager@@_N@Z','?FindBlendParent@@YAXPAUObjectMesh@@H0HPAVObjectData@@@Z']),
                        (9,['??0ObjectMesh@@QAE@XZ','??1ObjectMesh@@QAE@XZ'])]:
        item=inputs[index-1];raw=(WS/item['working_object']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Legacy mesh COFF changed')
        records=coff_function_records(raw)
        for name in names:
            record=records[name];legacy.append({'symbol':name,'object_sha256':item['sha256'],'file_offset':record['file_offset'],'size':record['size'],'body_sha256':hashlib.sha256(record['bytes']).hexdigest(),'rva':None})
    report={'reference':references,'legacy':legacy,'confirmed':['Legacy ctor omits blend pointer+160; actual FindBlendParent assigns it for every processed mesh,including count0 allocation','455 uses5803byte packed mesh and full zeroing;blend count+522,inline parent pointers+526,inline matrix writes start+646','Legacy array binding counts all duplicate-name matches and keeps last;455stops at first match','Legacy and455 both use720byte mesh-data records and424byte physique records'],
        'unknown':['Complete455mesh members/5803byte ownership and subobject lifecycles','455capacity/overflow domain:parent pointer copies beyond30overlap the observed matrix region;do not assume a safe50element object array','Real Character assets/full InitVertex triangles/textures/D3D9 render and all exception/OOM paths','No production constructor patch justified by unloaded fixture pointer alone'],
        'raw_analysis':'artifacts/character-analysis and artifacts/character-mesh-source;owned IDAc99d5253closed/save;no input EXE execution'}
    (WS/'inventory/character455-mesh-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:8Character455bodies/11instructions in both pinned PE;4legacy lifecycle bodies pinned.')

if __name__=='__main__':main()
