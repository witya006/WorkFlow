"""Generate an incomplete, evidence-based legacy Character interface for compilation.

This is a diagnostic header, not a completed SDK. Unrecovered inline functions and
constructors are DECLARED ONLY and must fail linking until actually reconstructed.
No guessed function bodies, default arguments, STL substitutions or dummy returns.
"""
import hashlib
import json
import re
from pathlib import Path

WS = Path(__file__).resolve().parents[1]

FIELDS = {
    'CHARACTEROBJECT': '''
    DWORD m_ID;
    char m_Name[256];
    DWORD m_Load;
    unsigned char unknown_108[264];
    DWORD m_MaxObj;
    ObjectMesh* m_pMesh;
    unsigned char unknown_218[128];
    DWORD unknown_298;
    DWORD m_Frame;
    DWORD m_OMaxFrame;
    DWORD m_Transition;
    DWORD m_TransitionStart;
    DWORD m_TransFrame;
    DWORD m_TransTime;
    D3DMATERIAL8 m_Material;
    unsigned char unknown_2f8[12];
    float m_Alpha;
''',
    'ObjectMesh': '''
    char m_Name[128];
    bool m_HaveParent;
    unsigned char unknown_081[7];
    ObjectMesh* m_pParent;
    DWORD m_BlendNum;
    unsigned char unknown_090[16];
    D3DXMATRIX* m_pMatBlend;
    unsigned char unknown_0a4[332];
    D3DXMATRIX m_MatResult;
    D3DXMATRIX m_BefMatResult;
    D3DXMATRIX m_BefMatLocal;
    unsigned char unknown_2b0[188];
    CharacterEffectSlot m_ParticleID[3];
    CharacterEffectSlot m_Entity;
    unsigned char unknown_3ac[12];
    float m_Alpha;
    unsigned char unknown_3bc[116];
''',
    'ChAnimation': '''
    DWORD m_Load;
    char m_Name[256];
    DWORD m_Ident;
    unsigned char unknown_108[12];
    void* m_pExtra;
''',
    'CObjectManager': '''
    unsigned char unknown_000[4];
    CHARACTEROBJECT** legacy_begin;
    CHARACTEROBJECT** legacy_end;
    CHARACTEROBJECT** legacy_capacity;
    DWORD legacy_next_id;
    char legacy_name[128];
    CObjectManager(); // Inline constructor not yet recovered.
''',
    'AnimationManager': '''
    unsigned char unknown_000[4];
    ChAnimation** legacy_begin;
    ChAnimation** legacy_end;
    ChAnimation** legacy_capacity;
    DWORD unknown_010;
    DWORD legacy_next_id;
    AnimationManager(); // Inline constructor not yet recovered.
''',
    'TextureManager': '''
    IDirect3DDevice8* legacy_device;
    unsigned char unknown_004[4];
    ChTexture** legacy_begin;
    ChTexture** legacy_end;
    ChTexture** legacy_capacity;
    DWORD unknown_014;
    DWORD legacy_next_id;
    char legacy_path[128];
    DWORD unknown_09c;
    TextureManager(); // Inline constructor not yet recovered.
''',
    'CMeshManager': '''
    unsigned char unknown_000[4];
    CObjectManager** legacy_begin;
    CObjectManager** legacy_end;
    CObjectManager** legacy_capacity;
    CMeshManager(); // Inline constructor not yet recovered.
''',
    'CRender': '''
    IDirect3DDevice8* legacy_device;
    unsigned char unknown_004[108];
    CObjectManager legacy_meshes;
    CObjectManager legacy_bones;
    TextureManager m_TM;
    CMeshManager legacy_parts;
    unsigned char unknown_248[108];
    IDirect3DTexture8* legacy_shadow[20];
    IDirect3DSurface8* legacy_shadow_surface;
    CRender(); // Inline constructor not yet recovered.
    void SetMipMap(DWORD); // Missing inline API: declaration, no implementation.
    IDirect3DTexture8* GetShadow(DWORD);
    void DrawCharacter(CHARACTEROBJECT*, float*, float);
    void DrawCharacter(CHARACTEROBJECT*, float*, float, float);
    void DrawCharacterShadow(CHARACTEROBJECT*, float*, float, float);
    bool LoadRealData(CHARACTEROBJECT*, TextureManager*);
''',
    'ChInterface': '''
    ChInterface(); // No additional storage has been established in the library.
    void SetTexPath(CHARACTEROBJECT*, char*); // Missing inline API.
''',
    'CHMEMORYINFO': '''
    DWORD m_TextureSize;
    DWORD m_TextureNum;
    DWORD m_VertexSize;
    DWORD m_VetexNum;
    DWORD m_AniSize;
    DWORD m_ObjectNum;
    DWORD m_ObjectSize;
''',
    'EffectList': '''
    void SetEffect(CHARACTEROBJECT*, DWORD); // Missing inline implementation.
''',
}


def main():
    source = WS/'inventory/character-public-contracts.json'
    contracts = json.loads(source.read_text(encoding='utf-8'))
    methods = {}
    free = []
    tags = {'ObjectMesh': 'struct', 'CHMEMORYINFO': 'struct'}
    for entry in contracts['contracts']:
        declaration = entry['declaration']
        if '`' in declaration:
            # Compiler-generated deleting destructors are not source declarations.
            continue
        for tag, name in re.findall(r'\b(class|struct) ([A-Za-z_]\w*)', declaration):
            if name.startswith(('D3D', '_D3D', 'IDirect', 'std')):
                continue
            if name in tags and tags[name] != tag:
                raise ValueError(f'Inconsistent class/struct tag: {name}')
            tags[name] = tag
        member = re.search(r'\b([A-Za-z_]\w*)::(~?\w+|operator=)\(', declaration)
        # Static data members need their original access for matching symbol decoration.
        static_data = re.search(r'\b([A-Za-z_]\w*)::(m_\w+)$', declaration)
        if member and not member[1].startswith('D3D'):
            name = member[1]
            text = declaration.replace(name+'::', '')
            # Member access is encoded in MSVC decorated names; preserve it.
            methods.setdefault(name, []).append('    '+text+';\npublic:')
        elif static_data:
            name = static_data[1]
            text = declaration.replace(name+'::', '')
            # Preserve public/private for data-member decorated names.
            methods.setdefault(name, []).append('    '+text+';\npublic:')
        elif not member:
            if declaration.startswith(('public:', 'private:', 'protected:')):
                raise ValueError('Unparsed member contract: '+declaration)
            free.append(('extern ' if '(' not in declaration else '')+declaration+';')
    # ChInterface derives from CRender in this reconstruction; no vtable is introduced.
    # Other API-only types are not constructed by the client. Their storage is unknown.
    order = list(FIELDS)
    other = sorted(set(methods)-set(order)-{'D3DXMATRIX'})
    for name in set(methods) | set(order):
        tags.setdefault(name, 'class')
    tags.setdefault('ChTexture', 'class')
    header = '''#pragma once
// DIAGNOSTIC RECONSTRUCTION. Completeness/CRT/inline behavior remain open.
#include <windows.h>
#include <d3d8.h>
#include <d3dx8.h>
#include <cstddef>
#include <string>
#include <map>
#include <vector>
'''
    header += ''.join(f'{tag} {name};\n' for name, tag in sorted(tags.items()))
    header += '''enum { MAXPARTICLE = 3, MAX_PATTERN_SIZE = 9 };
struct CharacterEffectSlot { float m_X, m_Y, m_Z; DWORD m_ID; };
'''
    for name in order+other:
        base = ' : public CRender' if name == 'ChInterface' else ''
        header += f'{tags.get(name, "class")} {name}{base} {{\npublic:\n'
        if name in FIELDS:
            header += FIELDS[name]
        else:
            header += '    // API only: storage is not reconstructed; do not instantiate this type.\n'
        header += '\n'.join(methods.get(name, []))+'\n};\n'
        if name == 'CRender':
            # Private static storage exists in the supplied library. Define only an accessor.
            header = header[:-3]+'    static CRender& GetRender() { return *m_Render; }\n};\n'
    header += '\n'.join(free)+'\n'
    header += '''// Shortened calls exist in client sources; original default arguments are not known.
void SetMeshEffect(CHARACTEROBJECT*, unsigned long, unsigned long);
bool IsHaveMeshEffect(CHARACTEROBJECT*, unsigned long, unsigned long);
'''
    asserts = {
        'CHARACTEROBJECT': (776, {'m_ID': 0, 'm_Name': 4, 'm_Load': 260, 'm_MaxObj': 528,
                                'm_pMesh': 532, 'm_Frame': 668, 'm_OMaxFrame': 672,
                                'm_Transition': 676, 'm_TransitionStart': 680,
                                'm_TransFrame': 684, 'm_TransTime': 688, 'm_Material': 692, 'm_Alpha': 772}),
        'ObjectMesh': (1072, {'m_HaveParent': 128, 'm_pParent': 136, 'm_BlendNum': 140,
                             'm_pMatBlend': 160, 'm_MatResult': 496, 'm_BefMatResult': 560,
                             'm_BefMatLocal': 624, 'm_ParticleID': 876, 'm_Entity': 924, 'm_Alpha': 952}),
        'ChAnimation': (280, {'m_Load': 0, 'm_Name': 4, 'm_Ident': 260, 'm_pExtra': 276}),
        'CObjectManager': (148, {'legacy_begin': 4, 'legacy_end': 8, 'legacy_capacity': 12, 'legacy_next_id': 16, 'legacy_name': 20}),
        'AnimationManager': (24, {}), 'TextureManager': (160, {'legacy_path': 28}),
        'CMeshManager': (16, {}),
        'CRender': (776, {'legacy_meshes': 112, 'legacy_bones': 260, 'm_TM': 408,
                          'legacy_parts': 568, 'legacy_shadow': 692, 'legacy_shadow_surface': 772}),
        'ChInterface': (776, {}),
        'CHMEMORYINFO': (28, {'m_TextureSize': 0, 'm_TextureNum': 4, 'm_VertexSize': 8,
                              'm_VetexNum': 12, 'm_AniSize': 16, 'm_ObjectNum': 20, 'm_ObjectSize': 24}),
    }
    header += 'static_assert(sizeof(void*)==4, "Recovered legacy Character requires x86");\n'
    for name, (size, fields) in asserts.items():
        header += f'static_assert(sizeof({name})=={size}, "{name} size");\n'
        for field, offset in fields.items():
            header += f'static_assert(offsetof({name}, {field})=={offset}, "{name}::{field}");\n'
    target = WS/'work/recovered/character-legacy/include/Character.h'
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.read_text(encoding='ascii') != header:
        target.write_text(header, encoding='ascii')
    report = {'library_sha256': contracts['library_sha256'], 'header': target.relative_to(WS).as_posix(),
              'header_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
              'public_contracts_input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'status': 'incomplete diagnostic interface; not production-ready',
              'layout_assertions': sum(1+len(fields) for _, fields in asserts.values()),
              'unimplemented_inline_api': ['CObjectManager/AnimationManager/TextureManager/CMeshManager/CRender/ChInterface constructors',
                   'SetMipMap', 'GetShadow', 'SetTexPath', 'EffectList::SetEffect',
                   'DrawCharacter/DrawCharacterShadow/LoadRealData/SetMeshEffect/IsHaveMeshEffect shortened overloads'],
              'unverified': ['Full layout of API-only classes remains missing',
                   'Names inferred from source use need final instruction cross-check',
                   'No successful whole-client compile/link; no runtime compatibility claimed',
                   'Old STL ABI must not cross into modern STL objects',
                   'CRender/ChInterface tail and total sizes inferred from observed accesses; validate initialization'],
              'method_declarations': sum(len(x) for x in methods.values()), 'free_declarations': len(free)}
    (WS/'inventory/character-header-recovery.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'Prepared incomplete header: {len(methods)} API types, {report["layout_assertions"]} layout assertions.')


if __name__ == '__main__':
    main()
