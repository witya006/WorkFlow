#pragma once
#include "client455_animation.h"

// Owned source type. Legacy AnimationManager is a different ABI (24 bytes).
#pragma pack(push,4)
struct RF455AnimationManager {
    RF455AnimationManager* self;
    std::uint32_t allocatorPadding;
    RF455AnimationStorage** begin;
    RF455AnimationStorage** end;
    RF455AnimationStorage** capacity;
    std::uint32_t counter,nextId;
    RF455AnimationStorage* cache[1000];
};
#pragma pack(pop)
static_assert(sizeof(RF455AnimationManager)==4028 && offsetof(RF455AnimationManager,cache)==28,"455 animation manager allocation");

extern "C" {
// Preserves the four uninitialized bytes of the empty allocator at +4.
void RF455_ConstructAnimationManager(RF455AnimationManager*);
void RF455_ResetAnimationCounters(RF455AnimationManager*);
int RF455_RegisterAnimation(RF455AnimationManager*,const char*,const RF455MeshMemoryOps*);
RF455AnimationStorage* RF455_GetOrRegisterAnimation(RF455AnimationManager*,const char*,const RF455MeshMemoryOps*);
RF455AnimationStorage* RF455_FindAnimationName(RF455AnimationManager*,const char*);
// Matches from the last BACKSLASH, including that separator.
RF455AnimationStorage* RF455_FindAnimationSuffix(RF455AnimationManager*,const char*);
RF455AnimationStorage* RF455_FindAnimationId(RF455AnimationManager*,std::uint32_t);
std::uint32_t RF455_FindAnimationIdByName(RF455AnimationManager*,const char*);
void RF455_DeleteAnimationName(RF455AnimationManager*,const char*,const RF455MeshMemoryOps*);
void RF455_DeleteAnimationId(RF455AnimationManager*,std::uint32_t,const RF455MeshMemoryOps*);
// Reference932F30: release records and vector; preserve counters/self/cache,
// including freed pointers in cache. Never query a freed cache entry.
void RF455_ReleaseAnimationManager(RF455AnimationManager*,const RF455MeshMemoryOps*);
}
