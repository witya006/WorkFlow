#ifndef RF455_RESOURCE_IO_H
#define RF455_RESOURCE_IO_H
#include <windows.h>
#include <stdio.h>

#pragma pack(push,1)
struct RF455_RpkNode {
    char name[52];
    DWORD declaredSize;
    WORD nameLength,childCount;
    DWORD childStart;
};
#pragma pack(pop)

// Explicit Release matches the engine's manual resource lifecycle. Constructors
// establish empty ownership; destructors do not invent automatic release calls.
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
    FILE* Open(const char* path,const char* mode) const;
};
struct RF455_RpkGroup {
    char directory[256];
    DWORD prefixLength,count;
    RF455_RpkFile* archives;
    RF455_RpkGroup();
    void LoadDirectory(const char* path);
    void Release();
    FILE* Open(char* path,const char* mode) const;
    BOOL Exists(char* path) const;
};

RF455_RpkGroup* RF455_SetResourceGroup(RF455_RpkGroup* group);
RF455_RpkGroup* RF455_GetResourceGroup();
//8E75D0/8E75E0 andthe gated8E75F0/8E7680 loose-file fallback.
BOOL RF455_SetResourceArchiveEnabled(BOOL enabled);
BOOL RF455_GetResourceArchiveEnabled();
FILE* RF455_OpenResource(char* path,const char* mode);
BOOL RF455_ResourceExists(char* path);
// End is checked before lowercasing, in both search and body loops.
bool RF455_ParticleScriptEnd(const char* token);
#endif
