#include "client455_legacy_model.h"
#include <cstring>
#include <initializer_list>

namespace {
template<class T> T get(const unsigned char* p,unsigned at){T v;std::memcpy(&v,p+at,sizeof(v));return v;}
template<class T> void put(unsigned char* p,unsigned at,T v){std::memcpy(p+at,&v,sizeof(v));}

struct Cursor {
    const unsigned char* bytes;
    std::size_t length,at=0;

    const unsigned char* take(std::size_t count,std::size_t stride=1){
        if(count>(length-at)/stride)return nullptr;
        const auto* result=bytes+at;
        at+=count*stride;
        return result;
    }
};

bool copyAllocation(unsigned char* part,unsigned offset,const unsigned char* source,
                    std::size_t length,const RF455MeshMemoryOps* memory){
    void* block=memory->allocate(memory->context,length);
    if(!block)return false;
    put(part,offset,block);
    if(length)std::memcpy(block,source,length);
    return true;
}

void copyWeight(unsigned char* destination,const unsigned char* source){
    // Confirmed fld/fstp93C641/93C64E, including masked sNaN quieting.
    __asm {
        mov eax,source
        mov edx,destination
        fld dword ptr[eax]
        fstp dword ptr[edx]
    }
}

RF455LegacyStatus readPart(Cursor& cursor,RF455LegacyPart* part,
                          RF455LegacyModel* model,const RF455MeshMemoryOps* memory){
    const auto* header=cursor.take(693);
    if(!header)return RF_LEGACY_FORMAT;
    auto* bytes=part->bytes;
    std::memcpy(bytes,header,693);
    const auto vertices=get<std::uint16_t>(header,392);
    const auto faces=get<std::uint16_t>(header,394);
    const auto physiques=get<std::uint16_t>(header,396);
    const auto compact=get<std::uint32_t>(header,642);
    put(model->bytes,24,compact); // Last record wins, as93C3F3.

    const auto* data=cursor.take(vertices,28);
    if(!data)return RF_LEGACY_FORMAT;
    if(!copyAllocation(bytes,696,data,28u*vertices,memory))return RF_LEGACY_MEMORY;
    data=cursor.take(faces,88);
    if(!data)return RF_LEGACY_FORMAT;
    if(!copyAllocation(bytes,700,data,88u*faces,memory))return RF_LEGACY_MEMORY;

    if(!compact){
        if(!physiques)return RF_LEGACY_OK;
        data=cursor.take(physiques,424);
        if(!data)return RF_LEGACY_FORMAT;
        return copyAllocation(bytes,704,data,424u*physiques,memory)?RF_LEGACY_OK:RF_LEGACY_MEMORY;
    }

    data=cursor.take(4);
    if(!data)return RF_LEGACY_FORMAT;
    const auto names=get<std::uint32_t>(data,0);
    put(bytes,708,names);
    if(!names)return RF_LEGACY_OK; // No compact physique payload consumed either.
    data=cursor.take(names,100);
    if(!data)return RF_LEGACY_FORMAT;
    if(!copyAllocation(bytes,712,data,100u*names,memory))return RF_LEGACY_MEMORY;
    data=cursor.take(physiques,40);
    if(!data)return RF_LEGACY_FORMAT;
    if(!copyAllocation(bytes,716,data,40u*physiques,memory))return RF_LEGACY_MEMORY;
    auto* expanded=static_cast<unsigned char*>(memory->allocate(memory->context,424u*physiques));
    if(!expanded)return RF_LEGACY_MEMORY;
    put(bytes,704,expanded);
    const auto* dictionary=get<const char*>(bytes,712);
    for(unsigned i=0;i<physiques;++i){
        const auto* source=data+40*i;
        auto* destination=expanded+424*i;
        std::memcpy(destination,source,8);
        const auto influences=get<std::int32_t>(source,4);
        if(influences>4)return RF_LEGACY_INFLUENCES; // Owned bounded domain.
        for(std::int32_t n=0;n<influences;++n){
            const auto index=get<std::uint32_t>(source,8+4*n);
            if(index>=names)return RF_LEGACY_NAME_INDEX;
            std::strncpy(reinterpret_cast<char*>(destination+8+100*n),dictionary+100*index,99);
            destination[107+100*n]=0;
            copyWeight(destination+408+4*n,source+24+4*n);
        }
    }
    return RF_LEGACY_OK;
}
}

extern "C" void RF455_ConstructLegacyPart(RF455LegacyPart* part){
    for(unsigned at:{696u,700u,704u,716u,712u})put<void*>(part->bytes,at,nullptr);
}

extern "C" void RF455_DestroyLegacyPart(RF455LegacyPart* part,const RF455MeshMemoryOps* memory){
    for(unsigned at:{696u,700u,704u,716u,712u}){
        void* block=get<void*>(part->bytes,at);
        if(block){memory->release(memory->context,block);put<void*>(part->bytes,at,nullptr);}
    }
}

extern "C" void RF455_ReleaseLegacyModel(RF455LegacyModel* model,const RF455MeshMemoryOps* memory){
    auto* parts=get<RF455LegacyPart*>(model->bytes,4);
    if(parts){
        auto* cookie=reinterpret_cast<unsigned char*>(parts)-4;
        const auto count=get<std::uint32_t>(cookie,0);
        for(std::uint32_t i=count;i;--i)RF455_DestroyLegacyPart(parts+i-1,memory);
        memory->release(memory->context,cookie);
        put<void*>(model->bytes,4,nullptr);
    }
    for(unsigned at:{12u,20u}){
        void* block=get<void*>(model->bytes,at);
        if(block){memory->release(memory->context,block);put<void*>(model->bytes,at,nullptr);}
    }
}

extern "C" void RF455_DeleteLegacyModel(RF455LegacyModel* model,const RF455MeshMemoryOps* memory){
    if(model){RF455_ReleaseLegacyModel(model,memory);memory->release(memory->context,model);}
}

extern "C" RF455LegacyStatus RF455_ReadLegacyModel(const void* input,std::size_t length,
    const RF455MeshMemoryOps* memory,RF455LegacyModel** output,std::size_t* consumed){
    if(!input || !memory || !memory->allocate || !memory->release || !output || !consumed)return RF_LEGACY_ARGUMENT;
    if(length<2)return RF_LEGACY_FORMAT;
    Cursor cursor={static_cast<const unsigned char*>(input),length};
    const auto count=get<std::uint16_t>(cursor.take(2),0);
    if(count>(length-2)/693)return RF_LEGACY_FORMAT;
    auto* model=static_cast<RF455LegacyModel*>(memory->allocate(memory->context,28));
    if(!model)return RF_LEGACY_MEMORY;
    for(unsigned at:{4u,12u,20u})put<void*>(model->bytes,at,nullptr);
    put(model->bytes,2,count);
    auto* cookie=static_cast<unsigned char*>(memory->allocate(memory->context,4+720u*count));
    if(!cookie){RF455_DeleteLegacyModel(model,memory);return RF_LEGACY_MEMORY;}
    put<std::uint32_t>(cookie,0,count);
    auto* parts=reinterpret_cast<RF455LegacyPart*>(cookie+4);
    put(model->bytes,4,parts);
    for(unsigned i=0;i<count;++i)RF455_ConstructLegacyPart(parts+i);
    for(unsigned i=0;i<count;++i){
        const auto status=readPart(cursor,parts+i,model,memory);
        if(status!=RF_LEGACY_OK){RF455_DeleteLegacyModel(model,memory);return status;}
    }
    *output=model;
    *consumed=cursor.at;
    return RF_LEGACY_OK;
}
