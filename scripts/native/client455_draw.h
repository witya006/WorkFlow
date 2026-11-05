#pragma once
#include "client455_shaders.h"
#include "client455_shared_buffers.h"

// Borrowed logical owner view. This is not the legacy D3D8 renderer ABI.
struct RF455CharacterDrawState {
    IDirect3DDevice9* device;
    unsigned vertexMode; // 2 = 36 bytes, 4 = 64 bytes.
    IDirect3DVertexDeclaration9* declaration36;
    IDirect3DVertexDeclaration9* declaration64;
    const float* light104; // 26 floats; direction at float16 as renderer+72.
    DWORD specularEnable; // renderer+33836; zero skips three material writes.
};
extern "C" {
// 91CDE0; changes exactly the recovered state set, not a state-block restore.
void RF455_SetCharacterDrawState(const RF455CharacterDrawState*);
// 91FB90; records even an invalid selection after binding null VS/PS.
HRESULT RF455_SelectCharacterShader(RF455ShaderManager*,unsigned index,unsigned* selected);
// 92D830; ambient c19 before diffuse c18. No implicit material conversion.
HRESULT RF455_SetCharacterMaterial(IDirect3DDevice9*,const void* material68);
// 91D120: skin*world (or pose*world), optional translation-only override.
// Uses the pinned D3DX multiply. No transpose/clamp of the reference bone count.
HRESULT RF455_UploadCharacterPalette(IDirect3DDevice9*,const RF455MeshStorage*,
    const void* world,const void* translationWorld,const RF455MeshMatrixOps*);
// Shared-buffer draw branch of92E140/92E5F0/930120/930A40. CPU-retained meshes
// take92DB60 instead; this entry requires that mesh+4506 be null. Indices are
// already rebased; BaseVertexIndex remains0, MinVertexIndex is pool remainder.
HRESULT RF455_SubmitSharedCharacterMesh(IDirect3DDevice9*,unsigned vertexMode,
    RF455VertexBufferPool* vertices36,RF455VertexBufferPool* vertices64,
    RF455IndexBufferPool*,const RF455MeshStorage*);
}
