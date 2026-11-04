// Standalone caller of the same production module. Engine allocation/warning
// hooks below are test instrumentation, never linked into the normal client.
#include "client455_resource_io.h"
#include <bcrypt.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int allocations=0,warnings=0;
void* Dmalloc(int size) { void* result=malloc(size);if (!result) ExitProcess(91);++allocations;return result; }
void Dfree(void* ptr) { if (ptr) { --allocations;free(ptr); } }
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
    return allocations?18:0;
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
    DWORD leaks=(DWORD)allocations,warningCount=(DWORD)warnings;
    write(out,&leaks,4);write(out,&warningCount,4);
    fclose(in);fclose(out);return leaks?34:0;
}

int main(int argc,char** argv) {
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    if (argc!=5) return 2;
    if (!strcmp(argv[1],"members")) return members(argv[2],argv[3],argv[4]);
    if (!strcmp(argv[1],"group")) return group(argv[2],argv[3],argv[4]);
    return 3;
}
