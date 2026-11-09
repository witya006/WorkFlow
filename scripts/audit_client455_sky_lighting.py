"""Pin selected lighting contracts and the separately tested source arithmetic."""
import hashlib
import json
import struct
from pathlib import Path

from audit_client455_item_payloads import record
from audit_client455_sky_atmosphere import merged_ranges
from checkpoint_client455_rvp_effects import check, load, require, sha
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe
from probe_client455_sky_lighting_math import verify


def main():
    raw_file = WS/'artifacts/client455-progress/sky-lighting127-reference.json'
    raw = json.loads(raw_file.read_text())
    selected = set(raw['selected'])
    assembly = {x['addr']:x for x in raw['assembly']}
    bounds = {x['query'].lower():x['fn'] for x in raw['bounds']['result']}
    cfg = {x['addr']:x for x in raw['cfg']}
    require(selected == set(assembly) == set(bounds) == set(cfg)
            and len(selected) == 17, 'Seventeen selected full functions')
    ranges = []
    for at in sorted(selected):
        code = next(x for x in raw['functions'] if x['addr'].lower() == at)
        require(sum(p['line_count'] for p in code['pages']) == code['pages'][0]['total_lines']
                and code['pages'][-1]['cursor']['done'], 'Complete selected pcode')
        a, g = assembly[at], cfg[at]
        addresses = {int(x['addr'], 16) for x in a['lines']}
        require(len(addresses) == len(a['lines']) == a['total_instructions']
                == sum(p['instruction_count'] for p in a['pages'])
                and a['pages'][-1]['cursor']['done']
                and all(len(p['asm']['lines']) == p['instruction_count'] <= 100 for p in a['pages']),
                'Complete bounded unique assembly')
        require(g['cursor']['done'] and len(g['blocks']) == g['count'] == g['total_blocks'],
                'Complete CFG')
        blocks = [b for b in g['blocks'] if b['size'] > 0]
        require(all(int(b['start'], 16) in addresses for b in blocks), 'Every positive CFG block covered')
        start = int(at, 16)
        parts = [(start, start+int(bounds[at]['size'], 16))]
        parts += [(int(b['start'], 16), int(b['end'], 16)) for b in blocks]
        ranges += [(at, begin, end-begin) for begin, end in merged_ranges(parts)]
    instructions = sum(a['total_instructions'] for a in assembly.values())
    require(instructions == 1538, 'Selected instruction total')
    session_file = WS/'artifacts/client455-progress/sky-lighting127-session.json'
    session = json.loads(session_file.read_text())
    require(session['closed']['success'] and session['closed']['saved']
            and session['after']['count'] == 0, 'Owned IDA saved/closed/list0')
    previous = WS/raw['reused_from']
    previous_raw = json.loads(previous.read_text())
    for at in raw['reused_assembly']:
        require(assembly[at] == next(x for x in previous_raw['assembly'] if x['addr'] == at),
                'Exact cached assembly reused')
    contexts = [(0x8b1220, 7), (0x8c3440, 64), (0x8c35a8, 64),
                (0x90af80, 144), (0x90a7d0, 48), (0x90a990, 64), (0xbf734c, 8)]
    pins = json.loads((WS/'config/client-target.json').read_text())
    references = []
    for folder, key in [('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]:
        file = WS/f'work/client-reference/{folder}/RF_Online.bin'
        data = file.read_bytes()
        require(sha(file) == pins[key]['sha256'] and pe(data)['architecture'] == 'x86', 'Pinned x86 input')
        bodies = [dict(function=at, rva=hex(begin-0x400000), bytes=size,
                       sha256=hashlib.sha256(read_va(data, begin, size)).hexdigest())
                  for at, begin, size in ranges]
        calls = []
        for a in assembly.values():
            for row in a['lines']:
                if not row['instruction'].startswith('call ') or not row.get('refs'):
                    continue
                at = int(row['addr'], 16)
                b = read_va(data, at, 5)
                if b[0] != 0xe8:
                    continue
                target = int(row['refs'][0]['addr'], 16)
                require(at+5+struct.unpack('<i', b[1:])[0] == target, 'Decoded direct call')
                calls.append(dict(rva=hex(at-0x400000), target_rva=hex(target-0x400000)))
        for at, target in [(0x8b2032, 0x900cd0), (0x8b235d, 0x8b1640), (0x8b2576, 0x8b2670)]:
            b = read_va(data, at, 5)
            require(b[0] == 0xe8 and at+5+struct.unpack('<i', b[1:])[0] == target,
                    'Previous Sun position/current light/then fog sampling order')
        require(read_va(data, 0x8b1220, 7) == b'\xd9\x05'+struct.pack('<I', 0x1154de8)+b'\xc3',
                'Unrecognized function bounded getter bytes;not fallback disasm count')
        require(read_va(data, 0xbf734c, 8) == b'\xff'*8, 'Both packed colors initialize FFFFFFFF')
        require(read_va(data, 0xaa9bb8, 8) == struct.pack('<d', .89999997615814208984375)
                and read_va(data, 0xb369b0, 4) == struct.pack('<f', 4294967296.0),
                'Exact divisor scale and unsigned correction')
        literal_refs = {(int(r['addr'], 16), 8 if r['name'].startswith('dbl_') else 4)
                        for a in assembly.values() for row in a['lines'] for r in row.get('refs', [])
                        if r['name'].startswith(('flt_', 'dbl_')) and int(r['addr'], 16) < 0xc00000}
        literals = [dict(rva=hex(at-0x400000), bytes=n, hex=read_va(data, at, n).hex())
                    for at, n in sorted(literal_refs)]
        context = [dict(rva=hex(at-0x400000), bytes=n, hex=read_va(data, at, n).hex())
                   for at, n in contexts]
        row = dict(sha256=sha(file), architecture='x86', image_base='0x400000',
                   ranges=bodies, decoded_calls=calls, numeric_literals=literals,
                   bounded_context_bytes=context)
        require(not references or {k:v for k,v in row.items() if k != 'sha256'}
                == {k:v for k,v in references[0].items() if k != 'sha256'}, 'Both455 selected evidence equal')
        references.append(row)
    native = load('client455-sky-lighting-math-native')
    require(native['script_sha256'] == sha(WS/'scripts/probe_client455_sky_lighting_math.py')
            and not native['natural_exit'] and not native['ordinary_runtime_integrated'], 'Current component only')
    for row in native['sources']+[native[x] for x in ['oracle', 'exe', 'trace', 'engine', 'normal_executable']]:
        check(row)
    verdict = verify(WS/native['trace']['file'])
    require(verdict == native['verdict'], 'Reproduced independent exact selected arithmetic')
    runtime = load('client455-sky-atmosphere-checkpoint')
    require(runtime['status'] == 'PARTIAL' and runtime['engine'] == native['engine']
            and runtime['normal_executable'] == native['normal_executable'], 'Runtime126 unchanged')
    gaps = [
        'Arithmetic is a separate source component,not yet called by ordinary frame;runtime gate remains126',
        'Restore full289point software scattering fog and flag2 endpoint ownership together with ordinary frame order and previous-frame Sun position',
        'Wire actual R3X/text endpoints,exposure setter,map texture-factor consumer and packed-tint consumers;other INS/Planet owners remain separate',
        'Modern CRT SunColor/scattering transcendental parity,allFP/RC/NaN/Inf and full lighting/reset/stage/gameplay/client acceptance remain open',
        'Zero divisor has no target fallback;do not silently substitute a successful black/default fog result',
    ]
    out = dict(status='PARTIAL_COMPONENT', scope='Confirmed ordinary455 lighting/fog contracts and exact selected source arithmetic',
               script_sha256=sha(Path(__file__)), raw=record(raw_file), session=record(session_file),
               reused_reference=record(previous), full_assembly=17, instructions=instructions,
               CFG_complete=True, references=references, component=record(WS/'inventory/client455-sky-lighting-math-native.json'),
               verdict=verdict, ordinary_runtime_gate=record(WS/'inventory/client455-sky-atmosphere-checkpoint.json'),
               ordinary_runtime_integrated=False, engine=native['engine'], normal_executable=native['normal_executable'],
               gaps=gaps, input_exe_executed=False, server_modified=False,
               M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-sky-lighting-reference.json').write_text(json.dumps(out, indent=2)+'\n')
    print('PARTIAL_COMPONENT:17fullasm/1538instructions/both455/129exactselectedcases;runtime126unchanged/full lighting OPEN')


if __name__ == '__main__':
    main()
