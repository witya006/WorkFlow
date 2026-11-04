#pragma once
#include <windows.h>
#include <d3d9.h>
#include <cstddef>
#include <cstdint>
#include <vector>
#include "client455_mesh_runtime.h"
#include "client455_character_rfs.h"

struct RF455CharacterDds {
    std::vector<unsigned char> bytes;
    std::uint32_t skipped,width,height;
    bool cube;
};
// Own checked input storage;valid header transformation is recovered from455.
// Invalid/truncated lengths return false rather than reproducing unchecked reads.
bool RF455_PrepareCharacterDds(const void* input,std::size_t length,std::uint32_t mipSkip,
    std::uint32_t maxWidth,std::uint32_t maxHeight,RF455CharacterDds* output);
struct RF455CharacterTextureApi {
    HRESULT (WINAPI* memory2D)(IDirect3DDevice9*,LPCVOID,UINT,UINT,UINT,UINT,DWORD,D3DFORMAT,D3DPOOL,DWORD,DWORD,D3DCOLOR,void*,PALETTEENTRY*,IDirect3DTexture9**);
    HRESULT (WINAPI* memoryCube)(IDirect3DDevice9*,LPCVOID,UINT,UINT,UINT,DWORD,D3DFORMAT,D3DPOOL,DWORD,DWORD,D3DCOLOR,void*,PALETTEENTRY*,IDirect3DCubeTexture9**);
    HRESULT (WINAPI* file2D)(IDirect3DDevice9*,LPCSTR,IDirect3DTexture9**);
};
// The renderer owner must install the actual pinned D3DX9exports. No default
// successful provider exists. Tests may wrap exports to observe their outputs.
const RF455CharacterTextureApi* RF455_SetCharacterTextureApi(const RF455CharacterTextureApi* api);
IDirect3DTexture9* RF455_LoadCharacterTextureFile(IDirect3DDevice9* device,const char* file,
    std::uint32_t mipSkip,bool oneMip,std::uint32_t maxWidth,std::uint32_t maxHeight,std::uint32_t* cubeFlag);

#pragma pack(push,4)
struct RF455TextureEntry {
    char name[256];std::uint32_t id;
    IDirect3DTexture9* texture;
    std::uint32_t estimatedBytes,flags;
};
struct RF455TextureManager {
    IDirect3DDevice9* device;
    std::uint32_t opaque4;
    RF455TextureEntry** begin;RF455TextureEntry** end;RF455TextureEntry** capacity;
    std::uint32_t estimatedBytes,nextId;
    char directory[256];std::uint32_t mipSkip;
};
#pragma pack(pop)
static_assert(sizeof(RF455TextureEntry)==272,"455 texture entry prefix");
static_assert(sizeof(RF455TextureManager)==288,"455 texture manager fields");
static_assert(offsetof(RF455TextureManager,begin)==8 && offsetof(RF455TextureManager,mipSkip)==284,"455manager offsets");
struct RF455TextureAccounting {std::uint32_t estimatedBytes,created;};
extern "C" {
void RF455_ConstructTextureManager(RF455TextureManager* manager);
void RF455_InitTextureManager(RF455TextureManager* manager);
void RF455_ClearTextureManager(RF455TextureManager* manager);
void RF455_DestroyTextureManager(RF455TextureManager* manager);
RF455TextureManager* RF455_LastTextureManager();
std::uint32_t RF455_GetTextureId(RF455TextureManager* manager,const char* name);
IDirect3DTexture9* RF455_GetTextureByName(RF455TextureManager* manager,const char* name);
IDirect3DTexture9* RF455_GetTextureById(RF455TextureManager* manager,std::uint32_t id);
bool RF455_AddTexture(RF455TextureManager* manager,const char* directory,const char* name);
void RF455_DeleteTextureByName(RF455TextureManager* manager,const char* name);
void RF455_DeleteTextureById(RF455TextureManager* manager,std::uint32_t id);
RF455TextureAccounting RF455_GetTextureAccounting();
}
RF455MeshMaterialOps RF455_TextureMaterialOps(RF455TextureManager* manager);
