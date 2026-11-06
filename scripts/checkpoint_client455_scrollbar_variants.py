"""Check bounded EX/Var evidence;production minimap/full455 remain open."""
import hashlib
import json
import re
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from audit_client455_scrollbar_variants import sprite_actions
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):
        return json.loads((WS / f'inventory/{name}.json').read_text())

    def check(row):
        if sha(WS / row['file']) != row['sha256']:
            raise ValueError('Changed variants evidence:' + row['file'])

    reference = load('client455-scrollbar-variants-reference')
    native = load('client455-scrollbar-variants-native')
    link = load('client455-normal-link')
    validate_normal_link(link)
    link_digest = sha(WS / 'inventory/client455-normal-link.json')
    if native['normal_link_sha256'] != link_digest or native['reference_sha256'] != sha(WS / 'inventory/client455-scrollbar-variants-reference.json'):
        raise ValueError('Refresh variant runs')
    for name in ['audit_client455_scrollbar_variants.py', 'probe_client455_scrollbar_variants.py']:
        owner = reference if name.startswith('audit') else native
        if owner['script_sha256'] != sha(WS / 'scripts' / name):
            raise ValueError('Changed variants script')
    if sha(WS / native['source']) != native['source_sha256']:
        raise ValueError('Changed native fixture')
    for name, digest in native['sources'].items():
        if sha(WS / 'scripts/native' / name) != digest:
            raise ValueError('Changed source algorithm')
        destination = 'guiscrollbar.h' if name.endswith('.h') else 'guiscrollbar.cpp'
        if sha(WS / 'work/client455-port/normal/source/userinterface/guicontroller' / destination) != digest:
            raise ValueError('Normal source differs from tested algorithm')
    if native['generator_sha256'] != sha(WS / 'scripts/prepare_client455_normal.py') or native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py'):
        raise ValueError('Changed native build route')
    count = 0
    for row in reference['raw_evidence']:
        check(row)
        body = json.loads((WS / row['file']).read_text())
        actual = list(assembly_rows(body.get('assemblies', []) if isinstance(body, dict) else body))
        if actual != row['assemblies']:
            raise ValueError('Incomplete variant instructions')
        count += len(actual)
    if count != 13:
        raise ValueError('Missing variant disassembly')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        binary = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = binary.read_bytes()
        if sha(binary) != pin['sha256'] or pe(raw)['architecture'] != 'x86' or len(pin['ranges']) != 37:
            raise ValueError('Changed455 pin')
        for row in pin['ranges'] + pin['data']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed variant target bytes')
    for row, skin in zip(reference['inputs'], reference['skin_resources']):
        if sha(Path(row['sprite']['file'])) != row['sprite']['sha256'] or sprite_actions(Path(row['sprite']['file'])) != skin['frames_per_action']:
            raise ValueError('Changed real common.spr')
        if len(skin['frames_per_action']) != 15:
            raise ValueError('Revisit action15 resource evidence')
    check(native['map'])
    mapping = (WS / native['map']['file']).read_text()
    for symbol in ['SetAmount@CGUIScrollbarEX', 'MouseEvent@CGUIScrollbarEX', 'SetAmount@CGUIScrollbarVar', 'MouseEvent@CGUIScrollbarVar', 'Draw@CGUIScrollbarVar']:
        if not re.search(re.escape(symbol) + r'[^\r\n]*guiscrollbar\.obj', mapping):
            raise ValueError('Missing real full-object variant method:' + symbol)
    if [row['nation'] for row in native['runs']] != ['Korea', 'Russia']:
        raise ValueError('Missing localized variant run')
    for row, cp in zip(native['runs'], [949, 1251]):
        for name in ['exe', 'output']:
            check(row[name])
        for item in row['inputs']:
            check(item)
        image = pe((WS / row['exe']['file']).read_bytes())
        if image['architecture'] != 'x86' or image['entry_rva'] != int(native['entry_rva'], 16):
            raise ValueError('Unexpected own entry')
        actual = json.loads((WS / row['output']['file']).read_text())
        if row['exit'] or actual != row['native'] or actual['status'] != 'PASS' or actual['codepage'] != cp:
            raise ValueError('Variant native failure')
        for key in ['EX_geometry', 'EX_base_snap_quirk', 'EX_no_repeat', 'EX_alpha', 'Var_geometry', 'Var_input', 'Var_row2_action2', 'queued_events', 'undefined_horizontal_refused']:
            if not actual[key]:
                raise ValueError('Missing variant behavior:' + key)
        if actual['production_minimap'] or actual['full_parent_input']:
            raise ValueError('Variant scope incorrectly broadened')
        if len(row['frames']) != 3:
            raise ValueError('Missing GPU frames')
        for frame in row['frames']:
            check(frame)
            if (frame['width'], frame['height']) != (640, 480) or (WS / frame['file']).stat().st_size != 640 * 480 * 4 or sha(WS / frame['preview']) != frame['preview_sha256']:
                raise ValueError('Changed GPU readback')
        if row['frames'][1]['sha256'] == row['frames'][2]['sha256']:
            raise ValueError('Pressed row unchanged')
    if [f['sha256'] for f in native['runs'][0]['frames']] != [f['sha256'] for f in native['runs'][1]['frames']]:
        raise ValueError('Profile GPU difference')
    for name in ['client455-scrollbar-native', 'client455-text-board-native', 'client455-text-metrics-native', 'client455-font-native', 'client455-modal-native']:
        report = load(name)
        if report['normal_link_sha256'] != link_digest or any(row['exit'] or row['native']['status'] != 'PASS' for row in report['runs']):
            raise ValueError('Affected GUI regression missing:' + name)
    tutorial, ui = load('client455-tutorial-board-native'), load('client455-ui-startup-native')
    if tutorial['normal_link_sha256'] != link_digest or tutorial['native']['status'] != 'PASS' or ui['normal_link_sha256'] != link_digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Current modal/Create regression missing')
    names = ['client455-scrollbar-variants-reference', 'client455-scrollbar-variants-native', 'client455-normal-link', 'client455-scrollbar-native', 'client455-text-board-native', 'client455-text-metrics-native', 'client455-font-native', 'client455-modal-native', 'client455-tutorial-board-native', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'distinct_EX_Var_source_and_full_object_tests': 'PASS', 'queued_input_and_GPU': 'PASS',
              'affected_GUI_and_existing_Create': 'PASS', 'production_minimap': 'OPEN', 'full_parent_input': 'OPEN',
              'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names}, 'gaps': reference['gaps'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-scrollbar-variants-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL: EX/Var source/queued input/GPU and affected GUI/Create PASS;production minimap,parent input,M9 OPEN')


if __name__ == '__main__':
    main()
