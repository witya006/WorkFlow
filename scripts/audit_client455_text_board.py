"""Pin TextBoard/typed text contracts; scrollbar input and full455 remain open."""
import hashlib
import json
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assemblies(body):
    if isinstance(body, list):
        for item in body:
            yield from assemblies(item)
    elif isinstance(body, dict) and isinstance(body.get('asm'), dict):
        lines = body['asm']['lines']
        if not body['cursor']['done'] or len(lines) != body['instruction_count'] or len(lines) != body['total_instructions']:
            raise ValueError('Incomplete TextBoard instructions')
        yield {'rva': hex(int(body['addr'], 16) - 0x400000), 'instructions': len(lines)}


def main():
    directory = WS / 'artifacts/client455-tutorial'
    names = ['textboard-initial063', 'textboard-metrics063', '064-643890-asm',
             'textboard-details064', 'textboard-draw064', 'textboard-contracts064',
             'textboard-helpers064', 'textboard-copy-scroll064', 'textboard-info064',
             'textboard-textinfo064', 'textboard-scroll-details064', 'textboard-primary-asm064',
             'textboard-ranges064', 'textboard-text-misc064', 'textboard-mbcp-callers064', 'textboard-mbcp-init064', 'textboard-mbcp-semantics064',
             'textboard-scroll-coupling064', 'textboard-scroll-observer064']
    raw_evidence = []
    for name in names:
        path = directory / f'{name}.json'
        body = json.loads(path.read_text())
        raw_evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path),
                             'assemblies': list(assemblies(body))})
    functions = json.loads((directory / 'textboard-ranges064.json').read_text())['result']
    callers = json.loads((directory / 'textboard-mbcp-callers064.json').read_text())['result']
    for fn in [callers[0]['xrefs'][0]['fn'], callers[1]['xrefs'][1]['fn']]:
        functions.append({'fn': fn, 'error': None})
    # Function size returned by the native list_funcs '*mbcp*' query.
    functions.append({'fn': {'addr': '0x88967d', 'size': '0x3c'}, 'error': None})
    functions.extend(json.loads((directory / 'textboard-scroll-observer064.json').read_text())['ranges']['result'])
    target = json.loads((WS / 'config/client-target.json').read_text())
    references = []
    for folder, pin in [('current', target['behavior_reference']), ('reference-backup', target['secondary_reference'])]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        if sha(path) != pin['sha256']:
            raise ValueError('Changed455 pin')
        raw = path.read_bytes()
        # MOVZX EAX,BYTE PTR[EBP+10], not a guessed WORD/int argument.
        for addr in [0x7B1F51, 0x7B1F69]:
            if read_va(raw, addr, 4) != bytes.fromhex('0f b6 45 10'):
                raise ValueError('BYTE copy capacity contract changed')
        ranges = []
        for row in functions:
            if row['error']:
                raise ValueError('Missing TextBoard function')
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            ranges.append({'rva': hex(address - 0x400000), 'bytes': size,
                           'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()})
        data = [{'rva': '0x6db98c', 'bytes': 168, 'role': 'TextBoard vtable',
                 'sha256': hashlib.sha256(read_va(raw, 0xADB98C, 168)).hexdigest()},
                {'rva': '0x6db984', 'bytes': 4, 'role': 'TextBoard scroll observer vtable',
                 'sha256': hashlib.sha256(read_va(raw, 0xADB984, 4)).hexdigest()}]
        if references and (ranges != references[0]['ranges'] or data != references[0]['data']):
            raise ValueError('TextBoard contracts differ between pins')
        references.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': ranges, 'data': data})
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    inputs = []
    for nation, folder in [('Korea', 'ko-kr'), ('Russia', 'ru-ru')]:
        path = client / f'DataTable/{folder}/NDLanguage.edf'
        inputs.append({'nation': nation, 'folder': folder, 'file': str(path), 'sha256': sha(path)})
    ucrt = Path('C:/Program Files (x86)/Windows Kits/10/Source/10.0.26100.0/ucrt')
    runtime_sources = [{'file': str(path), 'sha256': sha(path)} for path in
                       [ucrt / 'mbstring/mbctype.cpp', ucrt / 'initializers/multibyte_initializer.cpp']]
    report = {
        'scope': 'Ordinary TextBoard fragments/line caches/pixel layout/markup/draw,typed font/text metadata and scrollbar amount coupling;fullscrollbar/input/briefing/Tutorial OPEN',
        'references': references, 'raw_evidence': raw_evidence, 'inputs': inputs, 'installed_runtime_sources': runtime_sources,
        'script_sha256': sha(Path(__file__)),
        'facts': [
            'FONT_INFO16:BYTE size,DWORD style/color,float scale1;TextInfo28 caches WORD length at8,font at12;Clear retains cached length',
            'Separate fragment/line caches;limit1000;WORD base+offset markers;rebase when base+fragment reachesffff',
            'Pixel width/DBCS fit use current normal font;resize reflows only if actual width changes;too-narrow text can remain without a line',
            'Newline markers point at newline bytes;leading-newline and margin-only stale layout behavior preserved',
            'Font tag prefix case-insensitive;attribute keys case-sensitive;sticky color/style flags and color precedence;style token includes any adjacent closing bracket',
            '7B1F40 takes BYTE capacity;zero/wrapped256 leaves destination unchanged;mbsnbcpy follows ambient CRT multibyte state',
            'TextBoard markup and final draw copy share scratch;draw uses fixedscale1 despite typed FONT_INFO field',
            'Formatted-text and unwrapped-extent methods are exercised in full-object probe;production rich callers/legacy message sizing still await port',
            'Scrollbar total/current setters both call combined clamp/update;TextBoard computes amount/view in defaultheight+gap units',
            'Target CRT889853 initializes systemANSI using_setmbcp(-3);installed UCRT already does so;getmbcp0 also denotes an SBCS page and is not proof of different startup',
        ],
        'gaps': [
            'Full scrollbar thumb auto-sizing/geometry/timing/mouse/keyboard algorithms and variants remain legacy',
            'Production rich-text callers and legacy messagebox byte-count sizing remain unported;unused formatted/extent functions are stripped in production',
            'Other users of target shared102DAB0 scratch not yet connected;cross-subsystem scratch state domains OPEN',
            'Complete CRT locale/thread/create_locale updates beyond initial systemANSI startup remain OPEN',
            'Malformed non-advancing tags/32byte token overflow and WORD input overflow explicitly refused,not claimed target equivalence',
            'Private STL/allocator/OOM/unsafe/numeric/foreign-pointer domains and complete font/FreeType routing remain OPEN',
            'Full briefing/Avatar/world/Tutorial/fourstage/authentication/gameplay and prior unknown domains;M6F/M7/M9',
        ],
        'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN',
    }
    (WS / 'inventory/client455-text-board-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pinned_ranges': len(references[0]['ranges']), 'complete_assemblies': sum(len(row['assemblies']) for row in raw_evidence), 'fullscrollbar': 'OPEN'}))


if __name__ == '__main__':
    main()
