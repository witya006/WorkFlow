"""Pin packed455 parent/bone binding bodies and their decisive instructions."""
import hashlib,json
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];baseline=None
    facts=[(0x93cb9d,'8d5904','First influence name atrecord+4'),(0x93cbf6,'e845eeffff','First lookup against external array'),(0x93cc17,'e824eeffff','Fallback lookup against local array'),(0x93cc65,'83c364','Influence-name stride100'),(0x93cc82,'81c194010000','Bone-record stride404'),(0x93cc99,'89bb50ffffff','Write count atmesh+522,base698-176'),(0x93cce7,'8dbb54ffffff','Pointer copy destinationmesh+526,base698-172'),(0x93cced,'f3a5','Copy pointers after identity stores'),(0x93ccf2,'81c3ab160000','Mesh stride5803'),(0x93bb3a,'897500','Parent pointer destinationmesh+518'),(0x93bb3d,'c645fa01','Has-parent byte atmesh+512'),(0x93bb43,'c7857113000001000000','External-parent/rematch flag atmesh+5495')]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']:raise ValueError('Reference changed')
        functions=[];bodies=[]
        for name,va,size in [('lookup',0x93ba40,0x57),('parents',0x93bab0,0xbd),('rematch',0x93bb70,0xc1),('mesh08_bones',0x93cb00,0x253)]:
            body=read_va(data,va,size);bodies.append(body);functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and bodies!=baseline:raise ValueError('Reference binding bodies differ')
        baseline=bodies;instructions=[]
        for va,hexbytes,meaning in facts:
            if read_va(data,va,len(bytes.fromhex(hexbytes)))!=bytes.fromhex(hexbytes):raise ValueError('Binding instruction changed:'+hex(va))
            instructions.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':hexbytes,'meaning':meaning})
        references.append({'sha256':digest,'architecture':'x86','image_base':'0x400000','functions':functions,'instructions':instructions})
    report={'reference':references,'confirmed':['Case-sensitive first name match for parent and blend lookup','External skeleton first;local fallback;resolved names deduplicated in first-encounter order;unresolved occurrences not deduplicated','Parent pointer518,has-parent512,external/rematch5495;blend count522,pointers526,identity matrices646','Identity stores precede pointer copy:at31+selected names pointer copy overlaps first matrix bytes;do not invent disjoint50-slot ABI','Reference influence count is signed;nonpositive counts skip the slots'],
        'limits':['Owned >50resolved or >4positive influences/unterminated-record errors replace unchecked reference overflow/overread','Source API borrows input views and returns missing counts;reference vector frees and debug logging belong to later loader adapter','Complete mesh constructor/material/transform/animation/GPU/full normal loader remains open'],
        'raw_analysis':'artifacts/character-mesh08/bone-binding-insns.json;cached reference-0x93ba40-asm/reference-0x93bab0/reference-0x93bb70-asm/mesh08-0x93cb00;owned IDA6f091546closed/save;no input EXE execution'}
    (WS/'inventory/client455-mesh-bindings-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:455parent/bone bindings4bodies/12instruction sites match both pinned x86PE.')
if __name__=='__main__':main()
