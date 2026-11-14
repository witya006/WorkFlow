"""Bounded R3M reader checks; no extraction, build or client execution."""
import hashlib
import json
import struct
from pathlib import Path

from inspect_lobby_material_inputs import materials

ROOT = Path(__file__).resolve().parents[1]
VERSION = 0x3F8CCCCD


def fixture(layers=1):
    header = struct.pack('<IIif', layers, 1, -1, 1.0)
    name = b'panel\0'.ljust(128, b'\0')
    layer = struct.pack('<hiIII', 0, 2, 0, 0xFFFFFFFF, 0) + bytes(28)
    return struct.pack('<II', VERSION, 1) + header + name + layer * layers


def main():
    cases = []
    source = ROOT / 'work/client455-preview/runtime/Map/lobby/lobby.r3m'
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == '351d6312a210dacdef30ec36f2e7c50da1d95a16e9aca8d661a09633a43e6f0f'
    rows = materials(data)
    assert len(rows) == 100
    assert [row['index'] for row in rows] == list(range(100))
    for index, name, texture in ((30, 'wall_30', 1), (56, 'lobby_n_p_56', 3),
                                 (59, 'lobby_02_59', 14)):
        row = rows[index]
        assert row['name'] == name and row['basic_opaque']
        assert row['layers'][0]['texture_index'] == texture
    cases.append(dict(name='real_pinned_100_materials_and_3_mappings', passed=True))
    for count in (0, 1, 7):
        parsed = materials(fixture(count))
        assert len(parsed) == 1 and len(parsed[0]['layers']) == count
        assert parsed[0]['basic_opaque'] == (count == 1)
        cases.append(dict(name=f'valid_{count}_layers', passed=True))

    invalid = [
        ('empty_header', b'', 'Short R3M header'),
        ('short_header', bytes(7), 'Short R3M header'),
        ('wrong_version', struct.pack('<II', 0, 1), 'Unsupported R3M version/count'),
        ('count_zero', struct.pack('<II', VERSION, 0), 'Unsupported R3M version/count'),
        ('count_2049', struct.pack('<II', VERSION, 2049), 'Unsupported R3M version/count'),
        ('truncated_material', fixture()[:8 + 143], 'Truncated material header'),
        ('truncated_layer', fixture()[:-1], 'Invalid material layers'),
        ('eight_layers', fixture(8), 'Invalid material layers'),
        ('trailing_byte', fixture() + b'\0', 'R3M trailing bytes'),
    ]
    for name, payload, expected in invalid:
        try:
            materials(payload)
        except ValueError as error:
            assert str(error) == expected, (name, str(error))
        else:
            raise AssertionError(f'{name}: malformed input accepted')
        cases.append(dict(name=name, passed=True, rejection=expected))

    report = dict(passed=True, scope='R3M reader only; no PNG extraction or game run',
                  source=str(source), bytes=len(data), sha256=digest,
                  materials=len(rows), checks=len(cases), cases=cases)
    target = ROOT / 'inventory/client455-lobby-material-reader.json'
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, checks=len(cases), materials=len(rows), report=str(target))))


if __name__ == '__main__':
    main()
