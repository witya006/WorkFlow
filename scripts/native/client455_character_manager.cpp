#include "client455_character_manager.h"
#include <cstdio>
#include <cstring>
#include <limits>

namespace {
template<class T>T get(const unsigned char* bytes,unsigned at){T value;std::memcpy(&value,bytes+at,sizeof(value));return value;}
template<class T>void put(unsigned char* bytes,unsigned at,T value){std::memcpy(bytes+at,&value,sizeof(value));}
std::uint32_t key(std::uint32_t id,bool second){unsigned sum=0;for(unsigned i=0;i<4;++i)sum+=(id>>(8*i))&255;return ((second?7*sum:sum)%113)^2;}
unsigned slot(std::uint32_t id,unsigned probe){return 20*((key(id,false)+probe)%50)+(key(id,true)+probe)%20;}
void cache(RF455CharacterManager* manager,std::uint32_t id,RF455CharacterStorage* value){
    if(!value)return;for(unsigned i=0;i<3;++i){auto*& cell=manager->cache[slot(id,i)];if(!cell){cell=value;return;}if(cell==value)return;}
    manager->cache[slot(id,0)]=value;
}
void release(RF455CharacterStorage* character,const RF455MeshMemoryOps* memory){RF455_ReleaseModelMeshArray(&character->prefix,memory);memory->release(memory->context,character);}
void erase(RF455CharacterManager* manager,RF455CharacterStorage** at,const RF455MeshMemoryOps* memory){
    auto* character = *at;
    // A cached pointer may appear in several slots after the record ID changes.
    for (auto*& entry : manager->cache)
        if (entry == character) entry = nullptr;
    const auto tail = manager->end - at - 1;
    if (tail > 0) std::memmove(at, at + 1, sizeof(*at) * tail);
    --manager->end;
    release(character, memory);
}
bool copyResource(const RF455ResourceRead& input,const RF455MeshMemoryOps* memory,RF455RawModelBuffer* output){
    if(input.status!=RF455ResourceReadStatus::Ready)return false;
    const auto size=static_cast<std::uint32_t>(input.bytes->size());
    void* bytes=memory->allocate(memory->context,size);if(!bytes)return false;
    if(size)std::memcpy(bytes,input.bytes->data(),size);
    *output={bytes,size};return true;
}
}
extern "C" void RF455_ConstructCharacter(RF455CharacterStorage* character){
    auto* bytes=reinterpret_cast<unsigned char*>(character);std::memset(bytes,0,1188);
    put<std::uint32_t>(bytes,696,0xffffffff);put<std::uint32_t>(bytes,672,160);put<std::uint32_t>(bytes,684,160);
    for(unsigned at:{540u,604u})for(unsigned i=0;i<16;i+=5)put<std::uint32_t>(bytes,at+4*i,0x3f800000);
    //91C450 material RGBA=(1,0,0,1),then constructor's RGB overrides.
    for(unsigned at:{720u,736u,732u,748u})put<std::uint32_t>(bytes,at,0x3f800000);
    for(unsigned at:{720u,724u,728u})put<std::uint32_t>(bytes,at,0x3f19999a);
    for(unsigned at:{736u,740u,744u})put<std::uint32_t>(bytes,at,0x3e99999a);
    put<std::uint32_t>(bytes,792,0x3f800000);put<std::uint32_t>(bytes,716,3000);
}
extern "C" void RF455_ConstructCharacterManager(RF455CharacterManager* manager){manager->begin=manager->end=manager->capacity=nullptr;manager->nextId=0;std::memset(manager->cache,0,sizeof(manager->cache));}
extern "C" int RF455_AddCharacter(RF455CharacterManager* manager,RF455CharacterStorage* character,const RF455MeshMemoryOps* memory){
    put(character->prefix.bytes,0,manager->nextId++);
    const std::size_t size=manager->begin?manager->end-manager->begin:0,capacity=manager->begin?manager->capacity-manager->begin:0;
    if(size==capacity){if(size==0x3fffffff)return 0;std::size_t next=capacity+capacity/2;if(next>0x3fffffff)next=0;if(next<size+1)next=size+1;
        auto** array=static_cast<RF455CharacterStorage**>(memory->allocate(memory->context,4*next));if(!array)return 0;
        if(size)std::memcpy(array,manager->begin,4*size);if(manager->begin)memory->release(memory->context,manager->begin);manager->begin=array;manager->end=array+size;manager->capacity=array+next;
    }
    *manager->end++=character;return 1;
}
extern "C" RF455CharacterStorage* RF455_CreateCharacter(RF455CharacterManager* manager,const char* name,RF455CharacterStorage* parent,const RF455MeshMemoryOps* memory){
    if(!name || std::strlen(name)>=256 || std::strchr(name,'%'))return nullptr; // owned unsafe-name policy
    auto* record=static_cast<RF455CharacterStorage*>(memory->allocate(memory->context,1188));if(!record)return nullptr;RF455_ConstructCharacter(record);
    std::strcpy(reinterpret_cast<char*>(record->prefix.bytes+4),name);put(record->prefix.bytes,272,parent);
    if(!RF455_AddCharacter(manager,record,memory)){memory->release(memory->context,record);return nullptr;}return record;
}
extern "C" RF455CharacterStorage* RF455_FindCharacterName(RF455CharacterManager* manager,const char* name){for(auto** i=manager->begin;i!=manager->end;++i)if(!std::strcmp(reinterpret_cast<const char*>((*i)->prefix.bytes+4),name))return *i;return nullptr;}
extern "C" std::uint32_t RF455_CharacterId(RF455CharacterManager* manager,const char* name){auto* found=RF455_FindCharacterName(manager,name);return found?get<std::uint32_t>(found->prefix.bytes,0):0;}
extern "C" RF455CharacterStorage* RF455_FindCharacterId(RF455CharacterManager* manager,std::uint32_t id){
    for(unsigned i=0;i<3;++i){auto* value=manager->cache[slot(id,i)];if(value && get<std::uint32_t>(value->prefix.bytes,0)==id)return value;}
    for(auto** i=manager->begin;i!=manager->end;++i)if(get<std::uint32_t>((*i)->prefix.bytes,0)==id){cache(manager,id,*i);return *i;}return nullptr;
}
extern "C" void RF455_DeleteCharacterName(RF455CharacterManager* manager,const char* name,const RF455MeshMemoryOps* memory){for(auto** i=manager->begin;i!=manager->end;)if(!std::strcmp(reinterpret_cast<const char*>((*i)->prefix.bytes+4),name))erase(manager,i,memory);else ++i;}
extern "C" void RF455_DeleteCharacterId(RF455CharacterManager* manager,std::uint32_t id,const RF455MeshMemoryOps* memory){for(auto** i=manager->begin;i!=manager->end;)if(get<std::uint32_t>((*i)->prefix.bytes,0)==id)erase(manager,i,memory);else ++i;}
extern "C" void RF455_ClearCharacters(RF455CharacterManager* manager,const RF455MeshMemoryOps* memory){
    std::memset(manager->cache, 0, sizeof(manager->cache));
    for (auto** i = manager->begin; i != manager->end; ++i)
        if (*i) release(*i, memory);
    manager->end = manager->begin;
}
extern "C" void RF455_DestroyCharacterManager(RF455CharacterManager* manager,const RF455MeshMemoryOps* memory){RF455_ClearCharacters(manager,memory);if(manager->begin)memory->release(memory->context,manager->begin);manager->begin=manager->end=manager->capacity=nullptr;}
extern "C" void RF455_RefreshModelTextures(RF455KnownModelPrefix* model,RF455TextureManager* textures){
    auto* meshes=get<RF455MeshStorage*>(model->bytes,536);const auto count=get<std::uint32_t>(model->bytes,532);
    for(unsigned i=0;i<count;++i){auto* bytes=meshes[i].bytes;const unsigned ids[]={5111,5123,5127,5767,5771,5775},dest[]={5107,5115,5119,5791,5795,5799};
        for(unsigned n=0;n<6;++n)put(bytes,dest[n],RF455_GetTextureById(textures,get<std::uint32_t>(bytes,ids[n])));
        put(bytes,5283,get<void*>(bytes,5115));
    }
}
extern "C" int RF455_ReadMshFile(const char* name,const RF455MeshMemoryOps* memory,RF455RawModelBuffer* output){
    if(!name || !*name || !output || !memory || !memory->allocate || !memory->release)return 0;std::size_t i=std::strlen(name);while(i && name[i]!='.')--i;const char* extension=name+i+1;
    if(std::strlen(extension)>3 || _stricmp(extension,"MSH"))return 0;
    auto* resources=RF455_GetCharacterRfsCache();
    // Model parsers mutate their input: cached source bytes never become the
    // caller-owned buffer. Original 91F1B0 falls back after any failed RFS blob.
    if(copyResource(resources->ReadArchiveBytes(name),memory,output))return 1;
    return copyResource(resources->ReadLooseBytes(name),memory,output)?1:0;
}
