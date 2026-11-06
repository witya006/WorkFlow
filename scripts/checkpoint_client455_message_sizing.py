"""Accept the verified modal caller/sizing domain, without claiming full GUI parity."""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):
        return json.loads((WS / f'inventory/{name}.json').read_text())

    def check(row):
        if sha(WS / row['file']) != row['sha256']:
            raise ValueError('Changed message sizing evidence:' + row['file'])

    reference = load('client455-message-sizing-reference')
    modal = load('client455-modal-native')
    link = load('client455-normal-link')
    validate_normal_link(link)
    digest = sha(WS / 'inventory/client455-normal-link.json')
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_message_sizing.py'):
        raise ValueError('Stale message sizing reference')
    if modal['normal_link_sha256'] != digest or modal['source_sha256'] != sha(WS / modal['source']):
        raise ValueError('Stale modal native checks')
    preparation = load('client455-normal-preparation')
    if preparation['script_sha256'] != sha(WS / 'scripts/prepare_client455_normal.py'):
        raise ValueError('Stale source generator')
    for name in ['client455_modal_message.inc', 'client455_modal_init.inc', 'client455_gui_text_board.cpp', 'client455_gui_text_board.h']:
        if preparation['record_inputs'][name] != sha(WS / 'scripts/native' / name):
            raise ValueError('Changed message source:' + name)
    if modal['sources']['client455_modal_message.inc'] != preparation['record_inputs']['client455_modal_message.inc']:
        raise ValueError('Modal probe uses old SetMsg')
    for row in reference['raw_evidence']:
        check(row)
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256']:
            raise ValueError('Changed455pin')
        for row in pin['ranges']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed modal machine code')
    mapping = (WS / link['map']['file']).read_text()
    # The typed SetSize adapter can inline into SetMsg; its SetBound provider
    # and the executed geometry assertions establish the retained layout path.
    for symbol, provider in [('SetMsg@CGUIMessagebox', 'guimessagebox.obj'), ('SetBound@CGUIMessagebox', 'guimessagebox.obj'),
                             ('InsertFormatted455@CGUITextBoard', 'guitextboard.obj'), ('ResizeToText455@CGUITextBoard', 'guitextboard.obj')]:
        if not re.search(re.escape(symbol) + r'[^\r\n]*' + re.escape(provider), mapping, re.I):
            raise ValueError('Missing ordinary message provider:' + symbol)
    colors = []
    for run in modal['runs']:
        actual = run['native']
        if run['exit'] or actual['status'] != 'PASS' or actual['pixel_message_sizing_cases'] != 12:
            raise ValueError('Message sizing native checks failed')
        for key in ['ordinary_rich_wrapper', 'natural_extent_before_scroll_fallback', 'empty_extent_unsupported']:
            if not actual[key]:
                raise ValueError('Missing modal sizing contract:' + key)
        for frame in run['frames']:
            check(frame)
            if frame['file'].endswith(('modal-rich.bgra', 'modal-rich-wrapper.bgra')):
                pixels = Image.frombytes('RGBA', (640, 480), (WS / frame['file']).read_bytes(), 'raw', 'BGRA')
                rgba = pixels.tobytes()
                red = sum(rgba[i] > 100 and rgba[i] > 2 * rgba[i + 1] and rgba[i] > 2 * rgba[i + 2] for i in range(0, len(rgba), 4))
                if red < 3:
                    raise ValueError('Rich caller did not paint red text')
                colors.append({'nation': run['nation'], 'file': frame['file'], 'red_pixels': red})
    names = ['client455-modal-checkpoint', 'client455-text-board-checkpoint', 'client455-gui-input-checkpoint']
    for name in names:
        gate = load(name)
        if gate['status'] != 'PARTIAL' or gate['evidence_sha256']['client455-normal-link'] != digest:
            raise ValueError('Stale or unexpected broader checkpoint state')
    ui = load('client455-ui-startup-native')
    if ui['normal_link_sha256'] != digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Current exact PE Create required')
    names += ['client455-message-sizing-reference', 'client455-modal-native', 'client455-normal-preparation', 'client455-normal-link', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'ordinary_plain_rich_SetMsg': 'PASS', 'natural_pixel_extent_and_GDI_oracle': 'PASS',
              'actual_production_callers': 'PASS', 'localized_native_and_GPU': 'PASS', 'existing_Create': 'PASS',
              'rich_color_pixels': colors, 'empty_extent_domain': 'UNSUPPORTED', 'full_GUI_Tutorial': 'OPEN',
              'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names},
              'script_sha256': sha(Path(__file__)), 'gaps': reference['gaps'], 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-message-sizing-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL:ordinary modal plain/rich/pixel sizing/GDI/GPU/Create PASS;empty domain/fullGUI/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
