"""Verify the GDI/CGUIText source port without accepting full TextBoard or455."""
import hashlib
import json
import re
from pathlib import Path

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
            raise ValueError('Changed text-metrics evidence: ' + row['file'])

    reference = load('client455-text-metrics-reference')
    native = load('client455-text-metrics-native')
    link = load('client455-normal-link')
    if validate_normal_link(link) != 'PASS':
        raise ValueError('Successful ordinary client link required')
    for report, script in [(reference, 'audit_client455_text_metrics.py'),
                           (native, 'probe_client455_text_metrics.py')]:
        if report['script_sha256'] != sha(WS / 'scripts' / script):
            raise ValueError('Stale text-metrics verification')
    if native['reference_sha256'] != sha(WS / 'inventory/client455-text-metrics-reference.json'):
        raise ValueError('Changed reference manifest')
    link_digest = sha(WS / 'inventory/client455-normal-link.json')
    if native['normal_link_sha256'] != link_digest or native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py'):
        raise ValueError('Changed ordinary client inputs')
    if native['source_sha256'] != sha(WS / native['source']):
        raise ValueError('Changed native metric probe')

    preparation = load('client455-normal-preparation')
    if preparation['script_sha256'] != sha(WS / 'scripts/prepare_client455_normal.py'):
        raise ValueError('Stale client source generator')
    for name, digest in native['sources'].items():
        if digest != sha(WS / 'scripts/native' / name) or preparation['record_inputs'][name] != digest:
            raise ValueError('Changed ordinary text source: ' + name)
    manifest = WS / preparation['manifest']
    if sha(manifest) != preparation['manifest_sha256']:
        raise ValueError('Changed normal source manifest')
    for row in json.loads(manifest.read_text()):
        check(row)

    if len(reference['references']) != 2 or len(reference['assemblies']) != 5:
        raise ValueError('Missing reference evidence')
    for row in reference['raw_evidence'] + reference['assemblies']:
        check(row)
    for row in reference['assemblies']:
        body = json.loads((WS / row['file']).read_text())
        if not body['cursor']['done'] or len(body['asm']['lines']) != row['instructions']:
            raise ValueError('Incomplete metric instructions')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        binary = WS / f'work/client-reference/{folder}/RF_Online.bin'
        image = pe(binary.read_bytes())
        if sha(binary) != pin['sha256'] or image['architecture'] != 'x86' or image['image_base'] != 0x400000:
            raise ValueError('Changed455 pin identity')
        if len(pin['ranges']) != 15:
            raise ValueError('Missing metric function ranges')
        raw = binary.read_bytes()
        for row in pin['ranges'] + pin['data']:
            actual = read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])
            if hashlib.sha256(actual).hexdigest() != row['sha256']:
                raise ValueError('Changed455 metric contract')
    for row in reference['inputs']:
        if sha(Path(row['file'])) != row['sha256']:
            raise ValueError('Changed reference language data')

    check(native['map'])
    mapping = (WS / link['map']['file']).read_text()
    # Byte fitting is tested in the full-object probe; its production caller
    # will be introduced with the still-open TextBoard port.
    for symbol, provider in [
        ('SetString@CGUIText', 'guitext.obj'),
        ('RF455_UpdateGuiTextSize', 'RFClient455Facade:client455_gui_text_metrics.obj'),
        ('RF455_ForgetGuiText', 'RFClient455Facade:client455_gui_text_metrics.obj'),
        ('RF455_TextWidth', 'RFClient455Facade:client455_text_metrics.obj'),
        ('RF455_DefaultTextHeight', 'RFClient455Facade:client455_text_metrics.obj'),
    ]:
        if not re.search(re.escape(symbol) + r'[^\r\n]*' + re.escape(provider), mapping, re.I):
            raise ValueError('Missing ordinary provider: ' + symbol)
    if [row['nation'] for row in native['runs']] != ['Korea', 'Russia']:
        raise ValueError('Missing localized metric run')
    for row, codepage in zip(native['runs'], [949, 1251]):
        for name in ['exe', 'output', 'frame']:
            check(row[name])
        if pe((WS / row['exe']['file']).read_bytes())['entry_rva'] != int(native['entry_rva'], 16):
            raise ValueError('Wrong own metric entry')
        for item in row['inputs']:
            check(item)
        frame = row['frame']
        if (frame['width'], frame['height']) != (640, 480) or (WS / frame['file']).stat().st_size != 640 * 480 * 4:
            raise ValueError('Wrong metric viewport')
        if sha(WS / frame['preview']) != frame['preview_sha256']:
            raise ValueError('Changed metric preview')
        actual = json.loads((WS / row['output']['file']).read_text())
        if row['exit'] or actual != row['native'] or actual['status'] != 'PASS' or actual['codepage'] != codepage:
            raise ValueError('Native metric verification failed')
        for name in ['actual_CGUIText_geometry', 'style_flag_fallthrough', 'default_height_cache',
                     'partial_DBCS_prefix', 'early_geometry_after_font_ready', 'localized_fixture_roundtrip']:
            if not actual[name]:
                raise ValueError('Missing metric behavior: ' + name)
        if min(actual['byte_prefix_oracle_cases'], actual['fit_oracle_cases'], actual['rendered_pixels']) <= 0:
            raise ValueError('Missing independent GDI or rendered evidence')
        if any(actual[name] for name in ['full_TextBoard', 'FreeType_route', 'full_Tutorial']):
            raise ValueError('Metric scope incorrectly broadened')

    font = load('client455-font-native')
    modal = load('client455-modal-native')
    ui = load('client455-ui-startup-native')
    for report in [font, modal, ui]:
        if report['normal_link_sha256'] != link_digest:
            raise ValueError('Current affected regression required')
    for row in font['runs']:
        if row['exit'] or row['native']['status'] != 'PASS' or not row['native']['gdi_metrics_and_atlas_equal']:
            raise ValueError('Affected font regression failed')
        if sha(WS / row['output']) != row['output_sha256']:
            raise ValueError('Changed font regression output')
    for row in modal['runs']:
        check(row['output'])
        if row['exit'] or row['native']['status'] != 'PASS' or not row['native']['real_modal_controls']:
            raise ValueError('Affected ordinary modal regression failed')
    if not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Existing ordinary Create regression failed')
    kernels, _ = kernel_sources(WS / 'scripts/native')
    if len(kernels) != 20:
        raise ValueError('Canonical kernel discovery changed')

    names = ['client455-text-metrics-reference', 'client455-text-metrics-native',
             'client455-normal-preparation', 'client455-normal-link', 'client455-font-native',
             'client455-modal-native', 'client455-ui-startup-native']
    report = {
        'status': 'PARTIAL',
        'ordinary_GDI_CGUIText_geometry': 'PASS',
        'byte_prefix_and_DBCS_fit_GDI_oracle': 'PASS',
        'first_height_cache_and_style_fallthrough': 'PASS',
        'owned_early_geometry_lifecycle_adapter': 'PASS',
        'affected_font_modal_and_existing_Create': 'PASS',
        'full_TextBoard_and_scrollbar': 'OPEN',
        'FreeType_and_16byte_font_scale': 'OPEN',
        'full_Tutorial': 'OPEN',
        'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names},
        'gaps': reference['gaps'],
        'input_exe_executed': False, 'server_modified': False,
        'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN',
    }
    (WS / 'inventory/client455-text-metrics-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL: ordinary GDI text geometry/byte metrics/lifecycle and affected regressions PASS; fullTextBoard/FreeType/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
