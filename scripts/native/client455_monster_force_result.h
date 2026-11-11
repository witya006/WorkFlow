#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

struct RF455MonsterForceTarget {
    std::uint32_t serial;
    std::int32_t damage;
    std::uint8_t type;
};

struct RF455MonsterForceResult {
    static constexpr std::size_t maxTargets = 32;
    std::uint32_t serial;
    std::uint8_t actorType, index, level, critical, targetCount;
    std::array<RF455MonsterForceTarget, maxTargets> targets;
};

// 5/9 has a 15-byte prefix followed by 14 bytes per victim.
inline bool RF455_ReadMonsterForceResult(const char* bytes, std::size_t size,
                                         RF455MonsterForceResult& result) {
    constexpr std::size_t prefix = 15, victimStride = 14;
    if (!bytes || size < prefix) return false;
    const auto* data = reinterpret_cast<const std::uint8_t*>(bytes);
    const auto victims = data[14];
    RF455MonsterForceResult packet{};
    if (victims > packet.targets.size() || size != prefix + victims * victimStride) return false;
    packet.actorType = data[0];
    std::memcpy(&packet.serial, data + 1, sizeof packet.serial);
    packet.index = data[5];
    packet.level = data[6];
    packet.critical = data[12];
    packet.targetCount = victims;
    for (std::size_t i = 0; i < victims; ++i) {
        const auto* entry = data + prefix + i * victimStride;
        auto& target = packet.targets[i];
        target.type = entry[0];
        std::memcpy(&target.serial, entry + 1, sizeof target.serial);
        std::memcpy(&target.damage, entry + 5, sizeof target.damage);
    }
    result = packet;
    return true;
}
