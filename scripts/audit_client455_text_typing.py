"""Pin TextTypingBoard and its actual briefing callers; full briefing remains open."""
import hashlib
import json
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = WS / 'artifacts/client455-tutorial'
    names = ['briefing-core070', 'typing-core070', 'briefing-dependencies070', 'typing-details070', 'typing-reference070', 'briefing-base-draw071']
    raw_evidence = []
    for name in names:
        path = root / (name + '.json')
        raw_evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path)})
    body = json.loads((root / 'typing-reference070.json').read_text())
    base_draw = json.loads((root / 'briefing-base-draw071.json').read_text())
    assemblies = []
    for row in body['assemblies'] + base_draw['assemblies']:
        count = len(row['asm']['lines'])
        if not row['cursor']['done'] or count != row['instruction_count'] or count != row['total_instructions']:
            raise ValueError('Incomplete typing asm')
        assemblies.append({'rva': hex(int(row['addr'], 16) - 0x400000), 'instructions': count})
    target = json.loads((WS / 'config/client-target.json').read_text())
    references = []
    for folder, pin in [('current', target['behavior_reference']), ('reference-backup', target['secondary_reference'])]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256'] or pe(raw)['architecture'] != 'x86':
            raise ValueError('Changed455pin')
        functions = []
        for row in body['ranges']['result'] + base_draw['ranges']['result']:
            if row['error']:
                raise ValueError('Missing typing function')
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            functions.append({'rva': hex(address - 0x400000), 'bytes': size, 'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()})
        data = [{'rva': '0x6dbbd4', 'bytes': 168, 'role': 'TextTypingBoard vtable', 'sha256': hashlib.sha256(read_va(raw, 0xADBBD4, 168)).hexdigest()}]
        if references and (functions != references[0]['ranges'] or data != references[0]['data']):
            raise ValueError('Typing contracts differ between pins')
        references.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': functions, 'data': data})
    report = {'scope': 'CGUITextTypingBoard source/dependency for real briefing; no ordinary briefing instance yet',
              'references': references, 'assemblies': assemblies, 'raw_evidence': raw_evidence,
              'inputs': json.loads((WS / 'inventory/client455-modal-reference.json').read_text())['inputs'],
              'script_sha256': sha(Path(__file__)),
              'facts': ['Typing entries247470/2475A0/247640/247690/247940/247BD0 verified directly',
                        'WORD interval100 default;running/finished0,first/last0,cursorFFFF;Start storesDWORDclock+delay andprevious0',
                        'Update shown/running/notfinished gates,absolute start/loop comparisons and unsigned elapsed;zero previous is sentinel',
                        'One byte cursor except resource-codepage DBCS lead;spaces skip interval increments and crossing uses previous fragment string',
                        'Partial draw uses strict line-start<cursor but includes cursor byte;firstASCII alone remains invisible',
                        'Clear resets cursor and base caches but retains active/finished/timers;Finish sets endpoint andfinished1',
                        'Typing Draw calls60CAC0:own fill/image via6262E0 then children;070 contrary assumption corrected071;Update does not update child objects',
                        'Actual briefing733920 sets80ms,firstpage delay250/others0;733A50 reveal then nextpage/close;not yet connected in source'],
              'gaps': ['Actual CGUIBriefingWindow/board/key-guide/portrait/frame providers and production view/Tutorial/fourstage not yet ported',
                       'Negative accepted ranges lead to foreign/invalid marker reads in target;source explicitly refuses',
                       'Clear-while-active missing markers,WORD wrap/foreign pointers/OOM/clock reentrancy/failure domains remain unsupported or unverified',
                       'Full GUI flags/render layers/FreeType/scale/IME and complete client behavior remainOPEN'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-text-typing-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'ranges': len(functions), 'vtables': len(data), 'complete_assemblies': len(assemblies)}))


if __name__ == '__main__':
    main()
