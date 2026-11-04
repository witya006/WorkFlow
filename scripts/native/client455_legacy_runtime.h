#pragma once
#include "client455_legacy_model.h"
#include "client455_model_loader.h"
#include <vector>

struct RF455LegacyDiagnostics {
    void* context;
    void (__cdecl *write)(void*,const char* message);
    void (__cdecl *writeWide)(void*,const wchar_t* message);
};
// Persistent counterparts of the reference's zero-initialized global scratch.
// Grow without shrinking: unwritten fields retain their previous values.
// One renderer owner must serialize calls using this scratch, as in reference.
struct RF455LegacyScratch {
    std::vector<unsigned char> vertices,unique;
    std::vector<std::uint16_t> indices,rebasedIndices;
};
struct RF455LegacyLoadContext {
    RF455ModelLoadContext base;
    RF455VertexBufferPool* vertices36;
    std::uint32_t rendererMode;
    RF455LegacyScratch* scratch;
    RF455LegacyDiagnostics diagnostics;
};
struct RF455LegacyLoadStats {
    std::uint32_t publishedMeshes,indexedMeshes,cpuRetainedMeshes;
    RF455MeshBindingStats bindings;
};
enum RF455LegacyRuntimeStatus {
    RF_LEGACY_RUNTIME_OK=0,RF_LEGACY_RUNTIME_ARGUMENT=1,
    RF_LEGACY_RUNTIME_LIMIT=2,RF_LEGACY_RUNTIME_PHYSIQUE=3,
    RF_LEGACY_RUNTIME_NAMES=4,RF_LEGACY_RUNTIME_MEMORY=5,
    RF_LEGACY_RUNTIME_HEADER=6,RF_LEGACY_RUNTIME_IO=7,
    RF_LEGACY_RUNTIME_FORMAT=8,RF_LEGACY_RUNTIME_BINDING=9
};
extern "C" {
void RF455_ConvertLegacyVertex64(void* target,const void* exportedVertex28);
void RF455_ConvertLegacyUv64(void* target,const void* uv8);
void RF455_ConvertLegacyVertices36(const void* source64,void* target36,unsigned count);
RF455LegacyRuntimeStatus RF455_DecodeLegacyWeights(void* vertices64,unsigned vertexCount,
    const void* physiques424,unsigned count,const RF455LegacyDiagnostics* diagnostics);
RF455LegacyRuntimeStatus RF455_ResolveLegacyBones(RF455MeshStorage* parents,int parentCount,
    RF455MeshStorage* meshes,unsigned meshCount,const RF455LegacyModel* imported,
    const RF455LegacyDiagnostics* diagnostics,RF455MeshBindingStats* stats);
RF455LegacyRuntimeStatus RF455_IndexLegacyVertices(const void* expanded64,unsigned count,
    RF455MeshStorage* mesh,const RF455LegacyLoadContext* context,unsigned* uniqueCount);
// Filename has no extension gate here, as93C770. RFS then loose;always emits the
// reference's ImportMeshorBoneData(...):NULL message after a parsed raw buffer.
RF455LegacyRuntimeStatus RF455_ImportLegacyFile(const char* filename,
    const RF455MeshMemoryOps* memory,const RF455LegacyDiagnostics* diagnostics,
    RF455LegacyModel** output);
// Full valid-input converter route including loose MTG,2/4 renderer modes,
// CPU retention,parents/legacy physique binding andBONE flag. Existing published
// mesh array is overwritten without freeing it, as93CD60. Caller owns imports.
// Bounded invalid-input/nullallocation cleanup is not unchecked failure parity.
RF455LegacyRuntimeStatus RF455_LoadLegacyModel(RF455LegacyModel* imported,
    RF455KnownModelPrefix* external,RF455KnownModelPrefix* model,
    const RF455LegacyLoadContext* context,RF455LegacyLoadStats* stats);
}
