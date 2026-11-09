"""Reproduce selected455 atmosphere reference and source-provenance evidence."""
import hashlib
import json
import struct
from pathlib import Path

from audit_client455_item_payloads import record
from audit_client455_texture_lifetime import archive_objects
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from compare_client_binaries import WS, pe


def merged_ranges(ranges):
    result = []
    for start, end in sorted(ranges):
        if result and start <= result[-1][1]:
            result[-1][1] = max(end, result[-1][1])
        else:
            result.append([start, end])
    return result


def main():
    raw_file = WS/'artifacts/client455-progress/sky-atmosphere126-reference.json'
    raw = json.loads(raw_file.read_text())
    selected = set(raw['selected'])
    assembly = {x['addr'].lower(): x for x in raw['assembly']}
    bounds = {x['query'].lower(): x['fn'] for x in raw['bounds']['result']}
    cfg = {x['addr'].lower(): x for x in raw['cfg']}
    require(len(selected) == 16 and selected == set(assembly) == set(bounds) == set(cfg),
            'Sixteen selected functions with bounds, assembly and CFG')
    ranges = []
    for at in sorted(selected):
        code = next(x for x in raw['functions'] if x['addr'].lower() == at)
        require(sum(p['line_count'] for p in code['pages']) == code['pages'][0]['total_lines']
                and code['pages'][-1]['cursor']['done'], 'Complete selected pcode')
        asm, graph = assembly[at], cfg[at]
        require(len(asm['lines']) == asm['total_instructions']
                == sum(p['instruction_count'] for p in asm['pages'])
                and asm['pages'][-1]['cursor']['done']
                and all(len(p['asm']['lines']) == p['instruction_count'] <= 100
                        for p in asm['pages']), 'Complete bounded assembly pages')
        addresses = {int(x['addr'], 16) for x in asm['lines']}
        require(len(addresses) == len(asm['lines']), 'Unique instructions')
        require(graph['cursor']['done'] and len(graph['blocks'])
                == graph['count'] == graph['total_blocks'], 'Complete CFG')
        blocks = [b for b in graph['blocks'] if b['size'] > 0]
        require(all(int(b['start'], 16) in addresses and
                    int(b['end'], 16)-int(b['start'], 16) == b['size']
                    for b in blocks), 'Every positive CFG block covered, including lower tails')
        start = int(at, 16)
        parts = [(start, start+int(bounds[at]['size'], 16))]
        parts += [(int(b['start'], 16), int(b['end'], 16)) for b in blocks]
        for begin, end in merged_ranges(parts):
            ranges.append((at, begin, end-begin))
    instructions = sum(x['total_instructions'] for x in assembly.values())
    require(instructions == 2029, 'Selected instruction total')
    session_file = WS/'artifacts/client455-progress/sky-atmosphere126-session.json'
    session = json.loads(session_file.read_text())
    require(session['closed']['success'] and session['closed']['saved']
            and session['after']['count'] == 0, 'Owned IDA saved/closed/list0')

    pins = json.loads((WS/'config/client-target.json').read_text())
    references = []
    context_ranges = [(0x8c5890, 20), (0x8c43f0, 12), (0x8da175, 5),
                      (0x90ae40, 12), (0x90ae5b, 12), (0x90ae76, 12),
                      (0x90afdf, 32), (0xbf7354, 4)]
    for folder, key in [('current', 'behavior_reference'),
                        ('reference-backup', 'secondary_reference')]:
        file = WS/f'work/client-reference/{folder}/RF_Online.bin'
        data = file.read_bytes()
        require(sha(file) == pins[key]['sha256'] and pe(data)['architecture'] == 'x86',
                'Pinned x86 reference')
        bodies = [dict(function=at, rva=hex(begin-0x400000), bytes=size,
                       sha256=hashlib.sha256(read_va(data, begin, size)).hexdigest())
                  for at, begin, size in ranges]
        calls = []
        for asm in assembly.values():
            for row in asm['lines']:
                if not row['instruction'].startswith('call ') or not row.get('refs'):
                    continue
                at = int(row['addr'], 16)
                b = read_va(data, at, 5)
                if b[0] != 0xe8:
                    continue
                target = int(row['refs'][0]['addr'], 16)
                require(at+5+struct.unpack('<i', b[1:])[0] == target, 'Decoded direct call')
                calls.append(dict(rva=hex(at-0x400000), target_rva=hex(target-0x400000)))
        literal_refs = {(int(r['addr'], 16), 8 if r['name'].startswith('dbl_') else 4)
                        for asm in assembly.values() for row in asm['lines']
                        for r in row.get('refs', [])
                        if r['name'].startswith(('flt_', 'dbl_')) and int(r['addr'], 16) < 0xc00000}
        literals = [dict(rva=hex(at-0x400000), bytes=n, hex=read_va(data, at, n).hex())
                    for at, n in sorted(literal_refs)]
        sun = bytes.fromhex('000000000200000000000c00020003000000180004000a0000001c0001000500ff00000011000000')
        dome = bytes.fromhex('000000000200000000000c0001000500ff00000011000000')
        require(read_va(data, 0xbf7878, 40) == sun and read_va(data, 0xbf78a0, 24) == dome,
                'Actual36byte Sun and20byte Dome declarations')
        require(read_va(data, 0xbf7354, 4) == struct.pack('<f', .03), 'Night Mie file initializer')
        for at, target in [(0x8c5890, 0x8da0c0), (0x8c589f, 0x8b1260),
                           (0x8c43f1, 0x8b1280), (0x8c43f6, 0x8da1d0),
                           (0x8da175, 0x8d8540)]:
            b = read_va(data, at, 5)
            require(b[0] == 0xe8 and at+5+struct.unpack('<i', b[1:])[0] == target,
                    'Context resource callback call')
        context = [dict(rva=hex(at-0x400000), bytes=n, hex=read_va(data, at, n).hex())
                   for at, n in context_ranges]
        row = dict(sha256=sha(file), architecture='x86', image_base='0x400000',
                   ranges=bodies, decoded_calls=calls, numeric_literals=literals,
                   sun_declaration=sun.hex(), dome_declaration=dome.hex(),
                   bounded_context_bytes=context)
        require(not references or {k:v for k,v in row.items() if k != 'sha256'}
                == {k:v for k,v in references[0].items() if k != 'sha256'},
                'Both455 selected code/data/context equal')
        references.append(row)

    engine = load('client455-startup-engine-build')
    require(engine['objects'] == 67 and len(engine['derived_sources']) == 17
            and engine['script_sha256'] == sha(WS/'scripts/build_client455_engine_startup.py'),
            'Current engine67/17derived')
    sources = [record(WS/'scripts/native'/n)
               for n in ['client455_sky_atmosphere.h', 'client455_sky_atmosphere.inc',
                         'client455_sky_material.inc', 'client455_weather.cpp']]
    require(engine['sky_atmosphere'] == {Path(x['file']).name:x['sha256'] for x in sources[:2]},
            'Exact atmosphere source inputs')
    for source in engine['base_sources']+engine['derived_sources']:
        check(source)
    assets = load('client455-sky-atmosphere-inputs')
    require(len(assets['inputs']) == 3, 'Three pinned actual resources')
    for asset in assets['inputs']:
        check(asset)
        require(sha(Path(asset['original'])) == asset['sha256'], 'Original resource unchanged')
    previous = json.loads((WS/'artifacts/client455-progress/client455-startup-engine-build-before126.json').read_text())
    for name in ['core_header_overlay', 'sky_header_overlay', 'bsp_header_overlay',
                 'camera_header_overlay', 'particle_header_overlay']:
        require(engine[name] == previous[name], 'Shared declaration/layout unchanged')
    old = WS/'artifacts/client455-progress/engine-before126.lib'
    require(sha(old) == previous['library_sha256'], 'Exact125 engine backup')
    a, b = archive_objects(old, True), archive_objects(WS/engine['library'], True)
    require(set(a) == set(b) and len(a) == 67, 'Same67 archive members')
    changed, stamp, same = [], [], []
    for name in a:
        x, y = a[name]['payload'], b[name]['payload']
        if x == y:
            same.append(name)
        elif len(x) == len(y) and x[:4]+x[8:] == y[:4]+y[8:]:
            stamp.append(name)
        else:
            changed.append(name)
    expected = {'level.obj', 'skybox.obj', 'r3d3d8.obj', 'r3vertexbuffer.obj', 'client455_weather.obj'}
    require({Path(x.replace('\\','/')).name for x in changed} == expected, 'Intended payload changes only')
    gaps = [
        'Only selected atmosphere/Sun update restored;remaining8B1F20 light colors,exposure globals,day/night fog,light position and lens flare remain open',
        'Scattering parameters use confirmed initial values and day transition;indirect console/file parameter writers and dynamic day/night Mie controls remain open',
        'SunColor uses modern CRT transcendental operations;full x87/CRT pow/cos/exp and allFP/RC parity is not accepted',
        'Selected Sun helper uses correct36byte target declaration;general legacy vertex helpers and other renderer consumers remain separate work',
        'Resource creation/release/recreate and missing shader selected paths checked;full lost/reset/OOM/reentry/capability changes remain open',
        'Own GPU readbacks are not running reference455 visual equivalence;INS/Planet/full world/stages/auth/gameplay/Character/fullclient acceptance remain open',
        'Missing original e_neutrala/trade_bel/trade_bel.r3e warning retained without substitution',
    ]
    out = dict(status='CONFIRMED_SELECTED', scope='Ordinary sky atmosphere prepass/resources and selected Sun scalar update',
               script_sha256=sha(Path(__file__)), raw=record(raw_file), session=record(session_file),
               full_assembly=16, instructions=instructions, CFG_coverage_including_lower_chunks=True,
               references=references, sources=sources, engine=record(WS/engine['library']), old_engine=record(old),
               payload_changed_members=changed, timestamp_only_members=stamp, unchanged_members=same,
               headers_unchanged=True, inputs=record(WS/'inventory/client455-sky-atmosphere-inputs.json'),
               gaps=gaps, input_exe_executed=False, server_modified=False,
               M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-sky-atmosphere-reference.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(dict(asm=16, instructions=instructions, ranges=len(ranges), changed=changed,
                          timestamp_only=len(stamp), unchanged=len(same))))


if __name__ == '__main__':
    main()
