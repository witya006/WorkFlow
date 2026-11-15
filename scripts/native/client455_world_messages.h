#ifndef RF455_WORLD_MESSAGES_H
#define RF455_WORLD_MESSAGES_H

#include "client455_edf_input.h"
#include "client455_language.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>

struct RF455WorldEventMessage {
    char code[64];
    std::uint32_t field;
    char text[2560];
};

struct RF455WorldMonsterMessages {
    std::uint32_t key = 0;
    unsigned count = 0;

    const char* MessageAt(std::size_t slot) const
    {
        return slot < count && slot < messages.size() ? messages[slot].c_str() : nullptr;
    }

private:
    friend class RF455WorldMessages;
    std::array<std::string, 10> messages;
};

class RF455WorldMessages {
public:
    bool LoadEvents(const char* base, const char* localized)
    {
        // Pinned 455 x86 RVAs 0x1FD250 and 0x1FCF90.
        std::vector<RF455WorldEventMessage> next;
        if (!LoadTable(base, 2628, [&](const auto& plain, std::size_t count) {
            if (plain.size() != 8 + count * 2628) return false;
            next.resize(count);
            for (std::size_t i = 0; i < count; ++i) {
                const auto* row = plain.data() + 8 + i * 2628;
                auto& entry = next[i];
                if (!std::memchr(row, 0, sizeof(entry.code)) ||
                    !std::memchr(row + 68, 0, sizeof(entry.text))) return false;
                std::memcpy(entry.code, row, sizeof(entry.code));
                entry.field = Word(row + 64);
                std::memcpy(entry.text, row + 68, sizeof(entry.text));
            }
            return true;
        })) return false;
        const auto loaded = LoadTable(localized, 2560, [&](const auto& plain, std::size_t count) {
            if (count != next.size() || plain.size() != 8 + count * 2560) return false;
            for (std::size_t i = 0; i < count; ++i)
                if (!std::memchr(plain.data() + 8 + i * 2560, 0, sizeof(next[i].text)))
                    return false;
            for (std::size_t i = 0; i < count; ++i) {
                auto& entry = next[i];
                const auto* row = plain.data() + 8 + i * 2560;
                std::memcpy(entry.text, row, sizeof(entry.text));
            }
            return true;
        });
        // The original has already loaded the base catalog when the local
        // file fails to open. Keep the last full catalog on a failed reload.
        if (loaded || events.empty()) events.swap(next);
        return loaded;
    }

    bool LoadMonsters(const char* localized)
    {
        // Pinned RVA 0x203990 reads all row headers before message strings.
        return LoadTable(localized, 88, [&](const auto& plain, std::size_t count) {
            std::vector<RF455WorldMonsterMessages> next(count);
            std::size_t offset = 8 + count * 88;
            for (std::size_t i = 0; i < count; ++i) {
                const auto* row = plain.data() + 8 + i * 88;
                auto& entry = next[i];
                entry.key = Word(row);
                const auto active = Word(row + 84);
                if (active > entry.messages.size()) return false;
                entry.count = active;
                for (std::size_t slot = 0; slot < active; ++slot) {
                    const auto length = Word(row + 4 + slot * 4);
                    if (!length || length > plain.size() - offset || plain[offset + length - 1] != 0)
                        return false;
                    entry.messages[slot].assign(reinterpret_cast<const char*>(plain.data() + offset), length - 1);
                    offset += length;
                }
            }
            if (offset != plain.size()) return false;
            monsters.swap(next);
            return true;
        });
    }

    void Clear()
    {
        std::vector<RF455WorldEventMessage>().swap(events);
        std::vector<RF455WorldMonsterMessages>().swap(monsters);
    }

    const RF455WorldEventMessage* EventByCode(const char* code) const
    {
        if (!code || !*code) return nullptr;
        std::size_t length = 0;
        while (length < 8 && code[length]) ++length;
        if (length == 8) return nullptr;
        // Pinned RVA 0x1FD1A0 chooses the first case-insensitive match.
        for (const auto& entry : events)
            if (EqualCode(code, entry.code)) return &entry;
        return nullptr;
    }

    const RF455WorldMonsterMessages* MonsterByRow(std::size_t row) const
    {
        return row < monsters.size() ? &monsters[row] : nullptr;
    }

    const char* MonsterMessage(std::size_t row, std::size_t slot) const
    {
        const auto* entry = MonsterByRow(row);
        return entry ? entry->MessageAt(slot) : nullptr;
    }

private:
    std::vector<RF455WorldEventMessage> events;
    std::vector<RF455WorldMonsterMessages> monsters;

    static std::uint32_t Word(const unsigned char* data)
    {
        return static_cast<std::uint32_t>(data[0]) |
               (static_cast<std::uint32_t>(data[1]) << 8) |
               (static_cast<std::uint32_t>(data[2]) << 16) |
               (static_cast<std::uint32_t>(data[3]) << 24);
    }

    static unsigned char FoldAscii(unsigned char ch)
    {
        return ch >= 'A' && ch <= 'Z' ? static_cast<unsigned char>(ch + 'a' - 'A') : ch;
    }

    static bool EqualCode(const char* key, const char* stored)
    {
        while (*key && FoldAscii(*key) == FoldAscii(*stored)) {
            ++key;
            ++stored;
        }
        return *key == *stored;
    }

    template<class Consumer>
    static bool LoadTable(const char* path, std::uint32_t stride, Consumer consume)
    {
        try {
            return RF455_ReadEdfInput(path, [&](const unsigned char* envelope, std::size_t size) {
                std::vector<unsigned char> plain;
                if (!RF455_DecodeEdf(envelope, size, plain) || plain.size() < 8) return false;
                const auto count = Word(plain.data());
                if (Word(plain.data() + 4) != stride || count > (plain.size() - 8) / stride)
                    return false;
                return consume(plain, count);
            });
        } catch (const std::bad_alloc&) {
            return false;
        } catch (const std::length_error&) {
            return false;
        }
    }
};

#endif
