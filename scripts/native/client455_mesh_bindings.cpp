#include "client455_mesh_bindings.h"
#include <cstring>

namespace {
template<class T> T read(const unsigned char* bytes,unsigned offset) {
    T value;std::memcpy(&value,bytes+offset,sizeof(value));return value;
}
template<class T> void write(unsigned char* bytes,unsigned offset,T value) {
    std::memcpy(bytes+offset,&value,sizeof(value));
}
bool namesValid(const RF455MeshStorage* meshes,int count) {
    for(int n=0;n<count;++n)if(!std::memchr(meshes[n].bytes,0,256))return false;
    return true;
}
int bind(RF455MeshStorage* parents,int parentCount,RF455MeshStorage* meshes,int meshCount,bool rematch) {
    int matches=0;
    for(int n=0;n<meshCount;++n) {
        auto* bytes=meshes[n].bytes;
        if(rematch && !read<std::uint32_t>(bytes,5495))continue;
        auto* found=RF455_FindParentMesh(reinterpret_cast<const char*>(bytes+256),parents,parentCount);
        if(!found)continue;
        write(bytes,518,found);bytes[512]=1;
        if(parents!=meshes)write<std::uint32_t>(bytes,5495,1);
        ++matches;
    }
    return matches;
}
}
extern "C" RF455MeshStorage* RF455_FindParentMesh(const char* name,RF455MeshStorage* meshes,int count) {
    for(int n=0;n<count;++n)if(!std::strcmp(name,reinterpret_cast<const char*>(meshes[n].bytes)))return &meshes[n];
    return nullptr;
}
extern "C" int RF455_BindMeshParents(RF455MeshStorage* parents,int parentCount,RF455MeshStorage* meshes,int meshCount) {
    return bind(parents,parentCount,meshes,meshCount,false);
}
extern "C" int RF455_RematchMeshParents(RF455MeshStorage* parents,int parentCount,RF455MeshStorage* meshes,int meshCount) {
    return bind(parents,parentCount,meshes,meshCount,true);
}
extern "C" RF455MeshBindingStatus RF455_ResolveMesh08Bones(RF455MeshStorage* parents,int parentCount,
    RF455MeshStorage* meshes,int meshCount,const RF455Mesh08Part* parts,RF455MeshBindingStats* stats) {
    if(!stats || (parentCount>0 && !parents) || (meshCount>0 && (!meshes || !parts)))return RF_MESH_BIND_ARGUMENT;
    if(!namesValid(parents,parentCount) || !namesValid(meshes,meshCount))return RF_MESH_BIND_RECORD;
    RF455MeshBindingStats result={};
    for(int n=0;n<meshCount;++n) {
        const auto& part=parts[n];if(part.boneCount && !part.bones)return RF_MESH_BIND_ARGUMENT;
        RF455MeshStorage* selected[50];unsigned count=0;
        for(unsigned r=0;r<part.boneCount;++r) {
            const auto* record=part.bones+404u*r;const auto influences=read<std::int32_t>(record,0);
            if(influences>4)return RF_MESH_BIND_RECORD;
            for(int b=0;b<influences;++b) {
                const char* name=reinterpret_cast<const char*>(record+4+100*b);
                if(!std::memchr(name,0,100))return RF_MESH_BIND_RECORD;
                bool duplicate=false;
                for(unsigned i=0;i<count;++i)if(!std::strcmp(name,reinterpret_cast<const char*>(selected[i]->bytes)))duplicate=true;
                if(duplicate)continue;
                auto* found=RF455_FindParentMesh(name,parents,parentCount);
                if(!found)found=RF455_FindParentMesh(name,meshes,meshCount);
                if(!found){++result.missingNames;continue;}
                if(count==50)return RF_MESH_BIND_CAPACITY;
                selected[count++]=found;++result.resolvedNames;
            }
        }
        auto* bytes=meshes[n].bytes;write(bytes,522,count);
        // Verified reference order matters: pointers are copied AFTER identity
        // matrices. At count31+ their copy overlaps the first matrix bytes.
        // Preserve these observable writes; do not infer a disjoint50-slot ABI.
        for(unsigned i=0;i<count;++i)for(unsigned j=0;j<16;++j)
            write<std::uint32_t>(bytes,646+64*i+4*j,(j%5==0)?0x3f800000u:0u);
        if(count)std::memcpy(bytes+526,selected,4u*count);
    }
    *stats=result;return RF_MESH_BIND_OK;
}
