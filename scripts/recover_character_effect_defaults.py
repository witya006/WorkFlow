"""Verify call-site evidence for the two legacy mesh-effect default arguments.

Function correspondence is a structural inference, documented in research/.
Immediate arguments and call destinations are checked directly in both pinned PEs.
"""
import hashlib
import json
import struct
from compare_client_binaries import WS, pe


def verify_default_evidence():
    target = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    evidence = []
    for label, role in [('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]:
        data = (WS/f'work/client-reference/{label}/RF_Online.bin').read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != target[role]['sha256']:
            raise ValueError('Pinned client evidence changed')
        image = pe(data)

        def at(va, size):
            rva = va-image['image_base']
            section = next(s for s in image['sections'] if s['rva'] <= rva < s['rva']+s['raw_size'])
            offset = section['raw_offset']+rva-section['rva']
            result = data[offset:offset+size]
            if len(result) != size:
                raise ValueError('Truncated evidence instruction')
            return offset, result

        for name, push, call, destination in [
                ('SetMeshEffect', 0x46c6ad, 0x46c6e4, 0x929e70),
                ('IsHaveMeshEffect', 0x46c8c6, 0x46c8da, 0x927b80)]:
            offset, value = at(push, 2)
            call_offset, instruction = at(call, 5)
            if value != b'\x6a\x00' or instruction[0] != 0xe8:
                raise ValueError('Default-argument/call instruction changed')
            if call+5+struct.unpack_from('<i', instruction, 1)[0] != destination:
                raise ValueError('Effect call destination changed')
            evidence.append({'input': label, 'sha256': digest, 'architecture': 'x86',
                'inferred_legacy_api': name, 'default_argument': 0,
                'push_va': hex(push), 'push_rva': hex(push-image['image_base']),
                'push_file_offset': hex(offset), 'push_bytes': value.hex(),
                'call_va': hex(call), 'call_rva': hex(call-image['image_base']),
                'call_file_offset': hex(call_offset), 'call_bytes': instruction.hex(),
                'destination_va': hex(destination), 'destination_rva': hex(destination-image['image_base'])})
    return evidence


def main():
    report = {'facts': verify_default_evidence(),
        'correspondence': 'Structural inference from legacy CMeshItem::Render_RenderWithEffect and 455 caller 0x46c470; not symbolic identification',
        'scope': 'Reconstruct two missing legacy default arguments; no claim of complete effect behavior parity'}
    (WS/'inventory/character-effect-defaults.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('PASS: two zero arguments and call targets checked in both pinned x86 client binaries.')


if __name__ == '__main__':
    main()
