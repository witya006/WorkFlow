#include "client455_shared_buffers.h"
#include <cstring>
#include <vector>

namespace {
constexpr unsigned noSlot=1025;
template<class Pool> unsigned firstSlot(const Pool* pool,std::uint32_t size,std::uint32_t capacity){
    // The x86 add wraps before its unsigned comparison. Keep that behavior;
    // the real COM Lock remains responsible for rejecting invalid ranges.
    for(unsigned i=0;i<RF455_BUFFER_SLOTS;++i)if(pool->used[i]+size<=capacity)return i;
    return noSlot;
}
template<class Pool> void destroy(Pool* pool){
    for(unsigned i=0;i<RF455_BUFFER_SLOTS;++i)if(pool->buffers[i])pool->buffers[i]->Release();
}
int uploadVertex(RF455VertexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting,DWORD fvf){
    if(!pool->device)return 0;
    const unsigned slot=firstSlot(pool,size,RF455_VERTEX_BLOCK_BYTES);if(slot==noSlot)return 0;
    if(!pool->buffers[slot]){
        if(FAILED(pool->device->CreateVertexBuffer(RF455_VERTEX_BLOCK_BYTES,8,fvf,D3DPOOL_MANAGED,&pool->buffers[slot],nullptr)))return 0;
        ++accounting->created;accounting->bytes+=RF455_VERTEX_BLOCK_BYTES;
    }
    void* destination=nullptr;
    if(FAILED(pool->buffers[slot]->Lock(pool->used[slot],size,&destination,0)))return 0;
    std::memcpy(destination,source,size);pool->buffers[slot]->Unlock();
    *absolute=RF455_VERTEX_BLOCK_BYTES*slot+pool->used[slot];pool->used[slot]+=size;return 1;
}
void bindVertex(RF455VertexBufferPool* pool,std::uint32_t absolute,UINT stride){
    if(pool->device && absolute!=0xffffffffu && absolute/RF455_VERTEX_BLOCK_BYTES<RF455_BUFFER_SLOTS)
        pool->device->SetStreamSource(0,pool->buffers[absolute/RF455_VERTEX_BLOCK_BYTES],0,stride);
}
}
extern "C" void RF455_ConstructVertexPool(RF455VertexBufferPool* pool){std::memset(pool,0,sizeof(*pool));}
extern "C" void RF455_ConstructIndexPool(RF455IndexBufferPool* pool){std::memset(pool,0,sizeof(*pool));}
extern "C" void RF455_DestroyVertexPool(RF455VertexBufferPool* pool){destroy(pool);}
extern "C" void RF455_DestroyIndexPool(RF455IndexBufferPool* pool){destroy(pool);}
extern "C" int RF455_UploadVertices36(RF455VertexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting){return uploadVertex(pool,source,size,absolute,accounting,278);}
extern "C" int RF455_UploadVertices64(RF455VertexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting){return uploadVertex(pool,source,size,absolute,accounting,282);}
extern "C" int RF455_UploadIndices(RF455IndexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting){
    if(!pool->device)return 0;
    const unsigned slot=firstSlot(pool,size,RF455_INDEX_BLOCK_BYTES);if(slot==noSlot)return 0;
    if(!pool->buffers[slot]){
        if(FAILED(pool->device->CreateIndexBuffer(RF455_INDEX_BLOCK_BYTES,8,D3DFMT_INDEX16,D3DPOOL_MANAGED,&pool->buffers[slot],nullptr)))return 0;
        ++accounting->created;accounting->bytes+=RF455_INDEX_BLOCK_BYTES;
    }
    void* destination=nullptr;
    if(FAILED(pool->buffers[slot]->Lock(pool->used[slot],size,&destination,0)))return 0;
    std::memcpy(destination,source,size);pool->buffers[slot]->Unlock();
    *absolute=RF455_INDEX_BLOCK_BYTES*slot+pool->used[slot];pool->used[slot]+=size;return 1;
}
extern "C" void RF455_BindVertices36(RF455VertexBufferPool* pool,std::uint32_t absolute){bindVertex(pool,absolute,36);}
extern "C" void RF455_BindVertices64(RF455VertexBufferPool* pool,std::uint32_t absolute){bindVertex(pool,absolute,64);}
extern "C" void RF455_BindIndices(RF455IndexBufferPool* pool,std::uint32_t absolute){
    if(pool->device && absolute!=0xffffffffu && absolute/RF455_INDEX_BLOCK_BYTES<RF455_BUFFER_SLOTS)
        pool->device->SetIndices(pool->buffers[absolute/RF455_INDEX_BLOCK_BYTES]);
}
extern "C" void RF455_RebaseMesh08Indices(void* indices,std::uint16_t count,std::uint32_t vertexAbsolute){
    auto* bytes=static_cast<unsigned char*>(indices);const auto base=(vertexAbsolute%RF455_VERTEX_BLOCK_BYTES)>>6;
    for(unsigned i=0;i<count;++i){std::uint16_t value;std::memcpy(&value,bytes+2*i,2);value=static_cast<std::uint16_t>(value+base);std::memcpy(bytes+2*i,&value,2);}
}
extern "C" void RF455_UploadMesh08Gpu(RF455VertexBufferPool* vertices,RF455IndexBufferPool* indices,
    RF455BufferAccounting* accounting,RF455MeshStorage* mesh,const RF455Mesh08Part* part){
    if(!part->indexCount)return;
    std::vector<unsigned char> rebased(2u*part->indexCount);std::memcpy(rebased.data(),part->indices,rebased.size());
    std::uint32_t vertexAbsolute,indexAbsolute;std::memcpy(&vertexAbsolute,mesh->bytes+4494,4);std::memcpy(&indexAbsolute,mesh->bytes+4502,4);
    RF455_UploadVertices64(vertices,part->vertices,64u*part->vertexCount,&vertexAbsolute,accounting);
    std::memcpy(mesh->bytes+4494,&vertexAbsolute,4);
    RF455_RebaseMesh08Indices(rebased.data(),part->indexCount,vertexAbsolute);
    RF455_UploadIndices(indices,rebased.data(),static_cast<std::uint32_t>(rebased.size()),&indexAbsolute,accounting);
    std::memcpy(mesh->bytes+4502,&indexAbsolute,4);
}
