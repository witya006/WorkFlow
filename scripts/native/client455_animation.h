#pragma once
#include "client455_character_manager.h"
#include "client455_legacy_runtime.h"

struct RF455AnimationStorage {unsigned char bytes[284];};
struct RF455AnimationMemoryOps {
    RF455MeshMemoryOps memory;
    std::size_t (__cdecl *extent)(void*,const void* allocation);
};
RF455AnimationMemoryOps RF455_CrtAnimationMemoryOps();
#pragma pack(push,4)
struct RF455AnimationChannel {std::uint32_t count;const unsigned char* keys;};
struct RF455AnimationData {RF455AnimationChannel channel[4];};
struct RF455AniTrackView {const unsigned char* header;RF455AnimationData data;};
#pragma pack(pop)
static_assert(sizeof(RF455AnimationData)==32 && sizeof(RF455AnimationStorage)==284,"455 animation storage");
struct RF455AniView {std::uint32_t trackCount,maxFrame;std::size_t consumed;};
struct RF455AnimationBuffer {void* bytes;std::uint32_t length,accountedBytes;bool fromRfs;};
struct RF455AnimationContext {
    RF455AnimationMemoryOps memory;
    RF455LegacyDiagnostics diagnostics;
    std::uint32_t* importedBytes; // Cumulative DWORD1189608,notlive allocation total.
};
enum RF455AnimationStatus {
    RF_ANIMATION_OK=0,RF_ANIMATION_ARGUMENT=1,RF_ANIMATION_FORMAT=2,
    RF_ANIMATION_CAPACITY=3,RF_ANIMATION_MEMORY=4,RF_ANIMATION_IO=5,
    RF_ANIMATION_TYPE=6,RF_ANIMATION_NAME=7
};
enum RF455ImportedKind {RF_IMPORTED_NONE=0,RF_IMPORTED_ANI=1,RF_IMPORTED_LEGACY=2};
struct RF455ImportedResource {
    RF455ImportedKind kind;RF455AnimationBuffer animation;RF455LegacyModel* legacy;
};
struct RF455CharacterLoadContext {
    RF455LegacyLoadContext legacy;
    RF455AnimationContext animation;
};
extern "C" {
void RF455_ConstructAnimation(RF455AnimationStorage* record);
void RF455_DestroyAnimation(RF455AnimationStorage* record,const RF455MeshMemoryOps* memory);
// Borrowed key pointers,like93C1F0. Count is byte0;byte1 is ignored,records start2.
// A zero-count one-byte input is accepted as inreference;consumed remains2.
RF455AnimationStatus RF455_DecodeAni(const void* bytes,std::size_t length,
    RF455AniTrackView* tracks,std::size_t capacity,RF455AniView* output,std::size_t* failureEnd);
RF455AnimationStatus RF455_ReadAnimationFile(const char* name,const RF455AnimationContext* context,RF455AnimationBuffer* output);
RF455AnimationStatus RF455_ImportCharacterResource(const char* name,int synchronous,
    const RF455AnimationContext* context,RF455ImportedResource* output);
void RF455_ReleaseImportedResource(RF455ImportedResource* imported,const RF455MeshMemoryOps* memory);
RF455AnimationStatus RF455_FindAnimationMax(RF455AnimationStorage* record,const void* bytes,
    std::size_t extent,const RF455LegacyDiagnostics* diagnostics);
// Keeps loading4 set onboth success andfailure;retry short-circuits totrue.
int RF455_LoadAnimation(RF455AnimationStorage* record,int synchronous,const RF455AnimationContext* context);
RF455AnimationStatus RF455_ApplyAniTrack(const RF455AniTrackView* track,RF455KnownModelPrefix* model,
    const RF455MeshMemoryOps* memory,int* matchedIndex);
RF455AnimationStatus RF455_AttachAnimation(const void* bytes,std::size_t extent,
    RF455KnownModelPrefix* model,const RF455MeshMemoryOps* memory,int* lastIndex);
int RF455_ValidateLegacyModel(const RF455LegacyModel* imported,const RF455LegacyDiagnostics* diagnostics);
// Actual parent/no-parent route selection. Preserves the reference attempt flags.
// Private MSH input is released on every exit. Bounds/type/error domains differ
// from unchecked AV/OOM;ANI istyped foranimation,notlegacy ObjectData28.
int RF455_LoadCharacter(RF455CharacterStorage* record,int synchronous,const RF455CharacterLoadContext* context);
int RF455_MatchAnimation(RF455AnimationStorage* animation,RF455CharacterStorage* model,const RF455CharacterLoadContext* context);
}
