#include <limits.h>
#include "client455_resource_io.h"
#include <cstring>
#include <memory>

namespace {
constexpr std::uint64_t RF455_R3TMaxBytes = 128u * 1024u * 1024u;
constexpr std::size_t RF455_R3TNameBytes = 128;

template<class Record>
constexpr int RF455_TextureRegistryLimit()
{
    return static_cast<int>((INT_MAX - 4) / sizeof(Record));
}

bool RF455_ValidTextureRegistries()
{
    return stR3TexCnt > 0 && stR3TexCnt <= stR3TexMaxCnt &&
        stR3TexMaxCnt <= RF455_TextureRegistryLimit<R3Texture>() &&
        stR3D3DTexCnt > 0 && stR3D3DTexCnt <= stR3D3DTexMaxCnt &&
        stR3D3DTexMaxCnt <= RF455_TextureRegistryLimit<_R3D3DTEXTURE>() &&
        bool(stR3Texture) == bool(stR3D3DTexture);
}

template<class Record>
using StagedTextureRegistry455 = std::unique_ptr<Record, decltype(&Dfree)>;

template<class Record>
StagedTextureRegistry455<Record> RF455_StageTextureRegistry(Record* old, int oldCapacity, int capacity)
{
    const auto bytes = sizeof(Record) * capacity;
    StagedTextureRegistry455<Record> staged(static_cast<Record*>(Dmalloc(static_cast<int>(bytes))), &Dfree);
    if (!staged) return staged;

    const auto preserved = old ? sizeof(Record) * oldCapacity : 0;
    if (preserved) std::memcpy(staged.get(), old, preserved);
    std::memset(reinterpret_cast<unsigned char*>(staged.get()) + preserved, 0, bytes - preserved);
    return staged;
}

bool RF455_GrowTextureRegistries(int textureCapacity, int d3dCapacity)
{
    if (textureCapacity < stR3TexMaxCnt || textureCapacity > RF455_TextureRegistryLimit<R3Texture>() ||
        d3dCapacity < stR3D3DTexMaxCnt || d3dCapacity > RF455_TextureRegistryLimit<_R3D3DTEXTURE>())
        return false;
    StagedTextureRegistry455<R3Texture> textures(nullptr, &Dfree);
    StagedTextureRegistry455<_R3D3DTEXTURE> surfaces(nullptr, &Dfree);
    if (!stR3Texture || textureCapacity != stR3TexMaxCnt) {
        textures = RF455_StageTextureRegistry(stR3Texture, stR3TexMaxCnt, textureCapacity);
        if (!textures) return false;
    }
    if (!stR3D3DTexture || d3dCapacity != stR3D3DTexMaxCnt) {
        surfaces = RF455_StageTextureRegistry(stR3D3DTexture, stR3D3DTexMaxCnt, d3dCapacity);
        if (!surfaces) return false;
    }
    // Old and staged metadata borrow the same COM pointers until publication.
    if (textures) {
        Dfree(stR3Texture);
        stR3Texture = textures.release();
        stR3TexMaxCnt = textureCapacity;
    }
    if (surfaces) {
        Dfree(stR3D3DTexture);
        stR3D3DTexture = surfaces.release();
        stR3D3DTexMaxCnt = d3dCapacity;
    }
    return true;
}

struct RF455_R3TInput {
    const unsigned char* next;
    std::size_t remaining;

    template<class Field>
    bool read(Field& value) {
        if (sizeof(value) > remaining) return false;
        std::memcpy(&value, next, sizeof(value));
        next += sizeof(value);
        remaining -= sizeof(value);
        return true;
    }

    bool skip(std::size_t bytes) {
        if (bytes > remaining) return false;
        next += bytes;
        remaining -= bytes;
        return true;
    }

    bool readMember(const unsigned char*& data, DWORD& size) {
        if (!read(size)) return false;
        data = next;
        return skip(size);
    }
};

bool RF455_OpenR3TFrame(RF455_R3TInput& input, DWORD count)
{
    if (count > input.remaining / (RF455_R3TNameBytes + sizeof(DWORD)) ||
        !input.skip(static_cast<std::size_t>(count) * RF455_R3TNameBytes))
        return false;
    // DDS content can fail independently. Validate its outer frame before
    // the caller changes any reserved texture slots.
    auto frame = input;
    for (DWORD i = 0; i < count; ++i) {
        const unsigned char* member;
        DWORD size;
        if (!frame.readMember(member, size)) return false;
    }
    return true;
}

void RF455_WarnR3TVersion(char* name)
{
    Warning(name, "<-\xc0\xcc \xc6\xc4\xc0\xcf\xc0\xcc \xc0\xcc\xc0\xfc\xb9\xf6\xc0\xfc\xc0\xd4\xb4\xcf\xb4\xd9.");
}
}

// Client 455 x86 RVA 0x4F2260. Existing texture names reuse the reserved slots.
static R3Texture* RF455_ReserveR3T(char* name, DWORD flag, const DWORD* preparedCount = nullptr,
                                  RF455ResourceRead* lightmapSource = nullptr)
{
    if (!name || !*name) return NULL;
    if (strlen(name) >= sizeof(R3Texture::mName) - 1) {
        Warning("\xc0\xa2 \xc5\xd8\xbd\xba\xc3\xc4\xc0\xcc\xb8\xa7\xc0\xcc \xc0\xcc\xb7\xb8\xb0\xd4 \xb1\xe2\xb3\xc4...", "");
        return NULL;
    }
    // Engine Dmalloc/ReAlloc take signed byte counts and prepend a four-byte
    // allocation header. Validate pool state before looking up an entry.
    const int texLimit = RF455_TextureRegistryLimit<R3Texture>();
    const int d3dLimit = RF455_TextureRegistryLimit<_R3D3DTEXTURE>();
    if (!RF455_ValidTextureRegistries()) return NULL;
    DWORD count = 0;
    if (lightmapSource && !RF455_PrepareLightmapR3T455(name, *lightmapSource, count))
        return NULL;
    if (stR3Texture && !(stR3TexManageFlag & _R3TEX_MANAGE_FLAG_NO_SAME_CHECK)) {
        for (int i = 1; i < stR3TexCnt; ++i) {
            if (strcmp(stR3Texture[i].mName, name)) continue;
            ++stR3Texture[i].mSameCnt;
            return &stR3Texture[i];
        }
    }
    if (preparedCount) {
        count = *preparedCount;
    } else if (!lightmapSource) {
        const auto source = RF455_ReadResourceBytes(name, RF455_R3TMaxBytes);
        if (source.status == RF455ResourceReadStatus::Unavailable)
            Warning(name, "<-\xc0\xcc\xc6\xc4\xc0\xcf\xc0\xcc \xbe\xf8\xb4\xc2\xb5\xa5 r3m\xc6\xc4\xc0\xcf\xc0\xba \xc1\xb8\xc0\xe7\xc7\xd5\xb4\xcf\xb4\xd9.. \xbe\xc6\xb8\xb6 \xb7\xce\xba\xbf\xbf\xa1\xbc\xad\xb9\xf7\xb3\xb5\xc0\xbb\xb0\xcc\xb4\xcf\xb4\xd9...");
        if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return NULL;
        RF455_R3TInput input{source.bytes->data(), source.bytes->size()};
        float version;
        const bool header = input.read(version) && input.read(count);
        const bool validVersion = header && version >= 1.1f;
        if (!validVersion || !RF455_OpenR3TFrame(input, count)) {
            RF455_GetCharacterRfsCache()->RemovePayloadBytes(source.bytes);
            if (header && !validVersion) RF455_WarnR3TVersion(name);
            return NULL;
        }
    }

    // Compute growth before publishing a pool entry.
    const int texGrowth = stR3TexCnt == stR3TexMaxCnt ? 16 : 0;
    if (texGrowth > texLimit - stR3TexMaxCnt || count > static_cast<DWORD>(d3dLimit - stR3D3DTexCnt))
        return NULL;
    const int number = static_cast<int>(count);
    const int nextSlot = stR3D3DTexCnt + number;
    const int d3dGrowth = nextSlot >= stR3D3DTexMaxCnt ? number : 0;
    if (d3dGrowth > d3dLimit - stR3D3DTexMaxCnt) return NULL;

    char stagedName[sizeof(R3Texture::mName)];
    std::strcpy(stagedName, name);
    if (!RF455_GrowTextureRegistries(stR3TexMaxCnt + texGrowth, stR3D3DTexMaxCnt + d3dGrowth)) return NULL;

    auto& tex = stR3Texture[stR3TexCnt++];
    tex.mFlag = flag;
    tex.mStartID = static_cast<DWORD>(stR3D3DTexCnt);
    tex.mTexNum = count;
    strcpy(tex.mName, stagedName);
    stR3D3DTexCnt = nextSlot;
    return &tex;
}

R3Texture* R3GetTexInfoR3T(char* name, DWORD flag)
{
    return RF455_ReserveR3T(name, flag);
}

R3Texture* RF455_ReserveLightmapR3T455(char* name, DWORD flag, RF455ResourceRead& source)
{
    source = {};
    return RF455_ReserveR3T(name, flag, nullptr, &source);
}

R3Texture* R3GetLightmapTexInfo455(char* name, DWORD flag)
{
    RF455ResourceRead source;
    return RF455_ReserveLightmapR3T455(name, flag, source);
}

R3Texture* RF455_ReserveMapR3T(char* name, RF455ResourceRead& source)
{
    source = {};
    if (!name || !*name || strlen(name) >= sizeof(R3Texture::mName) - 1) return nullptr;
    // CLevel has cleared archive routing. Keep this loose lease across the
    // reserve, SetNoLodTextere and upload calls even when retention is disabled.
    auto* cache = RF455_GetCharacterRfsCache();
    source = cache->ReadLooseBytes(name, RF455_R3TMaxBytes);
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return nullptr;
    RF455_R3TInput input{source.bytes->data(), source.bytes->size()};
    float version;
    DWORD count;
    if (!input.read(version) || !input.read(count) || !(version >= 1.1f) ||
        !count || !RF455_OpenR3TFrame(input, count)) {
        cache->RemovePayloadBytes(source.bytes);
        source = {};
        return nullptr;
    }
    return RF455_ReserveR3T(name, 0, &count);
}

// Client 455 x86 RVA 0x4F33B0. Read size-delimited DDS after the name table.
static void RF455_UploadR3T(R3Texture* tex, const RF455ResourceRead& source)
{
    if (!tex || !memchr(tex->mName, '\0', sizeof(tex->mName))) return;
    if (source.status == RF455ResourceReadStatus::Unavailable) {
        Warning(tex->mName, "<-\xc0\xcc\xc6\xc4\xc0\xcf\xc0\xcc \xbe\xf8\xbd\xb4");
        return;
    }
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) return;
    RF455_R3TInput input{source.bytes->data(), source.bytes->size()};
    float version;
    DWORD count;
    if (!input.read(version) || !input.read(count)) {
        RF455_GetCharacterRfsCache()->RemovePayloadBytes(source.bytes);
        return;
    }
    if (!(version >= 1.1f)) {
        RF455_GetCharacterRfsCache()->RemovePayloadBytes(source.bytes);
        RF455_WarnR3TVersion(tex->mName);
        return;
    }
    if (!RF455_OpenR3TFrame(input, count)) {
        RF455_GetCharacterRfsCache()->RemovePayloadBytes(source.bytes);
        return;
    }
    if (!count || !stR3D3DTexture || stR3D3DTexCnt <= 0 || stR3D3DTexCnt > stR3D3DTexMaxCnt)
        return;
    const auto nextSlot = static_cast<DWORD>(stR3D3DTexCnt);
    if (!tex->mStartID || tex->mStartID >= nextSlot || count > tex->mTexNum ||
        count > nextSlot - tex->mStartID)
        return;

    for (DWORD i = 0; i < count; ++i) {
        const unsigned char* member;
        DWORD size;
        if (!input.readMember(member, size)) return;
        auto& slot = stR3D3DTexture[tex->mStartID + i];
        const DWORD detail = slot.mFlag & _R3D3DTEXTURE_FLAG_NO_LOD ? 0 : GetR3State()->mSceneTextureDetail;
        auto* loaded = RF455_LoadDDSFromBytes(member, size, detail);
        if (!loaded) continue;
        if (slot.m_pTexture) slot.m_pTexture->Release();
        slot.m_pTexture = loaded;
    }
}

void LoadR3T(R3Texture* tex)
{
    if (!tex || !memchr(tex->mName, '\0', sizeof(tex->mName))) return;
    const auto source = RF455_ReadResourceBytes(tex->mName, RF455_R3TMaxBytes);
    RF455_UploadR3T(tex, source);
}

void RF455_LoadMapR3T(R3Texture* tex, const RF455ResourceRead& source)
{
    RF455_UploadR3T(tex, source);
}
