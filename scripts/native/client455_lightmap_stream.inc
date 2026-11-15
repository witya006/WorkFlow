#include <limits.h>
#include "client455_resource_io.h"
#include <cstring>

static RF455ResourceRead RF455_ReadLightmapR3T(const char* path)
{
    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    return RF455_GetCharacterRfsCache()->ReadLooseBytes(path, maxBytes);
}

struct RF455_LightmapInput {
    const unsigned char* next;
    std::size_t remaining;

    const unsigned char* take(std::size_t bytes) {
        if (bytes > remaining) return nullptr;
        const auto* first = next;
        next += bytes;
        remaining -= bytes;
        return first;
    }

    template<class Field>
    bool read(Field& field) {
        const auto* bytes = take(sizeof(field));
        if (!bytes) return false;
        std::memcpy(&field, bytes, sizeof(field));
        return true;
    }
};

struct RF455_LightmapDDS {
    const unsigned char* bytes;
    DWORD size, bits, pixels;
    WORD mipWidth, mipHeight;
};

static bool RF455_ReadLightmapMember455(RF455_LightmapInput& input, RF455_LightmapDDS& member)
{
    static_assert(sizeof(_DDS_Header) == 128, "DDS x86 lightmap header");
    DWORD size;
    if (!input.read(size) || size < sizeof(_DDS_Header)) return false;
    const auto* bytes = input.take(size);
    if (!bytes) return false;

    _DDS_Header header;
    std::memcpy(&header, bytes, sizeof(header));
    if (header.dwMagic != 0x20534444) return false;
    const auto& desc = header.ddsd;
    const DWORD bits = desc.ddpfPixelFormat.dwRGBBitCount;
    if (desc.ddpfPixelFormat.dwFourCC || (bits != 16 && bits != 32) ||
        !desc.dwWidth || !desc.dwHeight || desc.dwWidth > 2048 || desc.dwHeight > 2048)
        return false;

    const WORD width = static_cast<WORD>(GetOneStepMipMap(static_cast<WORD>(desc.dwWidth)));
    const WORD height = static_cast<WORD>(GetOneStepMipMap(static_cast<WORD>(desc.dwHeight)));
    const DWORD bytesPerPixel = bits / 8;
    const DWORD pixels = desc.dwWidth * desc.dwHeight * bytesPerPixel;
    const DWORD mipInputBytes = 4u * width * height * bytesPerPixel;
    // MakeMipMap reads four input pixels per output pixel even when the
    // legacy dimension rule leaves an axis of at most four unchanged.
    if (pixels > size - sizeof(header) || mipInputBytes > size - sizeof(header)) return false;
    member = {bytes, size, bits, pixels, width, height};
    return true;
}

// Client 455 x86 RVA 0x4F1F20. Lightmaps use a direct loose-file path and
// follow the count with DDS members, each preceded by its byte size.
static bool RF455_OpenLightmapFrame455(char* name, const RF455ResourceRead& source,
                                     RF455_LightmapInput& members, DWORD& count)
{
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return false;
    const auto reject = [&] {
        RF455_GetCharacterRfsCache()->RemovePayloadBytes(source.bytes);
        return false;
    };
    RF455_LightmapInput input{source.bytes->data(), source.bytes->size()};
    float version;
    if (!input.read(version) || !input.read(count)) return reject();
    if (version != 1.1f && version != 1.2f) {
        Warning(name, "<-\xc0\xcc \xc6\xc4\xc0\xcf\xc0\xcc \xc0\xcc\xc0\xfc\xb9\xf6\xc0\xfc\xc0\xd4\xb4\xcf\xb4\xd9.");
        return reject();
    }
    if (count > input.remaining / (sizeof(DWORD) + sizeof(_DDS_Header))) return reject();
    members = input;
    for (DWORD i = 0; i < count; ++i) {
        RF455_LightmapDDS member;
        if (!RF455_ReadLightmapMember455(input, member)) return reject();
    }
    return true;
}

static bool RF455_PrepareLightmapR3T455(char* name, RF455ResourceRead& source, DWORD& count)
{
    source = RF455_ReadLightmapR3T(name);
    RF455_LightmapInput members{};
    if (RF455_OpenLightmapFrame455(name, source, members, count)) return true;
    source = {};
    return false;
}

_LIGHTMAP** RF455_LoadPreparedLightmap455(R3Texture* tex, const RF455ResourceRead& source)
{
    LightMapTexSize = 0;
    if (!tex || !memchr(tex->mName, '\0', sizeof(tex->mName))) return NULL;
    RF455_LightmapInput input{};
    DWORD count;
    if (!RF455_OpenLightmapFrame455(tex->mName, source, input, count)) return NULL;
    if (!count || count != tex->mTexNum || !stR3D3DTexture || stR3D3DTexCnt <= 0 ||
        stR3D3DTexCnt > stR3D3DTexMaxCnt)
        return NULL;
    const auto nextSlot = static_cast<DWORD>(stR3D3DTexCnt);
    if (!tex->mStartID || tex->mStartID >= nextSlot || count > nextSlot - tex->mStartID ||
        count > (INT_MAX - 4) / sizeof(_LIGHTMAP*))
        return NULL;

    // ReleaseLightMap owns the returned engine allocations. Stage CPU/GPU
    // members until every CPU map has been built.
    struct Pending {
        _LIGHTMAP** maps;
        LPDIRECT3DTEXTURE9* textures;
        DWORD ready;
        ~Pending() {
            for (DWORD i = 0; i < ready; ++i) {
                if (maps) {
                    Dfree(maps[i]->buf);
                    Dfree(maps[i]);
                }
                if (textures[i]) textures[i]->Release();
            }
            Dfree(maps);
            free(textures);
        }
    } pending = {NULL, static_cast<LPDIRECT3DTEXTURE9*>(calloc(count, sizeof(LPDIRECT3DTEXTURE9))), 0};
    if (!pending.textures) return NULL;
    pending.maps = static_cast<_LIGHTMAP**>(Dmalloc(static_cast<int>(count * sizeof(_LIGHTMAP*))));
    if (!pending.maps) return NULL;

    DWORD pixelBytes = 0, recordBytes = 0;
    for (DWORD i = 0; i < count; ++i) {
        RF455_LightmapDDS member;
        if (!RF455_ReadLightmapMember455(input, member)) return NULL;

        // Keep engine adapters on aligned, private data. This covers members
        // that start at odd offsets and protects the retained bytes.
        std::unique_ptr<BYTE, decltype(&free)> bytes(static_cast<BYTE*>(malloc(member.size)), free);
        if (!bytes) return NULL;
        std::memcpy(bytes.get(), member.bytes, member.size);
        BYTE* payload = bytes.get() + sizeof(_DDS_Header);

        auto* map = static_cast<_LIGHTMAP*>(Dmalloc(static_cast<int>(sizeof(_LIGHTMAP))));
        if (!map) return NULL;
        map->buf = static_cast<WORD*>(Dmalloc(static_cast<int>(sizeof(WORD) * member.mipWidth * member.mipHeight)));
        if (!map->buf) { Dfree(map); return NULL; }
        map->xl = member.mipWidth;
        map->yl = member.mipHeight;
        if (member.bits == 16)
            MakeMipMap(map->xl, map->yl, map->buf, reinterpret_cast<WORD*>(payload));
        else MakeMipMap(map->xl, map->yl, map->buf, payload);

        pending.maps[i] = map;
        ++pending.ready;
        if (GetD3dDevice()) pending.textures[i] = GetD3DTextureFromBuffer(bytes.get(), member.size, 0);
        pixelBytes += member.pixels;
        recordBytes += member.size;
    }

    for (DWORD i = 0; i < count; ++i) {
        if (!pending.textures[i]) continue;
        auto& slot = stR3D3DTexture[tex->mStartID + i];
        if (slot.m_pTexture) slot.m_pTexture->Release();
        slot.m_pTexture = pending.textures[i];
        pending.textures[i] = NULL;
    }
    LightMapTexSize = pixelBytes;
    stNowTexMem += recordBytes;
    _LIGHTMAP** maps = pending.maps;
    pending.maps = NULL;
    return maps;
}

_LIGHTMAP** LoadR3TLightMap(R3Texture* tex, D3DFORMAT)
{
    if (!tex || !memchr(tex->mName, '\0', sizeof(tex->mName))) {
        LightMapTexSize = 0;
        return NULL;
    }
    return RF455_LoadPreparedLightmap455(tex, RF455_ReadLightmapR3T(tex->mName));
}
