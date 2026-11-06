"""Pin the QBI scheduler, shared state and message/wait processor contracts."""
import hashlib
import json
import struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = WS / 'artifacts/client455-tutorial/runtime-reference.json'
    evidence = json.loads(source.read_text())
    catalog = json.loads((WS / 'artifacts/client455-tutorial/runtime-vtables.json').read_text())
    scripts = json.loads((WS / 'inventory/client455-tutorial-scripts-reference.json').read_text())
    assemblies = []
    for row in evidence['asm']:
        data = json.loads((WS / row['file']).read_text())
        if len(data['asm']['lines']) != data['instruction_count'] or not data['cursor']['done']:
            raise ValueError('Incomplete QBI scheduler assembly')
        assemblies.append({'file': row['file'], 'sha256': sha(WS / row['file']),
                           'instructions': data['instruction_count']})
    pins = []
    for folder, pin in zip(['current', 'reference-backup'], scripts['references']):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        if sha(path) != pin['sha256']:
            raise ValueError('Changed455pin')
        binary = path.read_bytes()
        ranges = []
        for row in evidence['ranges']['result'] + catalog['extra_ranges']:
            if row['error']:
                raise ValueError('Missing QBI runtime function')
            fn = row['fn']; addr, size = int(fn['addr'], 16), int(fn['size'], 16)
            ranges.append({'rva': hex(addr - 0x400000), 'bytes': size,
                           'sha256': hashlib.sha256(read_va(binary, addr, size)).hexdigest()})
        tables = []
        for item in pin['processor_types']:
            addr = 0x400000 + int(item['vtable_rva'], 16)
            entries = struct.unpack('<6I', read_va(binary, addr, 24))
            tables.append({'rva': item['vtable_rva'], 'type_name': item['type_name'],
                           'entries_rva': [hex(v - 0x400000) for v in entries]})
            if read_va(binary, entries[0], 0x19) != read_va(binary, 0x42BFB0, 0x19) or \
               read_va(binary, entries[1], 0x19) != read_va(binary, 0x42BFD0, 0x19):
                raise ValueError('QBI flag/data getter layout differs')
        if read_va(binary, 0x42C110, 0x13) != read_va(binary, 0x42C050, 0x13):
            raise ValueError('WAIT finish is not the confirmed empty MESSAGE finish')
        if pins and (ranges != pins[0]['ranges'] or tables != pins[0]['vtables']):
            raise ValueError('QBI scheduler contracts differ between pins')
        pins.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000',
                     'ranges': ranges, 'vtables': tables})
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    inputs = [{'file': str(root / f'DataTable/ko-kr/{name}'), 'name': name,
               'sha256': sha(root / f'DataTable/ko-kr/{name}')}
              for name in ['bw.scp', 'cw.scp', 'ar.scp']]
    report = {'scope': 'QBI common scheduler and message/wait rules; real UI/Avatar host and remaining processors OPEN',
              'references': pins, 'raw_evidence': {'file': source.relative_to(WS).as_posix(), 'sha256': sha(source)},
              'vtable_evidence': {'file': 'artifacts/client455-tutorial/runtime-vtables.json',
                                  'sha256': sha(WS / 'artifacts/client455-tutorial/runtime-vtables.json')},
              'assemblies': assemblies, 'script_sha256': sha(Path(__file__)), 'inputs': inputs,
              'supported_selectors': list(range(6)), 'open_selectors': list(range(6, 47)),
              'facts': ['Start at most one new QBI per tick; process all begun unfinished records before next iterator',
                        'Bit4 bypasses update and finishes; bit2 set before virtual Finish',
                        'All started QBI share one timer; start captures clock and clears input to11 and owner52',
                        'Type16 preserves global cursor button; failed Start still resets other types cursor',
                        'Refresh resets quest ID/count/flags/iterator but retains processor-private state',
                        'Last record completion decides quest end; callback may unload the entire script',
                        'WAIT DWORD elapsed is unsigned and inclusive; condition values4..10 use exact field comparisons'],
              'gaps': ['Remaining41 selectors and production host/CTutorialBoard/briefing/Avatar/stages/world',
                       'Wait condition gameplay names and real getters; message display side effects not implemented in host',
                       'Owner52 meaning and remaining context fields, arbitrary callback invalidation/OOM/reload error domains',
                       'Wire pointer domains in fixed message records with dataType0..3 rejected; not equivalence',
                       'No full Tutorial/online authentication/whole455 acceptance'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-tutorial-runtime-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pinned_functions': len(pins[0]['ranges']), 'vtables': len(pins[0]['vtables']),
                      'complete_asm_functions': len(assemblies), 'supported_selectors': list(range(6))}))


if __name__ == '__main__':
    main()
