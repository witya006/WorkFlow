"""Inspect CodeView type record kinds in a COFF archive; never load its code."""
import collections
import argparse
import hashlib
import json
import struct
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--extract', action='store_true')
    args = parser.parse_args()
    path = WS / 'work/client-build/source/RF_Client/CharacterMR.lib'
    data = path.read_bytes()
    if not data.startswith(b'!<arch>\n'):
        raise ValueError('Not an archive')
    pos = 8
    objects = []
    while pos < len(data):
        header = data[pos:pos+60]
        if len(header) != 60 or header[-2:] != b'`\n':
            raise ValueError('Malformed archive member')
        length = int(header[48:58])
        content = data[pos+60:pos+60+length]
        if len(content) != length:
            raise ValueError('Truncated archive member')
        if len(content) >= 20 and content[:2] == b'L\x01':
            machine, count = struct.unpack_from('<HH', content)
            optional = struct.unpack_from('<H', content, 16)[0]
            record = {'member': header[:16].decode('ascii').strip(), 'machine': hex(machine), 'type_sections': []}
            record['sha256'] = hashlib.sha256(content).hexdigest()
            if args.extract:
                output = WS / 'work/character-reverse' / f'member_{len(objects)+1:02d}.obj'
                output.parent.mkdir(parents=True, exist_ok=True)
                if output.exists() and output.read_bytes() != content:
                    raise ValueError(f'Preserving different working object: {output}')
                output.write_bytes(content)
                record['working_object'] = output.relative_to(WS).as_posix()
            for i in range(count):
                at = 20+optional+40*i
                section = content[at:at+8].rstrip(b'\0')
                size, raw = struct.unpack_from('<II', content, at+16)
                if section == b'.debug$T':
                    types = content[raw:raw+size]
                    signature = struct.unpack_from('<I', types)[0]
                    cursor = 4
                    kinds = collections.Counter()
                    strings = []
                    while cursor+4 <= len(types):
                        reclen, kind = struct.unpack_from('<HH', types, cursor)
                        if reclen < 2 or cursor+2+reclen > len(types):
                            raise ValueError('Bad CodeView type record')
                        kinds[hex(kind)] += 1
                        body = types[cursor+4:cursor+2+reclen]
                        if kind in (0x0016, 0x1005, 0x1509, 0x1515):
                            strings.append({'kind': hex(kind), 'hex': body.hex()})
                        cursor += 2+reclen
                    record['type_sections'].append({'size': size, 'signature': signature, 'record_kinds': dict(kinds), 'external_records': strings})
            objects.append(record)
        pos += 60+length+(length%2)
    report = {'file': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'architecture': 'COFF x86',
              'rva': None, 'objects': objects}
    (WS / 'inventory/character-codeview.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
