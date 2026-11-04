#pragma once
#include "client455_mesh_runtime.h"
#include <cstddef>

struct RF455MeshMemoryOps {
    void* context;
    void* (__cdecl *allocate)(void*,std::size_t);
    void (__cdecl *release)(void*,void*);
};
// Actual modern static CRT allocation provider. Owners may wrap it to account
// allocations;storage created by a different allocator must use its own ops.
RF455MeshMemoryOps RF455_CrtMeshMemoryOps();
extern "C" {
void RF455_DestroyMeshStorage(RF455MeshStorage* mesh,const RF455MeshMemoryOps* memory);
RF455MeshStorage* RF455_AllocateMeshArray(std::uint32_t count,RF455MeshAccounting* accounting,const RF455MeshMemoryOps* memory);
// Flags follow921480:bit2(array) selects DWORD cookie and reverse destruction;
// bit1(free) frees allocation. Return is original base (cookie for arrays),even
// when it was freed. Repeated destruction withlive COM fields is unsafe,as ref.
void* RF455_DeleteMeshStorage(RF455MeshStorage* mesh,unsigned flags,const RF455MeshMemoryOps* memory);
// Raw model prefix must have fields260(owns),532(count),536(mesh pointer).
// Only owned nonnull array is deleted. Pointer536 is cleared;count is retained.
void RF455_ReleaseModelMeshArray(void* modelPrefix,const RF455MeshMemoryOps* memory);
}
