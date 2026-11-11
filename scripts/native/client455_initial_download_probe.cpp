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

void mastery()
{
    std::array<std::uint8_t, 382> bytes{};
    write(bytes, 1, std::uint32_t{101});
    write(bytes, 9, std::uint32_t{202});
    write(bytes, 13, std::uint32_t{303});
    write(bytes, 17 + 47 * 4, std::uint32_t{404});
    write(bytes, 209 + 23 * 4, std::uint32_t{505});
    write(bytes, 313, std::uint32_t{606});
    write(bytes, 317, std::uint32_t{707});
    RF455MasteryDownload decoded{};
    check(RF455_ReadMasteryDownload(bytes.data(), 322, decoded) && decoded.oreCount == 0 &&
          decoded.weapon[0] == 101 && decoded.defence == 202 && decoded.shield == 303 &&
          decoded.skill[47] == 404 && decoded.force[23] == 505 && decoded.crafting[2] == 606 &&
          decoded.racial == 707, "mastery fields and empty ore tail");
    bytes[321] = 20;
    write(bytes, 360, std::uint16_t{0x0123});
    bytes[381] = 8;
    check(RF455_ReadMasteryDownload(bytes.data(), bytes.size(), decoded) && decoded.oreIndex[19] == 0x0123 &&
          decoded.oreQuantity[19] == 8, "split ore arrays");
    check(!RF455_ReadMasteryDownload(bytes.data(), 381, decoded) && decoded.oreCount == 20,
          "truncated ore quantity preserves output");
    bytes[321] = 21;
    check(!RF455_ReadMasteryDownload(bytes.data(), bytes.size(), decoded), "ore count limit");
    bytes[0] = 8;
    check(RF455_ReadMasteryDownload(bytes.data(), 1, decoded) && decoded.result == 8, "mastery failure result");
}

void quests()
{
    std::array<std::uint8_t, 30> bytes{};
    bytes[1] = 2;
    bytes[16] = 7;
    bytes[17] = 1;
    write(bytes, 18, std::uint16_t{271});
    write(bytes, 24, std::uint16_t{91});
    write(bytes, 26, std::uint32_t{832});
    RF455QuestDownload decoded{};
    check(RF455_ReadQuestDownload(bytes.data(), bytes.size(), decoded) && decoded.count == 2 &&
          decoded.quests[1].slot == 7 && decoded.quests[1].type == 1 && decoded.quests[1].index == 271 &&
          decoded.quests[1].progress[2] == 91 && decoded.quests[1].elapsedSeconds == 832, "14-byte quest record");
    check(!RF455_ReadQuestDownload(bytes.data(), 29, decoded) && decoded.count == 2, "truncated quest record");
    bytes[1] = 0;
    check(RF455_ReadQuestDownload(bytes.data(), 2, decoded) && !decoded.count, "empty quest list");
    bytes[0] = 9;
    check(RF455_ReadQuestDownload(bytes.data(), 1, decoded) && decoded.result == 9, "quest failure result");
}

void specialAndMiner()
{
    std::array<char, 68> bytes{};
    check(RF455_MatchDownloadList<RF455UnitDownloadEntry>(bytes.data(), 1, 1), "empty unit list");
    bytes[0] = 1;
    check(RF455_MatchDownloadList<RF455UnitDownloadEntry>(bytes.data(), 68, 1) &&
          !RF455_MatchDownloadList<RF455UnitDownloadEntry>(bytes.data(), 67, 1), "unit stride and truncation");
    check(RF455_MatchDownloadList<RF455AnimusDownloadEntry>(bytes.data(), 19, 1) &&
          !RF455_MatchDownloadList<RF455AnimusDownloadEntry>(bytes.data(), 20, 1), "Animus stride and extra bytes");
    bytes[1] = 1;
    check(RF455_MatchDownloadList<RF455MinerDownloadEntry>(bytes.data(), 7, 2) &&
          !RF455_MatchDownloadList<RF455MinerDownloadEntry>(bytes.data(), 1, 2) &&
          !RF455_MatchDownloadList<RF455MinerDownloadEntry>(bytes.data(), 7, 0), "miner prefix and stride");
}

void linker()
{
    std::array<std::uint8_t, 157> bytes{};
    write(bytes, 0, std::uint16_t{0xffff});
    write(bytes, 98, std::uint16_t{0x4abc});
    bytes[100] = 0xa4;
    write(bytes, 105, std::uint32_t{0x87654321});
    write(bytes, 133, std::uint32_t{0x12345678});
    write(bytes, 153, std::uint32_t{0xffffffff});
    RF455LinkerDownload decoded{};
    check(RF455_ReadLinkerDownload(bytes.data(), bytes.size(), decoded) && decoded.slots[0] == 0xffff &&
          decoded.slots[49] == 0x4abc && decoded.bankFlags == 0xa4 && decoded.windows[1] == 0x87654321 &&
          decoded.menu == 0x12345678 && decoded.menuEntries[4] == 0xffffffff, "Linker slots and saved window fields");
    check(!RF455_ReadLinkerDownload(bytes.data(), bytes.size() - 1, decoded) &&
          !RF455_ReadLinkerDownload(bytes.data(), bytes.size() + 1, decoded) && decoded.slots[49] == 0x4abc,
          "invalid Linker lengths preserve output");
}

void macroAndShout()
{
    std::array<std::uint8_t, 954> bytes{};
    write(bytes, 0, std::uint32_t{0x00070301});
    write(bytes, 8, std::uint32_t{0xffffffff});
    write(bytes, 20, std::uint32_t{0x12345678});
    write(bytes, 140, std::uint32_t{0x00020407});
    bytes[873] = 'M';
    bytes[953] = 'x';
    RF455MacroDownload macro{};
    check(RF455_ReadMacroDownload(bytes.data(), bytes.size(), macro) && macro.automatic[0].board == 1 &&
          macro.automatic[0].pack == 3 && macro.automatic[0].socket == 7 && macro.automatic[2].empty() &&
          macro.automaticSettings[2] == 0x12345678 && macro.actions[29].board == 7 &&
          macro.text[1][4][0] == 'M' && macro.text[1][4][80] == '\0', "macro references, settings and bounded text");
    check(!RF455_ReadMacroDownload(bytes.data(), 953, macro) && macro.text[1][4][0] == 'M',
          "truncated macro keeps previous value");

    bytes[585] = 'S';
    bytes[648] = '!';
    bytes[649] = 'x';
    RF455PatriarchShoutDownload shout{};
    check(RF455_ReadPatriarchShoutDownload(bytes.data(), 650, shout) && shout.text[9][0] == 'S' &&
          shout.text[9][63] == '!' && shout.text[9][64] == '\0', "shout stride and bounded text");
    check(!RF455_ReadPatriarchShoutDownload(bytes.data(), 651, shout) && shout.text[9][0] == 'S',
          "oversized shout keeps previous value");
}
}

int main()
{
    base();
    inventory();
    force();
    mastery();
    quests();
    specialAndMiner();
    linker();
    macroAndShout();
    std::puts("{\"status\":\"PASS\",\"base_bytes\":431,\"inventory_stride\":30,\"force_stride\":11,"
              "\"mastery_minimum\":322,\"quest_stride\":14,\"unit_stride\":67,\"animus_stride\":18,\"miner_stride\":5,"
              "\"linker_bytes\":157,\"macro_bytes\":954,\"shout_bytes\":650,"
              "\"empty_and_error_results\":true,\"bad_sizes_rejected\":true}");
}
