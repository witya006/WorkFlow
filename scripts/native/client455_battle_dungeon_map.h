#ifndef RF455_BATTLE_DUNGEON_MAP_H
#define RF455_BATTLE_DUNGEON_MAP_H

#include <array>
#include <cstddef>
#include <cstdint>

inline bool RF455_IsBattleDungeonPortal455(const char* name, unsigned raceSex)
{
    if (!name || raceSex >= 5) return false;
    // RVA 0x0F6820 searches for the race marker. Accept lowercase names from Map.edf as well.
    static const char* const markers[] = {"dp_bdbl01", "dp_bdcr01", "dp_bdac01"};
    const char* marker = markers[raceSex / 2];
    for (; *name; ++name) {
        const char* input = name;
        const char* expected = marker;
        for (; *input && *expected; ++input, ++expected) {
            const char ch = *input >= 'A' && *input <= 'Z' ? static_cast<char>(*input + ('a' - 'A')) : *input;
            if (ch != *expected) break;
        }
        if (!*expected) return true;
    }
    return false;
}

inline std::uint32_t RF455_BattleDungeonGateEffectId455(unsigned raceSex)
{
    return raceSex < 5 ? 0x50ffff43u + raceSex / 2 : 0;
}

struct RF455BattleDungeonGate {
    std::uint16_t word = 0xffffu;
    std::uint32_t serial = 0xffffffffu;
};

inline bool RF455_IsBattleDungeonGateValid455(const RF455BattleDungeonGate& gate)
{
    return gate.word != 0xffffu && gate.serial != 0xffffffffu;
}

inline bool RF455_ReadBattleDungeonGate455(std::uint8_t message, const char* bytes, std::size_t size,
                                         std::uint8_t& status, RF455BattleDungeonGate& out)
{
    if ((message != 104 && message != 202) || !bytes || !size) return false;
    const auto* data = reinterpret_cast<const unsigned char*>(bytes);
    const auto result = message == 202 ? data[0] : 0u;
    if (result) {
        status = static_cast<std::uint8_t>(result);
        return true;
    }
    const auto offset = message == 202 ? 1u : 2u;
    if (size < offset + 6) return false;
    RF455BattleDungeonGate pair;
    pair.word = static_cast<std::uint16_t>(data[offset] | (std::uint16_t(data[offset + 1]) << 8));
    pair.serial = std::uint32_t(data[offset + 2]) | (std::uint32_t(data[offset + 3]) << 8) |
        (std::uint32_t(data[offset + 4]) << 16) | (std::uint32_t(data[offset + 5]) << 24);
    status = 0;
    out = pair;
    return true;
}

inline std::array<unsigned char, 6> RF455_EncodeBattleDungeonEntry455(const RF455BattleDungeonGate& gate)
{
    return {{static_cast<unsigned char>(gate.word), static_cast<unsigned char>(gate.word >> 8),
             static_cast<unsigned char>(gate.serial), static_cast<unsigned char>(gate.serial >> 8),
             static_cast<unsigned char>(gate.serial >> 16), static_cast<unsigned char>(gate.serial >> 24)}};
}

inline std::array<unsigned char, 4> RF455_EncodeBattleDungeonOpen455(std::uint32_t serial)
{
    return {{static_cast<unsigned char>(serial), static_cast<unsigned char>(serial >> 8),
             static_cast<unsigned char>(serial >> 16), static_cast<unsigned char>(serial >> 24)}};
}

struct RF455BattleDungeonMap {
    std::uint8_t status = 0;
    std::uint16_t destination = 0;
    std::int16_t position[3]{};
};

inline bool RF455_ReadBattleDungeonMap455(std::uint8_t message, const char* bytes, std::size_t size,
                                         RF455BattleDungeonMap& out)
{
    if ((message != 204 && message != 208) || !bytes || !size) return false;
    const auto* data = reinterpret_cast<const unsigned char*>(bytes);
    RF455BattleDungeonMap reply;
    reply.status = data[0];
    if (!reply.status) {
        const bool entering = message == 204;
        if (size < (entering ? 12u : 9u)) return false;
        const auto readWord = [](const unsigned char* value) {
            return static_cast<std::uint16_t>(value[0] | (static_cast<unsigned>(value[1]) << 8));
        };
        // RVAs 0x182AD0 and 0x182C80 consume different map index widths.
        reply.destination = entering ? data[5] : readWord(data + 1);
        const auto* position = data + (entering ? 6 : 3);
        for (unsigned axis = 0; axis < 3; ++axis) {
            const auto word = readWord(position + axis * 2);
            const auto coordinate = word < 0x8000u ? static_cast<std::int32_t>(word) :
                                                     static_cast<std::int32_t>(word) - 0x10000;
            reply.position[axis] = static_cast<std::int16_t>(coordinate);
        }
    }
    out = reply;
    return true;
}

inline unsigned RF455_BattleDungeonEntryRefusal455(std::uint8_t status)
{
    if (status >= 1 && status <= 10) return 0x23d + status;
    if (status >= 14 && status <= 18) return 0x83f + status - 14;
    switch (status) {
    case 11: return 0x83d;
    case 12: return 0x83e;
    case 13: case 28: case 100: return 0xf65;
    case 19: return 0x907;
    case 20: return 0x9ab;
    case 29: return 0xf66;
    default: return 0x248;
    }
}

#endif
