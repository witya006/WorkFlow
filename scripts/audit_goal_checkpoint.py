"""Capture clean engine builds and verify the requested engine/reference checkpoint.

Raw build evidence stays in artifacts/. No supplied executable is executed.
"""
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_sections(data):
    machine, count = struct.unpack_from('<HH', data)
    if machine != 0x14c or len(data) < 20+40*count:
        raise ValueError('Expected complete x86 COFF object')
    result = hashlib.sha256()
    for index in range(count):
        at = 20+40*index
        name = data[at:at+8]
        if name.startswith(b'.debug'):
            continue
        size, start, reloc = struct.unpack_from('<III', data, at+16)
        reloc_count = struct.unpack_from('<H', data, at+32)[0]
        flags = struct.unpack_from('<I', data, at+36)[0]
        if reloc_count == 0xffff:
            raise ValueError('Relocation overflow unsupported in this audit')
        if (start and start+size > len(data)) or reloc+10*reloc_count > len(data):
            raise ValueError('Truncated COFF payload')
        result.update(name+struct.pack('<II', size, flags))
        if start:
            result.update(data[start:start+size])
        result.update(data[reloc:reloc+10*reloc_count])
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', choices=['clean1', 'clean2'])
    args = parser.parse_args()
    state_path = WS/'inventory/goal-checkpoint.json'
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {'engine_builds': {}}
    folder = WS/'artifacts/goal-checkpoint'
    folder.mkdir(parents=True, exist_ok=True)
    if args.capture:
        path = WS/'inventory/client-build-result.json'
        report = json.loads(path.read_text(encoding='utf-8'))
        if report['build_exit'] or report['input_integrity_issues'] or report['errors'] or len(report['generated_objects']) != 58:
            raise ValueError('Engine build not verified successful')
        source = WS/report['library']['file']
        if digest(source) != report['library']['sha256']:
            raise ValueError('Engine archive differs from build report')
        records = {}
        for item in report['generated_objects']:
            obj = WS/item['file']
            if digest(obj) != item['sha256'] or item['coff_machine'] != '0x14c':
                raise ValueError('Engine object differs from build report')
            records[obj.name] = runtime_sections(obj.read_bytes())
        saved = folder/(args.capture+'.lib')
        shutil.copyfile(source, saved)
        shutil.copyfile(path, folder/(args.capture+'-result.json'))
        shutil.copyfile(WS/'artifacts/client-build/build.txt', folder/(args.capture+'-build.txt'))
        state['engine_builds'][args.capture] = {'build_exit': 0, 'checked_at_utc': report['checked_at_utc'],
            'objects_x86': len(records), 'input_integrity_issues': [],
            'archive': saved.relative_to(WS).as_posix(), 'archive_sha256': digest(saved),
            'build_log_sha256': digest(folder/(args.capture+'-build.txt')),
            'runtime_section_fingerprints': records}
    else:
        if set(state['engine_builds']) != {'clean1', 'clean2'}:
            raise ValueError('Two separately captured clean builds are required')
        one, two = state['engine_builds']['clean1'], state['engine_builds']['clean2']
        for name, record in state['engine_builds'].items():
            if digest(WS/record['archive']) != record['archive_sha256']:
                raise ValueError('Saved engine build archive changed')
            if digest(folder/(name+'-build.txt')) != record['build_log_sha256']:
                raise ValueError('Saved build log changed')
        state['same_runtime_sections_and_relocations'] = one['runtime_section_fingerprints'] == two['runtime_section_fingerprints']
        target = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
        comparison = json.loads((WS/'inventory/client-binary-comparison.json').read_text(encoding='utf-8'))
        for item in comparison['inputs']:
            if digest(Path(item['original'])) != item['sha256'] or digest(Path(item['copy'])) != item['sha256']:
                raise ValueError('Pinned binary input/copy changed')
            if item['pe']['architecture'] != 'x86' or item['pe']['image_base'] != 0x400000:
                raise ValueError('Unexpected binary architecture/base')
        current = next(x for x in comparison['inputs'] if x['label'] == 'current')
        if current['sha256'] != target['behavior_reference']['sha256']:
            raise ValueError('Target does not identify the verified current binary')
        state['reference_verified'] = {'sha256': current['sha256'], 'architecture': 'x86', 'image_base': '0x400000',
            'copies_and_originals_match': True, 'comparison_manifest_sha256': digest(WS/'inventory/client-binary-comparison.json'),
            'target_manifest_sha256': digest(WS/'config/client-target.json')}
        helpers = json.loads((WS/'inventory/helper-spt-verification.json').read_text(encoding='utf-8'))
        if helpers['passed'] != 140 or len(helpers['files']) != 140 or helpers['total_helpers'] != 97543:
            raise ValueError('First-format verification is incomplete')
        state['first_format_verified'] = {'files': helpers['passed'], 'helpers': helpers['total_helpers'],
            'manifest_sha256': digest(WS/'inventory/helper-spt-verification.json'), 'scope': 'Helper-only SPT subset'}
        state['requested_checkpoint'] = 'Engine/reference work complete; client build stage already started, RF_Online.bin not completed'
    state_path.write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8')
    print('Captured '+args.capture if args.capture else json.dumps({k:v for k,v in state.items() if k != 'engine_builds'}))


if __name__ == '__main__':
    main()
