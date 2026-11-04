#pragma once
#include "client455_model_loader.h"

// Allocation size1188 is confirmed by931360/9313F0/931480/931ED0;only known
// fields have methods here. This storage does not supply all Character methods.
struct RF455CharacterStorage {RF455KnownModelPrefix prefix;unsigned char tail[388];};
static_assert(sizeof(RF455CharacterStorage)==1188,"455 character allocation");
#pragma pack(push,4)
struct RF455CharacterManager {
    std::uint32_t opaque0;RF455CharacterStorage** begin;RF455CharacterStorage** end;RF455CharacterStorage** capacity;
    std::uint32_t nextId;char name[128];RF455CharacterStorage* cache[1000];
};
#pragma pack(pop)
static_assert(sizeof(RF455CharacterManager)==4148 && offsetof(RF455CharacterManager,cache)==148,"455 manager fields");
struct RF455RawModelBuffer {void* bytes;std::uint32_t length;};
extern "C" {
void RF455_ConstructCharacter(RF455CharacterStorage* character);
// Preserves opaque0 andname128;zeros vector,nextId and1000cache slots.
void RF455_ConstructCharacterManager(RF455CharacterManager* manager);
RF455CharacterStorage* RF455_CreateCharacter(RF455CharacterManager* manager,const char* name,RF455CharacterStorage* parent,const RF455MeshMemoryOps* memory);
int RF455_AddCharacter(RF455CharacterManager* manager,RF455CharacterStorage* character,const RF455MeshMemoryOps* memory);
RF455CharacterStorage* RF455_FindCharacterName(RF455CharacterManager* manager,const char* name);
RF455CharacterStorage* RF455_FindCharacterId(RF455CharacterManager* manager,std::uint32_t id);
std::uint32_t RF455_CharacterId(RF455CharacterManager* manager,const char* name);
void RF455_DeleteCharacterName(RF455CharacterManager* manager,const char* name,const RF455MeshMemoryOps* memory);
void RF455_DeleteCharacterId(RF455CharacterManager* manager,std::uint32_t id,const RF455MeshMemoryOps* memory);
void RF455_ClearCharacters(RF455CharacterManager* manager,const RF455MeshMemoryOps* memory);
void RF455_DestroyCharacterManager(RF455CharacterManager* manager,const RF455MeshMemoryOps* memory);
// Borrowed texture pointers only,no AddRef. Caller keeps texture manager alive.
void RF455_RefreshModelTextures(RF455KnownModelPrefix* model,RF455TextureManager* textures);
// MSH-only raw IO:extension helper skips character0 when no dot;RFS first,
// loose fallback. Own length checks reject short/invalid reads;no input EXE runs.
int RF455_ReadMshFile(const char* name,const RF455MeshMemoryOps* memory,RF455RawModelBuffer* output);
}
