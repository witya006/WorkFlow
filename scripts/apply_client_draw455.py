"""Apply explicitly selectable 455 draw arguments, separately from compiler fixes.

Verify both pinned x86 binaries first; keep the legacy call when the build option
is disabled. Never rewrite unexpected changes or normalize source encodings.
"""
import hashlib
import json
import struct
from pathlib import Path
from compare_client_binaries import WS, pe

EDITS = {
    'RF_Client/cresobject.cpp': (b'_GetCharIF()->DrawCharacter( m_pBone, m_vecPos, m_vecRot[1] );',
        b'_GetCharIF()->DrawCharacter( m_pBone, m_vecPos, m_vecRot[1], m_fScale, 0.0f );'),
    'RF_Client/character/npc/cnpc.cpp': (b'_GetCharIF()->DrawCharacter( m_pMesh, m_vecPos, m_vecRot[1] );',
        b'_GetCharIF()->DrawCharacter( m_pMesh, m_vecPos, m_vecRot[1], m_fScale, 0.0f );'),
}


def binary_evidence():
    target = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    facts = []
    for folder, role in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data = (WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != target[role]['sha256']:
            raise ValueError('Pinned client changed')
        image = pe(data)

        def check(va, wanted):
            rva = va-image['image_base']
            s = next(s for s in image['sections'] if s['rva'] <= rva < s['rva']+s['raw_size'])
            offset = s['raw_offset']+rva-s['rva']
            if data[offset:offset+len(wanted)] != wanted:
                raise ValueError(f'Draw evidence changed at {va:x}')
            return {'va':hex(va),'rva':hex(rva),'file_offset':hex(offset),'bytes':wanted.hex()}

        instructions = [check(0x45d421, bytes.fromhex('d9ee')),
            check(0x45d42a, bytes.fromhex('d980f0000000')),
            check(0x45d454,b'\xe8'+struct.pack('<i',0x92fe80-0x45d459)),
            check(0x7cd2e1,bytes.fromhex('d9ee')),
            check(0x7cd2e9,b'\xe8'+struct.pack('<i',0x40a210-0x7cd2ee)),
            check(0x40a21f,bytes.fromhex('d980f0000000')),
            check(0x7cd310,b'\xe8'+struct.pack('<i',0x92fe80-0x7cd315)),
            check(0xaabd9c,struct.pack('<I',0x45d280)),
            check(0xaa9394,struct.pack('<I',0x7cd2a0))]
        facts.append({'input':folder,'sha256':digest,'architecture':'x86','instructions':instructions})
    return facts


def patched(data, before, after):
    if data.count(before) != 1:
        raise ValueError('Draw call anchor is not unique')
    newline = b'\r\n' if b'\r\n' in data else b'\n'
    start = data.rfind(b'\n',0,data.index(before))+1
    end = data.index(b'\n',data.index(before))+1
    line = data[start:end]
    replacement = (b'#if defined(RF_CLIENT_455_DRAW_ARGUMENTS)'+newline+
        line.replace(before,after)+b'#else'+newline+line+b'#endif'+newline)
    return data[:start]+replacement+data[end:]


def main():
    facts = binary_evidence()
    paths = json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))
    source = Path(paths['legacy_source'])/'RF Client Side'
    pending = []
    for relative, (before,after) in EDITS.items():
        original = (source/relative).read_bytes()
        desired = patched(original,before,after)
        destination = WS/'work/client-build/source'/relative
        if destination.read_bytes() not in (original,desired):
            raise ValueError(f'Preserving unexpected edits: {destination}')
        pending.append((destination,original,desired))
    report = []
    for destination,original,desired in pending:
        if destination.read_bytes() != desired:
            destination.write_bytes(desired)
        digest = hashlib.sha256(original).hexdigest()
        report.append({'file':destination.relative_to(WS).as_posix(),'original_sha256':digest,
            'input_sha256':digest,'patched_sha256':hashlib.sha256(desired).hexdigest(),
            'build_option':'RF_CLIENT_455_DRAW_ARGUMENTS','legacy_branch_preserved':True,
            'reason':'455 passes object m_fScale and zero scroll; no invented legacy default arguments.',
            'binary_evidence':facts})
    (WS/'inventory/client-behavior-patches.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: two byte-preserving, selectable 455 draw argument patches; both pinned PEs checked.')


if __name__=='__main__':
    main()
