#include "client455_texture.h"
#include "client455_character_dds_key.h"
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <utility>

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
struct ReleaseTexture {
    void operator()(IDirect3DTexture9* texture) const noexcept { texture->Release(); }
};
using TextureOwner = std::unique_ptr<IDirect3DTexture9, ReleaseTexture>;

enum class TextureLoadRoute { Custom, CustomOneMip, Plain };

// Manager entries are owned here. The public packed base remains unchanged.
struct OwnedTextureEntry : RF455TextureEntry {
    std::string path;
    TextureLoadRoute route = TextureLoadRoute::Custom;
    std::uint32_t mipSkip = 0;

    ~OwnedTextureEntry() { if (texture) texture->Release(); }
};

IDirect3DTexture9* takeDecodedTexture(HRESULT result, IDirect3DTexture9* texture)
{
    if (SUCCEEDED(result)) return texture;
    if (texture) texture->Release();
    return nullptr;
}

IDirect3DTexture9* loadPlainTexture(IDirect3DDevice9* device, const char* path)
{
    if (!textureApi || !textureApi->file2D) return nullptr;
    IDirect3DTexture9* texture = nullptr;
    if (textureApi->memory2D) {
        constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
        const auto source = RF455_GetCharacterRfsCache()->ReadLooseBytes(path, maxBytes);
        if (source.status == RF455ResourceReadStatus::Ready && source.bytes && !source.bytes->empty()) {
            // These are the D3DXCreateTextureFromFileA defaults.
            constexpr UINT d3dxDefault = 0xffffffffu;
            const HRESULT result = textureApi->memory2D(device, source.bytes->data(),
                static_cast<UINT>(source.bytes->size()), d3dxDefault, d3dxDefault, d3dxDefault,
                0, D3DFMT_UNKNOWN, D3DPOOL_MANAGED, d3dxDefault, d3dxDefault, 0, nullptr, nullptr, &texture);
            return takeDecodedTexture(result, texture);
        }
    }
    const HRESULT result = textureApi->file2D(device, path, &texture);
    return takeDecodedTexture(result, texture);
}

IDirect3DTexture9* loadCandidate(IDirect3DDevice9* device, const char* path,
    TextureLoadRoute route, std::uint32_t mipSkip, std::uint32_t& cube)
{
    if (route == TextureLoadRoute::Plain) return loadPlainTexture(device, path);
    return RF455_LoadCharacterTextureFile(device, path, mipSkip,
        route == TextureLoadRoute::CustomOneMip, 2048, 2048, &cube);
}

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
void erase(RF455TextureManager* manager,RF455TextureEntry** at){delete static_cast<OwnedTextureEntry*>(*at);const auto tail=manager->end-at-1;if(tail>0)std::memmove(at,at+1,4*tail);--manager->end;}
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
    auto* cache=RF455_GetCharacterRfsCache();auto input=cache->ReadArchiveBytes(file);
    if(input.status==RF455ResourceReadStatus::Unavailable)input=cache->ReadLooseBytes(file);
    if(input.status==RF455ResourceReadStatus::Unavailable || !input.declaredSize)return nullptr;
    std::uint32_t cube=0;IDirect3DTexture9* texture=nullptr;RF455CharacterDds prepared;
    if(input.status==RF455ResourceReadStatus::Ready && input.bytes && RF455_PrepareCharacterDds(input.bytes->data(),input.bytes->size(),mipSkip,maxWidth,maxHeight,&prepared)){
        cube=prepared.cube?1u:0u;
        if(prepared.cube){
            IDirect3DCubeTexture9* cubeTexture=nullptr;
            textureApi->memoryCube(device,prepared.bytes.data(),static_cast<UINT>(prepared.bytes.size()),prepared.width,0xffffffffu,0,D3DFMT_UNKNOWN,D3DPOOL_MANAGED,0xffffffffu,0xffffffffu,0,nullptr,nullptr,&cubeTexture);
            // RVA 0x533800 returns its separate, empty 2D output for cubes.
            if (cubeTexture) cubeTexture->Release();
        } else {
            const HRESULT result = textureApi->memory2D(device,prepared.bytes.data(),static_cast<UINT>(prepared.bytes.size()),prepared.width,prepared.height,oneMip?1u:0u,0,D3DFMT_UNKNOWN,D3DPOOL_MANAGED,0xffffffffu,0xffffffffu,oneMip?0xffffffffu:0u,nullptr,nullptr,&texture);
            texture = takeDecodedTexture(result, texture);
        }
    }
    *cubeFlag=cube;return texture;
}
extern "C" void RF455_InitTextureManager(RF455TextureManager* manager){manager->estimatedBytes=0;manager->nextId=1;manager->device=nullptr;manager->directory[0]=0;manager->mipSkip=0;}
extern "C" void RF455_ConstructTextureManager(RF455TextureManager* manager){manager->begin=manager->end=manager->capacity=nullptr;lastManager=manager;RF455_InitTextureManager(manager);}
extern "C" RF455TextureManager* RF455_LastTextureManager(){return lastManager;}
extern "C" void RF455_ClearTextureManager(RF455TextureManager* manager){for(auto** i=manager->begin;i!=manager->end;++i)delete static_cast<OwnedTextureEntry*>(*i);manager->end=manager->begin;}
extern "C" void RF455_DestroyTextureManager(RF455TextureManager* manager){RF455_ClearTextureManager(manager);std::free(manager->begin);manager->begin=manager->end=manager->capacity=nullptr;}
extern "C" std::uint32_t RF455_GetTextureId(RF455TextureManager* manager,const char* name){if(!name || !*name)return 0;auto* entry=lookup(manager,name);return entry?entry->id:0;}
extern "C" IDirect3DTexture9* RF455_GetTextureByName(RF455TextureManager* manager,const char* name){auto* entry=lookup(manager,name);return entry?entry->texture:nullptr;}
extern "C" IDirect3DTexture9* RF455_GetTextureById(RF455TextureManager* manager,std::uint32_t id){for(auto** i=manager->begin;i!=manager->end;++i)if((*i)->id==id)return (*i)->texture;return nullptr;}
extern "C" bool RF455_AddTexture(RF455TextureManager* manager,const char* directory,const char* name){
    if(!manager || !manager->device || !textureApi || !textureApi->file2D || !directory || !name || std::strlen(directory)>100 || std::strlen(name)>100 || std::strchr(directory,'%') || std::strchr(name,'%'))return false;
    try {
        std::string input(name);
        if (!input.empty()) _strupr(&input[0]);
        if (RF455_GetTextureByName(manager, input.c_str())) return false;
        const auto slash = input.rfind('\\');
        const auto leaf = slash == std::string::npos ? input : input.substr(slash + 1);
        const auto path = std::string(directory) + "\\" + leaf;
        const auto dot = path.rfind('.');
        if (dot == std::string::npos) return false;
        const auto rfc = path.substr(0, dot) + ".RFC";
        const auto rft = path.substr(0, dot) + ".RFT";
        const struct Candidate {
            const std::string& path;
            TextureLoadRoute route;
        } candidates[] = {
            {path, TextureLoadRoute::Custom}, {rfc, TextureLoadRoute::CustomOneMip},
            {rft, TextureLoadRoute::Custom}, {path, TextureLoadRoute::Plain},
            {rft, TextureLoadRoute::Custom}, {rfc, TextureLoadRoute::Plain}, {rft, TextureLoadRoute::Plain},
        };
        auto entry = std::make_unique<OwnedTextureEntry>();
        std::strncpy(entry->name, leaf.c_str(), 255);
        entry->id = manager->nextId;
        entry->mipSkip = manager->mipSkip;
        std::uint32_t cube = 0;
        for (const auto& candidate : candidates) {
            entry->texture = loadCandidate(manager->device, candidate.path.c_str(), candidate.route,
                entry->mipSkip, cube);
            if (&candidate == &candidates[0] && cube) entry->flags = 8;
            if (entry->texture) {
                entry->path = candidate.path;
                entry->route = candidate.route;
                break;
            }
        }
        if (!entry->texture) return false;
        D3DSURFACE_DESC desc{};
        if (FAILED(entry->texture->GetLevelDesc(0, &desc))) return false;
        const std::uint32_t bytes = 4u * desc.Width * desc.Height;
        entry->estimatedBytes = bytes;
        if (!append(manager, entry.get())) return false;
        entry.release();
        manager->estimatedBytes += bytes;
        ++manager->nextId;
        ++accounting.created;
        accounting.estimatedBytes += bytes;
        return true;
    } catch (const std::bad_alloc&) {
        return false;
    } catch (const std::length_error&) {
        return false;
    }
}
extern "C" void RF455_DeleteTextureByName(RF455TextureManager* manager,const char* name){
    if(!name || std::strlen(name)>=256)return;std::string exact(name);if(!exact.empty())_strupr(&exact[0]);
    for(auto** i=manager->begin;i!=manager->end;)if(!std::strcmp((*i)->name,exact.c_str()))erase(manager,i);else ++i;
}
extern "C" void RF455_DeleteTextureById(RF455TextureManager* manager,std::uint32_t id){for(auto** i=manager->begin;i!=manager->end;)if((*i)->id==id)erase(manager,i);else ++i;}
extern "C" RF455TextureAccounting RF455_GetTextureAccounting(){return accounting;}
RF455MeshMaterialOps RF455_TextureMaterialOps(RF455TextureManager* manager){return {manager,materialLookup,materialLoad};}

void RF455_DetachCharacterTextures(RF455TextureManager& manager) noexcept
{
    manager.device = nullptr;
    for (auto** at = manager.begin; at != manager.end; ++at) {
        TextureOwner old((*at)->texture);
        (*at)->texture = nullptr;
    }
}

HRESULT RF455_RecreateCharacterTextures(RF455TextureManager& manager, IDirect3DDevice9* device)
{
    if (!device || manager.device) return E_INVALIDARG;
    for (auto** at = manager.begin; at != manager.end; ++at)
        if (!*at || (*at)->texture) return E_INVALIDARG;

    try {
        std::vector<TextureOwner> staged;
        if (manager.begin) staged.reserve(static_cast<std::size_t>(manager.end - manager.begin));
        for (auto** at = manager.begin; at != manager.end; ++at) {
            const auto& entry = *static_cast<const OwnedTextureEntry*>(*at);
            std::uint32_t cube = 0;
            TextureOwner texture(loadCandidate(device, entry.path.c_str(), entry.route, entry.mipSkip, cube));
            if (!texture) return E_FAIL;
            staged.push_back(std::move(texture));
        }
        for (std::size_t i = 0; i < staged.size(); ++i)
            manager.begin[i]->texture = staged[i].release();
        manager.device = device;
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (const std::length_error&) {
        return E_OUTOFMEMORY;
    }
}
