"""Pin the455 RVP loader and independently decode its source-owned load model."""
import hashlib
import json
import math
import re
import struct
from collections import Counter
from pathlib import Path

from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bits(value):
    return struct.unpack('<I', struct.pack('<f', value))[0]


def number(text):
    match = re.match(r'^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', text)
    value = float(match[0]) if match else 0.0
    if not math.isfinite(value):
        raise ValueError('Unaccepted nonfinite RVP numeric domain')
    return struct.unpack('<f', struct.pack('<f', value))[0]


def integer(text):
    match = re.match(r'^[+-]?\d+', text)
    value = int(match[0]) if match else 0
    return max(-2147483648, min(2147483647, value)) & 0xffffffff


def decode(raw, dummies=None):
    # Target fscanf("%s") has NO comment stripping. Semicolon/underscore tokens
    # are unknown tokens, and the following tokens are still examined.
    raw = raw.split(b'\x1a', 1)[0]
    tokens = iter(part.decode('latin1') for part in re.split(br'[ \t\r\n\v\f]+', raw) if part)
    doc = dict(flags=0, totalFrame=0, ignoredTokens=0, actors=[], tracks=[])
    mode, frame = 0, 0
    def named(name, limit=None):
        return next((i for i, a in enumerate(doc['actors'][:limit])
                     if not a['flags'] & 2 and a['name'] == name), 0xffffffff)
    def arg():
        return next(tokens)
    def actor():
        return dict(flags=0, color=0, meshId=0, magicIndex=0, linkedActor=0xffffffff,
                    traceAction=0, traceOn=0, traceOff=0,
                    scale=bits(1), waveDistance=0, xAngle=0, yAngle=0,
                    **{key: '' for key in ['name', 'mesh', 'bone', 'texturePath', 'wave',
                                          'swordTrace', 'magicId', 'mapDummy']}, animations=[])
    sections = {'[object]': 1, '[preparetrack]': 2, '[track]': 3}
    string_props = {'texpath': 'texturePath', 'bone': 'bone', 'char_dummy': 'bone',
                    'sword_trace': 'swordTrace', 'magic_id': 'magicId'}
    floats = {'scale': 'scale', 'wav_dist': 'waveDistance', 'x_angle': 'xAngle', 'y_angle': 'yAngle'}
    for token in tokens:
        token = token.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))
        if token in sections:
            mode = sections[token]
            continue
        if mode == 1:
            if token.startswith('*'):
                a = actor()
                if token == '*magic':
                    a.update(flags=2, magicIndex=integer(arg()))
                else:
                    a.update(name=token, mesh=arg())
                doc['actors'].append(a)
                continue
            if not doc['actors']:
                doc['ignoredTokens'] += 1
                continue
            a = doc['actors'][-1]
            if token in string_props:
                a[string_props[token]] = arg()
            elif token in floats:
                a[floats[token]] = bits(number(arg()))
            elif token in ['collision', 'shadow']:
                a['flags'] |= 4 if token == 'collision' else 8
            elif token == 'color':
                rgb = [int(struct.unpack('<i', struct.pack('<I', integer(arg())))[0] / 2) for _ in range(3)]
                a.update(color=(0xff000000 | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]) & 0xffffffff,
                         flags=a['flags'] | 1)
            elif token == 'trace_on_off':
                a.update(zip(['traceAction', 'traceOn', 'traceOff'], [integer(arg()) for _ in range(3)]))
            elif token == 'mesh_id':
                a['meshId'] = integer(arg())
            elif token == 'ani':
                a['animations'].append(arg())
            elif token == 'wav':
                a['wave'] = arg()
                if a['waveDistance'] & 0x7fffffff == 0:
                    a['waveDistance'] = bits(200)
            elif token == 'char_link':
                a['texturePath'] = arg()
                index = named(a['texturePath'], len(doc['actors']) - 1)
                if index != 0xffffffff:
                    a['linkedActor'] = index
            elif token == 'map_dummy':
                a['mesh'] = a['mapDummy'] = arg()
            else:
                doc['ignoredTokens'] += 1
            continue
        if mode == 3 and token == '*frame':
            frame = bits(number(arg()))
            continue
        if mode == 2:
            if token == 'total_frame':
                doc['totalFrame'] = int(number(arg())) & 0xffffffff
                continue
            if token in ['wide', 'logo', 'no_camera', 'screen']:
                doc['flags'] |= {'wide': 1, 'logo': 2, 'no_camera': 4, 'screen': 8}[token]
                continue
            if token.startswith('*'):
                index = named(token)
                if index != 0xffffffff:
                    doc['actors'][index]['mapDummy'] = arg()
                else:
                    doc['ignoredTokens'] += 1
                continue
        if not mode:
            doc['ignoredTokens'] += 1
            continue
        track = dict(kind=0, frame=frame, first=0, second=0, actor=0xffffffff, value=0,
                     reference='', resource='', attachment='')
        if token == 'camera':
            track.update(kind=1, reference=arg().lower())
        elif token in ['fade_in', 'fade_out']:
            track.update(kind=2 if token == 'fade_in' else 3, value=integer(arg()))
        elif token in ['ani', 'char_fade_in', 'char_fade_out']:
            track.update(kind={'ani': 0x84, 'char_fade_in': 0x86, 'char_fade_out': 0x87}[token], actor=named(arg()))
            if track['actor'] == 0xffffffff:
                doc['ignoredTokens'] += 1
                continue
            track['value'] = integer(arg())
        elif token in ['magic', 'throw']:
            index = integer(arg())
            track.update(kind=0x88 if token == 'magic' else 0x8c,
                         actor=next((i for i, a in enumerate(doc['actors'])
                                     if a['flags'] & 2 and a['magicIndex'] == index), 0xffffffff))
            if track['actor'] == 0xffffffff:
                doc['ignoredTokens'] += 1
                continue
            if token == 'throw':
                track['reference'] = arg()
                if dummies is None:
                    raise ValueError('Throw requires camera names')
                if track['reference'][1:] not in dummies:
                    if named(track['reference'], len(doc['actors']) - 1) == 0xffffffff:
                        doc['ignoredTokens'] += 1
                        continue
                    track['attachment'] = arg()
        elif token == 'quake':
            track.update(kind=5, first=bits(number(arg())), second=bits(number(arg())))
        elif token == 'wav':
            track.update(kind=0x89, reference=arg(), resource=arg(), first=bits(number(arg())))
        elif token in ['blur', 'timer_rate']:
            track.update(kind=10 if token == 'blur' else 11, first=bits(number(arg())))
        else:
            doc['ignoredTokens'] += 1
            continue
        doc['tracks'].append(track)
    return doc


def main():
    evidence = WS / 'artifacts/client455-progress/rvp078-paged.json'
    body = json.loads(evidence.read_text())
    target = json.loads((WS / 'config/client-target.json').read_text())
    pins = []
    for folder, key in [('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]:
        path = WS / 'work/client-reference' / folder / 'RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != target[key]['sha256'] or pe(raw)['architecture'] != 'x86':
            raise ValueError('Changed455 pin')
        ranges = []
        for row in body['ranges']['result']:
            if row['error']:
                continue  # 8D4CD0 discovery was not a defined function, not claimed as one.
            address, size = int(row['fn']['addr'], 16), int(row['fn']['size'], 16)
            ranges.append(dict(rva=hex(address - 0x400000), bytes=size,
                               sha256=hashlib.sha256(read_va(raw, address, size)).hexdigest()))
        if pins and ranges != pins[0]['ranges']:
            raise ValueError('RVP455 ranges differ between pins')
        pins.append(dict(sha256=sha(path), architecture='x86', image_base='0x400000', ranges=ranges))
        if read_va(raw, 0xb378dc, 4) != b'wav\0':
            raise ValueError('RVP wave command string differs')
    assemblies = list(assembly_rows([body['create_asm'], body['curve_asm']]))
    if not body['create_tail']['cursor']['done']:
        raise ValueError('Incomplete Create pseudocode tail')
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    inputs, kinds, resources = [], Counter(), {}
    for path in sorted((root / 'Map').rglob('*.rvp')):
        doc = decode(path.read_bytes())
        kinds.update(row['kind'] for row in doc['tracks'])
        wanted = []
        for actor in doc['actors']:
            if not actor['flags'] & 2:
                wanted += [('mesh', actor['mesh']), ('bone', actor['bone']), ('texture_directory', actor['texturePath'])]
                wanted += [('animation', name) for name in actor['animations']]
            wanted += [('wave', actor['wave']), ('sword_trace', actor['swordTrace'])]
        wanted += [('wave', track['resource']) for track in doc['tracks'] if track['kind'] == 0x89]
        for kind, name in wanted:
            if not name:
                continue
            key = (kind, name.lower())
            if key not in resources:
                asset = root / name
                resources[key] = dict(kind=kind, relative=name, exists=asset.is_dir() if kind == 'texture_directory' else asset.is_file())
                if asset.is_file():
                    resources[key].update(sha256=sha(asset), bytes=asset.stat().st_size)
        row = dict(file=str(path), relative=path.relative_to(root).as_posix(), sha256=sha(path),
                   bytes=path.stat().st_size, actors=len(doc['actors']), tracks=len(doc['tracks']),
                   flags=doc['flags'], total_frame=doc['totalFrame'],
                   semantic_sha256=hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest())
        inputs.append(row)
    report = dict(scope='RVP source-owned load model/interpolation; full actor/audio/movie runtime remains required',
                  references=pins, assemblies=assemblies,
                  raw_evidence=dict(file=evidence.relative_to(WS).as_posix(), sha256=sha(evidence)),
                  script_sha256=sha(Path(__file__)), inputs=inputs,
                  totals=dict(files=len(inputs), actors=sum(r['actors'] for r in inputs),
                              tracks=sum(r['tracks'] for r in inputs), kinds=dict(kinds),
                              unique_resource_references=len(resources),
                              missing_resource_references=sum(not row['exists'] for row in resources.values())),
                  resource_references=list(resources.values()),
                  gaps=['Actual engine RTMovie player is still a compiled stub',
                        'Resource binding and effects/Character/actor/audio handles and side effects not implemented by this load model',
                        'Loader independent-if argument-keyword fallthrough, malformed/overflow and locale domains not fully certified',
                        'Full CGP_Tutorial/fourstage/auth/gameplay and all prior M6F/M7/M9 gaps remain'],
                  input_exe_executed=False, server_modified=False, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-rvp-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['totals']))


if __name__ == '__main__':
    main()
