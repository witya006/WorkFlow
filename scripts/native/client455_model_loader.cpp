#include "client455_model_loader.h"
#include <cstring>
#include <vector>

namespace {
template<class T>T get(const unsigned char* bytes,unsigned at){T value;std::memcpy(&value,bytes+at,sizeof(value));return value;}
template<class T>void put(unsigned char* bytes,unsigned at,T value){std::memcpy(bytes+at,&value,sizeof(value));}
struct Pending {
    const RF455MeshMemoryOps* memory;RF455MeshStorage* meshes=nullptr;std::vector<void*> bones;
    void freeBones(){for(auto* pointer:bones)memory->release(memory->context,pointer);bones.clear();}
    ~Pending(){freeBones();if(meshes)RF455_DeleteMeshStorage(meshes,3,memory);}
};
}
extern "C" RF455ModelLoadStatus RF455_LoadMesh08Model(void* input,std::size_t length,
    RF455KnownModelPrefix* model,const RF455ModelLoadContext* context,RF455ModelLoadStats* stats){
    if(!input || !model || !context || !stats || !context->memory.allocate || !context->memory.release || !context->matrices.inverse || !context->matrices.multiply || !context->textures || !context->vertices || !context->indices || !context->meshAccounting || !context->bufferAccounting)return RF_MODEL_ARGUMENT;
    if(length<8 || !std::memchr(model->bytes+276,0,256))return RF_MODEL_FORMAT;
    const auto count=get<std::uint16_t>(static_cast<unsigned char*>(input),6);std::vector<RF455Mesh08Part> parts(count);RF455Mesh08View view={};
    if(RF455_DecodeMesh08(input,length,parts.data(),parts.size(),&view)!=RF_MESH08_OK)return RF_MODEL_FORMAT;
    Pending pending={&context->memory};pending.bones.reserve(count);pending.meshes=RF455_AllocateMeshArray(count,context->meshAccounting,&context->memory);if(!pending.meshes)return RF_MODEL_MEMORY;
    const auto materials=RF455_TextureMaterialOps(context->textures);RF455ModelLoadStats result={};
    for(unsigned i=0;i<count;++i){
        auto* header=const_cast<unsigned char*>(parts[i].header);
        if(RF455_LoadMesh08Materials(&pending.meshes[i],header,reinterpret_cast<const char*>(model->bytes+276),context->textures->directory,&materials)!=RF_MESH_RUNTIME_OK)return RF_MODEL_HEADER;
        auto flag=get<std::uint32_t>(model->bytes,796);
        const auto headerResult=RF455_ApplyMesh08Header(&pending.meshes[i],&parts[i],&context->matrices,&flag);put(model->bytes,796,flag);
        if(headerResult!=RF_MESH_RUNTIME_OK)return RF_MODEL_HEADER;
        RF455_UploadMesh08Gpu(context->vertices,context->indices,context->bufferAccounting,&pending.meshes[i],&parts[i]);
        const auto size=404u*parts[i].boneCount;void* copy=context->memory.allocate(context->memory.context,size);if(!copy)return RF_MODEL_MEMORY;
        if(size)std::memcpy(copy,parts[i].bones,size);pending.bones.push_back(copy);parts[i].bones=static_cast<unsigned char*>(copy);
    }
    for(unsigned i=0;i<count;++i)pending.meshes[i].bytes[512]=0;
    RF455_BindMeshParents(pending.meshes,count,pending.meshes,count);
    auto* external=get<RF455KnownModelPrefix*>(model->bytes,272);RF455MeshStorage* parents=pending.meshes;int parentCount=count;
    if(external){parents=get<RF455MeshStorage*>(external->bytes,536);parentCount=get<std::int32_t>(external->bytes,532);RF455_BindMeshParents(parents,parentCount,pending.meshes,count);}
    if(RF455_ResolveMesh08Bones(parents,parentCount,pending.meshes,count,parts.data(),&result.bindings)!=RF_MESH_BIND_OK)return RF_MODEL_BINDING;
    pending.freeBones();put(model->bytes,536,pending.meshes);put<std::uint32_t>(model->bytes,532,count);pending.meshes=nullptr;
    result.publishedMeshes=count;*stats=result;return RF_MODEL_OK;
}
