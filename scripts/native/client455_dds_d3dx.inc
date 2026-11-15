#include "client455_character_rfs.h"

// Client 455 x86 RVA 0x4F1990. Use the same D3DX decode with loose-file bytes.
static LPDIRECT3DTEXTURE9 RF455_LoadLooseDdsD3dx455(const char* name, const RF455ResourceBytes& bytes)
{
    if (!bytes || bytes->empty()) return nullptr;
    auto* device = GetD3dDevice();
    if (!device) return nullptr;
    const auto preferred = GetR3State()->mBestTextureFormat;
    const bool automaticFormat = preferred == D3DFMT_DXT1;
    D3DXIMAGE_INFO info{};
    LPDIRECT3DTEXTURE9 texture = nullptr;
    const auto filter = D3DX_FILTER_TRIANGLE | D3DX_FILTER_MIRROR;
    const HRESULT result = D3DXCreateTextureFromFileInMemoryEx(device, bytes->data(),
        static_cast<UINT>(bytes->size()), D3DX_DEFAULT, D3DX_DEFAULT, D3DX_DEFAULT, 0,
        automaticFormat ? D3DFMT_UNKNOWN : preferred, D3DPOOL_MANAGED, filter, filter, 0,
        automaticFormat ? &info : nullptr, nullptr, &texture);
    if (FAILED(result)) {
        if (texture) texture->Release();
        if (result == D3DXERR_INVALIDDATA) RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
        return nullptr;
    }
    return texture;
}

LPDIRECT3DTEXTURE9 R3LoadDDSAndTextureMem(char* name)
{
    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    const auto source = RF455_GetCharacterRfsCache()->ReadLooseBytes(name, maxBytes);
    return source.status == RF455ResourceReadStatus::Ready ? RF455_LoadLooseDdsD3dx455(name, source.bytes) : nullptr;
}
