#pragma once
#include "client455_mesh08.h"
#include <cstdint>

// Only the byte ranges used by the recovered455 binding kernels are known.
// This storage is not a complete C++ ObjectMesh implementation or constructor.
struct RF455MeshStorage { unsigned char bytes[5803]; };
static_assert(sizeof(RF455MeshStorage)==5803,"Pinned455 packed mesh stride");
static_assert(sizeof(void*)==4,"455 binding kernels require x86");
struct RF455MeshBindingStats { std::uint32_t missingNames,resolvedNames; };
enum RF455MeshBindingStatus {
    RF_MESH_BIND_OK=0,RF_MESH_BIND_ARGUMENT=1,
    RF_MESH_BIND_RECORD=2,RF_MESH_BIND_CAPACITY=3
};
extern "C" {
// Preconditions: valid arrays, NUL-terminated mesh names/parent names (256byte
// fields) and query. Negative/zero counts retain reference empty-loop behavior.
RF455MeshStorage* RF455_FindParentMesh(const char* name,RF455MeshStorage* meshes,int count);
int RF455_BindMeshParents(RF455MeshStorage* parents,int parentCount,RF455MeshStorage* meshes,int meshCount);
int RF455_RematchMeshParents(RF455MeshStorage* parents,int parentCount,RF455MeshStorage* meshes,int meshCount);
// Borrows decoded404-byte records; does not take ownership of caller vectors.
// On error earlier meshes may be updated, current mesh is unchanged, stats are
// unchanged. Positive influence counts>4, unterminated fields, >50resolved names
// return explicit owned errors instead of reproducing reference overreads.
// 50 is a safety limit, not a claim about the original object's safe capacity.
RF455MeshBindingStatus RF455_ResolveMesh08Bones(RF455MeshStorage* parents,int parentCount,
    RF455MeshStorage* meshes,int meshCount,const RF455Mesh08Part* parts,RF455MeshBindingStats* stats);
}
