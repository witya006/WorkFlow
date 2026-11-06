"""Validate ordinary TextBoard port; full scrollbar/briefing/Tutorial stay open."""
import hashlib
import json
import re
from pathlib import Path
from audit_client455_text_board import assemblies
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
            raise ValueError('Changed TextBoard evidence: ' + row['file'])

    reference = load('client455-text-board-reference')
    native = load('client455-text-board-native')
    link = load('client455-normal-link')
    if validate_normal_link(link) != 'PASS':
        raise ValueError('Successful ordinary client link required')
    for report, script in [(reference, 'audit_client455_text_board.py'), (native, 'probe_client455_text_board.py')]:
        if report['script_sha256'] != sha(WS / 'scripts' / script):
            raise ValueError('Stale TextBoard verification')
    if native['reference_sha256'] != sha(WS / 'inventory/client455-text-board-reference.json'):
        raise ValueError('Changed TextBoard reference')
    link_digest = sha(WS / 'inventory/client455-normal-link.json')
    if native['normal_link_sha256'] != link_digest or native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py'):
        raise ValueError('Changed full-object probe inputs')
    if native['source_sha256'] != sha(WS / native['source']):
        raise ValueError('Changed TextBoard probe source')
    generator_digest = sha(WS / 'scripts/prepare_client455_normal.py')
    preparation = load('client455-normal-preparation')
    if native['generator_sha256'] != generator_digest or preparation['script_sha256'] != generator_digest:
        raise ValueError('Changed ordinary client generator')
    for name, digest in native['sources'].items():
        if digest != sha(WS / 'scripts/native' / name) or preparation['record_inputs'][name] != digest:
            raise ValueError('Changed TextBoard source: ' + name)
    manifest = WS / preparation['manifest']
    if sha(manifest) != preparation['manifest_sha256']:
        raise ValueError('Changed normal source manifest')
    for row in json.loads(manifest.read_text()):
        check(row)
    assembly_count = 0
    for row in reference['raw_evidence']:
        check(row)
        actual = list(assemblies(json.loads((WS / row['file']).read_text())))
        if actual != row['assemblies']:
            raise ValueError('Changed complete instructions')
        assembly_count += len(actual)
    if assembly_count != 17:
        raise ValueError('Missing TextBoard instructions')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        binary = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = binary.read_bytes()
        if sha(binary) != pin['sha256'] or pe(raw)['architecture'] != 'x86' or len(pin['ranges']) != 49:
            raise ValueError('Changed455 pin/ranges')
        for row in pin['ranges'] + pin['data']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed TextBoard binary contract')
    for row in reference['inputs'] + reference['installed_runtime_sources']:
        if sha(Path(row['file'])) != row['sha256']:
            raise ValueError('Changed resource or installed CRT source')
    mapping = (WS / link['map']['file']).read_text()
    for symbol in ['InsertText@CGUITextBoard', 'Layout@CGUITextBoard', 'DrawLine@CGUITextBoard']:
        if not re.search(re.escape(symbol) + r'[^\r\n]*guitextboard\.obj', mapping):
            raise ValueError('Missing ordinary TextBoard provider: ' + symbol)
    if 'client455_crt_multibyte.obj' in mapping:
        raise ValueError('Redundant experimental CRT adapter retained')
    check(native['map'])
    probe_mapping = (WS / native['map']['file']).read_text()
    # The small copy helper is inlined into the production DrawLine; its
    # external entry is retained by explicit calls in the full-object probe.
    for symbol in ['RF455_CopyGuiTextBytes8', 'RF455_ParseFontTag', 'InsertFormatted455@CGUITextBoard', 'ResizeToText455@CGUITextBoard']:
        if not re.search(re.escape(symbol) + r'[^\r\n]*guitextboard\.obj', probe_mapping):
            raise ValueError('Missing full-object formatted/extent provider: ' + symbol)
    if [row['nation'] for row in native['runs']] != ['Korea', 'Russia']:
        raise ValueError('Missing localized TextBoard run')
    for row, cp in zip(native['runs'], [949, 1251]):
        for name in ['exe', 'output']:
            check(row[name])
        image = pe((WS / row['exe']['file']).read_bytes())
        if image['architecture'] != 'x86' or image['entry_rva'] != int(native['entry_rva'], 16):
            raise ValueError('Wrong own TextBoard entry')
        for item in row['inputs']:
            check(item)
        if len(row['frames']) != 4:
            raise ValueError('Missing GPU scenarios')
        for frame in row['frames']:
            check(frame)
            if (frame['width'], frame['height']) != (640, 480) or (WS / frame['file']).stat().st_size != 640 * 480 * 4:
                raise ValueError('Wrong TextBoard viewport')
            if sha(WS / frame['preview']) != frame['preview_sha256']:
                raise ValueError('Changed TextBoard preview')
        actual = json.loads((WS / row['output']['file']).read_text())
        if row['exit'] or actual != row['native'] or actual['status'] != 'PASS' or actual['codepage'] != cp:
            raise ValueError('TextBoard native failed')
        for name in ['typed_FONT_INFO16_TextInfo28', 'actual_TextBoard', 'pixel_wrap_and_DBCS', 'fragment_line_cache',
                     'newline_and_margin_quirks', 'retention_and_WORD_rebase', 'markup_and_sticky_attributes',
                     'BYTE_copy_wrap_and_reuse', 'scroll_amount_and_view', 'real_GPU_fragments', 'explicit_crt_dbcs_sbcs_copy']:
            if not actual[name]:
                raise ValueError('Missing TextBoard contract: ' + name)
        if min(actual['color_pixels'], actual['markup_pixels'], actual['bottom_pixels']) <= 0:
            raise ValueError('Missing actual GPU evidence')
        if any(actual[name] for name in ['full_scrollbar_input', 'full_briefing', 'full_Tutorial']):
            raise ValueError('TextBoard scope broadened')
    for name in ['client455-text-metrics-native', 'client455-font-native', 'client455-modal-native']:
        report = load(name)
        if report['normal_link_sha256'] != link_digest or any(row['exit'] or row['native']['status'] != 'PASS' for row in report['runs']):
            raise ValueError('Current affected GUI regression required: ' + name)
    tutorial = load('client455-tutorial-board-native')
    if tutorial['normal_link_sha256'] != link_digest or tutorial['native']['status'] != 'PASS':
        raise ValueError('Current tutorial modal integration required')
    ui = load('client455-ui-startup-native')
    if ui['normal_link_sha256'] != link_digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Existing ordinary Create regression required')
    kernels, _ = kernel_sources(WS / 'scripts/native')
    if len(kernels) != 20:
        raise ValueError('Canonical kernel discovery changed')
    names = ['client455-text-board-reference', 'client455-text-board-native', 'client455-normal-preparation',
             'client455-normal-link', 'client455-text-metrics-native', 'client455-font-native',
             'client455-modal-native', 'client455-tutorial-board-native', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'ordinary_TextBoard_layout_and_draw': 'PASS',
              'formatted_text_and_extent_in_full_object_probe': 'PASS', 'production_rich_text_callers': 'OPEN',
              'typed_FONT_INFO16_TextInfo28': 'PASS', 'WORD_retention_rebase_and_BYTE_copy': 'PASS',
              'actual_scroll_amount_view_and_GPU': 'PASS', 'affected_GUI_and_existing_Create': 'PASS',
              'full_scrollbar_input_and_geometry': 'OPEN', 'full_briefing': 'OPEN', 'full_Tutorial': 'OPEN',
              'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names}, 'gaps': reference['gaps'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-text-board-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL: ordinary TextBoard/cache/markup/WORD/BYTE/GPU and affected regressions PASS; fullscrollbar/briefing/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
