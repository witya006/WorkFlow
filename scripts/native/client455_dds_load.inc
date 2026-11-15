#include "client455_resource_io.h"
#include <cstring>

static LPDIRECT3DTEXTURE9 RF455_LoadLooseDdsD3dx455(const char* name, const RF455ResourceBytes& bytes);

LPDIRECT3DTEXTURE9 R3LoadDDS(char* name, DWORD mipmap, DWORD maxWidth=2048, DWORD maxHeight=2048)
{
    // Client 455 x86 RVA 0x4F34F0 shares the resource resolver before DDS
    // decoding. A resolved image that fails decoding can still use D3DX's
    // loose-file fallback at RVA 0x4F1990.
    if (!name || !*name) return NULL;
    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    char archivePath[256];
    const auto length = std::strlen(name);
    RF455ResourceRead source;
    bool fromArchive = false;
    if (length < sizeof(archivePath)) {
        // The archive resolver can lowercase its argument in place.
        std::memcpy(archivePath, name, length + 1);
        source = RF455_ReadResourceBytes(archivePath, maxBytes, &fromArchive);
    } else {
        source = RF455_GetCharacterRfsCache()->ReadLooseBytes(name, maxBytes);
    }
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return NULL;
    auto* texture = RF455_LoadDDSFromBytes(source.bytes->data(), static_cast<DWORD>(source.bytes->size()),
                                         mipmap, maxWidth, maxHeight);
    if (texture) return texture;
    // D3DX's fallback opens only a loose file. Reuse bytes already read from
    // that file even when the cache's retention budget is zero.
    return fromArchive ? R3LoadDDSAndTextureMem(name) : RF455_LoadLooseDdsD3dx455(name, source.bytes);
}
