#include "client455_resource_io.h"
#include <io.h>
#include <string.h>
#include <stddef.h>
#include <stdlib.h>
#include <algorithm>
#include <limits>
#include <memory>
#include <new>
#include "jerror.h"

static_assert(sizeof(RF455_RpkNode)==64,"RPK node");
static_assert(offsetof(RF455_RpkNode,declaredSize)==52,"RPK declared size");
static_assert(sizeof(RF455_RpkFile)==276,"RPK file owner x86");
static_assert(sizeof(RF455_RpkGroup)==268,"RPK group owner x86");
static RF455_RpkGroup* activeGroup=NULL;
static BOOL archiveEnabled=FALSE;

namespace {
using FileOwner = std::unique_ptr<FILE, decltype(&fclose)>;
using FreeOwner = std::unique_ptr<void, decltype(&free)>;
constexpr size_t wireIndexStride = sizeof(DWORD) + sizeof(LONG) + sizeof(RF455_RpkNode);
constexpr size_t indexStride = wireIndexStride + sizeof(LONG);

RF455_RpkGroup* selectedScene = nullptr;
RF455_RpkGroup* selectedSceneGroup = nullptr;
char retainedDirectory[MAX_PATH]{};
RF455_RpkGroup retainedGroup;

void unselectScene() noexcept {
    if (selectedSceneGroup && activeGroup == selectedSceneGroup) {
        activeGroup = nullptr;
        archiveEnabled = FALSE;
    }
    selectedScene = nullptr;
    selectedSceneGroup = nullptr;
}

bool validIndex(DWORD count, const DWORD* children, const LONG* offsets,
                const RF455_RpkNode* nodes, unsigned long long payloadBytes) {
    for (DWORD i = 0; i < count; ++i) {
        const auto& node = nodes[i];
        if (children[i] >= count || node.nameLength > sizeof(node.name) ||
            node.childStart > count || node.childCount > count - node.childStart)
            return false;
        const LONG offset = offsets[i];
        if (offset != -1 && (offset < 0 || static_cast<unsigned long long>(offset) > payloadBytes))
            return false;
    }
    return true;
}

void releaseArchives(RF455_RpkFile* archives, DWORD count) noexcept {
    if (!archives) return;
    for (DWORD i = 0; i < count; ++i) archives[i].Release();
    free(archives);
}
}

RF455_RpkFile::RF455_RpkFile() { memset(this,0,sizeof(*this)); }
RF455_RpkGroup::RF455_RpkGroup() { memset(this,0,sizeof(*this)); }
RF455_RpkGroup::~RF455_RpkGroup() noexcept { Release(); }

BOOL RF455_RpkFile::LoadIndex(const char* path) {
    if (!path || !*path || strlen(path) >= sizeof(filename)) return FALSE;
    FileOwner fp(fopen(path, "rb"), fclose);
    if (!fp) return FALSE;
    float version;
    if (fread(&version, sizeof(version), 1, fp.get()) != 1) return FALSE;
    if (version!=1.0f) {
        fp.reset();
        Warning((char*)"name",(char*)"\x3c\x2d\xb9\xf6\xc1\xaf\xc0\xcc\x20\xbf\xb9\xc0\xfc\xb9\xf6\xc1\xaf\xc0\xd4\xb4\xcf\xb4\xd9\x2e");
        return FALSE;
    }
    DWORD nextCount = 0;
    if (fread(&nextCount, sizeof(nextCount), 1, fp.get()) != 1 || !nextCount ||
        nextCount > (MAXDWORD - 8) / wireIndexStride ||
        nextCount > (std::numeric_limits<size_t>::max)() / indexStride)
        return FALSE;
    const DWORD tableBytes = static_cast<DWORD>(wireIndexStride * nextCount);
    const DWORD nextPayloadBase = 8u + tableBytes;
    const auto fileBytes = _filelengthi64(_fileno(fp.get()));
    if (fileBytes < static_cast<__int64>(nextPayloadBase)) return FALSE;

    // This private allocation can fail cleanly. The engine allocator assumes
    // malloc succeeds and adds a signed-size header before returning the block.
    FreeOwner table(malloc(indexStride * nextCount), free);
    if (!table || fread(table.get(), 1, tableBytes, fp.get()) != tableBytes) return FALSE;
    auto* nextChildren = static_cast<DWORD*>(table.get());
    auto* nextOffsets = reinterpret_cast<LONG*>(nextChildren + nextCount);
    auto* nextNodes = reinterpret_cast<RF455_RpkNode*>(nextOffsets + nextCount);
    if (!validIndex(nextCount, nextChildren, nextOffsets, nextNodes,
                    static_cast<unsigned long long>(fileBytes - nextPayloadBase)))
        return FALSE;
    // Keep wire offsets in node order and sort a separate tail in the same allocation.
    auto* orderedOffsets = reinterpret_cast<LONG*>(nextNodes + nextCount);
    std::copy_n(nextOffsets, nextCount, orderedOffsets);
    std::sort(orderedOffsets, orderedOffsets + nextCount);

    // Commit after all reads and checks; a failed load leaves the old index usable.
    // path may alias filename on an explicit reload.
    memmove(filename, path, strlen(path) + 1);
    Release();
    table.release();
    children = nextChildren;
    offsets = nextOffsets;
    nodes = nextNodes;
    count = nextCount;
    payloadBase = nextPayloadBase;
    return TRUE;
}

void RF455_RpkFile::Release() {
    if (children) {
        free(children);
        children=NULL;offsets=NULL;nodes=NULL;
        // Reference retains filename/count/payloadBase.
    }
}

static unsigned pathComponent(char* part,const char* path,unsigned* consumed) {
    unsigned i=0,length=0;
    while (i<128 && path[i]=='\\') ++i;
    while (i<128 && path[i] && path[i]!='\\') part[length++]=path[i++];
    memset(part+length,0,4);
    *consumed=i;
    return length;
}

namespace {
LONG lookupOffset(const RF455_RpkFile& archive, DWORD parent, const char* path,
                  unsigned depth, DWORD& remaining) {
    if (!path || !*path) return 0;
    // The old lookup recurses for directories. Bound stack use for malformed
    // indexes and oversized chains; ordinary Win32 paths fit within this depth.
    if (depth >= MAX_PATH) return -1;
    char component[132];unsigned consumed;
    unsigned length=pathComponent(component,path,&consumed);
    const RF455_RpkNode& node=archive.nodes[parent];
    for (unsigned i=0;i<node.childCount;++i) {
        if (!remaining) return -1;
        --remaining;
        DWORD id=archive.children[node.childStart+i];
        if (archive.nodes[id].nameLength!=length || memcmp(archive.nodes[id].name,component,(length+3u)&~3u)) continue;
        if (archive.offsets[id]!=-1) return archive.offsets[id];
        const char* tail = path + consumed;
        if (*tail) ++tail;
        LONG found=lookupOffset(archive,id,tail,depth+1,remaining);
        if (found!=-1) return found;
    }
    return -1;
}
}

LONG RF455_RpkFile::LookupOffset(DWORD parent,const char* path) const {
    if (!children || !nodes || !offsets || parent >= count) return -1;
    // A tree visits at most count - 1 children, including repeated names in
    // separate subtrees. Allow extra visits but cap work for shared/cyclic links.
    DWORD remaining = 4u * count;
    return lookupOffset(*this, parent, path, 0, remaining);
}

std::uint64_t RF455_RpkFile::NextMemberOffset(LONG offset) const {
    if (!nodes || offset < 0 || !count) return 0;
    const auto* first = reinterpret_cast<const LONG*>(nodes + count);
    const auto* end = first + count;
    const auto* next = std::upper_bound(first, end, offset);
    return next == end ? 0 : static_cast<std::uint64_t>(payloadBase) + *next;
}

FILE* RF455_RpkFile::Open(const char* path,const char* mode) const {
    if (!path || !mode || !*mode) return NULL;
    LONG offset=LookupOffset(0,path);
    if (offset==-1) return NULL;
    FileOwner fp(fopen(filename,mode), fclose);
    if (!fp) return NULL;
    const auto position = static_cast<__int64>(payloadBase) + offset;
    if (_filelengthi64(_fileno(fp.get())) < position || _fseeki64(fp.get(),position,SEEK_SET))
        return NULL;
    // Readers see the real archive EOF. The original ignores declaredSize;
    // commercial RPKs contain inaccurate values in this field.
    return fp.release();
}

namespace {
// Report whether the published group is complete. The ordinary group API
// keeps its existing behavior of publishing usable slots from a partial scan.
bool scanGroup(RF455_RpkGroup& group, const char* path, bool requireComplete = false) {
    if (!path || !*path) return false;
    const auto pathLength = strlen(path);
    char pattern[256];
    if (pathLength > sizeof(pattern) - sizeof("\\*.*")) return false;
    sprintf(pattern,"%s\\*.*",path);
    constexpr DWORD maxArchives = 255;
    constexpr size_t nameSize = sizeof(RF455_RpkFile::filename);
    FreeOwner names(malloc(maxArchives * nameSize), free);
    if (!names) return false;
    auto* nameBytes = static_cast<char*>(names.get());
    WIN32_FIND_DATAA found;
    HANDLE handle=FindFirstFileA(pattern,&found);
    DWORD total=0;
    bool overflow = false;
    DWORD enumerationError = ERROR_NO_MORE_FILES;
    // Preserve the reference's immediate FindNextFile: the first result is skipped.
    if (handle != INVALID_HANDLE_VALUE) {
        while (FindNextFileA(handle,&found)) {
            if (!strcmp(found.cFileName,".") || !strcmp(found.cFileName,"..") || (found.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)) continue;
            _strlwr(found.cFileName);
            size_t len=strlen(found.cFileName);
            if (len<4 || strcmp(found.cFileName+len-3,"rpk")) continue;
            if (total == maxArchives) { overflow = true; break; }
            char* name = nameBytes + total++ * nameSize;
            *name = '\0';
            if (len < nameSize) memcpy(name, found.cFileName, len + 1);
        }
        enumerationError = overflow ? ERROR_SUCCESS : GetLastError();
        if (!FindClose(handle) && requireComplete) return false;
    } else {
        const DWORD error = GetLastError();
        if (!requireComplete || (error != ERROR_FILE_NOT_FOUND && error != ERROR_NO_MORE_FILES))
            return false;
        const DWORD attributes = GetFileAttributesA(path);
        if (attributes == INVALID_FILE_ATTRIBUTES || !(attributes & FILE_ATTRIBUTE_DIRECTORY))
            return false;
    }
    if (overflow) {
        // The legacy warning function appends the message and a postfix in
        // its own fixed 256-byte buffer.
        char displayPath[192];
        strncpy_s(displayPath, sizeof(displayPath), path, _TRUNCATE);
        Warning(displayPath,(char*)"\x72\x70\x6b\xc6\xc4\xc0\xcf\x20\xc3\xd6\xb4\xeb\x20\xb0\xb9\xbc\xf6\xb0\xa1\x20\xb3\xd1\xbe\xfa\xbd\xc0\xb4\xcf\xb4\xd9\x2e");
        return false;
    }
    if (enumerationError != ERROR_NO_MORE_FILES) return false;

    RF455_RpkGroup staged;
    if (total) {
        staged.archives = static_cast<RF455_RpkFile*>(malloc(sizeof(RF455_RpkFile)*total));
        if (!staged.archives) return false;
    }
    bool complete = true;
    for (DWORD i = 0; i < total; ++i) {
        auto& candidate = *new (staged.archives + i) RF455_RpkFile;
        ++staged.count;
        const char* name = nameBytes + i * nameSize;
        char file[nameSize];
        if (!*name || strlen(name) >= sizeof(file) - pathLength) {
            if (requireComplete) return false;
            complete = false;
            continue;
        }
        memcpy(file, path, pathLength);
        strcpy(file + pathLength, name);
        _strlwr(file);
        if (!candidate.LoadIndex(file)) {
            if (requireComplete) return false;
            strcpy(candidate.filename,file);
            complete = false;
        }
    }

    if (requireComplete) {
        // Verified replacement can reuse the same path and member offsets.
        // Existing leases stay readable while subsequent calls see disk data.
        auto* cache = RF455_GetCharacterRfsCache();
        for (DWORD i = 0; i < group.count; ++i)
            cache->RemoveRpkArchiveBytes(group.archives[i].filename);
        for (DWORD i = 0; i < staged.count; ++i)
            cache->RemoveRpkArchiveBytes(staged.archives[i].filename);
    }

    // A successful scan installs its group, including any unusable slots, in
    // enumeration order. Missing directory, overflow or allocation failure
    // leaves the old group intact.
    memmove(group.directory,path,pathLength+1);
    // Replacement keeps the selected owner and its current archive flag.
    releaseArchives(group.archives, group.count);
    group.prefixLength = static_cast<DWORD>(pathLength);
    group.count = staged.count;
    group.archives = staged.archives;
    staged.archives = nullptr;
    staged.count = 0;
    return complete && (requireComplete || total != 0);
}

bool withinIndexBudget(const RF455_RpkGroup& group) {
    constexpr unsigned long long budget = 16ull * 1024 * 1024;
    auto bytes = static_cast<unsigned long long>(group.count) * sizeof(RF455_RpkFile);
    for (DWORD i = 0; i < group.count; ++i)
        bytes += static_cast<unsigned long long>(group.archives[i].count) * indexStride;
    return bytes <= budget;
}
}

void RF455_RpkGroup::LoadDirectory(const char* path) {
    scanGroup(*this, path);
}

bool RF455_RpkGroup::TryReplaceDirectory455(const char* path) {
    try {
        return scanGroup(*this, path, true);
    } catch (const std::bad_alloc&) {
        return false;
    }
}

void RF455_RpkGroup::Release() noexcept {
    if (selectedScene == this || selectedSceneGroup == this) unselectScene();
    if (activeGroup == this) {
        activeGroup = NULL;
        archiveEnabled = FALSE;
    }
    releaseArchives(archives, count);
    archives = NULL;
    count = 0;
}

void RF455_SelectSceneResourceGroup(RF455_RpkGroup* scene,const char* path) {
    if (!scene) return;
    char absoluteDirectory[MAX_PATH];
    const DWORD absoluteLength = path && *path
        ? GetFullPathNameA(path, MAX_PATH, absoluteDirectory, nullptr) : 0;
    const bool cacheablePath = absoluteLength && absoluteLength < MAX_PATH;

    scene->Release();
    RF455_RpkGroup* group = scene;
    if (cacheablePath && retainedGroup.archives &&
        _stricmp(absoluteDirectory, retainedDirectory) == 0 &&
        _stricmp(path, retainedGroup.directory) == 0) {
        group = &retainedGroup;
    } else if (scanGroup(*scene, path) && cacheablePath && withinIndexBudget(*scene)) {
        retainedGroup.Release();
        strcpy(retainedDirectory, absoluteDirectory);
        strcpy(retainedGroup.directory, scene->directory);
        retainedGroup.prefixLength = scene->prefixLength;
        retainedGroup.count = scene->count;
        retainedGroup.archives = scene->archives;
        scene->archives = nullptr;
        scene->count = 0;
        group = &retainedGroup;
    }

    selectedScene = scene;
    selectedSceneGroup = group;
    RF455_SetResourceGroup(group);
}

void RF455_ActivateSceneResourceGroup(RF455_RpkGroup* scene) {
    if (scene && selectedScene == scene) RF455_SetResourceGroup(selectedSceneGroup);
}

void RF455_ReleaseSceneResourceGroup(RF455_RpkGroup* scene) noexcept {
    if (scene) scene->Release();
}

void RF455_ClearSceneResourceCache() noexcept {
    unselectScene();
    retainedGroup.Release();
    retainedDirectory[0] = '\0';
}

FILE* RF455_RpkGroup::Open(char* path,const char* mode) const {
    if (!path || !mode || !*mode) return NULL;
    _strlwr(path);
    if (!archives || strlen(path) < prefixLength) return NULL;
    for (DWORD i=0;i<count;++i) {
        FILE* fp=archives[i].Open(path+prefixLength,mode);
        if (fp) return fp;
    }
    return NULL;
}

RF455_RpkGroup* RF455_SetResourceGroup(RF455_RpkGroup* group) {
    activeGroup=group;archiveEnabled=group!=NULL;return activeGroup;
}
BOOL RF455_SetResourceArchiveEnabled(BOOL enabled){return archiveEnabled=enabled;}
BOOL RF455_GetResourceArchiveEnabled(){return archiveEnabled;}
BOOL RF455_RpkGroup::Exists(char* path) const {
    if (!path) return FALSE;
    _strlwr(path);
    if (!archives || strlen(path) < prefixLength) return FALSE;
    for (DWORD i=0;i<count;++i)
        if (archives[i].LookupOffset(0,path+prefixLength)!=-1) return TRUE;
    return FALSE;
}
RF455_RpkGroup* RF455_GetResourceGroup() { return activeGroup; }
FILE* RF455_OpenResource(char* path,const char* mode) {
    if (!path || !*path || !mode || !*mode) return NULL;
    if (archiveEnabled && activeGroup) {
        FILE* fp=activeGroup->Open(path,mode);
        if (fp) return fp;
    }
    return fopen(path,mode);
}
BOOL RF455_ResourceExists(char* path) {
    if (!path || !*path) return FALSE;
    if (archiveEnabled && activeGroup && activeGroup->Exists(path)) return TRUE;
    FILE* fp=fopen(path,"rb");
    if (!fp) return FALSE;
    fclose(fp);return TRUE;
}
bool RF455_ParticleScriptEnd(const char* token) { return strcmp(token,"end")==0; }
