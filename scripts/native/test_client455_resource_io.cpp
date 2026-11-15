// Standalone caller of the same production module. The engine warning hook is
// test instrumentation, never linked into the normal client.
#include "client455_resource_io.h"
#include <bcrypt.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <direct.h>

static unsigned warnings=0;
void Warning(char*,char*) { ++warnings; }

static bool read(FILE* fp,void* p,size_t size) { return fread(p,1,size,fp)==size; }
static bool write(FILE* fp,const void* p,size_t size) { return fwrite(p,1,size,fp)==size; }

static int members(const char* archive,const char* request,const char* output) {
    RF455_RpkFile rpk;
    if (!rpk.LoadIndex(archive)) return 10;
    FILE* in=fopen(request,"rb");FILE* out=fopen(output,"wb");
    if (!in || !out) return 11;
    char magic[8];DWORD count;
    if (!read(in,magic,8) || memcmp(magic,"RFPRQ455",8) || !read(in,&count,4)) return 12;
    write(out,"RFPOS455",8);write(out,&count,4);
    BCRYPT_ALG_HANDLE algorithm=NULL;
    if (BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,NULL,0)<0) return 13;
    for (DWORD i=0;i<count;++i) {
        char name[256];DWORD size;
        if (!read(in,name,256) || !read(in,&size,4) || name[255]) return 14;
        FILE* fp=rpk.Open(name,"rb");
        DWORD opened=fp!=NULL,position=fp?(DWORD)ftell(fp):0,consumed=0;
        unsigned char digest[32]={},buffer[65536];int after=EOF;
        if (fp) {
            BCRYPT_HASH_HANDLE hash=NULL;
            if (BCryptCreateHash(algorithm,&hash,NULL,0,NULL,0,0)<0) return 15;
            while (consumed<size) {
                DWORD want=size-consumed;if (want>sizeof(buffer)) want=sizeof(buffer);
                size_t got=fread(buffer,1,want,fp);
                if (!got) break;
                if (BCryptHashData(hash,buffer,(ULONG)got,0)<0) return 16;
                consumed+=(DWORD)got;
            }
            if (BCryptFinishHash(hash,digest,32,0)<0) return 17;
            BCryptDestroyHash(hash);
            after=fgetc(fp);fclose(fp);
        }
        write(out,&opened,4);write(out,&position,4);write(out,&consumed,4);
        write(out,digest,32);write(out,&after,4);
    }
    BCryptCloseAlgorithmProvider(algorithm,0);
    fclose(in);fclose(out);rpk.Release();rpk.Release();
    return rpk.children || rpk.offsets || rpk.nodes ? 18 : 0;
}

static int group(const char* path,const char* request,const char* output) {
    RF455_RpkGroup owner;
    owner.LoadDirectory(path);
    FILE* in=fopen(request,"rb");FILE* out=fopen(output,"wb");
    if (!in || !out) return 31;
    char magic[8];DWORD count;
    if (!read(in,magic,8) || memcmp(magic,"RFGRQ455",8) || !read(in,&count,4)) return 32;
    write(out,"RFGOS455",8);write(out,&owner.count,4);write(out,&owner.prefixLength,4);
    for (DWORD i=0;i<owner.count;++i) write(out,owner.archives[i].filename,256);
    RF455_SetResourceGroup(&owner);
    for (DWORD i=0;i<count;++i) {
        char name[256];DWORD active;
        if (!read(in,name,256) || !read(in,&active,4)) return 33;
        RF455_SetResourceGroup(active?&owner:NULL);
        BOOL exists=RF455_ResourceExists(name);
        FILE* fp=RF455_OpenResource(name,"rb");int first=fp?fgetc(fp):-2;
        if (fp) fclose(fp);
        write(out,name,256);write(out,&first,4);write(out,&exists,4);
    }
    RF455_SetResourceGroup(NULL);owner.Release();owner.Release();
    // Keep the old output shape. This field now checks released owner state;
    // the index allocations use CRT malloc/free and are not counted here.
    DWORD unreleased=owner.archives || owner.count,warningCount=warnings;
    write(out,&unreleased,4);write(out,&warningCount,4);
    fclose(in);fclose(out);return unreleased?34:0;
}

static bool fixture(const char* path, const void* bytes, size_t size) {
    FILE* fp = fopen(path, "wb");
    if (!fp) return false;
    const bool written = write(fp, bytes, size);
    return fclose(fp) == 0 && written;
}

static bool memberAndFollowingByte(const RF455_RpkFile& archive) {
    FILE* fp = archive.Open("dir\\a.spt", "rb");
    if (!fp) return false;
    char bytes[4];
    const bool found = ftell(fp) == 296 && read(fp, bytes, sizeof(bytes)) &&
                       !memcmp(bytes, "oneT", sizeof(bytes));
    fclose(fp);
    return found;
}

static int malformed(const char* valid, const char* scratch) {
    unsigned char original[302];
    FILE* fp = fopen(valid, "rb");
    if (!fp) return 41;
    const bool known = read(fp, original, sizeof(original)) && fgetc(fp) == EOF;
    fclose(fp);
    if (!known) return 41;

    RF455_RpkFile archive;
    if (!archive.LoadIndex(valid) || !memberAndFollowingByte(archive) ||
        archive.NextMemberOffset(0) != 299 || archive.NextMemberOffset(3) != 0 ||
        archive.NextMemberOffset(-1) != 0) return 42;
    if (archive.LoadIndex(scratch) || !memberAndFollowingByte(archive) ||
        archive.NextMemberOffset(0) != 299) return 43;

    // The input is scripts/test_map455.py's four-node fixture. Independently
    // corrupt count, child id, signed offset, name length, and child range.
    const struct Change { size_t at; DWORD value; size_t width; } corrupt[] = {
        {4, MAXDWORD, 4}, {8, 4, 4}, {32, 7, 4}, {40 + 56, 53, 2},
        {40 + 60, MAXDWORD, 4}
    };
    for (const auto& change : corrupt) {
        unsigned char bytes[sizeof(original)];
        memcpy(bytes, original, sizeof(bytes));
        memcpy(bytes + change.at, &change.value, change.width);
        if (!fixture(scratch, bytes, sizeof(bytes))) return 44;
        if (archive.LoadIndex(scratch) || !memberAndFollowingByte(archive)) return 45;
    }
    if (!fixture(scratch, original, sizeof(original)) || !archive.LoadIndex(scratch) ||
        !memberAndFollowingByte(archive) || archive.LookupOffset(0, "dir") != 0 ||
        archive.LookupOffset(9999, "dir\\a.spt") != -1)
        return 46;
    unsigned char cyclic[sizeof(original)];
    memcpy(cyclic, original, sizeof(cyclic));
    const DWORD directoryId = 1, rightChildRange = 2;
    // The directory points to itself twice. Every path component matches,
    // forcing both branches to fail before a naive search could return.
    memcpy(cyclic + 16, &directoryId, 4);
    memcpy(cyclic + 40 + 64 + 60, &rightChildRange, 4);
    char repeated[256] = "";
    for (unsigned i = 0; i < 40; ++i) strcat(repeated, "dir\\");
    strcat(repeated, "missing");
    if (!fixture(scratch, cyclic, sizeof(cyclic)) || !archive.LoadIndex(scratch) ||
        archive.LookupOffset(0, repeated) != -1) return 53;

    // Node order differs from payload order and two file nodes alias one start.
    unsigned char aliased[sizeof(original)];
    memcpy(aliased, original, sizeof(aliased));
    const LONG starts[] = {-1, 3, 0, 0};
    memcpy(aliased + 24, starts, sizeof(starts));
    if (!fixture(scratch, aliased, sizeof(aliased)) || !archive.LoadIndex(scratch) ||
        archive.NextMemberOffset(0) != 299 || archive.NextMemberOffset(3) != 0) return 89;
    archive.Release();
    archive.Release();
    if (archive.Open("dir\\a.spt", "rb") || archive.LookupOffset(0, "") != -1 ||
        archive.NextMemberOffset(0) != 0) return 47;

    if (!CreateDirectoryA("rpk-malformed-group", NULL) && GetLastError() != ERROR_ALREADY_EXISTS)
        return 48;
    const DWORD oldVersion = 0x40000000u;
    if (!fixture("rpk-malformed-group\\bad.rpk", &oldVersion, sizeof(oldVersion)) ||
        !fixture("rpk-malformed-group\\loose.spt", "L", 1)) return 49;
    if (!CreateDirectoryA("rpk-replacement-group", NULL) && GetLastError() != ERROR_ALREADY_EXISTS)
        return 54;
    if (!fixture("rpk-replacement-group\\good.rpk", original, sizeof(original))) return 54;
    RF455_RpkGroup group;
    const auto beforeWarnings = warnings;
    group.LoadDirectory("rpk-malformed-group\\");
    if (group.count != 1 || warnings != beforeWarnings + 1 || group.archives[0].children)
        return 50;
    RF455_SetResourceGroup(&group);
    RF455_SetResourceArchiveEnabled(FALSE);
    group.LoadDirectory("rpk-missing-group\\");
    if (group.count != 1 || strcmp(group.directory, "rpk-malformed-group\\") ||
        RF455_GetResourceGroup() != &group || RF455_GetResourceArchiveEnabled()) return 51;
    RF455_SetResourceArchiveEnabled(TRUE);
    char shortPath[] = "missing";
    char loosePath[] = "RPK-MALFORMED-GROUP\\LOOSE.SPT";
    fp = RF455_OpenResource(loosePath, "rb");
    const int first = fp ? fgetc(fp) : -2;
    if (fp) fclose(fp);
    const bool fallback = first == 'L' && RF455_ResourceExists(loosePath) &&
                          !RF455_ResourceExists(shortPath);
    if (!fallback) return 52;
    RF455_SetResourceArchiveEnabled(FALSE);
    group.LoadDirectory("rpk-replacement-group\\");
    if (group.count != 1 || strcmp(group.directory, "rpk-replacement-group\\") ||
        RF455_GetResourceGroup() != &group || RF455_GetResourceArchiveEnabled()) return 55;
    char packedPath[] = "rpk-replacement-group\\dir\\a.spt";
    if (RF455_ResourceExists(packedPath)) return 55;
    RF455_SetResourceArchiveEnabled(TRUE);
    group.LoadDirectory("rpk-replacement-group\\");
    if (RF455_GetResourceGroup() != &group || !RF455_GetResourceArchiveEnabled() ||
        !RF455_ResourceExists(packedPath)) return 56;
    group.Release();
    group.Release();
    if (group.archives || group.count || RF455_GetResourceGroup() || RF455_GetResourceArchiveEnabled())
        return 57;
    RF455_SetResourceGroup(&group);
    {
        RF455_RpkGroup scoped;
        scoped.LoadDirectory("rpk-replacement-group\\");
        if (scoped.count != 1 || !scoped.archives) return 58;
    }
    if (RF455_GetResourceGroup() != &group || !RF455_GetResourceArchiveEnabled()) return 59;
    {
        RF455_RpkGroup scoped;
        scoped.LoadDirectory("rpk-replacement-group\\");
        RF455_SetResourceGroup(&scoped);
        if (!RF455_ResourceExists(packedPath)) return 60;
    }
    if (RF455_GetResourceGroup() || RF455_GetResourceArchiveEnabled()) return 61;
    puts("PASS: malformed RPK, duplicate and unordered member offsets, bounded lookup, loose fallback and group lifetime");
    return 0;
}

static int sceneCache(const char* fixtureArchive, const char* realRoot) {
    unsigned char archive[302];
    FILE* fp = fopen(fixtureArchive, "rb");
    if (!fp) return 62;
    const bool sourceOkay = read(fp, archive, sizeof(archive)) && fgetc(fp) == EOF;
    fclose(fp);
    if (!sourceOkay) return 62;

    const char* const sceneDirectories[] = {"scene-a", "scene-b", "scene-a\\packs", "scene-b\\packs"};
    for (const auto* path : sceneDirectories) {
        if (!CreateDirectoryA(path, nullptr) && GetLastError() != ERROR_ALREADY_EXISTS) return 63;
    }
    if (!fixture("scene-a\\packs\\a.rpk", archive, sizeof(archive))) return 64;
    memcpy(archive + 296, "two", 3);
    if (!fixture("scene-b\\packs\\a.rpk", archive, sizeof(archive))) return 64;
    char cwd[512];
    if (!_getcwd(cwd, sizeof(cwd)) || _chdir("scene-a")) return 65;

    const auto open = [] {
        char member[] = "packs\\dir\\a.spt";
        FILE* stream = RF455_OpenResource(member, "rb");
        if (!stream) return EOF;
        const int first = fgetc(stream);
        fclose(stream);
        return first;
    };

    RF455_RpkGroup first, second, unrelated;
    RF455_SelectSceneResourceGroup(&first, "packs\\");
    auto* cached = RF455_GetResourceGroup();
    if (!cached || cached->count != 1 || open() != 'o') return 66;
    const auto* index = cached->archives[0].children;
    RF455_ReleaseSceneResourceGroup(&first);
    if (RF455_GetResourceGroup() || RF455_GetResourceArchiveEnabled()) return 67;

    // Invalidate the on-disk header while preserving the payload. A second
    // scan would fail, so this also proves that the old index was reused.
    memcpy(archive + 296, "one", 3);
    const DWORD invalidVersion = 0;
    memcpy(archive, &invalidVersion, sizeof(invalidVersion));
    if (!fixture("packs\\a.rpk", archive, sizeof(archive))) return 68;
    RF455_SelectSceneResourceGroup(&second, "packs\\");
    if (RF455_GetResourceGroup() != cached || cached->archives[0].children != index || open() != 'o')
        return 69;
    RF455_SetResourceGroup(&unrelated);
    RF455_SetResourceArchiveEnabled(FALSE);
    RF455_ReleaseSceneResourceGroup(&first);
    if (RF455_GetResourceGroup() != &unrelated || RF455_GetResourceArchiveEnabled()) return 70;
    RF455_ActivateSceneResourceGroup(&second);
    if (RF455_GetResourceGroup() != cached || open() != 'o') return 71;
    auto* bytesCache = RF455_GetCharacterRfsCache();
    bytesCache->Clear();
    const auto reads = bytesCache->Stats().payloadReads;
    char request[] = "packs\\dir\\a.spt";
    const auto memberBytes = RF455_ReadResourceBytes(request, 1024);
    if (memberBytes.status != RF455ResourceReadStatus::Ready || !memberBytes.bytes ||
        memberBytes.bytes->size() != 3 || memcmp(memberBytes.bytes->data(), "one", 3))
        return 83;
    const auto firstHit = RF455_ReadResourceBytes(request, 3);
    const auto rejected = RF455_ReadResourceBytes(request, 2);
    if (firstHit.bytes != memberBytes.bytes || rejected.status != RF455ResourceReadStatus::ReadError ||
        rejected.bytes || bytesCache->Stats().payloadReads != reads + 1) return 84;
    if (!CreateDirectoryA("packs\\dir", nullptr) && GetLastError() != ERROR_ALREADY_EXISTS) return 85;
    if (!fixture("packs\\dir\\a.spt", "L", 1)) return 85;
    RF455_SetResourceArchiveEnabled(FALSE);
    const auto loose = RF455_ReadResourceBytes(request, 1024);
    if (!loose.bytes || loose.bytes->size() != 1 || loose.bytes->front() != 'L') return 86;
    RF455_SetResourceArchiveEnabled(TRUE);
    if (RF455_ReadResourceBytes(request, 2).status != RF455ResourceReadStatus::ReadError) return 87;
    if (!DeleteFileA("packs\\dir\\a.spt")) return 88;

    RF455_ReleaseSceneResourceGroup(&second);
    if (_chdir(cwd) || _chdir("scene-b")) return 72;
    RF455_SelectSceneResourceGroup(&first, "packs\\");
    if (open() != 't') return 73;
    RF455_ReleaseSceneResourceGroup(&first);

    if (_chdir(cwd) || _chdir("scene-a")) return 74;
    RF455_SelectSceneResourceGroup(&second, "packs\\");
    if (open() != EOF) return 75;
    RF455_ReleaseSceneResourceGroup(&second);
    const float version = 1.0f;
    memcpy(archive, &version, sizeof(version));
    if (!fixture("packs\\a.rpk", archive, sizeof(archive))) return 76;
    RF455_SelectSceneResourceGroup(&second, "packs\\");
    if (open() != 'o') return 77;
    RF455_ClearSceneResourceCache();
    if (RF455_GetResourceGroup() || RF455_GetResourceArchiveEnabled()) return 78;

    // The production map directory uses the same ordered archive lookup and
    // currently fits in the one retained group.
    if (_chdir(realRoot)) return 79;
    RF455_SelectSceneResourceGroup(&first, ".\\Map\\Entity\\");
    auto* real = RF455_GetResourceGroup();
    char member[] = ".\\Map\\Entity\\e_battledungeon\\1.spt";
    if (!real || !real->count || !RF455_ResourceExists(member)) return 80;
    RF455_ReleaseSceneResourceGroup(&first);
    RF455_SelectSceneResourceGroup(&second, ".\\Map\\Entity\\");
    if (RF455_GetResourceGroup() != real || !RF455_ResourceExists(member)) return 81;
    RF455_SetResourceGroup(&unrelated);
    RF455_ClearSceneResourceCache();
    if (RF455_GetResourceGroup() != &unrelated || !RF455_GetResourceArchiveEnabled()) return 82;
    puts("PASS: scene RPK index reuse, root changes, retry and teardown");
    return 0;
}

int main(int argc,char** argv) {
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    if (argc!=5) return 2;
    if (!strcmp(argv[1],"members")) return members(argv[2],argv[3],argv[4]);
    if (!strcmp(argv[1],"group")) return group(argv[2],argv[3],argv[4]);
    if (!strcmp(argv[1],"malformed")) return malformed(argv[2],argv[3]);
    if (!strcmp(argv[1],"scenes")) return sceneCache(argv[2],argv[3]);
    return 3;
}
