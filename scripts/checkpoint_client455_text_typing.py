"""Accept the typing dependency domain; ordinary briefing/Tutorial stay open."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
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
            raise ValueError('Changed typing evidence:' + row['file'])

    reference, native, link = load('client455-text-typing-reference'), load('client455-text-typing-native'), load('client455-normal-link')
    validate_normal_link(link)
    digest = sha(WS / 'inventory/client455-normal-link.json')
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_text_typing.py') or native['script_sha256'] != sha(WS / 'scripts/probe_client455_text_typing.py') or native['reference_sha256'] != sha(WS / 'inventory/client455-text-typing-reference.json'):
        raise ValueError('Stale typing audit/probe')
    if native['normal_link_sha256'] != digest or native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py') or native['source_sha256'] != sha(WS / native['source']):
        raise ValueError('Stale typing build')
    preparation = load('client455-normal-preparation')
    if preparation['script_sha256'] != sha(WS / 'scripts/prepare_client455_normal.py'):
        raise ValueError('Stale typing generator')
    for name, value in native['sources'].items():
        if value != sha(WS / 'scripts/native' / name) or preparation['record_inputs'][name] != value:
            raise ValueError('Changed typing source:' + name)
    for row in reference['raw_evidence']:
        check(row)
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256']:
            raise ValueError('Changed455pin')
        for row in pin['ranges'] + pin['data']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed typing contract')
    check(native['map'])
    mapping = (WS / native['map']['file']).read_text()
    for symbol in ['Update@CGUITextTypingBoard', 'Draw@CGUITextTypingBoard', 'StartTyping455@CGUITextTypingBoard']:
        if not re.search(re.escape(symbol) + r'[^\r\n]*RFClient455Facade:client455_gui_text_typing_board.obj', mapping, re.I):
            raise ValueError('Typing native probe lost real source provider:' + symbol)
    if native['production_briefing_connected']:
        raise ValueError('Ordinary briefing must not be claimed by a component probe')
    for run, cp in zip(native['runs'], [949, 1251]):
        for field in ['exe', 'output']:
            check(run[field])
        for item in run['inputs'] + run['frames']:
            check(item)
        actual = json.loads((WS / run['output']['file']).read_text())
        binary = pe((WS / run['exe']['file']).read_bytes())
        if run['exit'] or actual != run['native'] or actual['status'] != 'PASS' or actual['codepage'] != cp or binary['architecture'] != 'x86':
            raise ValueError('Typing runtime failed')
        for key in ['delay_interval_cursor_trace', 'spaces_and_fragment_boundary', 'newline_page_range', 'resource_DBCS_not_CRT', 'zero_and_DWORD_wrap', 'virtual_Clear_retained_flags', 'hidden_and_children', 'negative_domain_refused']:
            if not actual[key]:
                raise ValueError('Missing typing trace:' + key)
        if actual['production_briefing'] or actual['full_Tutorial'] or actual['clock_queries'] != 42:
            raise ValueError('Incorrect typing scope or query count')
        if len(run['frames']) != 7 or run['frames'][1]['sha256'] != run['frames'][2]['sha256']:
            raise ValueError('Partial text differs from independent plain prefix')
    # Fixed prior commit pins the shared renderer's unchanged GPU output. It is
    # read only; no checkout, history rewrite, remote operation or input EXE run.
    baseline = '7115112'
    names = ['client455-text-board-native', 'client455-modal-native', 'client455-font-native', 'client455-text-metrics-native', 'client455-scrollbar-native', 'client455-scrollbar-variants-native', 'client455-minimap-opacity-native']
    compared = []
    def frames(run):
        if 'frames' in run:
            return run['frames']
        if isinstance(run.get('frame'), dict):
            return [run['frame']]
        return [{'file': run['frame'], 'sha256': run['frame_sha256']}]

    for name in names:
        current = load(name)
        if current['normal_link_sha256'] != digest or any(row['exit'] or row['native']['status'] != 'PASS' for row in current['runs']):
            raise ValueError('Current affected GUI required:' + name)
        old = json.loads(subprocess.check_output(['git', '-c', 'safe.directory=' + str(WS), 'show', baseline + ':inventory/' + name + '.json'], cwd=WS))
        for current_run, old_run in zip(current['runs'], old['runs']):
            now_frames, old_frames = frames(current_run), frames(old_run)
            if len(now_frames) != len(old_frames) or [x['sha256'] for x in now_frames] != [x['sha256'] for x in old_frames]:
                raise ValueError('Shared GUI GPU frame changed:' + name)
            compared.extend({'nation': current_run['nation'], 'file': frame['file'], 'sha256': frame['sha256']} for frame in now_frames)
    if len(compared) != 44:
        raise ValueError('Incomplete shared GUI GPU regression')
    ui = load('client455-ui-startup-native')
    if ui['normal_link_sha256'] != digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Current existing Create required')
    names += ['client455-text-typing-reference', 'client455-text-typing-native', 'client455-normal-preparation', 'client455-normal-link', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'typing_source_compiled_in_normal_facade': 'PASS', 'actual_full_object_typing_trace_and_GPU': 'PASS',
              'shared_renderer_GUIs_and_Create': 'PASS', 'shared_GUI_baseline_commit': baseline, 'unchanged_shared_GPU_frames': compared,
              'ordinary_briefing_instance': 'OPEN', 'full_Tutorial': 'OPEN', 'gaps': reference['gaps'],
              'script_sha256': sha(Path(__file__)), 'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names},
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-text-typing-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL:typing source/native/GPU and44unchanged GUI frames/Create PASS;production briefing/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
