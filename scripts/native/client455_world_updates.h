#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>

// Selected fixed-width little-endian x86 records from the 455 world dispatcher.
#pragma pack(push, 1)
struct RF455MonsterSpawn {
    std::uint16_t record, zoneIndex;
    std::uint32_t serial;
    std::int16_t position[3];
    std::uint8_t direction;
    std::uint16_t flags;
};

struct RF455MonsterMove {
    std::uint32_t serial;
    std::int16_t current[3];
    std::int16_t targetXZ[2];
};

struct RF455PlayerStatusUpdate {
    std::uint32_t serial;
    std::uint64_t flags;
};
#pragma pack(pop)

static_assert(sizeof(RF455MonsterSpawn) == 17 && offsetof(RF455MonsterSpawn, flags) == 15);
static_assert(sizeof(RF455MonsterMove) == 14 && offsetof(RF455MonsterMove, targetXZ) == 10);
static_assert(sizeof(RF455PlayerStatusUpdate) == 12 && offsetof(RF455PlayerStatusUpdate, flags) == 4);

template<class Record>
bool RF455_ReadWorldRecord(const char* bytes, std::size_t size, Record& record) {
    if (!bytes || size != sizeof(record)) return false;
    std::memcpy(&record, bytes, sizeof(record));
    return true;
}
