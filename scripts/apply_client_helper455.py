"""Select three instruction-confirmed helper-loader changes without recoding inputs."""
import hashlib
import json
import struct
from pathlib import Path
from compare_client_binaries import WS, pe
from apply_client_draw455 import merge_behavior_manifest


def binary_evidence():
    target = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    results = []
    for folder, role in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data = (WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != target[role]['sha256']:
            raise ValueError('Pinned helper reference changed')
        image = pe(data)

        def read(va, size):
            rva = va-image['image_base']
            s = next(s for s in image['sections'] if s['rva']<=rva<s['rva']+s['raw_size'])
            at = s['raw_offset']+rva-s['rva']
            if at+size>s['raw_offset']+s['raw_size']:
                raise ValueError('Helper evidence crosses stored section')
            return data[at:at+size], at

        def check(va, wanted):
            raw, at = read(va,len(wanted))
            if raw != wanted:
                raise ValueError(f'Helper evidence changed at {va:x}')
            return {'va':hex(va),'rva':hex(va-image['image_base']),
                    'file_offset':hex(at),'bytes':wanted.hex()}

        whole, _ = read(0x90bbf0,0x526)
        if hashlib.sha256(whole).hexdigest()!='a8c404bd7b22e72091b8f34453cb224ad11f14d0ab71074bcc19618051df27a4':
            raise ValueError('Complete pinned helper-loader body changed')
        checks = [check(0x90bc23,bytes.fromhex('8945040f84d1040000')),
            check(0x90bcc0,bytes.fromhex('8d54241452e8e9c60f00')),
            check(0x90bef2,bytes.fromhex('834c082004')),
            check(0x90c088,bytes.fromhex('3bc80f8230fcffff')),
            check(0xb39f08,b'-interior\0'),check(0xb38568,b'EXT.spt\0'),
            check(0x8eaa7f,bytes.fromhex('8db300020000508bce')+b'\xe8'+struct.pack('<i',0x90bbf0-0x8eaa8d))]
        results.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000',
            'loader_va':'0x90bbf0','loader_rva':'0x50bbf0','loader_size':len(whole),
            'loader_sha256':hashlib.sha256(whole).hexdigest(),'instructions':checks})
    return results


def edit(relative, edits, evidence):
    paths = json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    original = (Path(paths['legacy_source'])/'R3Engine/R3Engine'/relative).read_bytes()
    nl = b'\r\n' if b'\r\n' in original else b'\n'
    desired = original
    for before,after in edits:
        before,after = before.replace(b'\n',nl),after.replace(b'\n',nl)
        if desired.count(before)!=1:
            raise ValueError(f'Nonunique helper anchor: {relative}')
        desired = desired.replace(before,after,1)
    destination = WS/'work/client-build/source/R3Engine'/relative
    if destination.read_bytes() not in (original,desired):
        raise ValueError(f'Preserving unexpected helper source: {destination}')
    if destination.read_bytes()!=desired:
        destination.write_bytes(desired)
    return {'file':destination.relative_to(WS).as_posix(),
        'original_sha256':hashlib.sha256(original).hexdigest(),
        'input_sha256':hashlib.sha256(original).hexdigest(),
        'patched_sha256':hashlib.sha256(desired).hexdigest(),
        'build_option':'RF_CLIENT_455_HELPER_LOADER','legacy_branch_preserved':True,
        'reason':'455 resets count on missing input, lowercases every next-record token, and supports interior flag 4. Other legacy parser behavior remains.',
        'binary_evidence':evidence}


def main():
    evidence = binary_evidence()
    changes = [edit('2ndclass/extdummy.cpp',[
        (b'\tif(( fp =fopen( name,"rt" ))==NULL)',
         b'#if defined(RF_CLIENT_455_HELPER_LOADER)\n\tfp = fopen(name,"rt");\n\tmNum = 0;\n\tif (fp == NULL)\n#else\n\tif(( fp =fopen( name,"rt" ))==NULL)\n#endif'),
        (b'\t\tstrlwr(hole);\n_EXT_DUMMY_RELOAD:',
         b'#if defined(RF_CLIENT_455_HELPER_LOADER)\n_EXT_DUMMY_RELOAD:\n\t\tstrlwr(hole);\n#else\n\t\tstrlwr(hole);\n_EXT_DUMMY_RELOAD:\n#endif'),
        (b'\t\t\t\tif (!strcmp(hole,"-music"))\n\t\t\t\t\tmDummy[mNum].mFlag |= _DUMMY_FLAG_MUSIC;',
         b'\t\t\t\tif (!strcmp(hole,"-music"))\n\t\t\t\t\tmDummy[mNum].mFlag |= _DUMMY_FLAG_MUSIC;\n#if defined(RF_CLIENT_455_HELPER_LOADER)\n\t\t\t\tif (!strcmp(hole,"-interior"))\n\t\t\t\t\tmDummy[mNum].mFlag |= _DUMMY_FLAG_INTERIOR;\n#endif')],evidence),
        edit('2ndclass/extdummy.h',[(b'#define _DUMMY_FLAG_MUSIC',
             b'#if defined(RF_CLIENT_455_HELPER_LOADER)\n#define _DUMMY_FLAG_INTERIOR 0x4\n#endif\n\n#define _DUMMY_FLAG_MUSIC')],evidence)]
    merge_behavior_manifest(changes)
    print('PASS: 455 helper-loader count, per-record lowercase and interior changes; legacy branch retained.')


if __name__=='__main__':
    main()
