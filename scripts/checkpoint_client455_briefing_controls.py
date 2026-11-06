"""Accept verified controls and typing base-Draw correction;fullwindow remains open."""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image
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
            raise ValueError('Changed controls evidence:' + row['file'])

    reference, native, link = load('client455-briefing-controls-reference'), load('client455-briefing-controls-native'), load('client455-normal-link')
    validate_normal_link(link)
    digest = sha(WS / 'inventory/client455-normal-link.json')
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_briefing_controls.py') or native['script_sha256'] != sha(WS / 'scripts/probe_client455_briefing_controls.py') or native['reference_sha256'] != sha(WS / 'inventory/client455-briefing-controls-reference.json'):
        raise ValueError('Stale controls audit/probe')
    if native['normal_link_sha256'] != digest or native['source_sha256'] != sha(WS / native['source']) or native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py'):
        raise ValueError('Stale controls build')
    preparation = load('client455-normal-preparation')
    if preparation['script_sha256'] != sha(WS / 'scripts/prepare_client455_normal.py'):
        raise ValueError('Stale controls generator')
    for name, value in native['sources'].items():
        if value != sha(WS / 'scripts/native' / name) or preparation['record_inputs'][name] != value:
            raise ValueError('Changed controls source:' + name)
    for row in reference['raw_evidence']:
        check(row)
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256']:
            raise ValueError('Changed455pin')
        for row in pin['ranges'] + pin['data']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed control contract')
    for row in reference['inputs']:
        for role in ['common', 'tutorial', 'language']:
            if sha(Path(row[role]['file'])) != row[role]['sha256']:
                raise ValueError('Changed control resource')
    check(native['map'])
    mapping = (WS / native['map']['file']).read_text()
    for symbol in ['Update@RF455GuiAnimatedImage', 'SetRows455@CGUITutorialKeyBoard', 'Draw@CGUIBriefingBoard']:
        if not re.search(re.escape(symbol) + r'[^\r\n]*RFClient455Facade:client455_briefing_controls.obj', mapping, re.I):
            raise ValueError('Control probe lost source provider:' + symbol)
    for run in native['runs']:
        for field in ['exe', 'output']:
            check(run[field])
        for row in run['inputs'] + run['frames']:
            check(row)
        actual = json.loads((WS / run['output']['file']).read_text())
        if run['exit'] or actual != run['native'] or actual['status'] != 'PASS' or pe((WS / run['exe']['file']).read_bytes())['architecture'] != 'x86':
            raise ValueError('Controls native failed')
        for key in ['real_frame_caps', 'body_border_GPU', 'alpha_RGB', 'key_rows_gaps_stale', 'sprite_padding_UV', 'sheet_animation_pause_loop', 'forced_UV_and_zero_grid']:
            if not actual[key]:
                raise ValueError('Missing control behavior:' + key)
        if actual['key_selectors'] != 17 or actual['ordinary_briefing'] or actual['full_Tutorial'] or len(run['frames']) != 10:
            raise ValueError('Wrong control scope')
        frame = next(row for row in run['frames'] if row['file'].endswith('briefing-frame-self-fill.bgra'))
        image = Image.frombytes('RGBA', (640, 480), (WS / frame['file']).read_bytes(), 'raw', 'BGRA')
        if image.getpixel((100, 100))[:3] != (0x55, 0x66, 0x77) or image.getpixel((33, 100))[:3] != (0x55, 0x66, 0x77):
            raise ValueError('Base fill does not cover body/border before caps')
    typing = load('client455-text-typing-native')
    if typing['normal_link_sha256'] != digest:
        raise ValueError('Current corrected typing probe required')
    for run in typing['runs']:
        frame = next(row for row in run['frames'] if row['file'].endswith('typing-self-fill.bgra'))
        check(frame)
        raw = (WS / frame['file']).read_bytes()
        red = sum(raw[i:i + 3] == b'\0\0\xff' for i in range(0, len(raw), 4))
        if red != 80000:
            raise ValueError('Typing own-fill correction failed')
    gate = load('client455-text-typing-checkpoint')
    if gate['status'] != 'PARTIAL' or gate['evidence_sha256']['client455-normal-link'] != digest:
        raise ValueError('Corrected typing gate stale')
    ui = load('client455-ui-startup-native')
    if ui['normal_link_sha256'] != digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1 or ui['executable']['sha256'] != link['executable']['sha256']:
        raise ValueError('Exact current PE Create required')
    names = ['client455-briefing-controls-reference', 'client455-briefing-controls-native', 'client455-briefing-controls-production', 'client455-text-typing-native', 'client455-text-typing-checkpoint', 'client455-normal-preparation', 'client455-normal-link', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'source_frame_key_animation_controls': 'PASS', 'real_resources_and_GPU': 'PASS',
              'typing_base_Draw_correction': 'PASS', 'exact_current_PE_Create': 'PASS',
              'prior_GUI_evidence': 'REUSED_ONLY_AFTER_RUNTIME_BYTE_EQUALITY_EXCEPT_LINK_TIMESTAMPS',
              'ordinary_briefing_window': 'OPEN', 'full_Tutorial': 'OPEN', 'gaps': reference['gaps'],
              'script_sha256': sha(Path(__file__)), 'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names},
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-briefing-controls-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL:source frame/key/animation and corrected typing/baseDraw/GPU/Create PASS;fullbriefing/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
