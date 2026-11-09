"""Current partialM6 gate for actual atmosphere resources/prepass and Sun state."""
import json
from pathlib import Path

from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check, load, require, sha
from checkpoint_client455_sky_material import reviewed
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_sky_atmosphere import verify as verify_atmosphere
from probe_client455_sky_material import verify as verify_material
from probe_client455_sky_fade import verify as verify_fade
from probe_client455_world_frame import verify as verify_world


def previous_pixels(native, name):
    previous = json.loads((WS/f'artifacts/client455-progress/{name}-before126.json').read_text())
    byname = {Path(x['file']).name:x for x in previous['frames']}
    same = []
    for row in native['frames']:
        before = byname[Path(row['file']).name]
        check(before)
        require(row['sha256'] == before['sha256'], 'Previous125 frame preserved')
        same.append(Path(row['file']).name)
    return same


def native_provenance(native, link_hash):
    require(native['normal_link_sha256'] == link_hash and not native['natural_exit']
            and native['inputs_unchanged'], 'Current normal libraries and completed lab')
    require(native['script_sha256'] == sha(WS/'scripts/probe_client455_nuclear_registry.py')
            and native['builder_sha256'] == sha(WS/'scripts/client455_own_probe.py')
            and native['runtime_inputs_sha256'] == sha(WS/'scripts/client455_runtime_inputs.py'),
            'Exact current lab generator and staged resources')
    for key in ['source', 'included_source', 'driver_script', 'exe', 'map', 'console', 'output']:
        check(native[key])
    for row in native['inputs']:
        check(row)


def main():
    ref = load('client455-sky-atmosphere-reference')
    require(ref['status'] == 'CONFIRMED_SELECTED' and ref['full_assembly'] == 16
            and ref['instructions'] == 2029 and ref['CFG_coverage_including_lower_chunks']
            and ref['headers_unchanged'] and len(ref['payload_changed_members']) == 5
            and len(ref['unchanged_members']) == 62
            and ref['script_sha256'] == sha(WS/'scripts/audit_client455_sky_atmosphere.py'),
            'Current pin/source proof including lower function chunks')
    for row in [ref[x] for x in ['raw', 'session', 'engine', 'old_engine', 'inputs']]+ref['sources']:
        check(row)
    link = load('client455-normal-link')
    require(validate_normal_link(link) == 'PASS', 'Exact normal link')
    lh = sha(WS/'inventory/client455-normal-link.json')
    engine = load('client455-startup-engine-build')
    require(engine['library_sha256'] == ref['engine']['sha256']
            and any(x['file'] == engine['library'] and x['sha256'] == ref['engine']['sha256']
                    for x in link['libraries']), 'Current engine retained in ordinary PE')
    mapping = (WS/link['map']['file']).read_text(errors='replace')
    require(all(x in mapping for x in ['DrawSkyBoxRender@CLevel', 'DrawSkyBox@CSkyBox',
                'RF455_DrawSkyAtmosphere', 'RF455_UpdateSunValues', 'RF455_CreateSkyResources',
                'RF455_ReleaseSkyResources', 'RF455_SetVPIPTex1KeepingShader']),
            'Ordinary executable retains atmosphere update/draw/resources')

    atmosphere = reviewed('client455-sky-atmosphere', 5)
    native_provenance(atmosphere, lh)
    for row in [atmosphere['world_source'], atmosphere['trace']]+atmosphere['buffers']:
        check(row)
    av = verify_atmosphere((WS/atmosphere['exe']['file']).parent)
    require(atmosphere['status'] == 'PASS_SELECTED' and av == atmosphere['verdict']
            and av['prepass_cases'] == 16 and av['scalar_sun_cases'] == 72
            and av['geometry_max_absolute_error'] == 0
            and atmosphere['native']['released_by_device_callback']
            and atmosphere['native']['sun_width'] == atmosphere['native']['sun_height'] == 256,
            'Actual atmosphere geometry/shader/states/Sun bits/resources')
    material = reviewed('client455-sky-material', 5)
    native_provenance(material, lh)
    check(material['oracle']); check(material['trace'])
    mv = verify_material((WS/material['exe']['file']).parent)
    require(mv == material['verdict'] and mv['material_cases'] == 36
            and mv['profile_cases'] == 60 and mv['direct_unloaded_state'],
            'Current material/night-weight/unloaded regression')
    missing = Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'Map/Entity/e_neutrala/trade_bel/trade_bel.r3e'
    require(not missing.exists() and atmosphere['native']['warnings']
            == material['native']['warnings'] == 1, 'Known original missing resource warning retained')
    world = reviewed('client455-world-frame', 5)
    native_provenance(world, lh)
    validation = load('client455-world-frame-verification')
    require(world['status'] == 'PASS' and validation['native_sha256']
            == sha(WS/'inventory/client455-world-frame-native.json')
            and verify_world((WS/world['exe']['file']).parent) == world['verdict'] == validation['verdict'],
            'Current real world regression')
    fade = reviewed('client455-sky-fade', 5)
    native_provenance(fade, lh)
    require(fade['status'] == 'PASS_SELECTED' and not fade['native']['warnings']
            and verify_fade((WS/fade['exe']['file']).parent) == fade['verdict'],
            'Current actual fade regression')
    same_world = previous_pixels(world, 'client455-world-frame-native')
    same_fade = previous_pixels(fade, 'client455-sky-fade-native')
    consumers = load('client455-normal-consumers')
    require(consumers['native']['status'] == 'PASS'
            and consumers['normal_build_sha256'] == link['normal_build_sha256'], 'ANI/BBX native consumers')
    for row in consumers['libraries']+consumers['objects']:
        check(row)
    early, ui, contracts = load('client455-startup-native'), load('client455-ui-startup-native'), load('client455-startup-contracts-native')
    require(early['normal_link_sha256'] == ui['normal_link_sha256'] == lh
            and not early['debugger_exit'] and early['sound_return'] == 1
            and not ui['debugger_exit'] and ui['completed_existing_client_create']
            and any(x['name'] == 'after_client_create' and x['eax'] == 1 for x in ui['markers'])
            and contracts['build_sha256'] == sha(WS/'inventory/client455-startup-engine-build.json')
            and ui['script_sha256'] == sha(WS/'scripts/probe_client455_device_startup.py'),
            'Current own PE sound/device/existingCreate1/contracts')
    check(early['events']); check(ui['events'])
    for asset in load('client455-sky-atmosphere-inputs')['inputs']:
        require(any(x['file'].endswith('/'+asset['runtime_relative'])
                    and x['sha256'] == asset['sha256'] for x in ui['inputs']),
                'Ordinary device startup staged actual sky resources')
    previous = WS/'artifacts/client455-progress/client455-sky-material-checkpoint-before126.json'
    require(previous.exists(), 'Previous125 gate preserved')
    fresh = ['sky-atmosphere-reference', 'sky-atmosphere-inputs', 'sky-atmosphere-native',
             'sky-atmosphere-visual-review', 'sky-material-native', 'sky-material-visual-review',
             'sky-fade-native', 'sky-fade-visual-review', 'world-frame-native',
             'world-frame-verification', 'world-frame-visual-review', 'startup-engine-build',
             'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-native',
             'startup-contracts-native', 'ui-startup-native']
    out = dict(status='PARTIAL', scope=ref['scope'], script_sha256=sha(Path(__file__)),
               normal_executable=link['executable'], normal_link_sha256=lh,
               engine=ref['engine'], old_engine=ref['old_engine'], atmosphere=av,
               material=mv, fade=fade['verdict'], world=world['verdict'],
               world_frames_byte_equal125=same_world, fade_frames_byte_equal125=same_fade,
               viewed_GPU_frames=20, previous125_gate=record(previous),
               fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},
               full_lighting=False, full_atmosphere=False, full_world=False, gaps=ref['gaps'],
               unchanged_bulk_suites_rerun=False, input_exe_executed=False, server_modified=False,
               M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-sky-atmosphere-checkpoint.json').write_text(json.dumps(out, indent=2)+'\n')
    print('PARTIAL:16prepass/72Sun/4225vertices/8192triangles;20GPUviewed;material/fade/world/Create1PASS;full lighting/M9OPEN')


if __name__ == '__main__':
    main()
