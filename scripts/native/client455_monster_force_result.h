#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>

struct RF455MonsterForceResult {
    std::uint32_t serial, targetSerial;
    std::uint8_t actorType, index, level, targetType;
    bool hasTarget;
};

// 5/9 has a 15-byte prefix followed by 14 bytes per victim. The
// attacker animation uses the first victim to choose its facing.
inline bool RF455_ReadMonsterForceResult(const char* bytes, std::size_t size,
                                         RF455MonsterForceResult& result) {
    constexpr std::size_t prefix = 15, victimStride = 14, maxVictims = 32;
    if (!bytes || size < prefix) return false;
    const auto* data = reinterpret_cast<const std::uint8_t*>(bytes);
    const auto victims = data[14];
    if (victims > maxVictims || size != prefix + victims * victimStride) return false;

    RF455MonsterForceResult packet{};
    packet.actorType = data[0];
    std::memcpy(&packet.serial, data + 1, sizeof packet.serial);
    packet.index = data[5];
    packet.level = data[6];
    packet.hasTarget = victims != 0;
    if (packet.hasTarget) {
        packet.targetType = data[prefix];
        std::memcpy(&packet.targetSerial, data + prefix + 1, sizeof packet.targetSerial);
    }
    result = packet;
    return true;
}
