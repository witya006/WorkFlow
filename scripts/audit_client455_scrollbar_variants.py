"""Pin distinct EX/Var contracts and actual caller evidence for client455."""
import hashlib
import json
import struct
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sprite_actions(path):
    raw = path.read_bytes()
    version, actions = struct.unpack_from('<II', raw)
    if version != 0x3f8ccccd:
        raise ValueError('Unexpected sprite version')
    at, counts = 8, []
    for _ in range(actions):
        count, = struct.unpack_from('<I', raw, at)
        at += 4
        counts.append(count)
        for _ in range(count):
            size, = struct.unpack_from('<I', raw, at + 20)
            at += 24 + size
            if at > len(raw):
                raise ValueError('Truncated sprite')
    if at != len(raw):
        raise ValueError('Trailing sprite bytes')
    return counts


def main():
    root = WS / 'artifacts/client455-tutorial'
    names = ['scrollbar-exvar-decomp066', 'scrollbar-var-helpers066', 'scrollbar-variant-support066',
             'scrollbar-variant-asm066', 'scrollbar-variant-callers066', 'scrollbar-variant-ranges066',
             'scrollbar-variant-drawing066', 'scrollbar-variant-drawing-asm066']
    evidence = []
    for name in names:
        path = root / (name + '.json')
        body = json.loads(path.read_text())
        evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path),
                         'assemblies': list(assembly_rows(body.get('assemblies', []) if isinstance(body, dict) else body))})
    manifest = json.loads((root / 'scrollbar-variant-ranges066.json').read_text())
    functions = {int(row['addr'], 16): int(row['size'], 16)
                 for row in manifest['ranges']['result'][0]['data'] if int(row['addr'], 16) <= 0x63bed0}
    drawing = json.loads((root / 'scrollbar-variant-drawing-asm066.json').read_text())
    for row in manifest['support']['result'] + drawing['ranges']['result']:
        if row['error']:
            raise ValueError('Missing variant helper')
        functions[int(row['fn']['addr'], 16)] = int(row['fn']['size'], 16)
    #Caller ranges are independently supplied by xrefs,not guessed from names.
    for address, size in [(0x705160, 0x43c), (0x7059e0, 0x7c5)]:
        functions[address] = size
    target = json.loads((WS / 'config/client-target.json').read_text())
    pins = []
    for folder, pin in [('current', target['behavior_reference']), ('reference-backup', target['secondary_reference'])]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256'] or pe(raw)['architecture'] != 'x86':
            raise ValueError('Changed455 binary')
        ranges = [{'rva': hex(address - 0x400000), 'bytes': size,
                   'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()}
                  for address, size in sorted(functions.items())]
        data = [{'rva': hex(address - 0x400000), 'bytes': size, 'role': role,
                 'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()}
                for address, size, role in [(0xADB02C, 156, 'EX primary vtable through alpha'),
                                            (0xADB0FC, 164, 'Var primary vtable through amount')]]
        if pins and (ranges != pins[0]['ranges'] or data != pins[0]['data']):
            raise ValueError('Variant ranges differ between pins')
        pins.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': ranges, 'data': data})
    base = json.loads((WS / 'inventory/client455-scrollbar-reference.json').read_text())
    resources = [{'nation': row['nation'], 'sprite_sha256': row['sprite']['sha256'],
                  'frames_per_action': sprite_actions(Path(row['sprite']['file']))} for row in base['inputs']]
    report = {
        'scope': 'EX/Var distinct source contracts;full-object verification is not production minimap integration',
        'references': pins, 'raw_evidence': evidence, 'inputs': base['inputs'], 'skin_resources': resources, 'script_sha256': sha(Path(__file__)),
        'facts': [
            'EX adds plain CGUIButton at968 at construction,retains it for total0,and uses its dimensions for UpdateBar',
            'EX input directly calls base63A1A0 with inherited composite dimensions;no MOUSE_PRESSED repeat branch',
            'EX alpha changes plain thumb,arrows,inherited composite and self',
            'EX inherited Draw paints children then returns FALSE when unused composite remains hidden;GUIObject ctor show0',
            'EX constructor and amount have real CGUIMiniMapWindow callers705160/7059E0;not yet ported',
            'Var constructor has no direct xrefs in this pinned IDB;this does not prove never indirectly instantiated',
            'Var initializer virtual+24 is SetSprite,not RemoveAll;two inherited arrow children remain',
            'Var caps use common action15 frames0to5;row drawing deliberately uses common action2 frames1/4',
            'Target sprite loader8CFB90 requires actions<16,so ordinary loading cannot provide action15;selected common resources have15actions',
            'Var amount repositions composite at origin without UpdateBar,middleExtent=preferredHeight-total,including0/negative',
            'Var SetSize stores raw outer extent but clamps separate skin6x18;does not relayout or recompute amount',
            'Var track click uses full composite height;release switches skins without realigning;horizontal track local is uninitialized',
        ],
        'gaps': [
            'Production455 minimap owner/helper7B2C60,skin mapping and real input consumers not ported;unused variant methods may be stripped',
            'Var action15 cannot be supplied through ordinary target loader;fixture preserves missing-cap behavior and uses valid action2 rows',
            'Full parent input/show/focus routing,allresource skins/alpha/clipping/private ABI/lifecycle/OOM/FP/unsafe domains',
            'Var horizontal track click explicitly refused rather than inventing uninitialized value;no dynamic original execution',
            'Production rich callers/message sizing/fullbriefing/Avatar/world/Tutorial/fourstage/auth/gameplay;M6F/M7/M9',
        ],
        'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN',
    }
    (WS / 'inventory/client455-scrollbar-variants-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'functions': len(functions), 'assemblies': sum(len(row['assemblies']) for row in evidence), 'vtable_regions': 2}))


if __name__ == '__main__':
    main()
