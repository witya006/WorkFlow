"""Pin ordinary scrollbar geometry,input/math and the real composite-thumb frames."""
import hashlib
import json
import struct
from pathlib import Path
from audit_client455_text_board import assemblies
from build_client455_x87_math import read_va
from compare_client_binaries import WS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assembly_rows(body):
    if isinstance(body, list):
        for item in body:
            yield from assembly_rows(item)
    elif isinstance(body, dict) and isinstance(body.get('asm'), dict):
        canonical = dict(body)
        canonical['addr'] = body['asm']['start_ea']
        yield from assemblies(canonical)


def sprite_frames(path):
    raw = path.read_bytes()
    at = 0
    def take(size):
        nonlocal at
        if size > len(raw) - at:
            raise ValueError('Truncated scrollbar sprite')
        result = raw[at:at + size]
        at += size
        return result
    if struct.unpack('<I', take(4))[0] != 0x3f8ccccd:
        raise ValueError('Expected sprite1.1')
    actions = struct.unpack('<I', take(4))[0]
    rows = {}
    action2_count = 0
    for action in range(actions):
        count = struct.unpack('<I', take(4))[0]
        if action == 2:
            action2_count = count
        for frame in range(count):
            fmt, width, height, tw, th, size = struct.unpack('<6I', take(24))
            take(size)
            if action == 2:
                rows[frame]={'action':action,'frame':frame,'format':fmt,'width':width,'height':height,'texture_width':tw,'texture_height':th}
    if at != len(raw) or action2_count < 4:
        raise ValueError('Incomplete arrow sprite data')
    return {'frame_count':action2_count,'requests':[{'requested_frame':frame,**rows[min(frame,action2_count-1)]}for frame in [0,1,2,3,44,45,46,47,48,49]]}


def main():
    directory = WS / 'artifacts/client455-tutorial'
    names = ['scrollbar-core065', 'scrollbar-more065', 'scrollbar-helpers065', 'scrollbar-asm065',
             'scrollbar-support-asm065', 'scrollbar-ftol065', 'scrollbar-container-draw065', 'scrollbar-ranges065',
             'scrollbar-sprite-order065','scrollbar-frame-clamp-asm065']
    evidence = []
    for name in names:
        path = directory / f'{name}.json'
        evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path), 'assemblies': list(assembly_rows(json.loads(path.read_text())))})
    functions = json.loads((directory / 'scrollbar-ranges065.json').read_text())['result']
    clamp = json.loads((directory / 'scrollbar-frame-clamp-asm065.json').read_text())
    start, last = int(clamp['asm']['start_ea'],16),int(clamp['asm']['lines'][-1]['addr'],16)
    if clamp['asm']['lines'][-1]['instruction'] != 'retn 4':
        raise ValueError('Unexpected sprite clamp tail')
    functions.append({'error':None,'fn':{'addr':hex(start),'size':hex(last+3-start)}})
    target = json.loads((WS / 'config/client-target.json').read_text())
    pins = []
    for folder, pin in [('current', target['behavior_reference']), ('reference-backup', target['secondary_reference'])]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        if sha(path) != pin['sha256']:
            raise ValueError('Changed455 pin')
        raw = path.read_bytes()
        if read_va(raw,last,3)!=bytes.fromhex('c2 04 00'):
            raise ValueError('Sprite clamp tail bytes changed')
        ranges = []
        for row in functions:
            if row['error']:
                raise ValueError('Missing scrollbar function')
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            ranges.append({'rva': hex(address - 0x400000), 'bytes': size, 'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()})
        data = []
        for address, size, role in [(0xADAF74, 144, 'Scrollbar verified vtable prefix'), (0xADAEC4, 144, 'Composite thumb verified vtable prefix'), (0xAA9A50, 8, 'Half divisor2')]:
            value = read_va(raw, address, size)
            if role == 'Half divisor2' and value != struct.pack('<d', 2.0):
                raise ValueError('Changed snap half divisor')
            data.append({'rva': hex(address - 0x400000), 'bytes': size, 'role': role, 'sha256': hashlib.sha256(value).hexdigest()})
        if pins and (ranges != pins[0]['ranges'] or data != pins[0]['data']):
            raise ValueError('Scrollbar contracts differ between pins')
        pins.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': ranges, 'data': data})
    modal = json.loads((WS / 'inventory/client455-modal-reference.json').read_text())
    inputs = []
    for row in modal['inputs']:
        sprite, language = Path(row['sprite']['file']), Path(row['language']['file'])
        inputs.append({'nation': row['nation'], 'folder': 'ko-kr' if row['nation'] == 'Korea' else 'ru-ru',
                       'sprite': {'file': str(sprite), 'sha256': sha(sprite), 'frames': sprite_frames(sprite)},
                       'language': {'file': str(language), 'sha256': sha(language)}})
    report = {
        'scope': 'Ordinary scrollbar geometry/composite thumb/amount/snap/mouse/clock;EX/Var,parent input system and full455 remain OPEN',
        'references': pins, 'raw_evidence': evidence, 'inputs': inputs, 'script_sha256': sha(Path(__file__)),
        'facts': [
            'Composite thumb is a container with three image objects;default frame pairs44/47,45/48,46/49 in common action2',
            'Thumb SetSize enforces minimum6x18;auto thumb starts enabled with minimum20 and uses linear remainingExtent-total',
            'GetTrackLength is dynamic;UpdateBar multiplies signed32 current*length with wrap before integer division',
            'Pixel snapping uses x87 signed-int to double,divide/multiply,float spill;ftol2_sse has int32 CVTTSD2SI branch',
            'Small-range unordered compare selects upper endpoint;clock query order and DWORD wrap/product are observable',
            'Track/drag direction compares AFTER amount update;in-range movement often emits DOWN31 regardless of direction',
            'Thumb removal on zero total occurs only when child count is exactly3;Draw paints container then thumb again',
            'Modal helper requests5x18,but physical composite clamps to6x18;earlier062 width5 described requested legacy size',
            'Available common.spr action2 lacks requested44to49;target SetFrame clamps requests to last valid frame;synthetic fixture separately exercises all six cap frames',
        ],
        'gaps': [
            'CGUIScrollbarEX/Var and their real callers not yet ported;cached decomp evidence retained',
            'Default composite skin frames absent from selected real resources;full resource/version parity remains OPEN',
            'Legacy container lacks455 parent event bubbling/show inheritance;owned arrow/show adapter used;full parent input system OPEN',
            'General clipped rendering/alpha,all skin setters/private ABI/lifecycle/OOM/numeric/unmaskedFP and non-SSE2 fallback domains OPEN',
            'Zero adjustment modulo and forced UpdateBar(total0) explicitly refused;not claimed original fault equivalence',
            'Legacy GetMinSize/SetScrollSpeed compatibility wrappers await complete target caller/setter proof',
            'Production rich text/message sizing/full briefing/Avatar/world/Tutorial/fourstage/authentication/gameplay;M6F/M7/M9',
        ],
        'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN',
    }
    (WS / 'inventory/client455-scrollbar-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pinned_functions': len(pins[0]['ranges']), 'complete_assemblies': sum(len(row['assemblies']) for row in evidence), 'actual_common_action2_frames': [row['sprite']['frames']['frame_count'] for row in inputs]}))


if __name__ == '__main__':
    main()
