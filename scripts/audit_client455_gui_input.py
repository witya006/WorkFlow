"""Pin455base GUI mouse/key/focus/queue and main-list container contracts."""
import hashlib
import json
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    root = WS / 'artifacts/client455-tutorial'
    names = ['gui-input-initial068', 'gui-input-core068', 'gui-input-events068', 'gui-input-state068',
             'gui-input-focus068', 'gui-input-dispatch068', 'gui-mouse-device068', 'gui-input-queue068',
             'gui-input-lifecycle068', 'gui-input-container-more068', 'gui-input-container-asm068',
             'gui-input-core-asm068', 'gui-input-ranges068']
    evidence = []
    for name in names:
        path = root / (name + '.json')
        body = json.loads(path.read_text())
        evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path),
                         'assemblies': list(assembly_rows(body if isinstance(body, list) else body.get('assemblies', [])))})
    ranges = json.loads((root / 'gui-input-ranges068.json').read_text())['ranges']['result']
    target = json.loads((WS / 'config/client-target.json').read_text())
    pins = []
    for folder, pin in [('current', target['behavior_reference']), ('reference-backup', target['secondary_reference'])]:
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256'] or pe(raw)['architecture'] != 'x86':
            raise ValueError('Changed455binary')
        functions = []
        for row in ranges:
            if row['error']:
                raise ValueError('Missing GUI function')
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            functions.append({'rva': hex(address - 0x400000), 'bytes': size,
                              'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()})
        data = [{'rva': '0x6da6e4', 'bytes': 116, 'role': 'base GUIObject vtable prefix',
                 'sha256': hashlib.sha256(read_va(raw, 0xADA6E4, 116)).hexdigest()}]
        if pins and (functions != pins[0]['ranges'] or data != pins[0]['data']):
            raise ValueError('GUI contracts differ between pins')
        pins.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': functions, 'data': data})
    modal = json.loads((WS / 'inventory/client455-modal-reference.json').read_text())
    report = {
        'scope': '455base mouse/doubleclick/modal guard/key/focus/queue and main-list Add/Remove;fullGUI/IME/render layers/gameplay OPEN',
        'references': pins, 'raw_evidence': evidence, 'inputs': modal['inputs'], 'script_sha256': sha(Path(__file__)),
        'facts': ['Event7 is double stroke,8 right stroke;double threshold300 inclusive,DWORD wrap,conditional query then timestamp query',
                  'Base mouse flag88 defaults1;right-pressed and modal/last-click pointers are independent global state',
                  'Modal setter calls previous object callback even for same or null replacement;outside stroke closes popup without activating underlying target',
                  'MessageProc uses focus predicate,Ctrl/Alt filter,WM_KEYDOWN/WM_CHAR and full-high-half PROCESSKEY scan mapping',
                  'Focus emits previous blur before new eligibility check;failed candidate may leave old focus pointer while emitting blur',
                  'Queue dedup uses source,id,byte key;focus70/value80 dispatch and DWORD payload at32',
                  'Container default focus disabled;Add dedup+Show inheritance then main-list append,AddFront prepends;InputProc reverses main list',
                  'Remove null returns0,nonnull returns1 and kills eligible focus;mouse references to live removed objects retained;RemoveAll similarly focus-only',
                  '60D3D0/60D650 and60DE40/60E010 are list insertion/find helpers,not parent event bubbling',
                  'Ordinary scrollbar has no implicit arrow binding in638EE0/639590/627070;EX has explicit four registrations;owned ordinary adapter removed'],
        'gaps': ['Two other target container lists/render layers and full indexed compatibility API/callers remain unported',
                 'Full popup/GUIInput/IME/combobox/focus observers/value80 consumers and all downstream event7/8 gameplay actions',
                 'Other private destructor registry/cross-thread/OOM/invalid-pointer/failure and ABI domains;fullrenderer/resources/skins',
                 'Fullminimap/camera/rich callers/message sizing/briefing/Avatar/world/Tutorial/fourstage/auth;M6F/M7/M9'],
        'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN',
    }
    (WS / 'inventory/client455-gui-input-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'ranges': len(ranges), 'complete_assemblies': sum(len(row['assemblies']) for row in evidence)}))


if __name__ == '__main__':
    main()
