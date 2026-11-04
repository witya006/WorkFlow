#include "client455_texture.h"
#include "client455_character_dds_key.h"
#include <cstdlib>
#include <cstring>
#include <limits>
#include <string>

namespace {
const RF455CharacterTextureApi* textureApi=nullptr;
RF455TextureManager* lastManager=nullptr;
RF455TextureAccounting accounting={};
std::uint32_t get(const unsigned char* bytes,unsigned at){std::uint32_t value;std::memcpy(&value,bytes+at,4);return value;}
void put(unsigned char* bytes,unsigned at,std::uint32_t value){std::memcpy(bytes+at,&value,4);}
std::uint32_t skipMips(unsigned char* h,std::uint32_t requested,std::uint32_t maxWidth,std::uint32_t maxHeight){
    std::uint32_t bytes=0,i=0;if(maxWidth<256 || maxHeight<256)return 0;
    for(;i<requested || get(h,16)>maxWidth || get(h,12)>maxHeight;++i){
        if(i>=get(h,28))break;
        const auto size=get(h,20);bytes+=size;
        const auto height=get(h,12);if(height<=4)break;put(h,12,height>>1);
        const auto width=get(h,16);if(width<=4)break;put(h,16,width>>1);put(h,20,size/4);
    }
    put(h,28,get(h,28)-i);return bytes;
}
void repair(unsigned char* h){
    const auto flags=get(h,80);
    if(flags==5)put(h,80,4);
    else if(flags==65){const auto bits=get(h,88);
        if(bits==16){if(get(h,104)!=0x8000)put(h,92,3840);}
        else if(bits==32){put(h,92,0xff0000);put(h,96,65280);put(h,100,255);put(h,104,0xff000000);}
    }
    if(!get(h,76)){put(h,76,32);put(h,80,4);}
}
bool keys(const char* name,std::string& exact,std::string& alternate){
    if(!name || std::strlen(name)>=256 || std::strchr(name,'%'))return false;
    exact=name;if(!exact.empty())_strupr(&exact[0]);const auto dot=exact.rfind('.');if(dot==std::string::npos)return false;
    alternate=exact.substr(0,dot)+".RFT";return true;
}
RF455TextureEntry* lookup(RF455TextureManager* manager,const char* name){
    std::string exact,alternate;if(!keys(name,exact,alternate))return nullptr;
    for(auto** i=manager->begin;i!=manager->end;++i)if(!std::strcmp((*i)->name,exact.c_str()) || !std::strcmp((*i)->name,alternate.c_str()))return *i;
    return nullptr;
}
void release(RF455TextureEntry* entry){if(entry){if(entry->texture)entry->texture->Release();std::free(entry);}}
bool append(RF455TextureManager* manager,RF455TextureEntry* entry){
    const std::size_t size=manager->begin?static_cast<std::size_t>(manager->end-manager->begin):0;
    const std::size_t capacity=manager->begin?static_cast<std::size_t>(manager->capacity-manager->begin):0;
    if(size==capacity){
        if(size>=0x3fffffffu)return false;std::size_t next=capacity+capacity/2;
        if(next<capacity || next>0x3fffffffu)next=0;if(next<size+1)next=size+1;
        auto** array=static_cast<RF455TextureEntry**>(std::malloc(4*next));if(!array)return false;
        if(size)std::memcpy(array,manager->begin,4*size);std::free(manager->begin);
        manager->begin=array;manager->end=array+size;manager->capacity=array+next;
    }
    *manager->end++=entry;return true;
}
void erase(RF455TextureManager* manager,RF455TextureEntry** at){release(*at);const auto tail=manager->end-at-1;if(tail>0)std::memmove(at,at+1,4*tail);--manager->end;}
std::int32_t __cdecl materialLookup(void* manager,const char* name){return static_cast<std::int32_t>(RF455_GetTextureId(static_cast<RF455TextureManager*>(manager),name));}
int __cdecl materialLoad(void* manager,const char* directory,const char* name){return RF455_AddTexture(static_cast<RF455TextureManager*>(manager),directory,name)?1:0;}
}
bool RF455_PrepareCharacterDds(const void* input,std::size_t length,std::uint32_t mipSkip,std::uint32_t maxWidth,std::uint32_t maxHeight,RF455CharacterDds* output){
    if(!input || !output || length<128 || length>0xffffffffu)return false;
    auto* raw=static_cast<const unsigned char*>(input);unsigned char head[128];std::memcpy(head,raw,128);
    if(get(head,0)!=0x20534444u)for(unsigned n=0;n<128;++n)head[n]^=characterDdsKey[n];
    if(get(head,0)!=0x20534444u)return false;
    const bool cube=(get(head,112)&0x200)!=0;
    const auto skipped=get(head,28)?skipMips(head,mipSkip,maxWidth,maxHeight):0;
    if(skipped>length-128)return false;repair(head);
    RF455CharacterDds value;value.cube=cube;value.skipped=skipped;value.width=get(head,16);value.height=get(head,12);
    value.bytes.resize(length-skipped);std::memcpy(value.bytes.data(),head,128);
    if(length-skipped>128)std::memcpy(value.bytes.data()+128,raw+128+skipped,length-128-skipped);
    *output=std::move(value);return true;
}
const RF455CharacterTextureApi* RF455_SetCharacterTextureApi(const RF455CharacterTextureApi* api){const auto* previous=textureApi;textureApi=api;return previous;}
IDirect3DTexture9* RF455_LoadCharacterTextureFile(IDirect3DDevice9* device,const char* file,std::uint32_t mipSkip,bool oneMip,std::uint32_t maxWidth,std::uint32_t maxHeight,std::uint32_t* cubeFlag){
    if(!textureApi || !textureApi->memory2D || !textureApi->memoryCube || !cubeFlag || !file)return nullptr;
    std::uint32_t size=0;FILE* stream=RF455_GetCharacterRfsCache()->Open(file,&size);
    if(!stream){
        stream=std::fopen(file,"rb");FILE* measure=std::fopen(file,"rb");
        if(measure){const long begin=std::ftell(measure);std::fseek(measure,0,SEEK_END);size=static_cast<std::uint32_t>(std::ftell(measure)-begin);std::fclose(measure);}
        if(!stream)return nullptr;
    }
    if(!size){std::fclose(stream);return nullptr;}
    std::vector<unsigned char> raw(size);const auto read=std::fread(raw.data(),1,size,stream);
    std::uint32_t cube=0;IDirect3DTexture9* texture=nullptr;RF455CharacterDds prepared;
    if(read==size && RF455_PrepareCharacterDds(raw.data(),raw.size(),mipSkip,maxWidth,maxHeight,&prepared)){
        cube=prepared.cube?1u:0u;HRESULT hr;
        if(prepared.cube){
            IDirect3DCubeTexture9* abandoned=nullptr;
            hr=textureApi->memoryCube(device,prepared.bytes.data(),static_cast<UINT>(prepared.bytes.size()),prepared.width,0xffffffffu,0,D3DFMT_UNKNOWN,D3DPOOL_MANAGED,0xffffffffu,0xffffffffu,0,nullptr,nullptr,&abandoned);
            //933800 writes cube output into a separate local,then returns its
            // still-zero2D local. Preserve its null result andorphan ownership.
            // Test wrappers capture/release real orphan objects after checking.
        }else hr=textureApi->memory2D(device,prepared.bytes.data(),static_cast<UINT>(prepared.bytes.size()),prepared.width,prepared.height,oneMip?1u:0u,0,D3DFMT_UNKNOWN,D3DPOOL_MANAGED,0xffffffffu,0xffffffffu,oneMip?0xffffffffu:0u,nullptr,nullptr,&texture);
        if(FAILED(hr))texture=nullptr;
    }
    *cubeFlag=cube;std::fclose(stream);return texture;
}
extern "C" void RF455_InitTextureManager(RF455TextureManager* manager){manager->estimatedBytes=0;manager->nextId=1;manager->device=nullptr;manager->directory[0]=0;manager->mipSkip=0;}
extern "C" void RF455_ConstructTextureManager(RF455TextureManager* manager){manager->begin=manager->end=manager->capacity=nullptr;lastManager=manager;RF455_InitTextureManager(manager);}
extern "C" RF455TextureManager* RF455_LastTextureManager(){return lastManager;}
extern "C" void RF455_ClearTextureManager(RF455TextureManager* manager){for(auto** i=manager->begin;i!=manager->end;++i)release(*i);manager->end=manager->begin;}
extern "C" void RF455_DestroyTextureManager(RF455TextureManager* manager){RF455_ClearTextureManager(manager);std::free(manager->begin);manager->begin=manager->end=manager->capacity=nullptr;}
extern "C" std::uint32_t RF455_GetTextureId(RF455TextureManager* manager,const char* name){if(!name || !*name)return 0;auto* entry=lookup(manager,name);return entry?entry->id:0;}
extern "C" IDirect3DTexture9* RF455_GetTextureByName(RF455TextureManager* manager,const char* name){auto* entry=lookup(manager,name);return entry?entry->texture:nullptr;}
extern "C" IDirect3DTexture9* RF455_GetTextureById(RF455TextureManager* manager,std::uint32_t id){for(auto** i=manager->begin;i!=manager->end;++i)if((*i)->id==id)return (*i)->texture;return nullptr;}
extern "C" bool RF455_AddTexture(RF455TextureManager* manager,const char* directory,const char* name){
    if(!manager || !manager->device || !textureApi || !textureApi->file2D || !directory || !name || std::strlen(directory)>100 || std::strlen(name)>100 || std::strchr(directory,'%') || std::strchr(name,'%'))return false;
    std::string input(name);if(!input.empty())_strupr(&input[0]);if(RF455_GetTextureByName(manager,input.c_str()))return false;
    const auto slash=input.rfind('\\');const std::string leaf=slash==std::string::npos?input:input.substr(slash+1);
    const std::string path=std::string(directory)+"\\"+leaf;const auto dot=path.rfind('.');if(dot==std::string::npos)return false;
    const std::string rfc=path.substr(0,dot)+".RFC",rft=path.substr(0,dot)+".RFT";
    auto* entry=static_cast<RF455TextureEntry*>(std::malloc(sizeof(RF455TextureEntry)));if(!entry)return false;
    entry->name[0]=0;entry->id=entry->estimatedBytes=entry->flags=0;entry->texture=nullptr;
    std::strncpy(entry->name,leaf.c_str(),255);entry->id=manager->nextId;std::uint32_t cube=0;
    entry->texture=RF455_LoadCharacterTextureFile(manager->device,path.c_str(),manager->mipSkip,false,2048,2048,&cube);if(cube)entry->flags=8;
    if(!entry->texture)entry->texture=RF455_LoadCharacterTextureFile(manager->device,rfc.c_str(),manager->mipSkip,true,2048,2048,&cube);
    if(!entry->texture)entry->texture=RF455_LoadCharacterTextureFile(manager->device,rft.c_str(),manager->mipSkip,false,2048,2048,&cube);
    bool loaded=entry->texture!=nullptr;
    if(!loaded)loaded=SUCCEEDED(textureApi->file2D(manager->device,path.c_str(),&entry->texture));
    if(!loaded){entry->texture=RF455_LoadCharacterTextureFile(manager->device,rft.c_str(),manager->mipSkip,false,2048,2048,&cube);loaded=entry->texture!=nullptr;}
    if(!loaded)loaded=SUCCEEDED(textureApi->file2D(manager->device,rfc.c_str(),&entry->texture));
    if(!loaded)loaded=SUCCEEDED(textureApi->file2D(manager->device,rft.c_str(),&entry->texture));
    if(!loaded){release(entry);return false;}
    D3DSURFACE_DESC desc;entry->texture->GetLevelDesc(0,&desc);const std::uint32_t bytes=4u*desc.Width*desc.Height;
    manager->estimatedBytes+=bytes;entry->estimatedBytes=bytes;
    if(!append(manager,entry)){release(entry);return false;}
    ++manager->nextId;++accounting.created;accounting.estimatedBytes+=bytes;return true;
}
extern "C" void RF455_DeleteTextureByName(RF455TextureManager* manager,const char* name){
    if(!name || std::strlen(name)>=256)return;std::string exact(name);if(!exact.empty())_strupr(&exact[0]);
    for(auto** i=manager->begin;i!=manager->end;)if(!std::strcmp((*i)->name,exact.c_str()))erase(manager,i);else ++i;
}
extern "C" void RF455_DeleteTextureById(RF455TextureManager* manager,std::uint32_t id){for(auto** i=manager->begin;i!=manager->end;)if((*i)->id==id)erase(manager,i);else ++i;}
extern "C" RF455TextureAccounting RF455_GetTextureAccounting(){return accounting;}
RF455MeshMaterialOps RF455_TextureMaterialOps(RF455TextureManager* manager){return {manager,materialLookup,materialLoad};}
