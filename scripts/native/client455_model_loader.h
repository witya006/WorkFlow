#pragma once
#include "client455_model_lifecycle.h"
#include "client455_shared_buffers.h"
#include "client455_texture.h"

// Own view of the known minimum prefix,not the complete ObjectData C++ ABI.
// Bytes260=owns,272=external model pointer,276=texture directory,532=count,
// 536=mesh pointer,796=preserved/set special-name flag. Owner constructs it.
struct RF455KnownModelPrefix {unsigned char bytes[800];};
struct RF455ModelLoadContext {
    RF455MeshMemoryOps memory;RF455MeshMatrixOps matrices;
    RF455TextureManager* textures;RF455VertexBufferPool* vertices;RF455IndexBufferPool* indices;
    RF455MeshAccounting* meshAccounting;RF455BufferAccounting* bufferAccounting;
};
struct RF455ModelLoadStats {std::uint32_t publishedMeshes;RF455MeshBindingStats bindings;};
enum RF455ModelLoadStatus {
    RF_MODEL_OK=0,RF_MODEL_ARGUMENT=1,RF_MODEL_FORMAT=2,RF_MODEL_MEMORY=3,
    RF_MODEL_HEADER=4,RF_MODEL_BINDING=5
};
extern "C" {
// Valid-input MESH08 route:construct→materials/header/GPU per part→local then
// external parents→bone resolution→free bone scratch→publish pointer then count.
// Existing array is overwritten WITHOUT freeing it,as922A00;caller owns reload
// policy. Shared textures/buffers outlive meshes. Input header case is mutated.
// Bounded format/owned error cleanup differs from unchecked ref/OOM/debugbreak;
// this does not implement every format,file dispatch,BN/animation or full draw.
RF455ModelLoadStatus RF455_LoadMesh08Model(void* input,std::size_t length,
    RF455KnownModelPrefix* model,const RF455ModelLoadContext* context,RF455ModelLoadStats* stats);
}
