#pragma once
#include "client455_mesh_bindings.h"

struct RF455MeshAccounting { std::uint32_t constructed,bytesConstructed; };
struct RF455MeshMatrixOps {
    void* (__stdcall *inverse)(void* output,float* determinant,const void* input);
    void* (__stdcall *multiply)(void* output,const void* left,const void* right);
};
// The full455TextureManager/D3D9 backend must provide these operations. There
// is no default successful/no-op backend. Lab scripted providers test only the
// recovered request order; physical texture creation is a separate requirement.
struct RF455MeshMaterialOps {
    void* context;
    std::int32_t (__cdecl *lookup)(void*,const char* name);
    int (__cdecl *load)(void*,const char* directory,const char* name);
};
enum RF455MeshRuntimeStatus {
    RF_MESH_RUNTIME_OK=0,RF_MESH_RUNTIME_ARGUMENT=1,
    RF_MESH_RUNTIME_NAME=2,RF_MESH_RUNTIME_PATH=3,RF_MESH_RUNTIME_MATRIX=4
};
extern "C" {
// Final byte state and cumulative counters of455mesh constructor. This does not
// implement its destructor, owning subobject methods or full C++ class ABI.
void RF455_ConstructMeshStorage(RF455MeshStorage* mesh,RF455MeshAccounting* accounting);
// Writes only header-derived CPU fields and derived matrices, preserving other
// bytes. part/header must be valid decoded storage. inverse/multiply must be
// the pinned D3DX9_36 operations. Singular-matrix errors are owned safety policy:
// reference ignores their null result and may consume uninitialized stack data.
// Existing mesh/model flags remain set unless the reference overwrites them.
RF455MeshRuntimeStatus RF455_ApplyMesh08Header(RF455MeshStorage* mesh,
    const RF455Mesh08Part* part,const RF455MeshMatrixOps* matrices,std::uint32_t* modelFlag);
// Mutates only the primary basename in the input693-byte header with _strlwr,
// as reference does. Caller owns it. Missing textures still return success;
// unsuccessful lookup/load remains represented by texture ID0.
RF455MeshRuntimeStatus RF455_LoadMesh08Materials(RF455MeshStorage* mesh,
    unsigned char* header,const char* objectDirectory,const char* fallbackDirectory,
    const RF455MeshMaterialOps* materials);
}
