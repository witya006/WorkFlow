#pragma once

#include "client455_character_rfs.h"
#include <d3dx9.h>

// The scene owns the D3D texture; the cache retains only the authored PNG bytes.
inline HRESULT RF455_LoadLobbyTexture(IDirect3DDevice9* device, const char* path, IDirect3DTexture9** output)
{
    if (!output) return E_INVALIDARG;
    *output = nullptr;
    if (!device || !path || !*path) return E_INVALIDARG;

    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    auto* cache = RF455_GetCharacterRfsCache();
    const auto source = cache->ReadLooseBytes(path, maxBytes);
    const bool inMemory = source.status == RF455ResourceReadStatus::Ready && source.bytes;

    IDirect3DTexture9* texture = nullptr;
    HRESULT result;
    if (inMemory) {
        if (source.bytes->empty()) return D3DXERR_INVALIDDATA;
        result = D3DXCreateTextureFromFileInMemoryEx(device, source.bytes->data(),
            static_cast<UINT>(source.bytes->size()), D3DX_DEFAULT_NONPOW2, D3DX_DEFAULT_NONPOW2,
            D3DX_DEFAULT, 0, D3DFMT_A8R8G8B8, D3DPOOL_MANAGED, D3DX_FILTER_LINEAR, D3DX_FILTER_BOX,
            0, nullptr, nullptr, &texture);
        if (result == D3DXERR_INVALIDDATA) cache->RemoveLooseBytes(path);
    } else if (source.status == RF455ResourceReadStatus::ReadError && source.declaredSize > maxBytes) {
        result = D3DXCreateTextureFromFileExA(device, path, D3DX_DEFAULT_NONPOW2, D3DX_DEFAULT_NONPOW2,
            D3DX_DEFAULT, 0, D3DFMT_A8R8G8B8, D3DPOOL_MANAGED, D3DX_FILTER_LINEAR, D3DX_FILTER_BOX,
            0, nullptr, nullptr, &texture);
    } else {
        return source.status == RF455ResourceReadStatus::MemoryError ? E_OUTOFMEMORY : E_FAIL;
    }

    if (FAILED(result)) {
        if (texture) texture->Release();
        return result;
    }
    if (!texture) return E_FAIL;
    *output = texture;
    return result;
}
