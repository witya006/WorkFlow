#pragma once

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>

enum class RF455DownloadStep : std::uint8_t { Idle, Base, Inventory, Force, Mastery };

// Fixed-width x86 wire records from the 455 initial-download handlers.
#pragma pack(push, 1)
struct RF455ItemModifiers {
    std::uint8_t kind;
    std::uint32_t value;
    std::uint8_t timed;
    std::int64_t secondsRemaining;
};

struct RF455EquipmentEntry {
    std::uint8_t table;
    std::uint16_t index;
    std::uint32_t upgrade;
    RF455ItemModifiers modifiers;
};

struct RF455AccessoryEntry {
    std::uint8_t table;
    std::uint16_t index;
    std::uint16_t durability;
    std::int8_t slot;
    RF455ItemModifiers modifiers;
};

struct RF455BaseDownload {
    std::uint8_t result;
    std::uint16_t zoneIndex;
    std::uint32_t experienceMillionths;
    std::uint16_t classes[3];
    std::uint32_t hp, sp, fp;
    double rankingValues[3];
    std::uint32_t featureState;
    std::uint8_t featureMode, entryMode;
    std::uint16_t entryIndex;
    std::uint32_t maxHP, maxSP, maxFP;
    std::uint16_t mapIndex;
    float startPosition[3];
    RF455EquipmentEntry equipment[8];
    RF455AccessoryEntry accessories[7];
    RF455EquipmentEntry specialEquipment;
    std::uint8_t appearance;
    std::uint32_t featureFlags;
    std::uint8_t timeNotice, noticeHours, noticeMinutes, interfaceFlag;
    std::uint32_t maxSecondaryGauge, secondaryGauge;
    std::int8_t entryFlags[2];
};

struct RF455InventoryEntry {
    std::uint8_t table;
    std::uint16_t index;
    std::uint32_t countOrDurability;
    std::uint32_t animusProgressHigh;
    std::int8_t slot;
    std::uint32_t upgrade;
    RF455ItemModifiers modifiers;
};

struct RF455InventoryDownload {
    std::uint8_t result, bags, count;
    RF455InventoryEntry items[100];
};

struct RF455ForceEntry {
    std::uint16_t index;
    std::uint32_t mastery;
    std::uint8_t remaining[5];
};

struct RF455ForceDownload {
    std::uint8_t result, count;
    RF455ForceEntry items[255];
};
#pragma pack(pop)

static_assert(sizeof(RF455EquipmentEntry) == 21 && sizeof(RF455AccessoryEntry) == 20);
static_assert(sizeof(RF455BaseDownload) == 431 && offsetof(RF455BaseDownload, mapIndex) == 69 &&
              offsetof(RF455BaseDownload, equipment) == 83 && offsetof(RF455BaseDownload, accessories) == 251 &&
              offsetof(RF455BaseDownload, specialEquipment) == 391 && offsetof(RF455BaseDownload, maxSecondaryGauge) == 421);
static_assert(sizeof(RF455InventoryEntry) == 30 && offsetof(RF455InventoryEntry, slot) == 11 &&
              offsetof(RF455InventoryEntry, modifiers) == 16 && offsetof(RF455InventoryDownload, items) == 3);
static_assert(sizeof(RF455ForceEntry) == 11 && offsetof(RF455ForceDownload, items) == 2);

inline bool RF455_ReadBaseDownload(const void* data, std::size_t size, RF455BaseDownload& out)
{
    if (!data || size == 0) return false;
    RF455BaseDownload next{};
    const auto status = *static_cast<const std::uint8_t*>(data);
    if (status && size == 1) {
        next.result = status;
    } else {
        if (size != sizeof next) return false;
        std::memcpy(&next, data, sizeof next);
        if (!status) {
            for (auto coordinate : next.startPosition)
                if (!std::isfinite(coordinate)) return false;
        }
    }
    out = next;
    return true;
}

inline bool RF455_ReadInventoryDownload(const void* data, std::size_t size, RF455InventoryDownload& out)
{
    if (!data || size == 0) return false;
    const auto* bytes = static_cast<const std::uint8_t*>(data);
    if (bytes[0] ? size != 1 : size < 3 || bytes[1] > 5 || bytes[2] > 100 ||
                    size != 3 + sizeof(RF455InventoryEntry) * bytes[2]) return false;
    out = {};
    std::memcpy(&out, data, size);
    return true;
}

inline bool RF455_ReadForceDownload(const void* data, std::size_t size, RF455ForceDownload& out)
{
    if (!data || size == 0) return false;
    const auto* bytes = static_cast<const std::uint8_t*>(data);
    if (bytes[0] ? size != 1 : size < 2 || size != 2 + sizeof(RF455ForceEntry) * bytes[1]) return false;
    out = {};
    std::memcpy(&out, data, size);
    return true;
}
