"""Verify MESH08 framing operands against both pinned455x86images."""
import hashlib,json
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];baseline=None
    facts=[(0x922a6a,'c744241808000000','Start file cursor at8'),(0x922a91,'0fb77e06','Mesh count isWORD at+6'),(0x922b45,'05b5020000','Per-mesh header693bytes'),
        (0x9234c0,'0fb7043b','Vertex countWORD'),(0x9234d2,'ba40000000','Vertex allocation multiplier64'),(0x9234f3,'c1e606','Vertex copy size=count<<6'),
        (0x92350e,'0fb7043b','Index countWORD'),(0x923512,'3d00fa0000','Index count gate64000'),(0x923545,'ba02000000','Index bytes=count*2'),
        (0x923561,'03c0','Index copy size=count*2'),(0x92362f,'0fb7043a','Bone record countWORD'),(0x923638,'ba94010000','Bone record stride404')]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']:raise ValueError('MESH08 reference changed')
        bodies=[];functions=[]
        for name,va,size in [('detector',0x91f250,0x4c),('loader',0x922a00,0xe9b),('blend_names',0x93cb00,0x253)]:
            body=read_va(data,va,size);bodies.append(body);functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and bodies!=baseline:raise ValueError('MESH08 bodies differ betweenpins')
        baseline=bodies;instructions=[]
        for va,hexbytes,meaning in facts:
            wanted=bytes.fromhex(hexbytes)
            if read_va(data,va,len(wanted))!=wanted:raise ValueError('MESH08 operand changed:'+hex(va))
            instructions.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':hexbytes,'meaning':meaning})
        references.append({'sha256':digest,'architecture':'x86','image_base':'0x400000','functions':functions,'instructions':instructions})
    report={'reference':references,'format':{'magic_hex':'4d4553483038','count_offset':6,'count_bytes':2,'first_record':8,'header_bytes':693,'vertex_bytes':64,'index_bytes':2,'bone_record_bytes':404,'index_count_limit':64000},
        'confirmed':['Per mesh:693header,WORD vertex count/64byte records,WORD index count/WORD indices,WORD bone-record count/404byte records','Bone binding helper iterates404byte records:DWORD influence count followed by100byte name slots;GPU rebasing/runtime resolution separate','858loose real model files decoded andround-tripped in corpus report'],
        'limits':['This validates format framing,not full607line loader behavior','Source safety/capacity errors are own policy;reference has unchecked reads/debugbreak/OOM paths','Material texture loading,packed runtime mesh,shared GPU buffer rebasing,bone resolution andpublication remain open'],
        'raw_analysis':'artifacts/character-mesh-source/mesh08-0x93cb00.json and cached922A00body;artifacts/character-mesh08/framing-insns.json;owned IDAeb76ecefclosed/save;no input EXE execution'}
    (WS/'inventory/client455-mesh08-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:MESH08 3reference bodies/12framing instructions match both pinned455x86PE.')

if __name__=='__main__':main()
