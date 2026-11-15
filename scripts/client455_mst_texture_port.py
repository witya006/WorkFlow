"""Install checked standalone material texture registry functions."""

import re


def port_mst_texture_registry(raw, native, section):
    slot_owner = b'int R3GetPreTextureId('
    implementation = (native / 'client455_mst_texture_registry.inc').read_bytes()
    spans = []
    for anchor in (
        b'void SetNowR3D3DTexCnt(',
        b'void SetNowR3TexCnt(',
        b'char *R3GetTexName(int id)',
        slot_owner,
        b'void R3LoadTextureMem(',
        b'void R3ReleaseTextureMem(',
        b'void R3RestoreAllTextures()',
    ):
        start, end = section(raw, anchor, anchor)
        warning = {
            slot_owner: b'Warning("MST texture", " name is too long");',
            b'void R3LoadTextureMem(': b'Warning("R3T texture", " is loaded through its container");',
            b'void R3ReleaseTextureMem(': b'Warning("R3T texture", " released through a standalone slot");',
        }.get(anchor)
        if warning:
            original = re.findall(rb'Warning\("[^"\r\n]*",""\);', raw[start:end])
            if len(original) != 1 or implementation.count(warning) != 1:
                raise ValueError('Standalone texture warning boundary ' + repr(anchor))
            implementation = implementation.replace(warning, original[0])
        spans.append((start, end, anchor == slot_owner))
    for start, end, insert in sorted(spans, reverse=True):
        raw = raw[:start] + (implementation if insert else b'') + raw[end:]
    return raw
