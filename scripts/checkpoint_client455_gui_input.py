"""Check bounded455base GUI input/focus/queue evidence;fullGUI remains OPEN."""
import hashlib
import json
import re
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe
from prepare_client455_normal import kernel_sources


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):
        return json.loads((WS / f'inventory/{name}.json').read_text())

    def check(row):
        if sha(WS / row['file']) != row['sha256']:
            raise ValueError('Changed GUI input evidence:' + row['file'])

    reference, native, link = load('client455-gui-input-reference'), load('client455-gui-input-native'), load('client455-normal-link')
    validate_normal_link(link)
    digest = sha(WS / 'inventory/client455-normal-link.json')
    if native['normal_link_sha256'] != digest or native['reference_sha256'] != sha(WS / 'inventory/client455-gui-input-reference.json'):
        raise ValueError('Refresh GUI input run')
    for owner, script in [(reference, 'audit_client455_gui_input.py'), (native, 'probe_client455_gui_input.py')]:
        if owner['script_sha256'] != sha(WS / 'scripts' / script):
            raise ValueError('Changed GUI input script')
    if native['source_sha256'] != sha(WS / native['source']) or native['generator_sha256'] != sha(WS / 'scripts/prepare_client455_normal.py') or native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py'):
        raise ValueError('Changed GUI fixture/build')
    for name, value in native['sources'].items():
        if sha(WS / 'scripts/native' / name) != value:
            raise ValueError('Changed GUI algorithm')
    count = 0
    for row in reference['raw_evidence']:
        check(row)
        body = json.loads((WS / row['file']).read_text())
        actual = list(assembly_rows(body if isinstance(body, list) else body.get('assemblies', [])))
        if actual != row['assemblies']:
            raise ValueError('Changed complete GUI instructions')
        count += len(actual)
    if count != 15:
        raise ValueError('Missing GUI instruction dumps')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        image = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = image.read_bytes()
        if sha(image) != pin['sha256'] or pe(raw)['architecture'] != 'x86' or len(pin['ranges']) != 34:
            raise ValueError('Changed pinned455 binary')
        for row in pin['ranges'] + pin['data']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed GUI target range')
    text = (WS / link['map']['file']).read_text()
    for symbol, provider in [('InputProc@CGUIObject', 'guiobject.obj'), ('MsgProc@CGUIObject', 'guiobject.obj'), ('TryFocus455@CGUIObject', 'guiobject.obj'), ('EventProcess@CGUIObject', 'guiobjecteventproc.obj'), ('Add@CGUIContainer', 'guicontainer.obj'), ('Remove@CGUIContainer', 'guicontainer.obj'), ('RF455_GuiInputTime', 'RFClient455Facade:client455_gui_input.obj')]:
        if not re.search(re.escape(symbol) + r'[^\r\n]*' + re.escape(provider), text):
            raise ValueError('Missing ordinary production provider:' + symbol)
    check(native['map'])
    if [row['nation'] for row in native['runs']] != ['Korea', 'Russia']:
        raise ValueError('Missing localized GUI run')
    for row, cp in zip(native['runs'], [949, 1251]):
        for field in ['exe', 'output']:
            check(row[field])
        for item in row['inputs']:
            check(item)
        binary = pe((WS / row['exe']['file']).read_bytes())
        actual = json.loads((WS / row['output']['file']).read_text())
        if row['exit'] or binary['architecture'] != 'x86' or binary['entry_rva'] != int(native['entry_rva'], 16) or actual != row['native'] or actual['status'] != 'PASS' or actual['codepage'] != cp:
            raise ValueError('GUI native runtime failure')
        for key in ['double7_right8', 'threshold_wrap_clock', 'modal_and_input_flags', 'container_main_list_contracts', 'focus_order_and_predicate', 'key_scan_and_modifier', 'key_dedup_focus_value_queue', 'middle_button', 'ordinary_unbound_EX_bound']:
            if not actual[key]:
                raise ValueError('Missing GUI behavior:' + key)
        if any(actual[key] for key in ['full_GUI_IME', 'other_container_layers', 'full_Tutorial']):
            raise ValueError('GUI scope incorrectly broadened')
    names = ['client455-scrollbar-native', 'client455-scrollbar-variants-native', 'client455-minimap-opacity-native', 'client455-text-board-native', 'client455-text-metrics-native', 'client455-font-native', 'client455-modal-native']
    for name in names:
        report = load(name)
        if report['normal_link_sha256'] != digest or any(row['exit'] or row['native']['status'] != 'PASS' for row in report['runs']):
            raise ValueError('Current affected GUI regression required:' + name)
    tutorial, ui = load('client455-tutorial-board-native'), load('client455-ui-startup-native')
    if tutorial['normal_link_sha256'] != digest or tutorial['native']['status'] != 'PASS' or ui['normal_link_sha256'] != digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Current tutorial modal/Create check required')
    kernels, _ = kernel_sources(WS / 'scripts/native')
    if len(kernels) != 20:
        raise ValueError('Canonical kernel set changed')
    names += ['client455-gui-input-reference', 'client455-gui-input-native', 'client455-normal-preparation', 'client455-normal-link', 'client455-tutorial-board-native', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'base_mouse_key_focus_queue': 'PASS', 'main_list_container_and_binding_correction': 'PASS',
              'actual_ordinary_production_providers': 'PASS', 'affected_GUI_and_existing_Create': 'PASS',
              'full_GUI_IME_other_layers': 'OPEN', 'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names},
              'gaps': reference['gaps'], 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-gui-input-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL: baseGUI mouse/key/focus/queue/main-list/binding and affectedGUI/Create PASS;fullGUI/IME/otherlayers/M9 OPEN')


if __name__ == '__main__':
    main()
