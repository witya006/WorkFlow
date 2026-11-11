#include "client455_initial_download.h"

#include <array>
#include <cstdio>
#include <cstdlib>
#include <limits>

namespace {
void check(bool condition, const char* name)
{
    if (condition) return;
    std::fprintf(stderr, "%s\n", name);
    std::exit(1);
}

template <class T, std::size_t Size>
void write(std::array<std::uint8_t, Size>& bytes, std::size_t offset, T value)
{
    check(offset + sizeof value <= bytes.size(), "fixture write extent");
    std::memcpy(bytes.data() + offset, &value, sizeof value);
}

void base()
{
    std::array<std::uint8_t, 431> bytes{};
    write(bytes, 1, std::uint16_t{421});
    write(bytes, 3, std::uint32_t{431250});
    write(bytes, 7, std::uint16_t{11});
    write(bytes, 13, std::uint32_t{70000});
    write(bytes, 65, std::uint32_t{81000});
    write(bytes, 69, std::uint16_t{19});
    write(bytes, 71, -22.25f);
    write(bytes, 79, 333.5f);
    write(bytes, 83 + 21 * 7, std::uint8_t{7});
    write(bytes, 84 + 21 * 7, std::uint16_t{901});
    write(bytes, 251 + 20 * 6 + 5, std::int8_t{-1});
    write(bytes, 391, std::uint8_t{37});
    write(bytes, 421, std::uint32_t{90000});
    RF455BaseDownload decoded{};
    check(RF455_ReadBaseDownload(bytes.data(), bytes.size(), decoded), "431 byte base");
    check(decoded.zoneIndex == 421 && decoded.experienceMillionths == 431250 && decoded.classes[0] == 11 &&
          decoded.hp == 70000 && decoded.maxFP == 81000 && decoded.mapIndex == 19 &&
          decoded.startPosition[0] == -22.25f && decoded.startPosition[2] == 333.5f, "base core fields");
    check(decoded.equipment[7].table == 7 && decoded.equipment[7].index == 901 &&
          decoded.accessories[6].slot == -1 && decoded.specialEquipment.table == 37 &&
          decoded.maxSecondaryGauge == 90000, "base equipment and tail fields");
    check(!RF455_ReadBaseDownload(bytes.data(), bytes.size() - 1, decoded) &&
          !RF455_ReadBaseDownload(bytes.data(), bytes.size() + 1, decoded) &&
          decoded.mapIndex == 19, "base sizes and stable output");
    write(bytes, 71, std::numeric_limits<float>::infinity());
    check(!RF455_ReadBaseDownload(bytes.data(), bytes.size(), decoded), "nonfinite base position");
    bytes[0] = 3;
    check(RF455_ReadBaseDownload(bytes.data(), 1, decoded) && decoded.result == 3, "base failure result");
}

void inventory()
{
    std::array<std::uint8_t, 3003> bytes{};
    bytes[1] = 5;
    bytes[2] = 100;
    const std::size_t item = 3 + 99 * 30;
    write(bytes, item, std::uint8_t{24});
    write(bytes, item + 1, std::uint16_t{123});
    write(bytes, item + 3, std::uint32_t{678});
    write(bytes, item + 7, std::uint32_t{1});
    write(bytes, item + 11, std::int8_t{99});
    write(bytes, item + 12, std::uint32_t{0x12345678});
    write(bytes, item + 21, std::uint8_t{1});
    write(bytes, item + 22, std::int64_t{3600});
    RF455InventoryDownload decoded{};
    check(RF455_ReadInventoryDownload(bytes.data(), bytes.size(), decoded), "100 inventory records");
    const auto& last = decoded.items[99];
    check(last.table == 24 && last.index == 123 && last.countOrDurability == 678 && last.animusProgressHigh == 1 &&
          last.slot == 99 && last.upgrade == 0x12345678 && last.modifiers.timed && last.modifiers.secondsRemaining == 3600,
          "last inventory record offsets");
    check(!RF455_ReadInventoryDownload(bytes.data(), bytes.size() - 1, decoded) && decoded.count == 100,
          "truncated inventory preserves output");
    bytes[2] = 101;
    check(!RF455_ReadInventoryDownload(bytes.data(), bytes.size(), decoded), "inventory record cap");
    bytes[2] = 0;
    bytes[1] = 6;
    check(!RF455_ReadInventoryDownload(bytes.data(), 3, decoded), "inventory bag cap");
    bytes[1] = 0;
    check(RF455_ReadInventoryDownload(bytes.data(), 3, decoded) && !decoded.count, "empty inventory");
    bytes[0] = 8;
    check(RF455_ReadInventoryDownload(bytes.data(), 1, decoded) && decoded.result == 8, "inventory failure result");
}

void force()
{
    std::array<std::uint8_t, 24> bytes{};
    bytes[1] = 2;
    write(bytes, 2, std::uint16_t{513});
    write(bytes, 15, std::uint32_t{600000});
    RF455ForceDownload decoded{};
    check(RF455_ReadForceDownload(bytes.data(), bytes.size(), decoded) && decoded.items[0].index == 513 &&
          decoded.items[1].mastery == 600000, "11 byte Force stride");
    check(!RF455_ReadForceDownload(bytes.data(), 23, decoded) && decoded.count == 2, "truncated Force result");
    bytes[1] = 0;
    check(RF455_ReadForceDownload(bytes.data(), 2, decoded) && !decoded.count, "empty Force result");
    bytes[0] = 9;
    check(RF455_ReadForceDownload(bytes.data(), 1, decoded) && decoded.result == 9, "Force failure result");
}
}

int main()
{
    base();
    inventory();
    force();
    std::puts("{\"status\":\"PASS\",\"base_bytes\":431,\"inventory_stride\":30,\"force_stride\":11,"
              "\"empty_and_error_results\":true,\"bad_sizes_rejected\":true}");
}
