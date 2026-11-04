"""Recover partial legacy Character memory views from checked COFF instructions.

No Character.h substitute and no 455 CPU layout is inferred from the old library.
Unknown regions remain opaque; all generated C++ stays under ignored work/.
"""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from export_character_analysis import WS, coff_function_records


def operand(record, offset, prefix, width=4):
    code = record['bytes']
    if code is None or code[offset:offset+len(prefix)] != prefix:
        raise ValueError('Instruction does not match the inspected x86 encoding')
    start = offset+len(prefix)
    if start+width > len(code):
        raise ValueError('Truncated instruction operand')
    return int.from_bytes(code[start:start+width], 'little')


def main():
    inputs = json.loads((WS/'inventory/character-codeview.json').read_text(encoding='utf-8'))
    objects = {}
    for index in (3, 5, 6, 8, 9):
        item = inputs['objects'][index-1]
        data = (WS/item['working_object']).read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Character object digest changed')
        objects[index] = (item, coff_function_records(data))
    evidence = []

    def fact(name, index, symbol, offset, prefix, expected, width=4):
        item, functions = objects[index]
        record = functions[symbol]
        value = operand(record, offset, bytes.fromhex(prefix), width)
        if value != expected:
            raise ValueError(f'Unexpected operand for {name}: {value}')
        evidence.append({'fact': name, 'value': value, 'object': item['working_object'],
                         'object_sha256': item['sha256'], 'symbol': symbol,
                         'section': record['section'], 'symbol_section_offset': record['section_offset'],
                         'instruction_function_offset': hex(offset),
                         'instruction_file_offset': hex(record['file_offset']+offset),
                         'bytes': record['bytes'][offset:offset+len(bytes.fromhex(prefix))+width].hex(),
                         'function_sha256': hashlib.sha256(record['bytes']).hexdigest(), 'rva': None})
        return value

    load = '?LoadMeshData@ChInterface@@QAEPAVCHARACTEROBJECT@@PAVTextureManager@@PAVCObjectManager@@PAD_NPAV2@@Z'
    set_alpha = '?SetAlpha@ChInterface@@QAEXPAVCHARACTEROBJECT@@M@Z'
    get_alpha = '?GetAlpha@ChInterface@@QAEMPAVCHARACTEROBJECT@@@Z'
    effect = '?IsHaveEffect@ObjectMesh@@QAEHXZ'
    alloc = fact('CHARACTEROBJECT allocation bytes', 6, load, 0x18, '68', 776)
    stride = fact('ObjectMesh array stride in SetAlpha', 6, set_alpha, 0x1f, '05', 1072)
    fact('ObjectMesh constructor memory accounting bytes', 9, '??0ObjectMesh@@QAE@XZ', 0x0f, '05', stride)
    animation_size = fact('ChAnimation allocation bytes', 5, '?AddAnimation@AnimationManager@@QAE_NPAD@Z', 0x5e, '68', 280)
    count = fact('CHARACTEROBJECT mesh count offset', 6, set_alpha, 4, '8b8a', 528)
    mesh = fact('CHARACTEROBJECT mesh pointer offset', 6, set_alpha, 0xa, '8b82', 532)
    alpha = fact('CHARACTEROBJECT alpha offset, GetAlpha', 6, get_alpha, 4, 'd980', 772)
    fact('CHARACTEROBJECT alpha offset, SetAlpha', 6, set_alpha, 0x27, 'd99a', alpha)
    mesh_alpha = fact('ObjectMesh alpha offset', 6, set_alpha, 0x18, '05', 952)
    slots = fact('ObjectMesh first effect-active offset', 9, effect, 2, '8d91', 888)
    fact('ObjectMesh effect slot stride', 9, effect, 0xe, '83c2', 16, 1)
    fact('ObjectMesh effect slot count', 9, effect, 0x11, '83f8', 3, 1)
    extra = fact('ObjectMesh extra effect-active offset', 9, effect, 0x16, '8b91', 936)
    material = fact('CHARACTEROBJECT D3DMATERIAL8 offset', 6,
                    '?SetMaterial@ChInterface@@QAEXPAVCHARACTEROBJECT@@AAU_D3DMATERIAL8@@@Z', 0xe, '8db8', 692)
    fact('CHARACTEROBJECT D3DMATERIAL8 DWORD count', 6,
         '?SetMaterial@ChInterface@@QAEXPAVCHARACTEROBJECT@@AAU_D3DMATERIAL8@@@Z', 0x14, 'b9', 17)
    init = '?InitCharacter@ChInterface@@QAEXPAUIDirect3DDevice8@@@Z'
    fact('ChInterface embedded device field offset', 6, init, 6, '8981', 408)
    loaded = fact('CHARACTEROBJECT loaded DWORD offset', 9,
                  '?LoadRealData@CRender@@QAE_NPAVCHARACTEROBJECT@@PAVTextureManager@@_N@Z', 0xa, '8b86', 260)
    by_id = '?GetCharacter@CObjectManager@@QAEPAVCHARACTEROBJECT@@K@Z'
    fact('CObjectManager end pointer offset', 9, by_id, 0, '8b51', 8, 1)
    fact('CObjectManager begin pointer offset', 9, by_id, 3, '8b49', 4, 1)
    add = '?AddCharacter@CObjectManager@@QAEXPAVCHARACTEROBJECT@@@Z'
    fact('CObjectManager capacity pointer offset', 9, add, 0x13, '8b56', 12, 1)
    fact('CObjectManager next ID offset', 9, add, 0xb, '8b46', 16, 1)
    part = '?AddPartToMM@ChInterface@@QAEXPAD@Z'
    fact('CObjectManager allocation bytes', 6, part, 0x29, '68', 148)
    fact('CObjectManager name length diagnostic threshold', 6, part, 0x16, '81f9', 128)
    fact('CObjectManager name buffer offset', 6, part, 0x50, '8d56', 20, 1)
    destructor = '??1CRender@@QAE@XZ'
    fact('CRender embedded mesh manager offset', 9, destructor, 0x8e, '8d4f', 112, 1)
    fact('CRender embedded bone manager offset', 9, destructor, 0x7e, '8d8f', 260)
    fact('CRender embedded texture manager offset', 9, destructor, 0x6e, '8d8f', 408)
    fact('CRender embedded part manager offset', 9, destructor, 0x54, '8d8f', 568)
    fact('TextureManager last observed DWORD offset', 8, '?Init@TextureManager@@QAEHXZ', 0x11, '8981', 156)
    fact('Effect pattern count / all-pattern sentinel', 3, '?IsHaveMeshEffect@@YA_NPAVCHARACTEROBJECT@@KKK@Z', 5, '83fe', 9, 1)

    work = WS/'work/recovered/character-legacy'
    work.mkdir(parents=True, exist_ok=True)
    header = f'''#pragma once
#include <cstddef>
#include <cstdint>
// Partial memory views only. Unknown bytes are not reconstructed class members.
// Do not include this as Character.h or pass these views to the production client.
namespace character_legacy_evidence {{
struct ObjectMeshView;
struct CharacterObjectView {{
    std::uint8_t unknown_000[260];
    std::uint32_t loaded;
    std::uint8_t unknown_108[264];
    std::uint32_t mesh_count;
    ObjectMeshView* meshes;
    std::uint8_t unknown_218[156];
    float material_dwords[17];
    std::uint8_t unknown_2f8[12];
    float alpha;
}};
struct EffectSlotView {{ std::uint8_t unknown[12]; std::uint32_t active; }};
struct ObjectMeshView {{
    std::uint8_t unknown_000[876];
    EffectSlotView effects[3];
    std::uint8_t unknown_39c[12];
    std::uint32_t extra_effect_active;
    std::uint8_t unknown_3ac[12];
    float alpha;
    std::uint8_t unknown_3bc[116];
}};
struct ChAnimationView {{
    std::uint8_t unknown_000[280];
}};
// Prefix only; total CObjectManager size is not established.
struct ObjectManagerPrefixView {{
    std::uint8_t unknown_000[4];
    CharacterObjectView** begin;
    CharacterObjectView** end;
    CharacterObjectView** capacity;
    std::uint32_t next_id;
}};
static_assert(sizeof(void*)==4, "Legacy Character evidence requires x86");
static_assert(sizeof(CharacterObjectView)=={alloc});
static_assert(sizeof(ObjectMeshView)=={stride});
static_assert(sizeof(ChAnimationView)=={animation_size});
static_assert(offsetof(CharacterObjectView, loaded)=={loaded});
static_assert(offsetof(CharacterObjectView, mesh_count)=={count});
static_assert(offsetof(CharacterObjectView, meshes)=={mesh});
static_assert(offsetof(CharacterObjectView, alpha)=={alpha});
static_assert(offsetof(CharacterObjectView, material_dwords)=={material});
static_assert(offsetof(ObjectMeshView, alpha)=={mesh_alpha});
static_assert(offsetof(ObjectMeshView, effects)+offsetof(EffectSlotView, active)=={slots});
static_assert(offsetof(ObjectMeshView, extra_effect_active)=={extra});
static_assert(offsetof(ObjectManagerPrefixView, begin)==4);
static_assert(offsetof(ObjectManagerPrefixView, end)==8);
static_assert(offsetof(ObjectManagerPrefixView, capacity)==12);
static_assert(offsetof(ObjectManagerPrefixView, next_id)==16);
}}
'''
    (work/'memory_views.hpp').write_text(header, encoding='ascii')
    probe = '''#include "memory_views.hpp"
using namespace character_legacy_evidence;
int main() { return 0; }
'''
    (work/'probe.cpp').write_text(probe, encoding='ascii')
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    devcmd = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    log = WS/'artifacts/character-layout-build.txt'
    batch = work/'probe.cmd'
    batch.write_text(f'''@echo off
call "{devcmd}" -no_logo -arch=x86 -host_arch=x64 > env-init.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /c /std:c++17 /W4 /WX probe.cpp /Foprobe.obj > "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if result.returncode:
        raise RuntimeError(f'Native layout verification failed: {log}')
    obj = (work/'probe.obj').read_bytes()
    if struct.unpack_from('<H', obj)[0] != 0x14c:
        raise ValueError('Native probe was not compiled for x86')
    report = {'library_sha256': inputs['sha256'], 'architecture': 'x86',
              'rva': None, 'address_kind': 'Relocatable COFF section/function/file offsets; no PE RVA',
              'evidence': evidence, 'native_verification': {'compile_exit': 0, 'architecture': 'x86',
                  'probe_obj_sha256': hashlib.sha256(obj).hexdigest(),
                  'header_sha256': hashlib.sha256((work/'memory_views.hpp').read_bytes()).hexdigest(), 'executed': False},
              'limits': ['Partial old-library memory views, not Character.h.',
                         'No class constructors, ownership, STL/CRT ABI or 455 CPU layouts established.']}
    (WS/'inventory/character-legacy-layouts.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: {len(evidence)} instruction checks; native x86 layout assertions passed.')


if __name__ == '__main__':
    main()
