"""Pin briefing frame/key/animation controls and their real sprite geometry."""
import argparse
import hashlib
import json
from pathlib import Path
from audit_client455_minimap_opacity import sprite_geometry
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resources():
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    result = []
    for nation, folder in [('Korea', 'ko-kr'), ('Russia', 'ru-ru')]:
        row = {'nation': nation, 'folder': folder}
        for role, filename, requests in [('common', 'common.spr', {(4, 3), (4, 4), (9, 6), (9, 7)}),
                                         ('tutorial', 'tutorial.spr', {(0, 0)} | {(1, f) for f in range(5)} | {(2, f) for f in range(12)})]:
            path = root / f'SpriteImage/{folder}/{filename}'
            if not path.exists():
                path = root / f'SpriteImage/Common/{filename}'
            row[role] = {'file': str(path), 'relative': path.relative_to(root).as_posix(), 'sha256': sha(path), 'geometry': sprite_geometry(path, requests)}
        path = root / f'DataTable/{folder}/NDLanguage.edf'
        row['language'] = {'file': str(path), 'sha256': sha(path)}
        result.append(row)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resources-only', action='store_true')
    args = parser.parse_args()
    inputs = resources()
    if args.resources_only:
        print(json.dumps(inputs))
        return
    root = WS / 'artifacts/client455-tutorial'
    paths = [root / (name + '.json') for name in ['briefing-first071', 'briefing-control-asm071', 'briefing-ranges071', 'briefing-uv071', 'briefing-extra-ranges071', 'briefing-base-draw071']]
    functions = json.loads((root / 'briefing-ranges071.json').read_text())['ranges']['result']
    functions += json.loads((root / 'briefing-extra-ranges071.json').read_text())['result']
    functions += json.loads((root / 'briefing-base-draw071.json').read_text())['ranges']['result']
    raw_evidence = []
    for path in paths:
        body = json.loads(path.read_text())
        raw_evidence.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path), 'assemblies': list(assembly_rows(body.get('assemblies', [])))})
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
                raise ValueError('Missing briefing control function')
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            ranges.append({'rva': hex(address - 0x400000), 'bytes': size, 'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()})
        data = [{'rva': hex(address - 0x400000), 'bytes': size, 'role': role, 'sha256': hashlib.sha256(read_va(raw, address, size)).hexdigest()}
                for address, size, role in [(0xAE62F4, 148, 'BriefingBoard vtable'), (0xAE6394, 148, 'TutorialKeyBoard vtable'), (0xADA7D4, 116, 'GUIObjectAni vtable prefix')]]
        if references and (ranges != references[0]['ranges'] or data != references[0]['data']):
            raise ValueError('Briefing control contracts differ between pins')
        references.append({'sha256': pin['sha256'], 'architecture': 'x86', 'image_base': '0x400000', 'ranges': ranges, 'data': data})
    report = {'scope': 'Source briefing frame/key/animation controls;ordinary full briefing window/Tutorial not yet connected',
              'references': references, 'raw_evidence': raw_evidence, 'inputs': inputs, 'script_sha256': sha(Path(__file__)),
              'facts': ['BriefingBoard two cap children,body and two vertical border rectangles;alpha preservesRGB',
                        'Key guide uses tutorial21 actions0/1/2,ND1058,2rows max but originalcount retained in gap/or conditions',
                        'Missing key255 retains geometry and animation state;unsupported other keys reset animation but retain size',
                        'Second-key plus layout has two5px gaps but row width accounts for only one;stale dimensions determine row height',
                        'Sheet columns/rows BYTE,zero->1;Org dimensions divided by grid,UV extent divided by texture dimensions',
                        'FloatFPS x87 frame advance,loop resets0/discards excess and pauses;strict unsigned pause elapsed > interval',
                        'SetImage Ex resets UV to original/texture ratios;SetSheet does not advance UV until frame/update',
                        '4A63A0/633360 use screen capture pointer,not a close-caption flag;fullScreen input capture consumers still open'],
              'gaps': ['FullCGUIBriefingWindow/outline/portrait/showRichMessage and actualTutorial/fourstage/Avatar/world stillOPEN',
                       'BriefingBoard colors must be configured before accepted Draw;target ctor leaves those fields unspecified,source zero initialization is not parity for pre-Init use',
                       'New source animation bridge only covers verified unrotated/mode0/key/portrait sheet subset;legacy0.7Ani consumers not migrated',
                       'Nonfinite/negative frame/invalid pointers/resources/zero-texture/overflow and engine draw modes/rotation/failure domains not accepted',
                       'GUI screen capture full routing/lifetime,remaininglayers/IME/GUI/fullclient M6F/M9'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-briefing-controls-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'ranges': len(ranges), 'vtables': len(data), 'complete_assemblies': sum(len(x['assemblies']) for x in raw_evidence)}))


if __name__ == '__main__':
    main()
