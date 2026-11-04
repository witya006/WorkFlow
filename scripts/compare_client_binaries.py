"""Stage and compare the two client binaries; never execute either input."""
import hashlib
import json
import shutil
import struct
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def pe(data):
    if len(data) < 64:
        raise ValueError('Truncated DOS header')
    offset = struct.unpack_from('<I', data, 0x3c)[0]
    if offset+24 > len(data):
        raise ValueError('Truncated PE header')
    if data[:2] != b'MZ' or data[offset:offset+4] != b'PE\0\0':
        raise ValueError('Not a PE input')
    machine, count = struct.unpack_from('<HH', data, offset+4)
    optional_size = struct.unpack_from('<H', data, offset+20)[0]
    magic = struct.unpack_from('<H', data, offset+24)[0]
    if machine != 0x14c or magic != 0x10b:
        raise ValueError('Expected PE32 x86')
    base = struct.unpack_from('<I', data, offset+24+28)[0]
    entry = struct.unpack_from('<I', data, offset+24+16)[0]
    sections = []
    if optional_size < 96 or offset+24+optional_size+40*count > len(data):
        raise ValueError('Truncated optional header or section table')
    for i in range(count):
        at = offset+24+optional_size+40*i
        name = data[at:at+8].rstrip(b'\0').decode('ascii', errors='replace')
        vsize, rva, size, raw = struct.unpack_from('<IIII', data, at+8)
        sections.append({'name': name, 'rva': rva, 'virtual_size': vsize, 'raw_offset': raw, 'raw_size': size})
    return {'architecture': 'x86', 'image_base': base, 'entry_rva': entry, 'sections': sections}


def main():
    paths = json.loads((WS / 'config/paths.json').read_text(encoding='utf-8'))
    root = Path(paths['client_455'])
    expected = {x['path']: x['sha256'] for x in json.loads((WS / 'inventory/reference-binaries.json').read_text(encoding='utf-8')) if x['root'] == 'client_455'}
    inputs = []
    for name, label in [('RF_Online.bin.2026-10-18_12-15-42.backup', 'reference-backup'), ('RF_Online.bin', 'current')]:
        src = root / name
        data = src.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected[name]:
            raise ValueError(f'Input changed since audit: {name}')
        dst = WS / 'work/client-reference' / label / 'RF_Online.bin'
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Preserving different working input: {dst}')
        if not dst.exists():
            shutil.copyfile(src, dst)
        if hashlib.sha256(dst.read_bytes()).hexdigest() != digest:
            raise ValueError('Copy verification failed')
        inputs.append({'label': label, 'original': str(src), 'copy': str(dst), 'sha256': digest, 'size': len(data), 'pe': pe(data)})
    before, after = [Path(x['copy']).read_bytes() for x in inputs]
    if len(before) != len(after):
        raise ValueError('This baseline comparison expects equal-sized inputs')
    runs = []
    for at, (a, b) in enumerate(zip(before, after)):
        if a != b:
            if runs and runs[-1][1] == at:
                runs[-1][1] += 1
            else:
                runs.append([at, at+1])
    changes = []
    for start, end in runs:
        section = next((s for s in inputs[0]['pe']['sections'] if s['raw_offset'] <= start < s['raw_offset']+s['raw_size']), None)
        rva = start-section['raw_offset']+section['rva'] if section else None
        changes.append({'file_offset': hex(start), 'length': end-start, 'section': section['name'] if section else None,
                        'rva': hex(rva) if rva is not None else None,
                        'backup_hex': before[start:end].hex(), 'current_hex': after[start:end].hex()})
    report = {'inputs': inputs, 'changed_bytes': sum(b-a for a, b in runs), 'change_ranges': changes,
              'shared_numeric_constant': {'file_offset': '0x6adf48', 'rva': '0x6af748',
                                          'backup_double': struct.unpack_from('<d', before, 0x6adf48)[0],
                                          'current_double': struct.unpack_from('<d', after, 0x6adf48)[0]},
              'interpretation': 'Byte differences only. Version provenance and semantics require further evidence; no input executed.'}
    (WS / 'inventory/client-binary-comparison.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'changed_bytes': report['changed_bytes'], 'ranges': len(changes), 'changes': changes[:12]}, indent=2))


if __name__ == '__main__':
    main()
