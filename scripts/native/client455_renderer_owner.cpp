#include "client455_renderer_owner.h"
#include "client455_renderer_owner_constants.h"
#include <cstring>

extern "C" void RF455_ConstructCharacterRenderer(RF455CharacterRenderer* owner){
    RF455_ConstructCharacterManager(&owner->bones);RF455_ConstructCharacterManager(&owner->meshes);
    RF455_ConstructTextureManager(&owner->textures);
    owner->effects.begin=owner->effects.end=owner->effects.capacity=nullptr;
    RF455_ConstructVertexPool(&owner->vertices64);RF455_ConstructVertexPool(&owner->vertices36);RF455_ConstructIndexPool(&owner->indices);
    owner->device=nullptr;owner->opaque4=0;owner->sprite=nullptr;
    std::memset(&owner->light,0,sizeof(owner->light));owner->light.Type=D3DLIGHT_DIRECTIONAL;
    owner->light.Diffuse.r=owner->light.Diffuse.g=owner->light.Diffuse.b=.8f;
    owner->light.Ambient.r=owner->light.Ambient.g=owner->light.Ambient.b=1;
    owner->light.Direction.z=-1;owner->effects.nextId=0;owner->effects.active=0;
    owner->effects.batchEnabled=0;std::memset(owner->effects.resources,0,sizeof(owner->effects.resources));owner->effects.extra=nullptr;
    owner->vertexMode=2;owner->opaque33840=0;owner->frame8416=0;owner->indexedBlend=0;
}
extern "C" int RF455_SetCharacterRendererDevice(RF455CharacterRenderer* owner,RF455RendererShared* shared,
    IDirect3DDevice9* device,const RF455ShaderApi* api,const RF455RendererDiagnostics* diagnostics){
    owner->device=owner->textures.device=owner->vertices64.device=owner->vertices36.device=owner->indices.device=device;
    device->GetDeviceCaps(&owner->caps);
    owner->indexedBlend=owner->caps.MaxVertexBlendMatrixIndex!=0;
    if(!owner->indexedBlend)OutputDebugStringW(RF455_RENDERER_BLEND_WARNING);
    if(owner->caps.MaxVertexBlendMatrices==2 || owner->caps.MaxVertexBlendMatrices==4)owner->vertexMode=owner->caps.MaxVertexBlendMatrices;
    owner->specular=(owner->caps.ShadeCaps>>9)&1;int result=static_cast<int>(owner->specular);
    std::memcpy(shared->logPath,RF455_RENDERER_LOG_PATH,256);
    if(!shared->shaders.device){
        shared->shaders.device=device;
        result=RF455_InitializeCharacterShaders(&shared->shaders,api,&owner->sprite,&shared->declaration64,&shared->declaration36);
        if(result<0 && diagnostics && diagnostics->shaderFailure)return diagnostics->shaderFailure(diagnostics->context,result);
    }
    return result;
}
extern "C" void RF455_DestroyCharacterRenderer(RF455CharacterRenderer* owner,const RF455MeshMemoryOps* memory){
    for(auto* resource:owner->effects.resources)if(resource)resource->Release();
    if(owner->effects.extra)owner->effects.extra->Release();
    if(owner->sprite){owner->sprite->Release();owner->sprite=nullptr;}
    RF455_DestroyIndexPool(&owner->indices);RF455_DestroyVertexPool(&owner->vertices36);RF455_DestroyVertexPool(&owner->vertices64);
    for(auto** i=owner->effects.begin;i!=owner->effects.end;++i)if(*i){RF455_DestroyCharacterManager(*i,memory);memory->release(memory->context,*i);}
    if(owner->effects.begin)memory->release(memory->context,owner->effects.begin);
    owner->effects.begin=owner->effects.end=owner->effects.capacity=nullptr;
    RF455_DestroyTextureManager(&owner->textures);RF455_DestroyCharacterManager(&owner->meshes,memory);RF455_DestroyCharacterManager(&owner->bones,memory);
}
extern "C" RF455ModelLoadContext RF455_RendererModelContext(RF455CharacterRenderer* owner,const RF455MeshMemoryOps* memory,
    const RF455MeshMatrixOps* matrix,RF455MeshAccounting* meshes,RF455BufferAccounting* buffers){
    return {*memory,*matrix,&owner->textures,&owner->vertices64,&owner->indices,meshes,buffers};
}
extern "C" void RF455_BindRendererDrawContext(RF455CharacterRenderer* owner,RF455RendererShared* shared,RF455CharacterDrawContext* context){
    context->state={owner->device,owner->vertexMode,shared->declaration36,shared->declaration64,reinterpret_cast<const float*>(&owner->light),owner->specular};
    context->shaders=&shared->shaders;context->vertices36=&owner->vertices36;context->vertices64=&owner->vertices64;context->indices=&owner->indices;
    context->batchEnabled=owner->effects.batchEnabled!=0;
}
