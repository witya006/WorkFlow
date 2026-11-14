"""Extract at most three unchanged top-mip lobby UV atlases; never run game code."""
import argparse
import hashlib
import io
import json
import re
import struct
from pathlib import Path

from PIL import Image
from map455 import MapFile, inspect_r3t
from build_client455_x87_math import read_va

WS = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cstring(data):
    return data.split(b'\0', 1)[0].decode('cp949', errors='replace')


def materials(data):
    if len(data) < 8:
        raise ValueError('Short R3M header')
    version, count = struct.unpack_from('<II', data)
    if version != 0x3f8ccccd or not 0 < count <= 2048:
        raise ValueError('Unsupported R3M version/count')
    result, at = [], 8
    for index in range(count):
        if at + 144 > len(data):
            raise ValueError('Truncated material header')
        layers, flags, detail, scale = struct.unpack_from('<IIif', data, at)
        name = cstring(data[at+16:at+144]); at += 144
        if layers > 7 or at + layers*46 > len(data):
            raise ValueError('Invalid material layers')
        entries = []
        for layer in range(layers):
            tile, surface, alpha, argb, layer_flags = struct.unpack_from('<hiIII', data, at)
            entries.append(dict(surface=surface, texture_index=surface-1, alpha=alpha,
                                argb=hex(argb), flags=hex(layer_flags), tile_frames=tile))
            at += 46
        opaque = (layers == 1 and not flags & ~3 and detail == -1 and
                  entries[0]['alpha'] == 0 and int(entries[0]['argb'], 16) >> 24 == 255 and
                  not int(entries[0]['flags'], 16) & ~0x30000)
        result.append(dict(index=index, name=name, flags=hex(flags), detail_surface=detail,
                           layers=entries, basic_opaque=opaque, bsp_groups=0, bsp_faces=0))
    if at != len(data):
        raise ValueError('R3M trailing bytes')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--material', action='append', default=[], help='Exact material name; maximum three distinct atlases')
    args = parser.parse_args()
    source = WS/'work/client455-preview/runtime/Map/lobby'
    inputs = {ext: (source/f'lobby.{ext}').read_bytes() for ext in ('r3m', 'r3t', 'bsp')}
    rows = materials(inputs['r3m'])
    bsp = MapFile(inputs['bsp'], 'bsp')
    if bsp.sequential_offset_mismatches():
        raise ValueError('BSP stored/sequential offsets disagree')
    groups = bsp.read('ReadMatGroup')
    if len(groups) % 42:
        raise ValueError('Truncated BSP material group')
    for at in range(0, len(groups), 42):
        attr, faces, first, material, light = struct.unpack_from('<HHIhh', groups, at)
        if material < 0:
            continue
        if material >= len(rows):
            raise ValueError('BSP material outside table')
        rows[material]['bsp_groups'] += 1; rows[material]['bsp_faces'] += faces
    pe_path = WS/'work/client-reference/current/RF_Online.bin'
    pe = pe_path.read_bytes()
    pinned = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))['behavior_reference']
    if sha(pe) != pinned['sha256']:
        raise ValueError('Pinned DDS header-mask source changed')
    mask = read_va(pe, 0xbf7f00, 128)
    raw = inputs['r3t']; checked = inspect_r3t(raw, mask)
    textures, at = [], 8 + 128*len(checked['textures'])
    for index, item in enumerate(checked['textures']):
        size = struct.unpack_from('<I', raw, at)[0]; at += 4
        dds = raw[at:at+size]
        if item['masked_header']:
            dds = bytes(a ^ b for a, b in zip(dds[:128], mask)) + dds[128:]
        textures.append(dict(item, name=cstring(raw[8+128*index:8+128*(index+1)]), offset=at, dds=dds))
        at += size
    for row in rows:
        for layer in row['layers']:
            index = layer['texture_index']
            if not 0 <= index < len(textures):
                raise ValueError('Serialized R3M surface outside R3T (expected one-based)')
            layer['texture_name'] = textures[index]['name']
    if not args.material:
        for row in sorted(rows, key=lambda r: r['bsp_faces'], reverse=True):
            if row['basic_opaque'] and row['bsp_groups']:
                print(json.dumps(row, ensure_ascii=True))
        return
    selected = [r for r in rows if r['name'] in args.material]
    if {r['name'] for r in selected} != set(args.material) or any(not r['basic_opaque'] for r in selected):
        raise ValueError('Selection includes missing/non-basic-opaque material')
    indices = sorted({r['layers'][0]['texture_index'] for r in selected})
    if not 1 <= len(indices) <= 3:
        raise ValueError('Select one to three unique atlases')
    output = WS/'work/client-art/lobby-materials'; output.mkdir(parents=True, exist_ok=True)
    exports = []
    for index in indices:
        texture = textures[index]
        stem = re.sub(r'[^A-Za-z0-9_-]+', '_', Path(texture['name'].replace('\\', '/')).stem)
        filename = f'{index:03d}-{stem}.png'
        image = Image.open(io.BytesIO(texture['dds'])); image.load(); image = image.convert('RGBA')
        if image.size != (texture['width'], texture['height']):
            raise ValueError('Decoded DDS size differs from header')
        image.save(output/filename)
        with Image.open(output/filename) as reread:
            if reread.convert('RGBA').tobytes() != image.tobytes():
                raise ValueError('PNG round-trip changed decoded DDS pixels')
        exports.append(dict(texture_index=index, texture_name=texture['name'], png=filename,
                            size=list(image.size), dds_sha256=sha(texture['dds']), png_sha256=sha((output/filename).read_bytes()),
                            rgba_sha256=sha(image.tobytes()), dds_offset=texture['offset'], dds_size=texture['size'],
                            fourcc=texture['fourcc'], mipmaps=texture['mipmap_count'],
                            materials=[r for r in rows if r['layers'] and r['layers'][0]['texture_index'] == index]))
    report = dict(inputs={ext: dict(path=str(source/f'lobby.{ext}'), size=len(data), sha256=sha(data)) for ext, data in inputs.items()},
                  material_count=len(rows), texture_count=len(textures), bsp_group_count=len(groups)//42,
                  dds_mask=dict(pe_sha256=sha(pe), architecture='x86', rva='0x7f7f00', sha256=sha(mask)),
                  mapping='R3M surface is one-based: loader adds texture-start minus 1 before R3T registration.',
                  decode='Exact top-mip DDS decompression to RGBA PNG. No crop, resize, retouch, gamma conversion or UV change.',
                  limits='BSP face/group counts are usage evidence, not screen coverage. No live material-ID capture; no authored normal/roughness data inferred.',
                  exports=exports)
    receipt = output/'inputs.json'
    if receipt.exists():
        prior = json.loads(receipt.read_text(encoding='utf-8'))
        if prior['inputs'] != report['inputs']:
            raise ValueError('Input set changed; preserve prior evidence before extracting')
        by_index = {item['texture_index']: item for item in prior['exports']}
        by_index.update({item['texture_index']: item for item in exports})
        report['exports'] = [by_index[index] for index in sorted(by_index)]
    receipt.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(output=str(output), pngs=[e['png'] for e in exports]), ensure_ascii=True))


if __name__ == '__main__':
    main()
