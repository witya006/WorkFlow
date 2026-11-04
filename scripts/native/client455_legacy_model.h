#pragma once
#include "client455_model_lifecycle.h"

// Intermediate objects returned by93C2F0. These are not the5803byte runtime mesh.
// Unwritten bytes retain allocator contents, as in the reference constructors.
struct RF455LegacyPart {unsigned char bytes[720];};
struct RF455LegacyModel {unsigned char bytes[28];};
static_assert(sizeof(void*)==4,"Intermediate455 objects require x86 pointers");
enum RF455LegacyStatus {
    RF_LEGACY_OK=0, RF_LEGACY_ARGUMENT=1, RF_LEGACY_FORMAT=2,
    RF_LEGACY_MEMORY=3, RF_LEGACY_INFLUENCES=4, RF_LEGACY_NAME_INDEX=5
};
extern "C" {
void RF455_ConstructLegacyPart(RF455LegacyPart* part);
void RF455_DestroyLegacyPart(RF455LegacyPart* part,const RF455MeshMemoryOps* memory);
// Release fields/array cookie, preserving the28byte object's other fields.
void RF455_ReleaseLegacyModel(RF455LegacyModel* model,const RF455MeshMemoryOps* memory);
// Release fields then the owned28byte object itself.
void RF455_DeleteLegacyModel(RF455LegacyModel* model,const RF455MeshMemoryOps* memory);
// Bounded source adaptation of93C2F0. Output/consumed are unchanged on error.
// Raw header/geometry/plain physique bytes are copied. Compact influences are
// expanded via strncpy99+NUL and x87 weight copy. Trailing bytes are accepted.
// Bounds/count/index/null-allocation errors use own cleanup/status policies;
// this does not reproduce unchecked AV/overflow/exception behavior.
RF455LegacyStatus RF455_ReadLegacyModel(const void* input,std::size_t length,
    const RF455MeshMemoryOps* memory,RF455LegacyModel** output,std::size_t* consumed);
}
