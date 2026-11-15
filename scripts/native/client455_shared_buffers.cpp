#include "client455_shared_buffers.h"
#include <cstring>
#include <new>
#include <stdexcept>

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
// These managed pools use their existing system-memory backing for migration.
// Omitting WRITEONLY lets the old device provide a read-only Lock on demand.
HRESULT createVertexBuffer(IDirect3DDevice9* device, DWORD fvf, IDirect3DVertexBuffer9** buffer)
{
    return device->CreateVertexBuffer(RF455_VERTEX_BLOCK_BYTES, 0, fvf, D3DPOOL_MANAGED, buffer, nullptr);
}
HRESULT createIndexBuffer(IDirect3DDevice9* device, IDirect3DIndexBuffer9** buffer)
{
    return device->CreateIndexBuffer(RF455_INDEX_BLOCK_BYTES, 0, D3DFMT_INDEX16, D3DPOOL_MANAGED, buffer, nullptr);
}
int uploadVertex(RF455VertexBufferPool* pool,const void* source,std::uint32_t size,std::uint32_t* absolute,RF455BufferAccounting* accounting,DWORD fvf){
    if(!pool->device)return 0;
    const unsigned slot=firstSlot(pool,size,RF455_VERTEX_BLOCK_BYTES);if(slot==noSlot)return 0;
    if(!pool->buffers[slot]){
        if(FAILED(createVertexBuffer(pool->device,fvf,&pool->buffers[slot])))return 0;
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

using Slots = std::vector<RF455CharacterBufferSlot>;

template<class Pool>
HRESULT capturePool(const Pool& pool, std::uint32_t capacity, Slots& slots)
{
    for (unsigned slot = 0; slot < RF455_BUFFER_SLOTS; ++slot) {
        const auto used = pool.used[slot];
        auto* buffer = pool.buffers[slot];
        if (used > capacity || (used && !buffer)) return E_INVALIDARG;
        if (!buffer) continue;

        slots.push_back({slot, std::vector<unsigned char>(used)});
        if (!used) continue;
        void* source = nullptr;
        const HRESULT read = buffer->Lock(0, used, &source, D3DLOCK_READONLY);
        if (FAILED(read)) return read;
        if (source) std::memcpy(slots.back().bytes.data(), source, used);
        const HRESULT unlock = buffer->Unlock();
        if (!source) return E_FAIL;
        if (FAILED(unlock)) return unlock;
    }
    return S_OK;
}

template<class Pool>
bool emptyPool(const Pool& pool)
{
    if (pool.device) return false;
    for (unsigned slot = 0; slot < RF455_BUFFER_SLOTS; ++slot)
        if (pool.buffers[slot] || pool.used[slot]) return false;
    return true;
}

bool validSlots(const Slots& slots, std::uint32_t capacity)
{
    if (slots.size() > RF455_BUFFER_SLOTS) return false;
    bool seen[RF455_BUFFER_SLOTS] = {};
    for (const auto& slot : slots) {
        if (slot.slot >= RF455_BUFFER_SLOTS || seen[slot.slot] || slot.bytes.size() > capacity) return false;
        seen[slot.slot] = true;
    }
    return true;
}

template<class Pool, class Create>
HRESULT recreatePool(Pool& pool, const Slots& slots, Create create)
{
    for (const auto& slot : slots) {
        auto*& buffer = pool.buffers[slot.slot];
        const HRESULT created = create(&buffer);
        if (FAILED(created)) return created;
        if (!buffer) return E_FAIL;
        if (slot.bytes.empty()) continue;

        const auto used = static_cast<UINT>(slot.bytes.size());
        void* destination = nullptr;
        const HRESULT written = buffer->Lock(0, used, &destination, 0);
        if (FAILED(written)) return written;
        if (destination) std::memcpy(destination, slot.bytes.data(), used);
        const HRESULT unlock = buffer->Unlock();
        if (!destination) return E_FAIL;
        if (FAILED(unlock)) return unlock;
        pool.used[slot.slot] = used;
    }
    return S_OK;
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
        if(FAILED(createIndexBuffer(pool->device,&pool->buffers[slot])))return 0;
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

HRESULT RF455_CaptureCharacterBuffers(const RF455VertexBufferPool& vertices36,
    const RF455VertexBufferPool& vertices64, const RF455IndexBufferPool& indices,
    RF455CharacterBufferSnapshot& output)
{
    try {
        RF455CharacterBufferSnapshot staged;
        HRESULT result = capturePool(vertices36, RF455_VERTEX_BLOCK_BYTES, staged.vertices36);
        if (SUCCEEDED(result)) result = capturePool(vertices64, RF455_VERTEX_BLOCK_BYTES, staged.vertices64);
        if (SUCCEEDED(result)) result = capturePool(indices, RF455_INDEX_BLOCK_BYTES, staged.indices);
        if (FAILED(result)) return result;

        output.vertices36.swap(staged.vertices36);
        output.vertices64.swap(staged.vertices64);
        output.indices.swap(staged.indices);
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (const std::length_error&) {
        return E_OUTOFMEMORY;
    }
}

HRESULT RF455_RecreateCharacterBuffers(const RF455CharacterBufferSnapshot& snapshot,
    IDirect3DDevice9* device, RF455VertexBufferPool& vertices36,
    RF455VertexBufferPool& vertices64, RF455IndexBufferPool& indices)
{
    if (!device || &vertices36 == &vertices64 || !emptyPool(vertices36) || !emptyPool(vertices64) ||
        !emptyPool(indices) || !validSlots(snapshot.vertices36, RF455_VERTEX_BLOCK_BYTES) ||
        !validSlots(snapshot.vertices64, RF455_VERTEX_BLOCK_BYTES) ||
        !validSlots(snapshot.indices, RF455_INDEX_BLOCK_BYTES)) return E_INVALIDARG;

    RF455VertexBufferPool staged36{}, staged64{};
    RF455IndexBufferPool stagedIndices{};
    HRESULT result = recreatePool(staged36, snapshot.vertices36, [device](IDirect3DVertexBuffer9** buffer) {
        return createVertexBuffer(device, 278, buffer);
    });
    if (SUCCEEDED(result)) result = recreatePool(staged64, snapshot.vertices64, [device](IDirect3DVertexBuffer9** buffer) {
        return createVertexBuffer(device, 282, buffer);
    });
    if (SUCCEEDED(result)) result = recreatePool(stagedIndices, snapshot.indices, [device](IDirect3DIndexBuffer9** buffer) {
        return createIndexBuffer(device, buffer);
    });
    if (FAILED(result)) {
        destroy(&staged36);
        destroy(&staged64);
        destroy(&stagedIndices);
        return result;
    }

    staged36.device = staged64.device = stagedIndices.device = device;
    staged36.opaque8192 = vertices36.opaque8192;
    staged64.opaque8192 = vertices64.opaque8192;
    stagedIndices.opaque8192 = indices.opaque8192;
    vertices36 = staged36;
    vertices64 = staged64;
    indices = stagedIndices;
    return S_OK;
}
