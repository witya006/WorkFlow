"""Accept bounded real minimap owner/control evidence;full455remains OPEN."""
import hashlib
import json
import re
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from audit_client455_minimap_opacity import sprite_geometry
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
            raise ValueError('Changed opacity evidence:' + row['file'])

    reference, native, link = load('client455-minimap-opacity-reference'), load('client455-minimap-opacity-native'), load('client455-normal-link')
    validate_normal_link(link)
    link_digest = sha(WS / 'inventory/client455-normal-link.json')
    if native['normal_link_sha256'] != link_digest or native['reference_sha256'] != sha(WS / 'inventory/client455-minimap-opacity-reference.json'):
        raise ValueError('Refresh own opacity runs')
    for owner, name in [(reference, 'audit_client455_minimap_opacity.py'), (native, 'probe_client455_minimap_opacity.py')]:
        if owner['script_sha256'] != sha(WS / 'scripts' / name):
            raise ValueError('Changed opacity script')
    if sha(WS / native['source']) != native['source_sha256'] or native['generator_sha256'] != sha(WS / 'scripts/prepare_client455_normal.py') or native['builder_sha256'] != sha(WS / 'scripts/client455_own_probe.py'):
        raise ValueError('Changed native build route')
    for name, digest in native['sources'].items():
        if sha(WS / 'scripts/native' / name) != digest:
            raise ValueError('Changed opacity algorithm')
    implementation = WS / 'work/client455-port/normal/source/userinterface/gamewindow/etcwin/guiminimapwindow.cpp'
    if not implementation.read_bytes().endswith((WS / 'scripts/native/client455_minimap_opacity_owner.inc').read_bytes()):
        raise ValueError('Normal owner differs from verified implementation')
    total = 0
    for row in reference['raw_evidence']:
        check(row)
        body = json.loads((WS / row['file']).read_text())
        actual = list(assembly_rows(body.get('assemblies', []) if isinstance(body, dict) else body))
        if actual != row['assemblies']:
            raise ValueError('Incomplete opacity disassembly')
        total += len(actual)
    if total != 10:
        raise ValueError('Missing complete opacity assembly')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        binary = WS / f'work/client-reference/{folder}/RF_Online.bin'
        raw = binary.read_bytes()
        if sha(binary) != pin['sha256'] or pe(raw)['architecture'] != 'x86' or len(pin['ranges']) != 17:
            raise ValueError('Changed pinned455 image')
        for row in pin['ranges'] + pin['data']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed target opacity bytes')
    for row in reference['inputs']:
        for name, requests in [('common', {(8, f) for f in range(6, 19)}), ('main', {(5, 0), (5, 32)})]:
            item = row[name]
            if sha(Path(item['file'])) != item['sha256'] or sprite_geometry(Path(item['file']), requests) != item['geometry']:
                raise ValueError('Changed real minimap art')
    mapping = (WS / link['map']['file']).read_text()
    for symbol, provider in [('ScrollEvent@CGUIMiniMapWindow', 'guiminimapwindow.obj'), ('SetAlpha455@CGUIMiniMapWindow', 'guiminimapwindow.obj'), ('SetAmount@CGUIScrollbarEX', 'guiscrollbar.obj'), ('RF455_ConfigureOpacityScrollbar', 'RFClient455Facade:client455_minimap_opacity.obj')]:
        if not re.search(re.escape(symbol) + r'[^\r\n]*' + re.escape(provider), mapping):
            raise ValueError('Missing actual production provider:' + symbol)
    check(native['map'])
    if [r['nation'] for r in native['runs']] != ['Korea', 'Russia']:
        raise ValueError('Missing localized run')
    for row, cp in zip(native['runs'], [949, 1251]):
        for name in ['exe', 'output']:
            check(row[name])
        for item in row['inputs']:
            check(item)
        image = pe((WS / row['exe']['file']).read_bytes())
        actual = json.loads((WS / row['output']['file']).read_text())
        if image['architecture'] != 'x86' or image['entry_rva'] != int(native['entry_rva'], 16) or row['exit'] or actual != row['native'] or actual['status'] != 'PASS' or actual['codepage'] != cp:
            raise ValueError('Invalid own opacity runtime')
        for key in ['real_owner_EX', 'style0_and1', 'alignment', 'actual_mouse_parent_path', 'drag_release_quirk', 'mapped_alpha_groups', 'zoom_gate_state', 'camera_consumer_refused']:
            if not actual[key]:
                raise ValueError('Missing owner behavior:' + key)
        if actual['queued_amounts'] != 81 or any(actual[name] for name in ['full_minimap', 'target_parent_input', 'full_Tutorial']):
            raise ValueError('Invalid opacity scope')
        if len(row['frames']) != 3 or len({f['sha256'] for f in row['frames']}) != 3:
            raise ValueError('Missing distinct opacity GPU scenarios')
        for frame in row['frames']:
            check(frame)
            if (frame['width'], frame['height']) != (640, 480) or (WS / frame['file']).stat().st_size != 640 * 480 * 4 or sha(WS / frame['preview']) != frame['preview_sha256']:
                raise ValueError('Changed opacity frame')
        if min(actual[name] for name in ['full_pixels', 'half_pixels', 'low_pixels']) < 10000:
            raise ValueError('Missing actual frame/map background draw')
    for name in ['client455-scrollbar-variants-native', 'client455-scrollbar-native', 'client455-text-board-native', 'client455-text-metrics-native', 'client455-font-native', 'client455-modal-native']:
        report = load(name)
        if report['normal_link_sha256'] != link_digest or any(row['exit'] or row['native']['status'] != 'PASS' for row in report['runs']):
            raise ValueError('Affected GUI regression missing:' + name)
    tutorial, ui = load('client455-tutorial-board-native'), load('client455-ui-startup-native')
    if tutorial['normal_link_sha256'] != link_digest or tutorial['native']['status'] != 'PASS' or ui['normal_link_sha256'] != link_digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax'] != 1:
        raise ValueError('Current Create/modal regression missing')
    kernels, _ = kernel_sources(WS / 'scripts/native')
    if len(kernels) != 20:
        raise ValueError('Canonical kernel discovery changed')
    names = ['client455-minimap-opacity-reference', 'client455-minimap-opacity-native', 'client455-normal-preparation', 'client455-normal-link', 'client455-scrollbar-variants-native', 'client455-scrollbar-native', 'client455-text-board-native', 'client455-text-metrics-native', 'client455-font-native', 'client455-modal-native', 'client455-tutorial-board-native', 'client455-ui-startup-native']
    report = {'status': 'PARTIAL', 'actual_owner_EX_and_queued_mouse': 'PASS', 'normal_production_providers': 'PASS',
              'real_common_main_GPU_and_opacity81': 'PASS', 'affected_GUI_and_existing_Create': 'PASS',
              'full_minimap_and_camera_consumer': 'OPEN', 'target_parent_input': 'OPEN',
              'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in names}, 'gaps': reference['gaps'],
              'input_exe_executed': False, 'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-minimap-opacity-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL: actual minimap opacity owner/production EX/mouse queue/GPU and GUI/Create PASS;fullminimap/camera/target input/M9 OPEN')


if __name__ == '__main__':
    main()
