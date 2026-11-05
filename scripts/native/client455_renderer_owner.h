#pragma once
#include "client455_character_draw.h"

#pragma pack(push,4)
struct RF455RendererEffects {
    unsigned opaque0;RF455CharacterManager** begin;RF455CharacterManager** end;RF455CharacterManager** capacity;
    unsigned nextId;unsigned char active,opaque21[99];
    unsigned char batchEnabled,opaque121[3];
    IUnknown* resources[20];IUnknown* extra;unsigned char opaque208[8];
};
// Recovered455 storage only. Never overlay this on the old D3D8 CRender.
// Opaque fields retain their incoming bytes unless a confirmed write sets them.
struct RF455CharacterRenderer {
    IDirect3DDevice9* device;unsigned opaque4;D3DLIGHT9 light;IUnknown* sprite;
    RF455CharacterManager bones,meshes;unsigned opaque8412,frame8416;
    unsigned char indexedBlend,opaque8421[3];
    RF455TextureManager textures;RF455RendererEffects effects;
    RF455VertexBufferPool vertices64,vertices36;RF455IndexBufferPool indices;
    unsigned vertexMode;D3DCAPS9 caps;unsigned specular,opaque33840;
    float blendDuration;unsigned char opaque33848[8];
};
#pragma pack(pop)
static_assert(sizeof(RF455RendererEffects)==216 && sizeof(RF455CharacterRenderer)==0x8440,"455 renderer allocation");
static_assert(offsetof(RF455CharacterRenderer,bones)==116 && offsetof(RF455CharacterRenderer,meshes)==4264,"455 manager bases");
static_assert(offsetof(RF455CharacterRenderer,textures)==8424 && offsetof(RF455CharacterRenderer,effects)==8712,"455 owned objects");
static_assert(offsetof(RF455CharacterRenderer,vertices64)==8928 && offsetof(RF455CharacterRenderer,vertices36)==17128 && offsetof(RF455CharacterRenderer,indices)==25328,"455 pool bases");
static_assert(offsetof(RF455CharacterRenderer,caps)==33532 && offsetof(RF455CharacterRenderer,specular)==33836 && offsetof(RF455CharacterRenderer,blendDuration)==33844,"455 caps andpose fields");
static_assert(offsetof(D3DCAPS9,MaxVertexBlendMatrices)==168 && offsetof(D3DCAPS9,MaxVertexBlendMatrixIndex)==172 && offsetof(D3DCAPS9,ShadeCaps)==56,"455 caps reads");

// Original shader manager/declarations are shared globals,not per-renderer.
struct RF455RendererShared {
    RF455ShaderManager shaders;
    IDirect3DVertexDeclaration9* declaration64;IDirect3DVertexDeclaration9* declaration36;
    char logPath[256];
};
struct RF455RendererDiagnostics {
    void* context;
    int (__cdecl *shaderFailure)(void*,int shaderResult);
};
extern "C" {
void RF455_ConstructCharacterRenderer(RF455CharacterRenderer*);
// Borrowed device,including pools/textures;GetDeviceCaps HRESULT is ignored.
// Shared shader bootstrap runs only when shared.shaders.device is null.
int RF455_SetCharacterRendererDevice(RF455CharacterRenderer*,RF455RendererShared*,
    IDirect3DDevice9*,const RF455ShaderApi*,const RF455RendererDiagnostics*);
// Releases resources in9228A0 order. Shared shaders/declarations outlive this.
// Nonnull released pool/effect slots are retained;repeat destruction is unsafe.
void RF455_DestroyCharacterRenderer(RF455CharacterRenderer*,const RF455MeshMemoryOps*);
// These source adapters connect owned resources to the existing typed kernels.
RF455ModelLoadContext RF455_RendererModelContext(RF455CharacterRenderer*,const RF455MeshMemoryOps*,
    const RF455MeshMatrixOps*,RF455MeshAccounting*,RF455BufferAccounting*);
void RF455_BindRendererDrawContext(RF455CharacterRenderer*,RF455RendererShared*,RF455CharacterDrawContext*);
}
