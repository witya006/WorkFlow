#include "client455_model_lifecycle.h"
#include <unknwn.h>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <initializer_list>

namespace {
template<class T>T get(const unsigned char* bytes,unsigned offset){T x;std::memcpy(&x,bytes+offset,sizeof(x));return x;}
template<class T>void put(unsigned char* bytes,unsigned offset,T x){std::memcpy(bytes+offset,&x,sizeof(x));}
void* __cdecl allocate(void*,std::size_t size){return std::malloc(size);}
void __cdecl release(void*,void* pointer){std::free(pointer);}
void destroyTables(unsigned char* tables,const RF455MeshMemoryOps* memory){
    for(unsigned i=0;i<20;++i)for(unsigned at:{4*i,4*(i+20)}){
        void* pointer=get<void*>(tables,at);if(pointer){memory->release(memory->context,pointer);put<void*>(tables,at,nullptr);}
    }
    std::memset(tables,0,168);
}
void destroyStrings(unsigned char* object,const RF455MeshMemoryOps* memory){
    // Five old basic_string fields,reverse member order. Preserve all bytes
    // except capacity=15,length=0,first byte=0;the freed pointer tail survives.
    for(unsigned at:{132u,96u,68u,32u,4u}){
        if(get<std::uint32_t>(object,at+20)>=16)memory->release(memory->context,get<void*>(object,at));
        put<std::uint32_t>(object,at+20,15);put<std::uint32_t>(object,at+16,0);object[at]=0;
    }
}
}
RF455MeshMemoryOps RF455_CrtMeshMemoryOps(){return {nullptr,allocate,release};}
extern "C" void RF455_DestroyMeshStorage(RF455MeshStorage* mesh,const RF455MeshMemoryOps* memory){
    auto* bytes=mesh->bytes;
    for(unsigned at:{4486u,4490u}){auto* object=get<IUnknown*>(bytes,at);if(object)object->Release();}
    for(unsigned at:{5095u,5099u,4506u}){void* pointer=get<void*>(bytes,at);if(pointer){memory->release(memory->context,pointer);put<void*>(bytes,at,nullptr);}}
    destroyTables(bytes+5595,memory);destroyStrings(bytes+5163,memory);
}
extern "C" RF455MeshStorage* RF455_AllocateMeshArray(std::uint32_t count,RF455MeshAccounting* accounting,const RF455MeshMemoryOps* memory){
    // Owned overflow/null-allocation errors. Valid MESH08 counts are WORDs.
    if(count>((std::numeric_limits<std::size_t>::max)()-4)/5803)return nullptr;
    auto* base=static_cast<unsigned char*>(memory->allocate(memory->context,4+5803u*count));if(!base)return nullptr;
    put(base,0,count);auto* meshes=reinterpret_cast<RF455MeshStorage*>(base+4);
    for(std::uint32_t i=0;i<count;++i)RF455_ConstructMeshStorage(&meshes[i],accounting);return meshes;
}
extern "C" void* RF455_DeleteMeshStorage(RF455MeshStorage* mesh,unsigned flags,const RF455MeshMemoryOps* memory){
    auto* base=reinterpret_cast<unsigned char*>(mesh);
    if(flags&2){base-=4;const auto count=get<std::uint32_t>(base,0);for(auto i=count;i>0;--i)RF455_DestroyMeshStorage(&mesh[i-1],memory);}
    else RF455_DestroyMeshStorage(mesh,memory);
    if(flags&1)memory->release(memory->context,base);return base;
}
extern "C" void RF455_ReleaseModelMeshArray(void* modelPrefix,const RF455MeshMemoryOps* memory){
    auto* bytes=static_cast<unsigned char*>(modelPrefix);auto* meshes=get<RF455MeshStorage*>(bytes,536);
    if(get<std::uint32_t>(bytes,260) && meshes){RF455_DeleteMeshStorage(meshes,3,memory);put<RF455MeshStorage*>(bytes,536,nullptr);}
}
