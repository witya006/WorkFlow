#include <climits>
#include <cstring>

void RestoreSystemTexture();

namespace {
bool ValidTextureSurface455(int id)
{
    return stR3D3DTexture && id > 0 && id < stR3D3DTexCnt && id < stR3D3DTexMaxCnt;
}

bool OwnsTextureSlot455(const R3Texture& owner, DWORD slot)
{
    return (owner.mName[0] || !(owner.mFlag & _R3TEXFLAG_NONE_R3T)) && owner.mStartID && owner.mStartID <= slot &&
           slot - owner.mStartID < owner.mTexNum;
}

R3Texture* TextureSlotOwner455(int id)
{
    if (!ValidTextureSurface455(id) || !stR3Texture || stR3TexCnt > stR3TexMaxCnt) return nullptr;
    const auto slot = static_cast<DWORD>(id);
    for (int index = stR3TexCnt - 1; index > 0; --index) {
        auto& owner = stR3Texture[index];
        if (OwnsTextureSlot455(owner, slot)) return &owner;
    }
    return nullptr;
}

void UploadMstTexture455(R3Texture& owner, _R3D3DTEXTURE& surface)
{
    if (surface.m_pTexture) return;
    const DWORD detail = (surface.mFlag & _R3D3DTEXTURE_FLAG_NO_LOD) ? 0 : GetR3State()->mSceneTextureDetail;
    surface.m_pTexture = R3LoadDDS(owner.mName, detail, 2048, 2048);
}

int NextMstTextureCapacity455(int count, int capacity, int limit)
{
    if (count < capacity) return capacity;
    constexpr int step = 16;
    return capacity + (limit - capacity < step ? limit - capacity : step);
}
}

void SetNowR3D3DTexCnt(int count)
{
    if (count < 1 || count >= stR3D3DTexCnt || stR3D3DTexCnt > stR3D3DTexMaxCnt || !stR3D3DTexture) return;
    // CEntity has taken ownership of the detached COM pointers before truncation.
    std::memset(stR3D3DTexture + count, 0, sizeof(*stR3D3DTexture) * (stR3D3DTexCnt - count));
    stR3D3DTexCnt = count;
}

void SetNowR3TexCnt(int count)
{
    if (count < 1 || count >= stR3TexCnt || stR3TexCnt > stR3TexMaxCnt || !stR3Texture) return;
    std::memset(stR3Texture + count, 0, sizeof(*stR3Texture) * (stR3TexCnt - count));
    stR3TexCnt = count;
}

char* R3GetTexName(int id)
{
    if (!stR3Texture || id < 0 || id >= stR3TexCnt || id >= stR3TexMaxCnt) return nullptr;
    return stR3Texture[id].mName;
}

int R3GetPreTextureId(char* name)
{
    if (!name || !*name) return 0;
    if (std::strlen(name) >= sizeof(R3Texture::mName) - 1) {
        Warning("MST texture", " name is too long");
        return 0;
    }
    if (!RF455_ValidTextureRegistries()) return 0;
    if (stR3Texture && !(stR3TexManageFlag & _R3TEX_MANAGE_FLAG_NO_SAME_CHECK)) {
        for (int index = 1; index < stR3TexCnt; ++index) {
            auto& texture = stR3Texture[index];
            if (!(texture.mFlag & _R3TEXFLAG_NONE_R3T) || texture.mTexNum != 1 || !texture.mName[0] ||
                texture.mStartID >= static_cast<DWORD>(stR3D3DTexCnt) ||
                !ValidTextureSurface455(static_cast<int>(texture.mStartID)) || std::strcmp(texture.mName, name)) continue;
            if (texture.mSameCnt == MAXDWORD) return 0;
            ++texture.mSameCnt;
            return static_cast<int>(texture.mStartID);
        }
    }

    char stagedName[sizeof(R3Texture::mName)];
    std::strcpy(stagedName, name);
    const int textureCapacity = NextMstTextureCapacity455(stR3TexCnt, stR3TexMaxCnt,
        RF455_TextureRegistryLimit<R3Texture>());
    const int d3dCapacity = NextMstTextureCapacity455(stR3D3DTexCnt, stR3D3DTexMaxCnt,
        RF455_TextureRegistryLimit<_R3D3DTEXTURE>());
    if (textureCapacity <= stR3TexCnt || d3dCapacity <= stR3D3DTexCnt ||
        !RF455_GrowTextureRegistries(textureCapacity, d3dCapacity)) return 0;

    // Append to keep registry order and prevent a retired row aliasing an R3T slice.
    const int id = stR3D3DTexCnt;
    auto& texture = stR3Texture[stR3TexCnt];
    texture = {};
    std::strcpy(texture.mName, stagedName);
    texture.mStartID = static_cast<DWORD>(id);
    texture.mTexNum = 1;
    texture.mFlag = _R3TEXFLAG_NONE_R3T | _R3TEXFLAG_MIPMAP;
    stR3D3DTexture[id] = {};
    ++stR3TexCnt;
    ++stR3D3DTexCnt;
    return id;
}

void R3LoadTextureMem(int id)
{
    auto* owner = TextureSlotOwner455(id);
    if (!owner || stR3D3DTexture[id].m_pTexture) return;
    if (!(owner->mFlag & _R3TEXFLAG_NONE_R3T)) {
        Warning("R3T texture", " is loaded through its container");
        return;
    }
    if (owner->mTexNum == 1 && owner->mStartID == static_cast<DWORD>(id))
        UploadMstTexture455(*owner, stR3D3DTexture[id]);
}

void R3ReleaseTextureMem(int id)
{
    auto* owner = TextureSlotOwner455(id);
    if (!owner || !stR3D3DTexture[id].m_pTexture) return;
    if (owner->mSameCnt) {
        --owner->mSameCnt;
        return;
    }
    if (!(owner->mFlag & _R3TEXFLAG_NONE_R3T))
        Warning("R3T texture", " released through a standalone slot");
    owner->mName[0] = '\0';
    SAFE_RELEASE(stR3D3DTexture[id].m_pTexture);
}

void R3RestoreAllTextures()
{
    if (stR3Texture && stR3TexCnt <= stR3TexMaxCnt) {
        for (int index = 1; index < stR3TexCnt; ++index) {
            auto& owner = stR3Texture[index];
            if (!(owner.mFlag & _R3TEXFLAG_NONE_R3T) || owner.mTexNum != 1 || !owner.mName[0] ||
                owner.mStartID >= static_cast<DWORD>(stR3D3DTexCnt)) continue;
            const int id = static_cast<int>(owner.mStartID);
            if (ValidTextureSurface455(id)) UploadMstTexture455(owner, stR3D3DTexture[id]);
        }
    }
    RestoreSystemTexture();
}
