#include "client455_resource_text.h"
#include <cerrno>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>
#include <vector>

namespace {
bool ReadDummyFloat455(RF455ResourceText& source, char (&token)[256], float& value)
{
    if (!source.read(token)) return false;
    char* end = nullptr;
    const double parsed = std::strtod(token, &end);
    constexpr float max = (std::numeric_limits<float>::max)();
    if (end == token || *end || !std::isfinite(parsed) || parsed > max || parsed < -max) return false;
    value = static_cast<float>(parsed);
    return true;
}

bool ReadDummyWord455(RF455ResourceText& source, char (&token)[256], DWORD& value)
{
    if (!source.read(token)) return false;
    char* end = nullptr;
    errno = 0;
    const long parsed = std::strtol(token, &end, 10);
    if (end == token || *end || errno == ERANGE) return false;
    value = static_cast<DWORD>(parsed);
    return true;
}

void StoreDummyFog455(_EXT_DUMMY& helper, unsigned index, float distance)
{
    static_assert(sizeof(float) == sizeof(DWORD), "455 helper fog lane");
    std::memcpy(&helper.mdwArgv[index], &distance, sizeof(distance));
}

bool ReadDummyAttributes455(RF455ResourceText& source, char (&token)[256], _EXT_DUMMY& helper)
{
    while (source.read(token)) {
        if (!std::strcmp(token, "script_end") || token[0] == '*') return true;
        if (!std::strcmp(token, "-node_tm")) {
            for (auto& row : helper.mMat)
                for (float& field : row)
                    if (!ReadDummyFloat455(source, token, field)) return false;
            MatrixInvert(helper.mInvMat, helper.mMat);
        }
        if (!std::strcmp(token, "-id") && !ReadDummyWord455(source, token, helper.mID)) return false;
        if (!std::strcmp(token, "-music")) helper.mFlag |= _DUMMY_FLAG_MUSIC;
        if (!std::strcmp(token, "-interior")) helper.mFlag |= _DUMMY_FLAG_INTERIOR;
        if (!std::strcmp(token, "-fog_color")) {
            DWORD red, green, blue;
            if (!ReadDummyWord455(source, token, red) || !ReadDummyWord455(source, token, green) ||
                !ReadDummyWord455(source, token, blue)) return false;
            helper.mFlag |= _DUMMY_FLAG_FOG;
            helper.mdwArgv[0] = 0xff000000u | (red << 16) | (green << 8) | blue;
            const auto* state = GetR3State();
            // RVA 0x50BFAF/0x50BFC5 read the base fog distances.
            StoreDummyFog455(helper, 1, state->mMainFogStart);
            StoreDummyFog455(helper, 2, state->mMainFogEnd);
        }
        if (!std::strcmp(token, "-fog_start")) {
            float distance;
            if (!ReadDummyFloat455(source, token, distance)) return false;
            StoreDummyFog455(helper, 1, distance);
        }
        if (!std::strcmp(token, "-fog_end")) {
            float distance;
            if (!ReadDummyFloat455(source, token, distance)) return false;
            StoreDummyFog455(helper, 2, distance);
        }
    }
    token[0] = '\0';
    return !source.failed();
}

bool ReadExtDummies455(RF455ResourceText& source, std::vector<_EXT_DUMMY>& result)
{
    char token[256];
    do {
        if (!source.read(token)) return false;
    } while (std::strcmp(token, "script_begin"));

    constexpr std::size_t maxCount = ((std::numeric_limits<int>::max)() - 4) / sizeof(_EXT_DUMMY);
    bool hasToken = source.read(token);
    while (hasToken) {
        _strlwr(token);
        if (!std::strcmp(token, "script_end")) return true;
        if (token[0] != '*') {
            hasToken = source.read(token);
            continue;
        }

        _EXT_DUMMY helper{};
        std::strncpy(helper.mName, token + 1, sizeof(helper.mName) - 1);
        MatrixIdentity(helper.mMat);
        for (float& field : helper.mBBmin)
            if (!ReadDummyFloat455(source, token, field)) return false;
        for (float& field : helper.mBBmax)
            if (!ReadDummyFloat455(source, token, field)) return false;
        if (!ReadDummyAttributes455(source, token, helper) || result.size() == maxCount) return false;
        result.push_back(helper);
        // The attributes consume a new helper marker or the exact end token.
        hasToken = token[0] != '\0';
    }
    return !source.failed();
}
}

BOOL CExtDummy::LoadExtDummy(char* name)
{
    ReleaseExtDummy();
    RF455ResourceText source;
    if (!source.open(name)) return FALSE;
    std::vector<_EXT_DUMMY> records;
    try {
        if (!ReadExtDummies455(source, records)) {
            if (source.hasCachedInput()) RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
            return FALSE;
        }
    } catch (const std::bad_alloc&) {
        return FALSE;
    }
    if (records.empty()) return TRUE;

    const auto bytes = records.size() * sizeof(_EXT_DUMMY);
    auto* ready = static_cast<_EXT_DUMMY*>(Dmalloc(static_cast<int>(bytes)));
    if (!ready) return FALSE;
    std::memcpy(ready, records.data(), bytes);
    mDummy = ready;
    mNum = mMaxNum = static_cast<DWORD>(records.size());
    return TRUE;
}
