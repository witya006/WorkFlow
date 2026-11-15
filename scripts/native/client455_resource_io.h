#ifndef RF455_RESOURCE_IO_H
#define RF455_RESOURCE_IO_H
#include <windows.h>
#include <stdio.h>
#include "client455_character_rfs.h"

#pragma pack(push,1)
struct RF455_RpkNode {
    char name[52];
    DWORD declaredSize;
    WORD nameLength,childCount;
    DWORD childStart;
};
#pragma pack(pop)

// File indexes are explicitly released by their archive group.
struct RF455_RpkFile {
    char filename[256];
    RF455_RpkNode* nodes;
    LONG* offsets;
    DWORD* children;
    DWORD count,payloadBase;
    RF455_RpkFile();
    BOOL LoadIndex(const char* path);
    void Release();
    LONG LookupOffset(DWORD parent,const char* path) const;
    // Exclusive absolute end from the next distinct payload start, or 0 for EOF.
    std::uint64_t NextMemberOffset(LONG offset) const;
    FILE* Open(const char* path,const char* mode) const;
};
struct RF455_RpkGroup {
    char directory[256];
    DWORD prefixLength,count;
    RF455_RpkFile* archives;
    RF455_RpkGroup();
    ~RF455_RpkGroup() noexcept;
    RF455_RpkGroup(const RF455_RpkGroup&) = delete;
    RF455_RpkGroup& operator=(const RF455_RpkGroup&) = delete;
    void LoadDirectory(const char* path);
    // As for LoadDirectory, path includes the trailing resource separator.
    // Keep the current group when any archive slot fails to load.
    bool TryReplaceDirectory455(const char* path);
    void Release() noexcept;
    FILE* Open(char* path,const char* mode) const;
    BOOL Exists(char* path) const;
};

RF455_RpkGroup* RF455_SetResourceGroup(RF455_RpkGroup* group);
RF455_RpkGroup* RF455_GetResourceGroup();
// Scene archives reuse one bounded index. The scene member owns an ordinary
// group when its directory cannot be retained. Resource files stay streamed.
// Retained indexes assume archive files are immutable until replacement or
// explicit reset. Use these entry points on the engine resource thread.
void RF455_SelectSceneResourceGroup(RF455_RpkGroup* scene,const char* path);
void RF455_ActivateSceneResourceGroup(RF455_RpkGroup* scene);
void RF455_ReleaseSceneResourceGroup(RF455_RpkGroup* scene) noexcept;
void RF455_ClearSceneResourceCache() noexcept;
//8E75D0/8E75E0 andthe gated8E75F0/8E7680 loose-file fallback.
BOOL RF455_SetResourceArchiveEnabled(BOOL enabled);
BOOL RF455_GetResourceArchiveEnabled();
FILE* RF455_OpenResource(char* path,const char* mode);
// Only consumers that own bounded reads use this API. Existing FILE callers
// continue to see the physical end of the pack. The optional origin flag is
// set when an archive member was selected, including an archive read error.
RF455ResourceRead RF455_ReadResourceBytes(char* path,std::uint64_t maxBytes,bool* fromArchive=nullptr);
// On success, an RPK stream is binary and bounded by archiveBytes. A loose
// stream uses CRT text mode and returns UINT64_MAX for the extent.
FILE* RF455_OpenResourceTextStream455(char* path, std::uint64_t& archiveBytes);
BOOL RF455_ResourceExists(char* path);
// End is checked before lowercasing, in both search and body loops.
bool RF455_ParticleScriptEnd(const char* token);
#endif
