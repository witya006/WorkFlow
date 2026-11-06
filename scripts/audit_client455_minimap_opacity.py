"""Pin the real minimap opacity control,its owner and resource geometry."""
import hashlib
import json
import struct
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sprite_geometry(path, requests):
    raw, at = path.read_bytes(), 8
    version, actions = struct.unpack_from('<II', raw)
    if version != 0x3f8ccccd:
        raise ValueError('Unexpected sprite version')
    frames, counts = {}, []
    for action in range(actions):
        count, = struct.unpack_from('<I', raw, at)
        at += 4
        counts.append(count)
        for frame in range(count):
            fmt, width, height, tw, th, size = struct.unpack_from('<6I', raw, at)
            at += 24 + size
            if at > len(raw):
                raise ValueError('Truncated sprite frame')
            if (action, frame) in requests:
                frames[f'{action}:{frame}'] = {'width': width, 'height': height, 'texture_width': tw, 'texture_height': th, 'format': fmt}
    if at != len(raw):
        raise ValueError('Trailing sprite data')
    return {'frame_counts': counts, 'requested': frames}


def main():
    root = WS / 'artifacts/client455-tutorial'
    names = ['minimap-initial067', 'minimap-helpers067', 'minimap-more067', 'minimap-bindings067',
             'minimap-opacity067', 'minimap-accessors067', 'minimap-opacity-asm067', 'minimap-ranges067', 'minimap-drawing067']
    evidence = []
    for name in names:
        path = root / (name + '.json')
        body = json.loads(path.read_text())
        assembly = body.get('assemblies', []) if isinstance(body, dict) else body
        evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path), 'assemblies': list(assembly_rows(assembly))})
    ranges = json.loads((root / 'minimap-ranges067.json').read_text())['ranges']['result']
    ranges += json.loads((root / 'minimap-drawing067.json').read_text())['ranges']['result']
    pins, target = [], json.loads((WS / 'config/client-target.json').read_text())
    for folder, pin in [('current', target['behavior_reference']), ('reference-backup', target['secondary_reference'])]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256'] or pe(raw)['architecture'] != 'x86':
            raise ValueError('Changed pinned455 binary')
        functions = []
        for row in ranges:
            if row['error']:
                raise ValueError('Missing opacity function')
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            functions.append({'rva': hex(address - 0x400000), 'bytes': size, 'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()})
        data = [{'rva': hex(address - 0x400000), 'bytes': size, 'role': role,
                 'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()}
                for address, size, role in [(0xAE4904, 4, 'minimap scroll observer'), (0xAE492C, 216, 'minimap primary vtable')]]
        if pins and (functions != pins[0]['ranges'] or data != pins[0]['data']):
            raise ValueError('Minimap contracts differ between pins')
        pins.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': functions, 'data': data})
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    base = json.loads((WS / 'inventory/client455-scrollbar-reference.json').read_text())
    inputs = []
    for row in base['inputs']:
        folder = row['folder']
        main_sprite = client / f'SpriteImage/{folder}/main.spr'
        if not main_sprite.exists():
            main_sprite = client / 'SpriteImage/Common/main.spr'
        common = Path(row['sprite']['file'])
        inputs.append({'nation': row['nation'], 'folder': folder, 'language': row['language'],
                       'common': {'file': str(common), 'sha256': sha(common), 'geometry': sprite_geometry(common, {(8, f) for f in range(6, 19)})},
                       'main': {'file': str(main_sprite), 'sha256': sha(main_sprite), 'geometry': sprite_geometry(main_sprite, {(5, 0), (5, 32)})}})
    report = {'scope': 'Minimap opacity EX control and mapped legacy owner integration;full455minimap/world/parent input OPEN',
              'references': pins, 'raw_evidence': evidence, 'inputs': inputs, 'script_sha256': sha(Path(__file__)),
              'facts': ['7B2C60/7B2B80 are generic alignment helpers;7B5450 style0 configures common8frames12to18,horizontal,no auto thumb',
                        'Minimap Init centers opacity EX relative to frame then adds15y,sets80/80 and scroll observer',
                        '709E10 maps own current to BYTE(255*(current+20)/100),then checks camera zoom gate independently of source',
                        '7099E0 applies alpha to individual owned groups,EX and list contents;background multiplier0.8 only alpha100,otherwise0.6',
                        '5558E0 uses eligibility/suppression/ack state;positive555940 camera consumer still needs455world integration'],
              'gaps': ['Full455minimap layout/additional controls/map generation/markers/tooltips and all remaining alpha groups',
                       'Actual camera zoom consumer555940/Avatar/world and suppression setters;positive unsupported branch explicitly refused',
                       'Full parent input/show/focus and all skin/alpha/clipping/lifecycle/FP/unsafe domains;briefing/Tutorial/M6F/M9'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-minimap-opacity-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'functions': len(ranges), 'assemblies': sum(len(r['assemblies']) for r in evidence),
                      'geometry': [{'nation': row['nation'], 'common': row['common']['geometry']['requested'], 'main': row['main']['geometry']['requested']} for row in inputs]}))


if __name__ == '__main__':
    main()
