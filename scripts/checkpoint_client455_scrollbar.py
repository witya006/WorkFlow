"""Verify ordinary scrollbar source port;derived variants/full455 remain open."""
import hashlib
import json
import re
from pathlib import Path
from audit_client455_scrollbar import assembly_rows, sprite_frames
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
            raise ValueError('Changed scrollbar evidence: ' + row['file'])

    reference = load('client455-scrollbar-reference')
    native = load('client455-scrollbar-native')
    link = load('client455-normal-link')
    if validate_normal_link(link) != 'PASS':
        raise ValueError('Successful ordinary client link required')
    for report, script in [(reference, 'audit_client455_scrollbar.py'), (native, 'probe_client455_scrollbar.py')]:
        if report['script_sha256'] != sha(WS / 'scripts' / script):
            raise ValueError('Stale scrollbar verification')
    link_digest = sha(WS / 'inventory/client455-normal-link.json')
    if native['normal_link_sha256'] != link_digest or native['reference_sha256'] != sha(WS / 'inventory/client455-scrollbar-reference.json'):
        raise ValueError('Changed ordinary client/reference')
    if native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py') or native['source_sha256'] != sha(WS / native['source']):
        raise ValueError('Changed native probe inputs')
    preparation = load('client455-normal-preparation')
    generator = sha(WS / 'scripts/prepare_client455_normal.py')
    if native['generator_sha256'] != generator or preparation['script_sha256'] != generator:
        raise ValueError('Changed source generator')
    for name, digest in native['sources'].items():
        if digest != sha(WS / 'scripts/native' / name) or preparation['record_inputs'][name] != digest:
            raise ValueError('Changed ordinary scrollbar source')
    manifest = WS / preparation['manifest']
    if sha(manifest) != preparation['manifest_sha256']:
        raise ValueError('Changed generated sources')
    for row in json.loads(manifest.read_text()):
        check(row)
    assembly_count = 0
    for row in reference['raw_evidence']:
        check(row)
        actual = list(assembly_rows(json.loads((WS / row['file']).read_text())))
        if actual != row['assemblies']:
            raise ValueError('Changed complete scrollbar assembly')
        assembly_count += len(actual)
    if assembly_count != 15:
        raise ValueError('Missing scrollbar instruction dumps')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        binary = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = binary.read_bytes()
        if sha(binary) != pin['sha256'] or pe(raw)['architecture'] != 'x86' or len(pin['ranges']) != 23:
            raise ValueError('Changed455 pin/functions')
        for row in pin['ranges'] + pin['data']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed scrollbar contract')
    for row in reference['inputs']:
        for name in ['sprite', 'language']:
            if sha(Path(row[name]['file'])) != row[name]['sha256']:
                raise ValueError('Changed real scrollbar input')
        if sprite_frames(Path(row['sprite']['file'])) != row['sprite']['frames']:
            raise ValueError('Changed frame/clamp manifest')
    mapping = (WS / link['map']['file']).read_text()
    for symbol in ['SetAmount@CGUIScrollbar', 'MouseEvent@CGUIScrollbar', 'MouseMotionEvent@CGUIScrollbar', 'Draw@CGUIScrollbarButton']:
        if not re.search(re.escape(symbol) + r'[^\r\n]*guiscrollbar\.obj', mapping):
            raise ValueError('Missing ordinary scrollbar provider: ' + symbol)
    check(native['map'])
    if [row['nation'] for row in native['runs']] != ['Korea', 'Russia']:
        raise ValueError('Missing localized run')
    for row, ref, cp in zip(native['runs'], reference['inputs'], [949, 1251]):
        for name in ['exe', 'output']:
            check(row[name])
        image = pe((WS / row['exe']['file']).read_bytes())
        if image['architecture'] != 'x86' or image['entry_rva'] != int(native['entry_rva'], 16):
            raise ValueError('Wrong own scrollbar entry')
        for item in row['inputs']:
            check(item)
        if len(row['frames']) != 5:
            raise ValueError('Missing real/synthetic GPU scenarios')
        for frame in row['frames']:
            check(frame)
            if (frame['width'], frame['height']) != (640, 480) or (WS / frame['file']).stat().st_size != 640 * 480 * 4:
                raise ValueError('Wrong viewport size')
            if sha(WS / frame['preview']) != frame['preview_sha256']:
                raise ValueError('Changed preview')
        actual = json.loads((WS / row['output']['file']).read_text())
        if row['exit'] or actual != row['native'] or actual['status'] != 'PASS' or actual['codepage'] != cp:
            raise ValueError('Native scrollbar failed')
        for name in ['ordinary_scrollbar', 'composite_thumb', 'vertical_horizontal_geometry', 'minimum_and_linear_auto_size',
                     'x87_snap_and_SSE2_int32', 'DWORD_repeat_clock_and_query_order', 'mouse_drag_release_and_direction_quirk',
                     'actual_queued_scroll_events', 'child_count_removal_quirk']:
            if not actual[name]:
                raise ValueError('Missing scrollbar behavior: ' + name)
        if any(actual[name] for name in ['full_EX_Var', 'full_parent_bubbling', 'full_briefing', 'full_Tutorial']):
            raise ValueError('Scrollbar scope incorrectly broadened')
        if actual['real_action2_frames'] != ref['sprite']['frames']['frame_count']:
            raise ValueError('Real sprite count mismatch')
        if min(actual[name] for name in ['plain_pixels', 'segmented_pixels', 'pressed_pixels', 'synthetic_pixels', 'synthetic_pressed_pixels']) <= 0:
            raise ValueError('Missing GPU output')
        if row['frames'][3]['sha256'] == row['frames'][4]['sha256']:
            raise ValueError('Synthetic pressed state unchanged')
        if actual['real_action2_frames'] <= 44 and row['frames'][1]['sha256'] != row['frames'][2]['sha256']:
            raise ValueError('Real unavailable-frame clamp not preserved')
    for name in ['client455-text-board-native', 'client455-text-metrics-native', 'client455-font-native', 'client455-modal-native']:
        report = load(name)
        if report['normal_link_sha256'] != link_digest or any(row['exit'] or row['native']['status'] != 'PASS' for row in report['runs']):
            raise ValueError('Current affected GUI regression required: ' + name)
    tutorial = load('client455-tutorial-board-native')
    if tutorial['normal_link_sha256'] != link_digest or tutorial['native']['status'] != 'PASS':
        raise ValueError('Current tutorial modal regression required')
    ui = load('client455-ui-startup-native')
    if ui['normal_link_sha256'] != link_digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Current existing Create required')
    kernels, _ = kernel_sources(WS / 'scripts/native')
    if len(kernels) != 20:
        raise ValueError('Canonical kernel discovery changed')
    names = ['client455-scrollbar-reference', 'client455-scrollbar-native', 'client455-normal-preparation', 'client455-normal-link',
             'client455-text-board-native', 'client455-text-metrics-native', 'client455-font-native',
             'client455-modal-native', 'client455-tutorial-board-native', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'ordinary_scrollbar_geometry_amount_mouse_clock': 'PASS',
              'composite_thumb_and_row_sampling': 'PASS', 'x87_snap_and_supported_SSE2_conversion': 'PASS',
              'real_resource_clamp_and_owned_synthetic_GPU': 'PASS', 'affected_GUI_and_existing_Create': 'PASS',
              'EX_Var_and_complete_parent_input': 'OPEN', 'full_briefing': 'OPEN', 'full_Tutorial': 'OPEN',
              'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names}, 'gaps': reference['gaps'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-scrollbar-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL: ordinary scrollbar/composite/math/mouse/clock/GPU and affected regressions PASS; EX/Var/parent input/briefing/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
