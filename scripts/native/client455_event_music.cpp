#include "client455_event_music.h"
#include "client455_edf_input.h"
#include "client455_language.h"
#include "client455_resource_text.h"
#include <cstdlib>
#include <cstring>
#include <new>
#include <stdexcept>

namespace {
bool bgmId455(const char* token)
{
    // 0x4BE380 first attempts a signed decimal prefix, then hexadecimal.
    if (std::strtol(token, nullptr, 10)) return true;
    if (token[0] != '0' || (token[1] != 'x' && token[1] != 'X') || !token[2])
        return false;
    std::uint32_t id = 0;
    for (const char* digit = token + 2; *digit; ++digit) {
        unsigned value;
        if (*digit >= '0' && *digit <= '9') value = *digit - '0';
        else if (*digit >= 'a' && *digit <= 'f') value = *digit - 'a' + 10;
        else if (*digit >= 'A' && *digit <= 'F') value = *digit - 'A' + 10;
        else return false;
        id = (id << 4) | value;
    }
    return id != 0;
}

std::uint32_t eventWord455(const unsigned char* bytes)
{
    std::uint32_t value;
    std::memcpy(&value, bytes, sizeof(value));
    return value;
}
}

bool RF455EventMusicCatalog::loadBgm(const char* path)
{
    RF455ResourceText input;
    if (!input.open(path)) return false;
    const auto reject = [&] {
        if (input.hasCachedInput()) RF455_GetCharacterRfsCache()->RemoveLooseBytes(path);
        return false;
    };
    try {
        char token[256];
        do {
            if (!input.read(token)) return reject();
        } while (std::strcmp(token, "[BGMList]") != 0);

        std::vector<std::string> next;
        while (input.read(token)) {
            if (!bgmId455(token)) continue;
            if (!input.read(token)) return reject();
            if (std::strlen(token) > 58) continue;
            _strlwr(token);
            next.emplace_back(token);
        }
        if (input.failed()) return reject();
        music.swap(next);
        return true;
    } catch (const std::bad_alloc&) {
        return reject();
    } catch (const std::length_error&) {
        return reject();
    }
}

bool RF455EventMusicCatalog::loadEventSound(const char* path)
{
    // 0x1FE290/0x1F0CC0 read the country table's row count and stride.
    try {
        return RF455_ReadEdfInput(path, [&](const unsigned char* raw, std::size_t size) {
            std::vector<unsigned char> plain;
            constexpr std::size_t headerSize = 8;
            constexpr std::size_t minimumStride = 8;
            if (!RF455_DecodeEdf(raw, size, plain) || plain.size() < headerSize) return false;
            const auto count = eventWord455(plain.data());
            const auto stride = eventWord455(plain.data() + 4);
            if (stride < minimumStride || count > (plain.size() - headerSize) / stride) return false;
            std::vector<Event> next;
            next.reserve(count);
            const auto* row = plain.data() + headerSize;
            for (std::uint32_t i = 0; i < count; ++i, row += stride)
                next.push_back({eventWord455(row), eventWord455(row + 4)});
            events.swap(next);
            return true;
        });
    } catch (const std::bad_alloc&) {
        return false;
    } catch (const std::length_error&) {
        return false;
    }
}

void RF455EventMusicCatalog::clear()
{
    music.clear();
    events.clear();
}

const char* RF455EventMusicCatalog::musicAt(std::uint32_t slot) const
{
    return slot < music.size() ? music[slot].c_str() : nullptr;
}

const char* RF455EventMusicCatalog::musicForMonster(std::uint32_t code) const
{
    std::uint32_t slot;
    return trackForMonster(code, slot) ? musicAt(slot) : nullptr;
}

bool RF455EventMusicCatalog::trackForMonster(std::uint32_t code, std::uint32_t& slot) const
{
    // 0x1FE410 returns the first matching row's slot, not the BGM manifest ID.
    for (const auto& event : events) {
        if (event.monster != code) continue;
        if (event.slot >= music.size()) return false;
        slot = event.slot;
        return true;
    }
    return false;
}
