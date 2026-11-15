#pragma once

#include "client455_resource_text.h"
#include <cstdint>
#include <cstdlib>
#include <limits>
#include <new>
#include <vector>

enum class RF455EffectManifestKind { Entity, Magic };

struct RF455EffectManifestEntry {
    std::uint32_t id;
    char path[90];
};

inline std::uint32_t RF455_EffectManifestId455(const char* token)
{
    const auto decimal = static_cast<std::uint32_t>(std::atol(token));
    if (decimal) return decimal;
    if (token[0] != '0' || (token[1] != 'x' && token[1] != 'X')) return 0;

    std::uint32_t result = 0;
    unsigned shift = 0;
    for (auto* end = token + std::strlen(token); end != token + 2; shift = (shift + 4) & 31u) {
        const int ch = std::tolower(static_cast<unsigned char>(*--end));
        if (ch >= '0' && ch <= '9') result += static_cast<std::uint32_t>(ch - '0') << shift;
        else if (ch >= 'a' && ch <= 'f') result += static_cast<std::uint32_t>(ch - 'a' + 10) << shift;
        else return 0;
    }
    return result;
}

inline bool RF455_ReadEffectManifest455(const char* path, RF455EffectManifestKind kind,
                                        std::vector<RF455EffectManifestEntry>& out,
                                        std::size_t* skippedTooLong = nullptr)
{
    RF455ResourceText input;
    if (!input.open(path)) return false;
    const char* header = kind == RF455EffectManifestKind::Entity ? "[EffectEntityList]" : "[MagcicSptList]";
    const auto reject = [&]() {
        if (input.hasCachedInput()) RF455_GetCharacterRfsCache()->RemoveLooseBytes(path);
        return false;
    };
    char token[256];
    for (;;) {
        if (!input.read(token)) return reject();
        if (!std::strcmp(token, header)) break;
    }

    // The larger destination uses 100-byte rows and Dmalloc(int) adds four bytes.
    constexpr std::size_t rowLimit = ((std::numeric_limits<int>::max)() - 4) / 100;
    std::vector<RF455EffectManifestEntry> parsed;
    std::size_t skipped = 0;
    while (input.read(token)) {
        const auto id = RF455_EffectManifestId455(token);
        if (!id) continue;
        if (!input.read(token) || !*token) return reject();
        if (kind == RF455EffectManifestKind::Entity) _strlwr(token);
        RF455EffectManifestEntry entry{};
        const auto length = std::strlen(token);
        if (length >= sizeof(entry.path)) {
            ++skipped;
            continue;
        }
        if (parsed.size() == rowLimit) return reject();
        entry.id = id;
        std::memcpy(entry.path, token, length + 1);
        try { parsed.push_back(entry); }
        catch (const std::bad_alloc&) { return false; }
    }
    if (input.failed()) return reject();
    if (skippedTooLong) *skippedTooLong = skipped;
    out.swap(parsed);
    return true;
}
