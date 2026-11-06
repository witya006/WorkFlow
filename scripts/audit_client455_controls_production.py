"""Compare current own PE with070 before choosing unchanged-code regressions."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_normal_link_evidence import validate_normal_link


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    baseline = '6173adf'
    def prior(name):
        return json.loads(subprocess.check_output(['git', '-c', 'safe.directory=' + str(WS), 'show', baseline + ':inventory/' + name + '.json'], cwd=WS))
    old_link = prior('client455-normal-link')
    old_start = prior('client455-startup-native')
    old_path = WS / old_start['staged_executable']
    old = old_path.read_bytes()
    current = json.loads((WS / 'inventory/client455-normal-link.json').read_text())
    validate_normal_link(current)
    new_path = WS / current['executable']['file']
    new = new_path.read_bytes()
    if sha(old) != old_link['executable']['sha256']:
        raise ValueError('Changed own070baseline')
    def layout(raw):
        nt, = struct.unpack_from('<I', raw, 60)
        count, = struct.unpack_from('<H', raw, nt + 6)
        optional_size, = struct.unpack_from('<H', raw, nt + 20)
        at = nt + 24 + optional_size
        sections = []
        for index in range(count):
            row = at + 40 * index
            virtual_size, rva, size, offset = struct.unpack_from('<4I', raw, row + 8)
            sections.append({'name': raw[row:row + 8].split(b'\0')[0].decode(), 'rva': rva, 'size': size, 'offset': offset})
        debug_rva, debug_size = struct.unpack_from('<II', raw, nt + 24 + 96 + 6 * 8)
        debug = []
        for section in sections:
            if section['rva'] <= debug_rva < section['rva'] + section['size']:
                debug_at = section['offset'] + debug_rva - section['rva']
                for index in range(debug_size // 28):
                    row = debug_at + 28 * index
                    kind, size, _, offset = struct.unpack_from('<4I', raw, row + 12)
                    debug.append({'directory_offset': row, 'type': kind, 'data_offset': offset, 'data_bytes': size})
        return {'timestamp_offset': nt + 8, 'sections': sections, 'debug': debug}
    old_layout, new_layout = layout(old), layout(new)
    timestamp_offsets = [new_layout['timestamp_offset']] + [row['directory_offset'] + 4 for row in new_layout['debug']]
    old_runtime, new_runtime = bytearray(old), bytearray(new)
    for offset in timestamp_offsets:
        old_runtime[offset:offset + 4] = b'\0' * 4
        new_runtime[offset:offset + 4] = b'\0' * 4
    differences = []
    for index, (left, right) in enumerate(zip(old, new)):
        if left != right:
            if differences and differences[-1]['offset'] + differences[-1]['bytes'] == index:
                differences[-1]['bytes'] += 1
            else:
                differences.append({'offset': index, 'bytes': 1})
    report = {'scope': 'Read-only own PE metadata/runtime comparison;not455equivalence', 'baseline_commit': baseline,
              'baseline': {'file': old_path.relative_to(WS).as_posix(), 'sha256': sha(old)}, 'current': current['executable'],
              'same_size': len(old) == len(new), 'same_layout': old_layout == new_layout, 'layout': new_layout,
              'timestamp_metadata_offsets': timestamp_offsets, 'same_runtime_bytes_ignoring_link_timestamps': old_runtime == new_runtime,
              'normalized_runtime_sha256': {'old': sha(old_runtime), 'new': sha(new_runtime)},
              'differences': [{**row, 'old': old[row['offset']:row['offset'] + row['bytes']].hex(), 'new': new[row['offset']:row['offset'] + row['bytes']].hex()} for row in differences],
              'sections': [{'name': row['name'], 'old_sha256': sha(old[row['offset']:row['offset'] + row['size']]),
                            'new_sha256': sha(new[row['offset']:row['offset'] + row['size']])} for row in new_layout['sections']],
              'normal_link_sha256': sha((WS / 'inventory/client455-normal-link.json').read_bytes()),
              'script_sha256': sha(Path(__file__).read_bytes()), 'input_exe_executed': False, 'server_modified': False}
    (WS / 'inventory/client455-briefing-controls-production.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'same_size': report['same_size'], 'same_layout': report['same_layout'], 'runtime_equal_after_timestamp_mask': old_runtime == new_runtime, 'differences': report['differences'], 'changed_sections': [row['name'] for row in report['sections'] if row['old_sha256'] != row['new_sha256']]}))


if __name__ == '__main__':
    main()
