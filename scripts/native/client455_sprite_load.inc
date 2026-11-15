// Pinned 455 x86 SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
// RVA 4D1600 / 4CFB90: SPR owner loading; renderer and animation are unchanged.
#include "client455_character_rfs.h"
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <memory>
#include <new>
#include <stdexcept>
#include <utility>
#include <vector>

extern void SetDDSTexSizeDebug(DWORD size);
static_assert(sizeof(_FRAME_INFO) == 20, "455 sprite frame layout");
namespace {
struct SpriteInput455 {
    FILE* file = nullptr;
    const BYTE* next = nullptr;
    std::uint64_t remaining = 0;
    bool read(void* target, size_t count) {
        if (count > remaining) return false;
        if (count) {
            if (file) {
                if (std::fread(target, 1, count, file) != count) return false;
            } else {
                std::memcpy(target, next, count);
                next += count;
            }
        }
        remaining -= count;
        return true;
    }
    bool skip(std::uint64_t count) {
        if (count > remaining) return false;
        if (count) {
            if (file) {
                if (_fseeki64(file, static_cast<__int64>(count), SEEK_CUR)) return false;
            } else next += static_cast<size_t>(count);
        }
        remaining -= count;
        return true;
    }
    bool readPixels(size_t required, DWORD size, std::vector<BYTE>& scratch, const BYTE*& pixels) {
        if (!file) {
            pixels = next;
            return skip(size);
        }
        scratch.resize(required);
        pixels = scratch.data();
        return read(scratch.data(), required) && skip(size - required);
    }
};
struct SpriteFrames455 {
    WORD counts[_MAX_ACTIONS] = {};
    _FRAME_INFO* frames[_MAX_ACTIONS] = {};
    ~SpriteFrames455() {
        for (unsigned action = 0; action < _MAX_ACTIONS; ++action) {
            if (!frames[action]) continue;
            for (unsigned frame = 0; frame < counts[action]; ++frame)
                if (frames[action][frame].Tex)
                    static_cast<LPDIRECT3DTEXTURE9>(frames[action][frame].Tex)->Release();
            Dfree(frames[action]);
        }
    }
};
bool spritePayload455(DWORD format, DWORD width, DWORD height, std::uint64_t& required) {
    std::uint64_t stride;
    switch (format) {
    case D3DFMT_DXT1: stride = width >> 1; break;
    case D3DFMT_DXT5: stride = width; break;
    case D3DFMT_A8R8G8B8: stride = 4ull * width; break;
    case D3DFMT_A1R5G5B5:
    case D3DFMT_R5G6B5: stride = 2ull * width; break;
    default: return false;
    }
    required = stride * height;
    return true;
}
enum class SpriteRead455 { Ready, Malformed, AllocationFailed };

SpriteRead455 spriteRead455(SpriteInput455& input, SpriteFrames455& staged, DWORD& actions) {
    float version = 0;
    if (!input.read(&version, sizeof(version)) || version != 1.1f ||
        !input.read(&actions, sizeof(actions)) || actions >= _MAX_ACTIONS ||
        std::uint64_t(actions) * sizeof(DWORD) > input.remaining) return SpriteRead455::Malformed;
    std::vector<BYTE> scratch;
    for (DWORD action = 0; action < actions; ++action) {
        DWORD count = 0;
        if (!input.read(&count, sizeof(count)) || count > 65535 ||
            std::uint64_t(count) * 24 > input.remaining) return SpriteRead455::Malformed;
        staged.counts[action] = static_cast<WORD>(count);
        if (count) {
            staged.frames[action] = static_cast<_FRAME_INFO*>(Dmalloc(sizeof(_FRAME_INFO) * count));
            if (!staged.frames[action]) return SpriteRead455::AllocationFailed;
            std::memset(staged.frames[action], 0, sizeof(_FRAME_INFO) * count);
        }
        for (DWORD frame = 0; frame < count; ++frame) {
            DWORD header[6]; // format, original width/height, texture width/height, byte count.
            if (!input.read(header, sizeof(header))) return SpriteRead455::Malformed;
            for (unsigned dimension = 1; dimension <= 4; ++dimension)
                if (header[dimension] > 65535) return SpriteRead455::Malformed;
            std::uint64_t required = 0;
            if (!header[3] || !header[4] ||
                !spritePayload455(header[0], header[3], header[4], required) ||
                required > header[5] || header[5] > input.remaining) return SpriteRead455::Malformed;
            // Only the original upload stride is consumed by the texture helper.
            // Extra compatible payload is skipped without a second large allocation.
            const BYTE* pixels;
            if (!input.readPixels(static_cast<size_t>(required), header[5], scratch, pixels))
                return SpriteRead455::Malformed;
            auto& out = staged.frames[action][frame];
            out.Format = header[0]; out.Size = header[5];
            out.OrgXL = static_cast<WORD>(header[1]); out.OrgYL = static_cast<WORD>(header[2]);
            out.XL = static_cast<WORD>(header[3]); out.YL = static_cast<WORD>(header[4]);
            SetDDSTexSizeDebug(out.Size);
            // The legacy upload signature takes BYTE*, but only reads the pixels.
            if (out.XL && out.YL && required)
                out.Tex = GetDDSTexFromBuffer(out.XL, out.YL, out.Format, const_cast<BYTE*>(pixels));
            // A valid SPR still publishes CPU metadata when no GPU/device exists.
        }
    }
    return SpriteRead455::Ready; // Trailing file bytes remain compatible with 455.
}
}

void CSprite::LoadSprite(char* name) {
    if (!name) { Warning("Invalid sprite path", ""); return; }
    size_t length = 0;
    while (length < sizeof(mFileName) && name[length]) ++length;
    if (length == sizeof(mFileName)) { Warning("Sprite path is too long", ""); return; }
    std::memmove(mFileName, name, length + 1); // GetFileName() may be the argument.
    RF455_GetCharacterRfsCache()->RemoveLooseBytes(mFileName);
    if (mIsLoadedTexMem) ReleaseTexMemSprite();
    RestoreTexMemSprite();
}

bool CSprite::LoadMinimapSprite455(const char* name) {
    if (!name || !*name) return false;
    if (IsLoaded455() && HasFrame455(0, 0) && _stricmp(mFileName, name) == 0)
        return true;

    CSprite staged;
    staged.LoadSprite(const_cast<char*>(name));
    if (!staged.HasFrame455(0, 0)) {
        staged.ReleaseSprite();
        return false;
    }

    // The window borrows this object's address. Replace its state only after
    // decoding the new terrain, and release the old frames via the temporary.
    std::swap(*this, staged);
    staged.ReleaseSprite();
    return true;
}

void CSprite::RestoreTexMemSprite() {
    if (mIsLoadedTexMem) return;
    auto* cache = RF455_GetCharacterRfsCache();
    constexpr std::size_t maxCachedBytes = 16u * 1024u * 1024u;
    const auto budget = cache->ByteBudget();
    const auto limit = budget < maxCachedBytes ? budget : maxCachedBytes;
    const auto source = limit ? cache->ReadLooseBytes(mFileName, limit) : RF455ResourceRead{};
    const bool inMemory = source.status == RF455ResourceReadStatus::Ready && source.bytes;
    std::unique_ptr<FILE, decltype(&std::fclose)> file(nullptr, &std::fclose);
    SpriteInput455 input;
    if (inMemory) {
        input = {nullptr, source.bytes->data(), source.bytes->size()};
    } else {
        if (limit && (source.status != RF455ResourceReadStatus::ReadError || source.declaredSize <= limit)) {
            if (source.status == RF455ResourceReadStatus::MemoryError)
                Warning(mFileName, " <- Sprite allocation failed");
            else if (source.status == RF455ResourceReadStatus::Unavailable)
                Warning(mFileName, " <- Sprite file could not be opened");
            else Warning(mFileName, " <- Invalid or incomplete sprite");
            return;
        }
        file.reset(std::fopen(mFileName, "rb"));
        if (!file) { Warning(mFileName, " <- Sprite file could not be opened"); return; }
        if (_fseeki64(file.get(), 0, SEEK_END)) { Warning(mFileName, " <- Sprite seek failed"); return; }
        const __int64 length = _ftelli64(file.get());
        if (length < 0 || _fseeki64(file.get(), 0, SEEK_SET)) { Warning(mFileName, " <- Sprite length failed"); return; }
        input = {file.get(), nullptr, static_cast<std::uint64_t>(length)};
    }
    SpriteFrames455 staged;
    DWORD actions = 0;
    try {
        const auto result = spriteRead455(input, staged, actions);
        if (result == SpriteRead455::Malformed) {
            if (inMemory) cache->RemoveLooseBytes(mFileName);
            Warning(mFileName, " <- Invalid or incomplete sprite");
            return;
        }
        if (result == SpriteRead455::AllocationFailed) { Warning(mFileName, " <- Sprite allocation failed"); return; }
    } catch (const std::bad_alloc&) { Warning(mFileName, " <- Sprite allocation failed"); return;
    } catch (const std::length_error&) { Warning(mFileName, " <- Sprite payload is too large"); return; }
    if (file && std::fclose(file.release())) { Warning(mFileName, " <- Sprite close failed"); return; }
    for (unsigned action = 0; action < _MAX_ACTIONS; ++action) {
        mFrames[action] = staged.counts[action];
        mFrameInfo[action] = staged.frames[action];
        staged.frames[action] = nullptr;
    }
    mActions = actions;
    mIsLoadedTexMem = TRUE;
}
