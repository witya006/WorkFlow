"""Wire the verified special-material path into the ordinary BSP draw owner."""
from compare_client_binaries import WS
from prepare_client455_normal import section

def once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Special material boundary '+repr(old))
    return raw.replace(old,new)

def render(raw):
    token=b'void DrawOneMatGroup(CVertexBuffer *vbuffer,_BSP_MAT_GROUP *m_group)';start,end=section(raw,token,token);body=raw[start:end]
    first=body.index(b'\tPreRenderSetting(0,vbuffer,m_group);');last=body.index(b'\n\n\tpd3dDevice->DrawIndexedPrimitive',first)
    body=body[:first]+b'''    const bool special455=(mat->m_dwFlag&0x01000000u)!=0;
    if(special455)prepareMaterialShader455(mat,m_group);
    else{PreRenderSetting(0,vbuffer,m_group);PreRenderOneLayer(vbuffer,m_group);}
    const bool lobbyMaterial455Bound=!special455&&beginLobbyMaterial455(pd3dDevice,mat,m_group);
'''+body[last:]
    first=body.index(b'\tAfterRenderOneLayer(vbuffer,m_group);');last=body.index(b'\n\n\tif( mat->m_dwLayerNum',first)
    body=body[:first]+b'''    if(lobbyMaterial455Bound)endLobbyMaterial455();
    if(special455)finishMaterialShader455(mat);
    else{AfterRenderOneLayer(vbuffer,m_group);AfterRenderSetting(0,vbuffer,m_group);}
    if(mat->m_dwFlag&0x40){drawSplat455(vbuffer,m_group,mat);return;}
'''+body[last:]
    body=once(body,b'if( mat->m_dwLayerNum == 1 || (mat->m_Layer[1].m_dwFlag & _MAT_ENV_BUMP) )',b'if(special455 || mat->m_dwLayerNum == 1 || (mat->m_Layer[1].m_dwFlag & _MAT_ENV_BUMP))')
    return raw[:start]+(WS/'scripts/native/client455_material_shaders.inc').read_bytes()+b'\n'+(WS/'scripts/native/client455_lobby_material.inc').read_bytes()+b'\n'+body+raw[end:]

def particle_render(raw):
    raw=b'#include "client455_shader_lights.h"\n'+raw
    token=b'void DrawCParticle(';start,end=section(raw,token,token);body=raw[start:end]
    anchor=b'\tMultiTexOff();';body=once(body,anchor,b'    if(particle->mFlag&0x100000u)RF455_UpdateParticleShaderLight(particle->mLightID,world_mat[3]);\n'+anchor)
    return raw[:start]+body+raw[end:]
