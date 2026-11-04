"""Pin the455 graphics creation path without executing the reference binary."""
import hashlib
import json
import struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    records=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']:raise ValueError('Pinned graphics reference changed')
        functions=[];bodies=[]
        for name,va,size in [('device_enumeration',0x8ef080,0x60b),('device_creation',0x8ef690,0x51e),('window_init',0x8f0330,0x21a)]:
            body=read_va(data,va,size);bodies.append(body)
            functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and bodies!=baseline:raise ValueError('Graphics reference bodies differ')
        baseline=bodies
        checks=[(0x8ef872,bytes.fromhex('834f0c04'),'force flag0x4 before CreateDevice'),
                (0x8ef8a3,bytes.fromhex('ffd2'),'indirect IDirect3D9 CreateDevice call'),
                (0x8f0344,b'\xe8'+struct.pack('<i',0xa07f9c-0x8f0349),'Direct3DCreate9 import thunk')]
        facts=[]
        for va,wanted,meaning in checks:
            if read_va(data,va,len(wanted))!=wanted:raise ValueError(f'Graphics instruction changed:{va:x}')
            facts.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':wanted.hex(),'meaning':meaning})
        for va,value in [(0x8ef341,0x40),(0x8ef373,0x80),(0x8ef3a2,0x20)]:
            instruction=read_va(data,va,11)
            if instruction[:3]!=bytes.fromhex('c7849c') or instruction[-4:]!=struct.pack('<I',value):raise ValueError('VP flag store changed')
            facts.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':instruction.hex(),'meaning':f'candidate vertex processing flag {value:#x}'})
        records.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000','functions':functions,'instructions':facts})
    report={'binary_evidence':records,'confirmed':'Reference uses D3D9; creation code selects candidate VP flags and ORs0x4. Own legacy graphics lab uses D3D8 HAL/SWVP0x20, a different API/configuration.',
            'unknown':['Actual reference runtime x87 control word and other startup changes: reference EXE never executed.',
                       'Full renderer/shader/device-reset parity; these static checks do not prove pixel equivalence.']}
    (WS/'inventory/client455-graphics-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:455D3D9 creation/enumeration3functions and6instruction sites match both pinned PE.')


if __name__=='__main__':main()
