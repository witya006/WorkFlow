#include "client455_animation_manager.h"
#include <cstring>

namespace {
template<class T>T read(const void* bytes,unsigned at){
    T value;std::memcpy(&value,static_cast<const unsigned char*>(bytes)+at,sizeof(value));return value;
}
template<class T>void write(void* bytes,unsigned at,T value){
    std::memcpy(static_cast<unsigned char*>(bytes)+at,&value,sizeof(value));
}
bool normalize(const char* input,char (&name)[256]){
    // Explicit owned policy outside the reference's defined short-name domain.
    if(!input || std::strlen(input)>=255 || std::strchr(input,'%'))return false;
    std::strcpy(name,input);_strlwr(name);return true;
}
unsigned cacheSlot(std::uint32_t id,unsigned probe){
    const unsigned sum=(id&255)+((id>>8)&255)+((id>>16)&255)+(id>>24);
    const unsigned row=(sum%113)^2,column=((7*sum)%113)^2;
    return 20*((row+probe)%50)+(column+probe)%20;
}
void remember(RF455AnimationManager* manager,std::uint32_t id,RF455AnimationStorage* record){
    for(unsigned i=0;i<3;++i){
        auto*& value=manager->cache[cacheSlot(id,i)];
        if(!value){value=record;return;}
        if(value==record)return;
    }
    manager->cache[cacheSlot(id,0)]=record;
}
bool append(RF455AnimationManager* manager,RF455AnimationStorage* record,const RF455MeshMemoryOps* memory){
    const std::size_t size=manager->begin?manager->end-manager->begin:0;
    const std::size_t capacity=manager->begin?manager->capacity-manager->begin:0;
    if(size==capacity){
        if(size==0x3fffffff)return false;
        std::size_t next=capacity+capacity/2;
        if(next>0x3fffffff)next=0;
        if(next<size+1)next=size+1;
        auto** values=static_cast<RF455AnimationStorage**>(memory->allocate(memory->context,4*next));
        if(!values)return false;
        if(size)std::memcpy(values,manager->begin,4*size);
        if(manager->begin)memory->release(memory->context,manager->begin);
        manager->begin=values;manager->end=values+size;manager->capacity=values+next;
    }
    *manager->end++=record;return true;
}
void erase(RF455AnimationManager* manager,RF455AnimationStorage** at,const RF455MeshMemoryOps* memory){
    RF455_DestroyAnimation(*at,memory);memory->release(memory->context,*at);
    const auto tail=manager->end-at-1;
    if(tail>0)std::memmove(at,at+1,4*tail);
    --manager->end;
    // Both reference deletion routes deliberately leave the cache unchanged.
}
}

extern "C" void RF455_ResetAnimationCounters(RF455AnimationManager* manager){manager->counter=0;manager->nextId=1;}
extern "C" void RF455_ConstructAnimationManager(RF455AnimationManager* manager){
    manager->self=manager;manager->begin=manager->end=manager->capacity=nullptr;
    RF455_ResetAnimationCounters(manager);std::memset(manager->cache,0,sizeof(manager->cache));
}
extern "C" RF455AnimationStorage* RF455_FindAnimationName(RF455AnimationManager* manager,const char* input){
    char name[256];if(!normalize(input,name))return nullptr;
    for(auto** at=manager->begin;at!=manager->end;++at){
        if(!std::strcmp(reinterpret_cast<const char*>((*at)->bytes+5),name))return *at;
    }
    return nullptr;
}
extern "C" std::uint32_t RF455_FindAnimationIdByName(RF455AnimationManager* manager,const char* name){
    const auto* record=RF455_FindAnimationName(manager,name);return record?read<std::uint32_t>(record->bytes,264):0;
}
extern "C" RF455AnimationStorage* RF455_FindAnimationSuffix(RF455AnimationManager* manager,const char* input){
    char name[256];if(!normalize(input,name))return nullptr;
    for(auto** at=manager->begin;at!=manager->end;++at){
        const auto* last=std::strrchr(reinterpret_cast<const char*>((*at)->bytes+5),'\\');
        if(last && !std::strcmp(last,name))return *at;
    }
    return nullptr;
}
extern "C" RF455AnimationStorage* RF455_FindAnimationId(RF455AnimationManager* manager,std::uint32_t id){
    for(unsigned i=0;i<3;++i){
        auto* value=manager->cache[cacheSlot(id,i)];
        if(value && read<std::uint32_t>(value->bytes,264)==id)return value;
    }
    for(auto** at=manager->begin;at!=manager->end;++at){
        if(read<std::uint32_t>((*at)->bytes,264)==id){remember(manager,id,*at);return *at;}
    }
    return nullptr;
}
extern "C" int RF455_RegisterAnimation(RF455AnimationManager* manager,const char* input,const RF455MeshMemoryOps* memory){
    char name[256];if(!normalize(input,name) || RF455_FindAnimationName(manager,name))return 0;
    auto* record=static_cast<RF455AnimationStorage*>(memory->allocate(memory->context,284));
    if(!record)return 0;
    RF455_ConstructAnimation(record);write(record->bytes,264,manager->nextId);
    std::strcpy(reinterpret_cast<char*>(record->bytes+5),name);
    if(!append(manager,record,memory)){memory->release(memory->context,record);return 0;}
    ++manager->nextId;return 1;
}
extern "C" RF455AnimationStorage* RF455_GetOrRegisterAnimation(RF455AnimationManager* manager,const char* name,const RF455MeshMemoryOps* memory){
    auto* record=RF455_FindAnimationName(manager,name);
    if(!record && RF455_RegisterAnimation(manager,name,memory))record=RF455_FindAnimationName(manager,name);
    return record;
}
extern "C" void RF455_DeleteAnimationName(RF455AnimationManager* manager,const char* input,const RF455MeshMemoryOps* memory){
    char name[256];if(!normalize(input,name))return;
    for(auto** at=manager->begin;at!=manager->end;){
        if(!std::strcmp(reinterpret_cast<const char*>((*at)->bytes+5),name))erase(manager,at,memory);else ++at;
    }
}
extern "C" void RF455_DeleteAnimationId(RF455AnimationManager* manager,std::uint32_t id,const RF455MeshMemoryOps* memory){
    for(auto** at=manager->begin;at!=manager->end;){
        if(read<std::uint32_t>((*at)->bytes,264)==id)erase(manager,at,memory);else ++at;
    }
}
extern "C" void RF455_ReleaseAnimationManager(RF455AnimationManager* manager,const RF455MeshMemoryOps* memory){
    for(auto** at=manager->begin;at!=manager->end;++at){
        if(*at){RF455_DestroyAnimation(*at,memory);memory->release(memory->context,*at);}
    }
    if(manager->begin)memory->release(memory->context,manager->begin);
    manager->begin=manager->end=manager->capacity=nullptr;
}
