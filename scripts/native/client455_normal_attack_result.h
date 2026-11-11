#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

struct RF455NormalAttackTarget {
    std::uint32_t serial;
    std::int32_t damage;
    std::uint32_t supportCode;
    std::uint8_t type, support;
};

struct RF455NormalAttackResult {
    std::array<RF455NormalAttackTarget, 32> targets;
    std::uint32_t attackerSerial;
    std::uint16_t projectile;
    std::uint8_t attackerType, attackPart, critical, support, targetCount;
};

// RVA 0x1a4a10, group 5 / opcode 7.
inline bool RF455_ReadNormalAttackResult(const char* bytes, std::size_t size, RF455NormalAttackResult& out)
{
    constexpr std::size_t Prefix = 11, TargetBytes = 14;
    if (!bytes || size < Prefix) return false;
    const auto* data = reinterpret_cast<const std::uint8_t*>(bytes);
    RF455NormalAttackResult packet{};
    packet.targetCount = data[10];
    if (packet.targetCount > packet.targets.size() || size != Prefix + TargetBytes * packet.targetCount)
        return false;
    packet.attackerType = data[0];
    std::memcpy(&packet.attackerSerial, data + 1, 4);
    packet.attackPart = data[5];
    std::memcpy(&packet.projectile, data + 6, 2);
    packet.critical = data[8];
    packet.support = data[9];
    for (unsigned i = 0; i < packet.targetCount; ++i) {
        const auto* wire = data + Prefix + i * TargetBytes;
        auto& target = packet.targets[i];
        target.type = wire[0];
        std::memcpy(&target.serial, wire + 1, 4);
        std::memcpy(&target.damage, wire + 5, 4);
        target.support = wire[9];
        std::memcpy(&target.supportCode, wire + 10, 4);
    }
    out = packet;
    return true;
}

// 455 5/13, 5/14 and 5/15 carry one target without a projectile field.
inline bool RF455_ReadCreatureAttack(const char* bytes, std::size_t size, std::uint8_t attackerType,
                                    RF455NormalAttackResult& out)
{
    if (!bytes || size != 15) return false;
    const auto* data = reinterpret_cast<const std::uint8_t*>(bytes);
    RF455NormalAttackResult packet{};
    packet.attackerType = attackerType;
    packet.projectile = 0xffff;
    packet.targetCount = 1;
    std::memcpy(&packet.attackerSerial, data, sizeof packet.attackerSerial);
    packet.attackPart = data[4];
    packet.critical = data[5];
    auto& target = packet.targets.front();
    target.type = data[6];
    std::memcpy(&target.serial, data + 7, sizeof target.serial);
    std::memcpy(&target.damage, data + 11, sizeof target.damage);
    out = packet;
    return true;
}
