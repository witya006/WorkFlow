#include "client455_resource_io.h"
#include <string.h>
#include <stddef.h>
#include <new>
#include "jmalloc.h"
#include "jerror.h"

static_assert(sizeof(RF455_RpkNode)==64,"RPK node");
static_assert(offsetof(RF455_RpkNode,declaredSize)==52,"RPK declared size");
static_assert(sizeof(RF455_RpkFile)==276,"RPK file owner x86");
static_assert(sizeof(RF455_RpkGroup)==268,"RPK group owner x86");
static RF455_RpkGroup* activeGroup=NULL;

RF455_RpkFile::RF455_RpkFile() { memset(this,0,sizeof(*this)); }
RF455_RpkGroup::RF455_RpkGroup() { memset(this,0,sizeof(*this)); }

BOOL RF455_RpkFile::LoadIndex(const char* path) {
    strcpy(filename,path);
    FILE* fp=fopen(filename,"rb");
    if (!fp) return FALSE;
    float version;
    fread(&version,4,1,fp);
    if (version!=1.0f) {
        fclose(fp);
        Warning((char*)"name",(char*)"\x3c\x2d\xb9\xf6\xc1\xaf\xc0\xcc\x20\xbf\xb9\xc0\xfc\xb9\xf6\xc1\xaf\xc0\xd4\xb4\xcf\xb4\xd9\x2e");
        return FALSE;
    }
    fread(&count,4,1,fp);
    payloadBase=8+72*count;
    children=(DWORD*)Dmalloc(72*count);
    offsets=(LONG*)(children+count);
    nodes=(RF455_RpkNode*)(children+2*count);
    fread(children,4*count,1,fp);
    fread(offsets,4*count,1,fp);
    fread(nodes,64*count,1,fp);
    fclose(fp);
    return TRUE;
}

void RF455_RpkFile::Release() {
    if (children) {
        Dfree(children);
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

LONG RF455_RpkFile::LookupOffset(DWORD parent,const char* path) const {
    if (!path || !*path) return 0;
    char component[132];unsigned consumed;
    unsigned length=pathComponent(component,path,&consumed);
    const RF455_RpkNode& node=nodes[parent];
    for (unsigned i=0;i<node.childCount;++i) {
        DWORD id=children[node.childStart+i];
        if (nodes[id].nameLength!=length || memcmp(nodes[id].name,component,(length+3u)&~3u)) continue;
        if (offsets[id]!=-1) return offsets[id];
        LONG found=LookupOffset(id,path+consumed+1);
        if (found!=-1) return found;
    }
    return -1;
}

FILE* RF455_RpkFile::Open(const char* path,const char* mode) const {
    LONG offset=LookupOffset(0,path);
    if (offset==-1) return NULL;
    FILE* fp=fopen(filename,mode);
    if (fp) fseek(fp,(LONG)(payloadBase+(DWORD)offset),SEEK_SET);
    return fp;
}

void RF455_RpkGroup::LoadDirectory(const char* path) {
    strcpy(directory,path);
    char pattern[256];sprintf(pattern,"%s\\*.*",path);
    WIN32_FIND_DATAA found;
    HANDLE handle=FindFirstFileA(pattern,&found);
    if (handle==INVALID_HANDLE_VALUE) return;
    char (*names)[256]=(char(*)[256])Dmalloc(65536);
    DWORD total=0;
    // Preserve the reference's immediate FindNextFile: the first result is skipped.
    while (FindNextFileA(handle,&found)) {
        if (!strcmp(found.cFileName,".") || !strcmp(found.cFileName,"..") || (found.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)) continue;
        _strlwr(found.cFileName);
        size_t len=strlen(found.cFileName);
        if (len>=4 && found.cFileName[len-1]=='k' && found.cFileName[len-2]=='p' && found.cFileName[len-3]=='r')
            strcpy(names[total++],found.cFileName);
    }
    FindClose(handle);
    if (total>255) {
        Warning((char*)path,(char*)"\x72\x70\x6b\xc6\xc4\xc0\xcf\x20\xc3\xd6\xb4\xeb\x20\xb0\xb9\xbc\xf6\xb0\xa1\x20\xb3\xd1\xbe\xfa\xbd\xc0\xb4\xcf\xb4\xd9\x2e");
    } else if (total) {
        prefixLength=(DWORD)strlen(path);count=total;
        archives=(RF455_RpkFile*)Dmalloc(sizeof(RF455_RpkFile)*total);
        for (DWORD i=0;i<total;++i) new (archives+i) RF455_RpkFile;
        for (DWORD i=0;i<count;++i) {
            char file[256];sprintf(file,"%s%s",path,names[i]);_strlwr(file);
            archives[i].LoadIndex(file);
        }
    }
    Dfree(names);
}

void RF455_RpkGroup::Release() {
    if (archives) {
        for (DWORD i=0;i<count;++i) archives[i].Release();
        Dfree(archives);archives=NULL;count=0;
    }
}

FILE* RF455_RpkGroup::Open(char* path,const char* mode) const {
    _strlwr(path);
    for (DWORD i=0;i<count;++i) {
        FILE* fp=archives[i].Open(path+prefixLength,mode);
        if (fp) return fp;
    }
    return NULL;
}

RF455_RpkGroup* RF455_SetResourceGroup(RF455_RpkGroup* group) { return activeGroup=group; }
BOOL RF455_RpkGroup::Exists(char* path) const {
    _strlwr(path);
    for (DWORD i=0;i<count;++i)
        if (archives[i].LookupOffset(0,path+prefixLength)!=-1) return TRUE;
    return FALSE;
}
RF455_RpkGroup* RF455_GetResourceGroup() { return activeGroup; }
FILE* RF455_OpenResource(char* path,const char* mode) {
    if (activeGroup) {
        FILE* fp=activeGroup->Open(path,mode);
        if (fp) return fp;
    }
    return fopen(path,mode);
}
BOOL RF455_ResourceExists(char* path) {
    if (!path || !*path) return FALSE;
    if (activeGroup && activeGroup->Exists(path)) return TRUE;
    FILE* fp=fopen(path,"rb");
    if (!fp) return FALSE;
    fclose(fp);return TRUE;
}
bool RF455_ParticleScriptEnd(const char* token) { return strcmp(token,"end")==0; }
