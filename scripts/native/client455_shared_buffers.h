#pragma once
#include <windows.h>
#include <d3d9.h>
#include <cstddef>
#include <cstdint>
#include "client455_mesh_runtime.h"

constexpr std::uint32_t RF455_VERTEX_BLOCK_BYTES=2300000;
constexpr std::uint32_t RF455_INDEX_BLOCK_BYTES=1000000;
constexpr unsigned RF455_BUFFER_SLOTS=1024;
#pragma pack(push,4)
struct RF455VertexBufferPool {
    IDirect3DVertexBuffer9* buffers[RF455_BUFFER_SLOTS];
    std::uint32_t used[RF455_BUFFER_SLOTS],opaque8192;
    IDirect3DDevice9* device; // borrowed
};
struct RF455IndexBufferPool {
    IDirect3DIndexBuffer9* buffers[RF455_BUFFER_SLOTS];
    std::uint32_t used[RF455_BUFFER_SLOTS],opaque8192;
    IDirect3DDevice9* device; // borrowed
};
#pragma pack(pop)
static_assert(sizeof(RF455VertexBufferPool)==8200 && sizeof(RF455IndexBufferPool)==8200,"455shared pool size");
static_assert(offsetof(RF455VertexBufferPool,used)==4096 && offsetof(RF455VertexBufferPool,device)==8196,"455shared pool fields");
struct RF455BufferAccounting {std::uint32_t bytes,created;};
// Explicit accounting storage is shared by the renderer owner, corresponding
// to reference global DWORDs. These routines increment it only on creation.
// Inputs must be valid source storage/pools. This is not the full renderer ABI.
extern "C" {
void RF455_ConstructVertexPool(RF455VertexBufferPool* pool);
void RF455_ConstructIndexPool(RF455IndexBufferPool* pool);
// Destruction releases nonnull slots in ascending order; fields are NOT reset.
// Do not destroy a pool twice or reuse it without constructing it again.
void RF455_DestroyVertexPool(RF455VertexBufferPool* pool);
void RF455_DestroyIndexPool(RF455IndexBufferPool* pool);
int RF455_UploadVertices36(RF455VertexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting);
int RF455_UploadVertices64(RF455VertexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting);
int RF455_UploadIndices(RF455IndexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting);
void RF455_BindVertices36(RF455VertexBufferPool* pool,std::uint32_t absolute);
void RF455_BindVertices64(RF455VertexBufferPool* pool,std::uint32_t absolute);
void RF455_BindIndices(RF455IndexBufferPool* pool,std::uint32_t absolute);
void RF455_RebaseMesh08Indices(void* indices,std::uint16_t count,std::uint32_t vertexAbsolute);
// Mesh08 caller behavior: only nonzero indexCount uploads; upload failures do
// not abort, and failed vertex upload leaves its existing offset for rebase.
// Header/CPU/bone/owner publication and full loader unwind are separate.
void RF455_UploadMesh08Gpu(RF455VertexBufferPool* vertices,RF455IndexBufferPool* indices,
    RF455BufferAccounting* accounting,RF455MeshStorage* mesh,const RF455Mesh08Part* part);
}
