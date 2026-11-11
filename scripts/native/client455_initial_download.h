#pragma once

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>

enum class RF455DownloadStep : std::uint8_t { Idle, Base, Inventory, Force, Mastery, Quest, Special, Miner, Linker };

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

struct RF455MasteryDownload {
    std::uint8_t result;
    std::uint32_t weapon[2], defence, shield;
    std::uint32_t skill[48], force[24], crafting[3], racial;
    std::uint8_t oreCount;
    std::uint16_t oreIndex[20];
    std::uint8_t oreQuantity[20];
};

struct RF455QuestDownloadEntry {
    std::uint8_t slot, type;
    std::uint16_t index;
    std::uint16_t progress[3];
    std::uint32_t elapsedSeconds;
};

struct RF455QuestDownload {
    std::uint8_t result, count;
    RF455QuestDownloadEntry quests[255];
};

struct RF455UnitBullet {
    std::uint16_t index, remaining;
};

struct RF455UnitDownloadEntry {
    std::uint8_t slot, unitFlags, frame;
    std::uint32_t durability;
    std::uint8_t parts[6];
    RF455UnitBullet ammunition[2], spare[8];
    std::int32_t tractionDebt;
    std::uint8_t tail[10];
};

struct RF455AnimusDownloadEntry {
    std::uint8_t index;
    std::uint64_t experience;
    std::uint32_t hp;
    std::uint8_t tail[5];
};

struct RF455MinerDownloadEntry {
    std::uint8_t slot, table;
    std::uint16_t index;
    std::uint8_t quantity;
};
#pragma pack(pop)

static_assert(sizeof(RF455EquipmentEntry) == 21 && sizeof(RF455AccessoryEntry) == 20);
static_assert(sizeof(RF455BaseDownload) == 431 && offsetof(RF455BaseDownload, mapIndex) == 69 &&
              offsetof(RF455BaseDownload, equipment) == 83 && offsetof(RF455BaseDownload, accessories) == 251 &&
              offsetof(RF455BaseDownload, specialEquipment) == 391 && offsetof(RF455BaseDownload, maxSecondaryGauge) == 421);
static_assert(sizeof(RF455InventoryEntry) == 30 && offsetof(RF455InventoryEntry, slot) == 11 &&
              offsetof(RF455InventoryEntry, modifiers) == 16 && offsetof(RF455InventoryDownload, items) == 3);
static_assert(sizeof(RF455ForceEntry) == 11 && offsetof(RF455ForceDownload, items) == 2);
static_assert(sizeof(RF455MasteryDownload) == 382 && offsetof(RF455MasteryDownload, skill) == 17 &&
              offsetof(RF455MasteryDownload, force) == 209 && offsetof(RF455MasteryDownload, oreCount) == 321 &&
              offsetof(RF455MasteryDownload, oreIndex) == 322 && offsetof(RF455MasteryDownload, oreQuantity) == 362);
static_assert(sizeof(RF455QuestDownloadEntry) == 14 && offsetof(RF455QuestDownload, quests) == 2);
static_assert(sizeof(RF455UnitDownloadEntry) == 67 && offsetof(RF455UnitDownloadEntry, spare) == 21 &&
              offsetof(RF455UnitDownloadEntry, tractionDebt) == 53);
static_assert(sizeof(RF455AnimusDownloadEntry) == 18 && offsetof(RF455AnimusDownloadEntry, hp) == 9);
static_assert(sizeof(RF455MinerDownloadEntry) == 5);

template <class Entry>
inline bool RF455_MatchDownloadList(const char* bytes, std::size_t size, std::size_t prefix)
{
    if (!bytes || !prefix || size < prefix) return false;
    const auto count = static_cast<std::uint8_t>(bytes[prefix - 1]);
    return size == prefix + count * sizeof(Entry);
}

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

inline bool RF455_ReadMasteryDownload(const void* data, std::size_t size, RF455MasteryDownload& out)
{
    if (!data || size == 0) return false;
    const auto* bytes = static_cast<const std::uint8_t*>(data);
    constexpr std::size_t countOffset = offsetof(RF455MasteryDownload, oreCount);
    constexpr std::size_t quantityOffset = offsetof(RF455MasteryDownload, oreQuantity);
    if (bytes[0]) {
        if (size != 1) return false;
    } else {
        if (size <= countOffset || size > sizeof out) return false;
        const unsigned ores = bytes[countOffset];
        if (ores > 20 || (ores && size < quantityOffset + ores)) return false;
    }
    out = {};
    std::memcpy(&out, data, size);
    return true;
}

inline bool RF455_ReadQuestDownload(const void* data, std::size_t size, RF455QuestDownload& out)
{
    if (!data || size == 0) return false;
    const auto* bytes = static_cast<const std::uint8_t*>(data);
    if (bytes[0] ? size != 1 : size < 2 || size != 2 + sizeof(RF455QuestDownloadEntry) * bytes[1]) return false;
    out = {};
    std::memcpy(&out, data, size);
    return true;
}
