"""Generate the two GPU stream declarations recovered from supplied client code.

These are GPU stream layouts, not guessed CHARACTEROBJECT/ObjectMesh class layouts.
"""
import hashlib
import json
import struct
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    comparison = json.loads((WS / 'inventory/client-binary-comparison.json').read_text(encoding='utf-8'))
    inputs = comparison['inputs']
    body = []
    for entry in inputs:
        raw = Path(entry['copy']).read_bytes()
        rva = 0x51fd40
        section = next(s for s in entry['pe']['sections'] if s['rva'] <= rva < s['rva']+s['raw_size'])
        offset = rva-section['rva']+section['raw_offset']
        body.append(raw[offset:offset+0x2d2])
    if body[0] != body[1]:
        raise ValueError('Analyzed initialization differs between backup and target')
    rows = [
        [(0, 0, 2, 0, 0, 0), (0, 12, 2, 0, 1, 0), (0, 24, 7, 0, 2, 0),
         (0, 32, 2, 0, 3, 0), (0, 44, 1, 0, 5, 0), (0, 52, 2, 0, 6, 0), (255, 0, 17, 0, 0, 0)],
        [(0, 0, 2, 0, 0, 0), (0, 12, 0, 0, 1, 0), (0, 16, 2, 0, 3, 0),
         (0, 28, 1, 0, 5, 0), (255, 0, 17, 0, 0, 0)]
    ]
    target = WS / 'work/recovered/character455'
    target.mkdir(parents=True, exist_ok=True)
    header = '''#pragma once
#include <cstddef>
#include <cstdint>
#include <d3d9.h>
namespace rf455_recovered {
struct GpuVertex64 {
    float position[3];
    float blend_weights[3];
    std::int16_t blend_indices[4];
    float normal[3];
    float uv[2];
    float tangent[3];
};
struct GpuVertex36 {
    float position[3];
    float blend_weight;
    float normal[3];
    float uv[2];
};
static_assert(sizeof(GpuVertex64)==64);
static_assert(offsetof(GpuVertex64, blend_weights)==12);
static_assert(offsetof(GpuVertex64, blend_indices)==24);
static_assert(offsetof(GpuVertex64, normal)==32);
static_assert(offsetof(GpuVertex64, uv)==44);
static_assert(offsetof(GpuVertex64, tangent)==52);
static_assert(sizeof(GpuVertex36)==36);
static_assert(offsetof(GpuVertex36, blend_weight)==12);
static_assert(offsetof(GpuVertex36, normal)==16);
static_assert(offsetof(GpuVertex36, uv)==28);
static_assert(sizeof(D3DVERTEXELEMENT9)==8);
static_assert(D3DDECLTYPE_FLOAT1==0 && D3DDECLTYPE_FLOAT2==1 && D3DDECLTYPE_FLOAT3==2);
static_assert(D3DDECLTYPE_SHORT4==7 && D3DDECLTYPE_UNUSED==17);
'''
    for i, elements in enumerate(rows):
        header += f'inline constexpr D3DVERTEXELEMENT9 declaration_{i}[] = {{\n'
        header += ''.join('    {' + ','.join(str(x) for x in row) + '},\n' for row in elements)
        header += '};\n'
    header += '}\n'
    (target / 'vertex_declarations.hpp').write_text(header, encoding='ascii')
    probe = '''#include "vertex_declarations.hpp"
#include <cstdio>
int main() {
  for (const auto &e : rf455_recovered::declaration_0) {
    if (std::fwrite(&e, sizeof(e), 1, stdout)!=1) return 2;
  }
  for (const auto &e : rf455_recovered::declaration_1) {
    if (std::fwrite(&e, sizeof(e), 1, stdout)!=1) return 2;
  }
  return 0;
}
'''
    # Binary stdout on Windows is selected by the caller's _setmode addition below.
    probe = probe.replace('#include <cstdio>', '#include <cstdio>\n#include <io.h>\n#include <fcntl.h>')
    probe = probe.replace('int main() {', 'int main() {\n  _setmode(_fileno(stdout), _O_BINARY);')
    (target / 'probe.cpp').write_text(probe, encoding='ascii')
    expected = b''.join(struct.pack('<HHBBBB', *row) for elements in rows for row in elements)
    (target / 'expected.bin').write_bytes(expected)
    report = {'binary_sha256': inputs[1]['sha256'], 'architecture': 'x86', 'function_va': '0x91fd40',
              'function_rva': '0x51fd40', 'function_size': '0x2d2',
              'function_sha256': hashlib.sha256(body[1]).hexdigest(), 'same_function_bytes_as_backup': True,
              'source': 'sub_91FD40 stack-built D3DVERTEXELEMENT9 arrays; full decompile stored locally',
              'declarations': rows, 'gpu_struct_sizes': [64, 36], 'expected_bytes_sha256': hashlib.sha256(expected).hexdigest(),
              'limit': 'GPU stream compatibility only; no CPU Character class layout or renderer equivalence claimed.'}
    (WS / 'inventory/character455-vertex-layouts.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('Generated two recovered GPU vertex declarations; native ABI probe pending.')


if __name__ == '__main__':
    main()
