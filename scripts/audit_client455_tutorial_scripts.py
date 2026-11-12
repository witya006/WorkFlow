"""Pin the 455 SCP reader and independently walk every supplied client script.

This is a file-format audit. It does not certify execution of the 47 commands.
"""
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

from compare_client_binaries import WS
from build_client455_x87_math import read_va


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixed_size(selector):
    if selector < 4:
        return None
    if selector == 4:
        return 16
    if selector == 5 or 23 <= selector <= 26 or 40 <= selector <= 46:
        return 12
    if 6 <= selector <= 8 or 12 <= selector <= 18 or 27 <= selector <= 39:
        return 20
    if 9 <= selector <= 11:
        return 24
    if 19 <= selector <= 22:
        return 8
    raise ValueError(f'Unknown SCP selector {selector}')


def inspect(raw, visit=None):
    at = 0

    def take(size):
        nonlocal at
        if size < 0 or size > len(raw) - at:
            raise ValueError(f'Truncated SCP at {at}, requested {size}')
        result = raw[at:at + size]
        at += size
        return result

    def u8():
        return take(1)[0]

    def u16():
        return struct.unpack('<H', take(2))[0]

    def u32():
        return struct.unpack('<I', take(4))[0]

    count = u32()
    if count > (len(raw) - at) // 70:
        raise ValueError('SCP quest count exceeds input')
    types = Counter()
    canonical = bytearray(struct.pack('<I', count))
    quests = []
    messages = strings = string_bytes = mismatches = 0
    for quest_index in range(count):
        quest_id = u32()
        name = take(64)
        total = u16()
        canonical += struct.pack('<I', quest_id) + name + struct.pack('<H', total)
        quest_types = Counter()
        for _ in range(total):
            selector = u8()
            size = fixed_size(selector)
            if size is None:
                data_start = at
                data_type = u8()
                identifier = u16()  # QBI identifier, not its ordinal in the sequence.
                hint_id = u32()
                limits = take(3)  # Minimum level, maximum level, map.
                action, duration, display = u32(), u32(), u32()
                lines = u8()
                if visit is not None:
                    visit(quest_index, name.split(b'\0', 1)[0], selector, raw[data_start:at])
                canonical += struct.pack('<BBHI', selector, data_type, identifier, hint_id)
                canonical += limits + struct.pack('<IIIB', action, duration, display, lines)
                for _ in range(lines):
                    font = take(12)  # Serialized HSD_FONT, including its raw padding.
                    length = u16()
                    text = take(length)
                    canonical += font + struct.pack('<H', length) + text
                    string_bytes += length
                messages += 1
                strings += lines
            else:
                data = take(size)
                if visit is not None:
                    visit(quest_index, name.split(b'\0', 1)[0], selector, data)
                data_type = data[0]
                identifier = struct.unpack_from('<H', data, 2)[0]
                canonical += struct.pack('<BBH', selector, data_type, identifier) + data[1:2] + data[4:]
            mismatches += data_type != selector
            types[selector] += 1
            quest_types[selector] += 1
        quests.append({'id': quest_id, 'name_sha256': sha(name),
                       'instructions': total, 'selectors': dict(sorted(quest_types.items()))})
    return {'quests': quests, 'quest_count': count, 'instructions': sum(types.values()),
            'selectors': dict(sorted(types.items())), 'messages': messages,
            'strings': strings, 'string_bytes': string_bytes,
            'selector_data_type_mismatches': mismatches, 'parsed_bytes': at,
            'trailer_bytes': len(raw) - at,
            'semantic_sha256': sha(canonical)}


def main():
    evidence = WS / 'artifacts/client455-tutorial/scripts-reference.json'
    reference = json.loads(evidence.read_text())
    selection_path = WS / 'artifacts/client455-tutorial/script-selection.json'
    selection = json.loads(selection_path.read_text())
    asm_path = WS / 'artifacts/client455-tutorial/qbi-asm.json'
    asm = json.loads(asm_path.read_text())
    if len(asm['asm']['lines']) != asm['instruction_count'] or not asm['cursor']['done']:
        raise ValueError('SCP reader disassembly is incomplete')
    target = json.loads((WS / 'config/client-target.json').read_text())
    pins = []
    previous = None
    for folder, key in [('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]:
        binary = (WS / f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(binary) != target[key]['sha256']:
            raise ValueError('Changed pinned client')
        ranges = []
        for row in reference['ranges']['result'] + selection['ranges']['result']:
            if row['error'] or not row['fn']:
                raise ValueError('Missing reader function')
            fn = row['fn']
            addr, size = int(fn['addr'], 16), int(fn['size'], 16)
            ranges.append({'rva': hex(addr - 0x400000), 'bytes': size,
                           'sha256': sha(read_va(binary, addr, size))})
        if previous is not None and ranges != previous:
            raise ValueError('Reader contracts differ between pins')
        previous = ranges
        def string(addr):
            return read_va(binary, addr, 160).split(b'\0', 1)[0].decode('ascii')

        prefixes = [string(addr) for addr in [0xAAD860, 0xAAD85C, 0xAAD858]]
        suffixes = [string(addr) for addr in [0xAAD854, 0xAAD850, 0xAAD84C, 0xAAD848]]
        if prefixes != ['b', 'c', 'a'] or suffixes != ['w', 'r', 'f', 's']:
            raise ValueError('Unexpected board filename selectors')
        types = []
        for addr, ctor in reference['constructors'].items():
            vt = next(r for r in ctor['refs'] if r['name'].startswith('??_7'))
            vt_addr = int(vt['addr'], 16)
            col = struct.unpack('<I', read_va(binary, vt_addr - 4, 4))[0]
            td = struct.unpack('<I', read_va(binary, col + 12, 4))[0]
            types.append({'constructor_rva': hex(int(addr, 16) - 0x400000),
                          'vtable_rva': hex(vt_addr - 0x400000),
                          'type_descriptor_rva': hex(td - 0x400000), 'type_name': string(td + 8)})
        if pins and types != pins[0]['processor_types']:
            raise ValueError('QBI RTTI differs between pins')
        pins.append({'sha256': sha(binary), 'architecture': 'x86',
                     'image_base': '0x400000', 'ranges': ranges,
                     'processor_types': types, 'filename_prefixes': prefixes, 'filename_suffixes': suffixes})
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    inputs = []
    other_inputs = []
    aggregate = Counter()
    for path in sorted((root / 'DataTable').rglob('*')):
        if not path.is_file() or path.suffix.lower() != '.scp':
            continue
        raw = path.read_bytes()
        selected = len(path.stem) == 2 and path.stem[0].lower() in 'bca' and path.stem[1].lower() in 'wrfs'
        metadata = {'relative': path.relative_to(root).as_posix(), 'file': str(path),
                    'bytes': len(raw), 'sha256': sha(raw)}
        try:
            layout = inspect(raw)
        except ValueError as error:
            if selected:
                raise ValueError(f'{path}: {error}') from error
            other_inputs.append({**metadata, 'status': 'not accepted by 455 reader',
                                 'error': str(error), 'selected_by_board_formatter': False})
            continue
        if not selected:
            other_inputs.append({**metadata, 'status': 'parsed; runtime selection unproven',
                                 'layout': layout, 'selected_by_board_formatter': False})
            continue
        aggregate.update(layout['selectors'])
        inputs.append({**metadata, 'layout': layout})
    if not inputs:
        raise ValueError('No client scripts found')
    report = {'scope': '455 SCP wire reader only; command execution and full Tutorial are OPEN',
              'references': pins, 'raw_evidence': {'file': evidence.relative_to(WS).as_posix(),
                                                'sha256': sha(evidence.read_bytes())},
              'reader_asm': {'file': asm_path.relative_to(WS).as_posix(), 'sha256': sha(asm_path.read_bytes())},
              'selection_evidence': {'file': selection_path.relative_to(WS).as_posix(), 'sha256': sha(selection_path.read_bytes())},
              'script_sha256': sha(Path(__file__).read_bytes()), 'inputs': inputs, 'other_inputs': other_inputs,
              'selectors': dict(sorted(aggregate.items())),
              'fixed_payload_bytes': {str(i): fixed_size(i) for i in range(47)},
              'gaps': ['Full QBI execution and owned processor classes, Tutorial board/UI/Avatar/stages',
                       'Fixed record payload members beyond type/id are retained losslessly but not yet all named',
                       'Malformed inputs rejected atomically; target unchecked reads/partial mutation are not reproduced',
                       'No whole-client or online-authentication acceptance'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-tutorial-scripts-reference.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(inputs), 'quests': sum(r['layout']['quest_count'] for r in inputs),
                      'instructions': sum(r['layout']['instructions'] for r in inputs),
                      'selectors': sorted(aggregate),
                      'trailers': sum(r['layout']['trailer_bytes'] for r in inputs),
                      'other_inputs': [{'relative': r['relative'], 'status': r['status']} for r in other_inputs]}))


if __name__ == '__main__':
    main()
