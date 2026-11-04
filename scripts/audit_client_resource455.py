"""Recheck archive-lifecycle/selection and existence contracts in both pinned PE."""
import hashlib
import json
import struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    prior=json.loads((WS/'inventory/client455-map-resources.json').read_text(encoding='utf-8'))
    functions=[('rpk_release',0x8e6d60,0x36),('group_release',0x8e7440,0x65),
               ('group_exists',0x8e7510,0x60),('set_active',0x8e75d0,0xa),
               ('resource_exists',0x8e75f0,0x48),('file_exists',0x8e7130,0x19),
               ('material_binary',0x90b1c0,0x1ad),('load_entities',0x8f94a0,0x3f2),
               ('release_bsp',0x8f9ad0,0x14a),('load_level',0x8ea220,0x926)]
    checks=[(0x8fe2ed,0x8e71c0,'BSP loads group from EntityPath'),(0x8fe2f3,0x8e75d0,'BSP selects its group'),
            (0x8f9532,0x8e75d0,'LoadEntities selects group after allocation'),(0x8f9ad9,0x8e7440,'ReleaseBsp releases archive group first'),
            (0x8ea245,0x8e75d0,'LoadLevel resets group at start'),(0x8ea735,0x8e75d0,'LoadLevel resets before light map'),
            (0x8eaa73,0x8e75d0,'LoadLevel resets before helper path'),(0x8e0b93,0x8e75f0,'Entity binary material uses archive-aware existence')]
    records=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']:raise ValueError('Pinned resource PE changed')
        bodies=[read_va(data,va,size) for _,va,size in functions]
        if baseline is not None and bodies!=baseline:raise ValueError('Resource lifecycle bodies differ')
        baseline=bodies
        instructions=[]
        for va,dest,meaning in checks:
            wanted=b'\xe8'+struct.pack('<i',dest-va-5)
            if read_va(data,va,5)!=wanted:raise ValueError(f'Resource call changed:{va:x}')
            instructions.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':wanted.hex(),'destination':hex(dest),'meaning':meaning})
        records.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000',
                        'functions':[{'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()} for (name,va,size),body in zip(functions,bodies)],
                        'instructions':instructions})
    report={'binary_evidence':records,'base_contracts_report':'inventory/client455-map-resources.json',
            'base_contracts_report_sha256':hashlib.sha256((WS/'inventory/client455-map-resources.json').read_bytes()).hexdigest(),
            'scope':'Manual decomp/disassembly plus reproducible checks of archive ownership/selection/existence. Native source results recorded separately.',
            'known_reference_quirks':['unchecked metadata reads/allocations, invalid tables and overlong paths unsafe',
                                      'directory scan skips first Win32 result, accepts any last3letters rpk with length>=4, limit check only after collecting',
                                      'group lowercases caller path and strips prefix by length without matching prefix text',
                                      'positioned FILE has physical archive EOF, no member size boundary',
                                      'repeat successful index/group loading does not implicitly release prior allocation']}
    if len(prior['binary_evidence'])!=2:raise ValueError('Both base references required')
    (WS/'inventory/client455-resource-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: resource lifecycle/exists10functions and8call sites match both pinned PE.')


if __name__=='__main__':main()
