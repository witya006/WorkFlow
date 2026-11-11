#include "client455_normal_attack_result.h"

#include <array>
#include <cstdio>

int main()
{
    constexpr std::size_t Prefix = 11, TargetBytes = 14;
    std::array<char, Prefix + TargetBytes * 32> bytes{};
    bytes[0] = 15;
    const std::uint16_t noProjectile = 0xffff;
    std::memcpy(bytes.data() + 6, &noProjectile, sizeof noProjectile);
    bytes[8] = 1;
    bytes[9] = 1;
    bytes[10] = 32;
    bytes[11] = 1;
    const std::int32_t block = -2, largeDamage = 70000;
    const std::uint32_t serial = 0x000fc001, support = 0x00080042;
    std::memcpy(bytes.data() + Prefix + 1, &serial, sizeof serial);
    std::memcpy(bytes.data() + Prefix + 5, &block, sizeof block);
    bytes[Prefix + 9] = 1;
    std::memcpy(bytes.data() + Prefix + 10, &support, sizeof support);
    std::memcpy(bytes.data() + Prefix + TargetBytes * 31 + 5, &largeDamage, sizeof largeDamage);

    RF455NormalAttackResult packet{};
    if (!RF455_ReadNormalAttackResult(bytes.data(), bytes.size(), packet) ||
        packet.attackerType != 15 || packet.projectile != 0xffff || !packet.critical ||
        !packet.support || packet.targetCount != 32 || packet.targets[0].serial != serial ||
        packet.targets[0].type != 1 || packet.targets[0].damage != block ||
        packet.targets[0].support != 1 || packet.targets[0].supportCode != support ||
        packet.targets[31].damage != largeDamage) return 1;

    if (RF455_ReadNormalAttackResult(nullptr, bytes.size(), packet) ||
        RF455_ReadNormalAttackResult(bytes.data(), Prefix - 1, packet) ||
        RF455_ReadNormalAttackResult(bytes.data(), bytes.size() - 1, packet)) return 2;
    bytes[10] = 33;
    if (RF455_ReadNormalAttackResult(bytes.data(), bytes.size(), packet) || packet.targetCount != 32)
        return 3;
    bytes[10] = 0;
    if (!RF455_ReadNormalAttackResult(bytes.data(), Prefix, packet) || packet.targetCount ||
        RF455_ReadNormalAttackResult(bytes.data(), Prefix + 1, packet)) return 4;
    std::puts("PASS: 5/7 zero and 32 targets, signed damage, support fields and size rejection");
}
