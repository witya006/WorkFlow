"""Pin statically inspected 455 weather/helper consumer; do not execute inputs."""
import hashlib
import json
import struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    facts=[]
    weather_body=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']: raise ValueError('Pinned weather input changed')
        body=read_va(data,0x8cad00,0x3a7)
        if weather_body is not None and body!=weather_body: raise ValueError('Weather bodies differ between pinned inputs')
        weather_body=body
        checks=[(0x8cad68,bytes.fromhex('8b8de8020000'),'read BSP helper owner at +744'),
            (0x8cad78,bytes.fromhex('6a04'),'interior mask 4'),
            (0x8cada7,b'\xe8'+struct.pack('<i',0x90bb90-0x8cadac),'helper flag list'),
            (0x8cafdd,bytes.fromhex('8b8de8020000'),'same owner for bbox query'),
            (0x8cafe4,b'\xe8'+struct.pack('<i',0x90ba90-0x8cafe9),'helper bbox contains camera'),
            (0x8cb046,bytes.fromhex('6a00'),'stop state'),
            (0x8cb04e,bytes.fromhex('6a01'),'start state'),
            (0x8cb052,b'\xe8'+struct.pack('<i',0x8e0220-0x8cb057),'apply particle state'),
            (0xb373b8,struct.pack('<d',.24),'strict lower time threshold'),
            (0xb373b0,struct.pack('<d',.83),'strict upper time threshold')]
        instructions=[]
        for va,wanted,meaning in checks:
            if read_va(data,va,len(wanted))!=wanted:
                raise ValueError(f'Weather instruction changed at {va:x}')
            instructions.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':wanted.hex(),'meaning':meaning})
        facts.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000',
            'function_va':'0x8cad00','function_rva':'0x4cad00','size':len(body),
            'body_sha256':hashlib.sha256(body).hexdigest(),'instructions':instructions})
    report={'binary_evidence':facts,'scope':'Manual whole-function analysis plus reproducible instruction checks, not runtime weather validation',
        'confirmed':{'helper_owner_bsp_offset':744,'environment_particle_pointer_offsets':[96,100],
            'environment_layer_iterations':2,'interior_flag':4,'flagged_helper_stack_capacity':1024,
            'camera_test_position':'global inverse-view translation; not weather creation position offset by forward vector*50',
            'particle_type_1':'stop on any containing interior helper; else start only if stopped; attr0x10000 adds strict .24<getter<.83 stop condition',
            'particle_type_2':'retains fixed world bbox stop/restart rule',
            'lifecycle':'ClearVariable0x8F66B0 and ReleaseEntities0x8F9940 clear owner; level load0x8EAA93 binds owner'},
        'unknown':['meaning of time getter0x8B1430 beyond returning float at0x1154DEC',
            'complete two-layer environment configuration/parser/lifecycle and particle changes',
            'all other possible consumers and full normal map runtime'],
        'implementation':'Not yet ported; legacy source has one environment particle and no helper-owner binding. Do not copy 455 object offsets into the old CBsp layout.'}
    (WS/'inventory/client455-weather-helper.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: weather/interior helper consumer instructions verified in both pinned PE; implementation remains open.')


if __name__=='__main__': main()
