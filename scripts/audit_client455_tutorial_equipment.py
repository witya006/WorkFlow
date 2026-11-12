"""Audit lesson-five command operands against the pinned client data."""
import json
import struct
from collections import Counter
from pathlib import Path

from audit_client455_item_payloads import decode, item_tables
from audit_client455_tutorial_scripts import inspect, sha, WS


def main():
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455']) / 'DataTable'
    raw_items = (root / 'Item.edf').read_bytes()
    tables, _, _ = item_tables(decode(raw_items))
    codes = {}
    for kind in (6, 11, 18):
        table = tables[kind]
        codes[kind] = {}
        for row in range(table['count']):
            index, code = struct.unpack_from('<II', table['data'], row * table['stride'])
            if index < table['count']:
                codes[kind].setdefault(code, index)

    shapes, grants, cursors = Counter(), Counter(), Counter()
    unmatched = []
    names = {b'TutorialEquipment', b'iTutorialEquipment'}
    admitted = {0, 1, 4, 5, 13, 14, 19, 20, 21, 23, 24, 25, 26, 27, 29, 32, 35, 40}
    file_names = {race + role for race in 'bca' for role in 'wrfs'}
    for path in sorted(root.rglob('*.scp')):
        if path.stem.lower() not in file_names:
            continue
        granted = set()

        def visit(quest, name, selector, data):
            if quest != 4:
                return
            def require(condition):
                if not condition:
                    raise ValueError(f'{path}: unsupported lesson-five selector {selector}, {data.hex()}')
            require(name in names and selector in admitted and data[0] == selector)
            if selector in (19, 20, 21):
                require(data[6:8] == b'\0\0')
            if selector in (23, 24, 25, 26):
                require(data[6] in (3, 12))
            if selector == 27:
                require(data[6:10] == b'\xff' * 4 and data[14] == 1)
            if selector == 35:
                require(data[6] == 1)
            if selector == 40:
                kind = data[6]
                code = struct.unpack_from('<I', data, 8)[0]
                require(code in codes.get(kind, {}))
                grants[kind, code, codes[kind][code]] += 1
                granted.add(code)
            if selector == 32:
                window = data[15]
                address = struct.unpack_from('<I', data, 16)[0]
                require(data[14] == 0 and (window == 0 or (window == 90 and address in (3, 12))))
                if window == 0 and address != 0xffffffff and address not in granted:
                    unmatched.append({'script': path.relative_to(root).as_posix(),
                                      'command': struct.unpack_from('<H', data, 2)[0],
                                      'code': hex(address)})
                cursors[window] += 1

        layout = inspect(path.read_bytes(), visit)
        shapes[layout['quests'][4]['instructions']] += 1
    if not shapes:
        raise ValueError('No lesson-five scripts')
    print(json.dumps({
        'item_edf_sha256': sha(raw_items), 'scripts': sum(shapes.values()),
        'instruction_counts': dict(sorted(shapes.items())),
        'cursor_windows': dict(sorted(cursors.items())),
        'cursor_codes_without_prior_grant': unmatched,
        'grants': sum(grants.values()),
        'grant_rows': [{'category': kind, 'code': hex(code), 'index': index, 'count': count}
                       for (kind, code, index), count in sorted(grants.items())],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
