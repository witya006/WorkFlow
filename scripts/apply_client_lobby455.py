"""Select the confirmed 455 connection-success -> lobby transition.

Retains the legacy CheckFiles block in the unselected branch; does not provide a
dummy CheckFiles or enable _DEVELOPER_. Other file checks are outside this finding.
"""
import hashlib
import json
import struct
from pathlib import Path
from compare_client_binaries import WS,pe
from apply_client_draw455 import merge_behavior_manifest
from apply_client_port_patches import PATCHES


def binary_evidence():
    pinned = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    facts = []
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data = (WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != pinned[key]['sha256']:
            raise ValueError('Pinned client changed')
        image = pe(data)

        def check(va,wanted):
            rva = va-image['image_base']
            section = next(s for s in image['sections'] if s['rva']<=rva<s['rva']+s['raw_size'])
            at = section['raw_offset']+rva-section['rva']
            if data[at:at+len(wanted)] != wanted:
                raise ValueError(f'Lobby transition evidence changed at {va:x}')
            return {'va':hex(va),'rva':hex(rva),'file_offset':hex(at),'bytes':wanted.hex()}

        # Successful connection state -> unconditional jump -> lobby load.
        checks = [check(0x53fdc0,b'\xe8'+struct.pack('<i',0x539b90-0x53fdc5)),
            check(0x53fdc5,bytes.fromhex('85c07402eb60')),
            check(0x53fe2b,b'\x68'+struct.pack('<I',0xab0264)+b'\x8b\x0d'+struct.pack('<I',0x1028aac)+b'\xe8'+struct.pack('<i',0x7c8600-0x53fe3b)),
            check(0xab0264,b'.\\map\\lobby\\lobby.BSP\0'),
            check(0x53fe45,b'\xe8'+struct.pack('<i',0x8d2070-0x53fe4a))]
        facts.append({'input':folder,'sha256':digest,'architecture':'x86','instructions':checks,
            'scope':'This success edge enters lobby loading directly; no general claim about 455 file verification elsewhere.'})
    return facts


def main():
    evidence = binary_evidence()
    paths = json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    relative = 'RF_Client/gameprogress/cgp_login.cpp'
    original = (Path(paths['legacy_source'])/'RF Client Side'/relative).read_bytes()
    base = original
    for before,after in PATCHES[relative]:
        if base.count(before) != 1:
            raise ValueError('Compiler patch anchor changed')
        base = base.replace(before,after,1)
    destination = WS/'work/client-build/source'/relative
    key = destination.relative_to(WS).as_posix()
    compiler = next(x for x in json.loads((WS/'inventory/client-source-patches.json').read_text(encoding='utf-8')) if x['file']==key)
    if hashlib.sha256(base).hexdigest()!=compiler['patched_sha256']:
        raise ValueError('Compiler patch chain changed')
    call = base.index(b'char *check = CheckFiles();')
    start = base.rfind(b'#ifndef _DEVELOPER_',0,call)
    end = base.index(b'#endif',call)+len(b'#endif')
    block = base[start:end]
    if start<0 or block.count(b'CheckFiles();')!=1 or block.count(b'#ifndef')!=1:
        raise ValueError('Unexpected legacy verification block')
    nl = b'\r\n' if b'\r\n' in original else b'\n'
    selected = (b'#if !defined(RF_CLIENT_455_LOBBY_TRANSITION)'+nl+block+nl+b'#endif')
    desired = base[:start]+selected+base[end:]
    current = destination.read_bytes()
    if current not in (original,base,desired):
        raise ValueError('Preserving unexpected login source changes')
    if current!=desired:
        destination.write_bytes(desired)
    merge_behavior_manifest([{'file':key,'original_sha256':hashlib.sha256(original).hexdigest(),
        'input_sha256':hashlib.sha256(base).hexdigest(),'patched_sha256':hashlib.sha256(desired).hexdigest(),
        'build_option':'RF_CLIENT_455_LOBBY_TRANSITION','legacy_branch_preserved':True,
        'reason':'455 success edge reaches lobby directly. Retain original CheckFiles block outside selected reference branch; no dummy return or _DEVELOPER_ change.',
        'binary_evidence':evidence}])
    print('PASS: confirmed 455 success-to-lobby edge selected separately; legacy CheckFiles branch preserved.')


if __name__=='__main__':
    main()
