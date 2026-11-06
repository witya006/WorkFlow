"""Pin modal plain/rich replacement and natural pixel extent before scroll fallback."""
import hashlib
import json
import struct
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = WS / 'artifacts/client455-tutorial'
    names = ['message-sizing-reference069', 'message-sizing-decompile069',
             'message-sizing-plain069', 'message-sizing-wrappers069']
    evidence = []
    bodies = {}
    for name in names:
        path = root / (name + '.json')
        body = json.loads(path.read_text())
        bodies[name] = body
        assemblies = body.get('assemblies', [body['assembly']] if 'assembly' in body else [])
        rows = []
        for asm in assemblies:
            count = len(asm['asm']['lines'])
            if not asm['cursor']['done'] or count != asm['instruction_count'] or count != asm['total_instructions']:
                raise ValueError('Incomplete modal instructions')
            rows.append({'rva': hex(int(asm['addr'], 16) - 0x400000), 'instructions': count})
        evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path), 'assemblies': rows})
    functions = bodies[names[0]]['ranges']['result'] + bodies[names[3]]['ranges']['result']
    target = json.loads((WS / 'config/client-target.json').read_text())
    references = []
    for folder, pin in [('current', target['behavior_reference']), ('reference-backup', target['secondary_reference'])]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256'] or pe(raw)['architecture'] != 'x86':
            raise ValueError('Changed455pin')
        ranges = []
        for row in functions:
            if row['error']:
                raise ValueError('Missing modal function')
            addr, count = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            ranges.append({'rva': hex(addr - 0x400000), 'bytes': count,
                           'sha256': hashlib.sha256(read_va(raw, addr, count)).hexdigest()})
        if struct.unpack('<I', read_va(raw, 0xAE4504 + 12, 4))[0] != 0x701630:
            raise ValueError('Messagebox SetSize vtable entry changed')
        if struct.unpack('<I', read_va(raw, 0xADB98C + 164, 4))[0] != 0x644270:
            raise ValueError('TextBoard plain-color entry changed')
        if references and ranges != references[0]['ranges']:
            raise ValueError('Message sizing differs between455pins')
        references.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': ranges})
    report = {
        'scope': 'Ordinary CGUIMessagebox plain/rich caller, color and natural pixel sizing; fullGUI/Tutorial/M9 OPEN',
        'references': references, 'raw_evidence': evidence, 'script_sha256': sha(Path(__file__)),
        'facts': ['701870 null pointer returns before any mutation; nonnull clears and replaces board, then unwrapped extent',
                  'Default FONT_INFO16 color FFE3E0D9; formatted flag selects644540 vs plain-color6444D0/644270',
                  'Natural extent computed before reading width/height for scrollable sizing;300/250 are fallback caps only',
                  'Scrollable overflow adds scrollbar, sizes it, then attaches board observer;no unconditional removal in SetMsg',
                  'Dialog minimum200x100;no-scroll margins30/30,scroll margins60/45 plus scrollbar/button sizes',
                  'Target virtual SetSize701630 takes width/height;legacy source SetBound kept as adaptation bridge',
                  'Ordinary wrapper700720 forwards runtime formatted/close flags;constructor7010E0 and error wrapper700570 pass plain0'],
        'gaps': ['Empty/nonadvancing formatted fragment extent:643D30 newline local uninitialized;source explicitly refuses zero fragments',
                 'Signed-overflow/invalid geometry/OOM domains and any unobserved scroll-attach edge require additional evidence',
                 'Global base GUI SetSize is still legacy nonvirtual;typed modal SetSize and SetBound adaptation only',
                 'All455wrapper variants/guards and callers beyond the ported ordinary signature;source create-info extension is not original455ABI',
                 'FullBriefing/Tutorial/Avatar/world/fourstage/auth/gameplay;fullclient acceptance remainsOPEN'],
        'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M9': 'OPEN',
    }
    (WS / 'inventory/client455-message-sizing-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'ranges': len(functions), 'complete_assemblies': sum(len(x['assemblies']) for x in evidence)}))


if __name__ == '__main__':
    main()
