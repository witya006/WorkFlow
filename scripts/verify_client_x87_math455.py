"""Check actual linked math instructions and global wrapper edges without executing PE."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va,FUNCTIONS


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--lab',action='store_true')
    args=cli.parse_args()
    mode='lab' if args.lab else 'normal'
    folder='build-helper-lab' if args.lab else 'build-character-diagnostic'
    build=WS/'work/client-build'/folder
    result=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    if result['build_exit'] or result['unresolved_symbols'] or result['build_settings'].get('RF_CLIENT_455_X87_MATH')!='ON':
        raise ValueError('Successful math-enabled client build required')
    data=(build/'Release/RF_Online.bin').read_bytes()
    if pe(data)['image_base']!=0x400000: raise ValueError('Unexpected client base')
    mapping=(build/'RF_Online-Release.map').read_bytes()
    symbols={}
    for line in mapping.decode('ascii',errors='replace').splitlines():
        match=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line)
        if match:
            if match[1] not in {'_RF455_MatrixInvert','_RF455_Vector3fTransform','_RF455_AffineEpsilon'} and not match[1].startswith(('?MatrixInvert@@','?Vector3fTransform@@')):
                continue
            if match[1] in symbols and symbols[match[1]]!=int(match[2],16):
                raise ValueError('Duplicate link symbol addresses')
            symbols[match[1]]=int(match[2],16)
    proof=json.loads((WS/'inventory/client455-x87-math.json').read_text(encoding='utf-8'))
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    reference=(WS/'work/client-reference/current/RF_Online.bin').read_bytes()
    if hashlib.sha256(reference).hexdigest()!=target['behavior_reference']['sha256']:
        raise ValueError('Pinned current math reference changed')
    epsilon=symbols['_RF455_AffineEpsilon']
    if read_va(data,epsilon,4)!=read_va(reference,0xab0d60,4): raise ValueError('Linked epsilon changed')
    functions=[]
    for name,reference_va,size in FUNCTIONS:
        address=symbols[name]
        wanted=bytearray(read_va(reference,reference_va,size))
        actual=read_va(data,address,size)
        if name=='_RF455_MatrixInvert': wanted[0x21:0x25]=struct.pack('<I',epsilon)
        if actual!=wanted: raise ValueError(f'Linked math instructions differ: {name}')
        prefix='?MatrixInvert@@' if name=='_RF455_MatrixInvert' else '?Vector3fTransform@@'
        wrappers=[(symbol,va) for symbol,va in symbols.items() if symbol.startswith(prefix)]
        if len(wrappers)!=1: raise ValueError(f'Missing/ambiguous global wrapper: {prefix}')
        wrapper,wrapper_va=wrappers[0]
        edge=read_va(data,wrapper_va,5)
        kind='tail-jump'
        call_offset=0
        if edge==bytes.fromhex('558bec5de9'):
            edge=read_va(data,wrapper_va,9)
            call_offset=4
            kind='balanced-frame-tail-jump'
        elif edge[0]!=0xe9:
            prefix=bytes.fromhex('558bec8b450c508b4d0851') if name=='_RF455_MatrixInvert' else bytes.fromhex('558bec8b4510508b4d0c518b550852')
            suffix=bytes.fromhex('83c4085dc3') if name=='_RF455_MatrixInvert' else bytes.fromhex('83c40c5dc3')
            edge=read_va(data,wrapper_va,len(prefix)+5+len(suffix))
            if edge[:len(prefix)]!=prefix or edge[len(prefix)]!=0xe8 or edge[-len(suffix):]!=suffix:
                raise ValueError(f'Global math wrapper has unexpected instructions: {wrapper}')
            call_offset=len(prefix)
            kind='integer-only-forward-call'
        destination=wrapper_va+call_offset+5+struct.unpack_from('<i',edge,call_offset+1)[0]
        thunks=[]
        if destination!=address:
            thunk=read_va(data,destination,5)
            if thunk[0]!=0xe9:
                raise ValueError(f'Unexpected forwarding thunk at {destination:#x} for {wrapper}')
            thunks.append({'va':hex(destination),'rva':hex(destination-0x400000),'bytes':thunk.hex()})
            destination+=5+struct.unpack_from('<i',thunk,1)[0]
        if destination!=address:
            raise ValueError(f'Global math wrapper selects {destination:#x}, expected {address:#x}: {wrapper}')
        functions.append({'symbol':name,'va':hex(address),'rva':hex(address-0x400000),'size':size,
            'linked_sha256':hashlib.sha256(actual).hexdigest(),'reference_va':hex(reference_va),
            'reference_rva':hex(reference_va-0x400000),'instruction_identity':True,
            'wrapper':wrapper,'wrapper_va':hex(wrapper_va),'wrapper_rva':hex(wrapper_va-0x400000),
            'wrapper_kind':kind,'wrapper_edge':edge.hex(),'linker_thunks':thunks})
    path=WS/'inventory/client455-x87-link.json'
    report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    report[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),
        'sha256':hashlib.sha256(data).hexdigest(),'architecture':'x86','image_base':'0x400000',
        'map_sha256':hashlib.sha256(mapping).hexdigest(),'math_library_sha256':proof['library_sha256'],
        'functions':functions,'executed_by_this_check':False,
        'limits':'Two exact linked instruction sequences and integer-only global wrapper bindings; other engine functions and normal game startup remain outside this check.'}
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {mode} client links both exact 455 math sequences and both global wrapper bindings.')


if __name__=='__main__': main()
