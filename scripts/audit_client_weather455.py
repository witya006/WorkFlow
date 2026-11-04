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
            (0x90af71,bytes.fromhex('6808040000'),'read 1032-byte R3X payload'),
            (0xb39d8c,b'*ENVIRONMENT2\0','text second layer name'),
            (0xb39d78,b'*ENVIRONMENT_ID2\0','text second layer id'),
            (0x90b0da,bytes.fromhex('a3407f1501'),'R3X first environment id destination'),
            (0x90b0ff,bytes.fromhex('890d447f1501'),'R3X second environment id destination'),
            (0x8dbc13,bytes.fromhex('818dc804000000000100'),'night particle attribute0x10000'),
            (0xbf7348,struct.pack('<f',3),'initial day clock acceleration'),
            (0x8b12c0,bytes.fromhex('d9442404d91d4873bf00c3'),'clock rate setter preserves mutable initial rate'),
            (0x8f9b6c,bytes.fromhex('bd02000000'),'release both environment layers'),
            (0xb373b8,struct.pack('<d',.24),'strict lower time threshold'),
            (0xb373b0,struct.pack('<d',.83),'strict upper time threshold')]
        instructions=[]
        for va,wanted,meaning in checks:
            if read_va(data,va,len(wanted))!=wanted:
                raise ValueError(f'Weather instruction changed at {va:x}')
            instructions.append({'va':hex(va),'rva':hex(va-0x400000),'bytes':wanted.hex(),'meaning':meaning})
        functions=[]
        for name,va,size in [('material_text',0x90a4d0,0x9f6),('material_r3x',0x90aed0,0x28b),
                ('environment_load',0x8f8c90,0x187),('level_release',0x8f9ad0,0x14a),
                ('weather_draw',0x8cb0b0,0x93),('set_clock_hms',0x8b12e0,0xcc),
                ('clock_hms',0x8b13b0,0x75),('set_clock_fraction',0x8b1440,0x55),
                ('level_frame',0x8e7910,0xfc)]:
            functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,
                'sha256':hashlib.sha256(read_va(data,va,size)).hexdigest()})
        facts.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000',
            'function_va':'0x8cad00','function_rva':'0x4cad00','size':len(body),
            'body_sha256':hashlib.sha256(body).hexdigest(),'instructions':instructions,'related_functions':functions})
    report={'binary_evidence':facts,'scope':'Manual whole-function analysis plus reproducible instruction checks, not runtime weather validation',
        'confirmed':{'helper_owner_bsp_offset':744,'environment_particle_pointer_offsets':[96,100],
            'environment_layer_iterations':2,'interior_flag':4,'flagged_helper_stack_capacity':1024,
            'camera_test_position':'global inverse-view translation; not weather creation position offset by forward vector*50',
            'particle_type_1':'stop on any containing interior helper; else start only if stopped; attr0x10000 adds strict .24<getter<.83 stop condition',
            'particle_type_2':'retains fixed world bbox stop/restart rule',
            'lifecycle':'ClearVariable0x8F66B0 and ReleaseEntities0x8F9940 clear owner; level load0x8EAA93 binds owner'},
        'format':{'version':1.1,'reader_payload_bytes':1032,'legacy_payload_bytes':1024,
            'environment_name_offsets':[256,392],'environment_id_offsets':[384,520],'scene_flags_offset':524},
        'clock':'normalized day fraction: HMS setter/getter use 86400 seconds, mutable speed initialized3.0. Full lighting/time synchronization remains open.',
        'unknown':['complete particle455 behavior, graphics and clock numeric/environment equivalence',
            'all other possible consumers and full normal map runtime'],
        'implementation':'Source branch RF_CLIENT_455_WEATHER ports two layers, R3X/text fields, load/release/update/draw split, helper owner/interior and night flag. CPU native validation is separate; full weather/GPU/time acceptance remains open.'}
    (WS/'inventory/client455-weather-helper.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: weather config/lifecycle/interior/night and clock evidence verified in both pinned PE.')


if __name__=='__main__': main()
