#include "client455_initial_download.h"
#include "client455_world_updates.h"
#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/manager/cgrounditemmanager.h"
#include "network/cnetworkmgr.h"

#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <memory>

namespace {
void check(bool condition, const char* name)
{
    if (condition) return;
    std::fprintf(stderr, "%s\n", name);
    std::exit(1);
}

template <class T, class Byte, std::size_t Size>
void write(std::array<Byte, Size>& bytes, std::size_t offset, T value)
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

void store()
{
    std::array<char, 33> bytes{};
    RF455StoreDownload packet{};
    check(RF455_ReadStoreDownload(bytes.data(), 1, packet) && packet.count == 0, "empty store list");
    bytes[0] = 2;
    write(bytes, 17, std::uint32_t{0x12345678});
    write(bytes, 21, -20.5f);
    write(bytes, 29, 231.0f);
    check(RF455_ReadStoreDownload(bytes.data(), bytes.size(), packet) && packet.count == 2 &&
          packet.entries[1].index == 0x12345678 && packet.entries[1].position[0] == -20.5f &&
          packet.entries[1].position[2] == 231.0f, "store list layout");
    check(!RF455_ReadStoreDownload(bytes.data(), 32, packet), "truncated store list");
    write(bytes, 25, std::numeric_limits<float>::infinity());
    check(!RF455_ReadStoreDownload(bytes.data(), 33, packet) && packet.entries[1].position[1] == 0,
          "nonfinite store coordinates preserve previous state");
}

template<class Record, std::size_t Size>
Record readWorldFixture(const std::array<char, Size>& bytes) {
    Record record{};
    check(!RF455_ReadWorldRecord(bytes.data(), Size - 1, record), "short world record");
    check(!RF455_ReadWorldRecord(bytes.data(), Size + 1, record), "oversize world record");
    check(!RF455_ReadWorldRecord(nullptr, Size, record), "null world record");
    check(RF455_ReadWorldRecord(bytes.data(), Size, record), "valid world record");
    return record;
}

void worldUpdates() {
    std::array<char, 17> spawn{};
    write(spawn, 0, std::uint16_t{321});
    write(spawn, 2, std::uint16_t{42});
    write(spawn, 4, std::uint32_t{0x12345678});
    write(spawn, 8, std::int16_t{-4800});
    write(spawn, 12, std::int16_t{4200});
    write(spawn, 14, std::uint8_t{128});
    write(spawn, 15, std::uint16_t{0x8041});
    const auto actor = readWorldFixture<RF455MonsterSpawn>(spawn);
    check(actor.record == 321 && actor.zoneIndex == 42 && actor.serial == 0x12345678 &&
          actor.position[0] == -4800 && actor.position[2] == 4200 &&
          actor.direction == 128 && actor.flags == 0x8041, "monster spawn layout");

    std::array<char, 14> move{};
    write(move, 0, std::uint32_t{0x12345678});
    write(move, 6, std::int16_t{470});
    write(move, 10, std::int16_t{-4500});
    const auto motion = readWorldFixture<RF455MonsterMove>(move);
    check(motion.serial == actor.serial && motion.current[1] == 470 &&
          motion.targetXZ[0] == -4500, "monster movement layout");

    std::array<char, 12> status{};
    write(status, 0, std::uint32_t{0x87654321});
    write(status, 4, std::uint64_t{0x8000000000004000});
    const auto player = readWorldFixture<RF455PlayerStatusUpdate>(status);
    check(player.serial == 0x87654321 && player.flags == 0x8000000000004000,
          "64-bit player status layout");

    std::array<char, 8> refresh{};
    write(refresh, 0, std::uint8_t{1});
    write(refresh, 1, std::uint8_t{2});
    write(refresh, 2, std::uint16_t{0x89ab});
    write(refresh, 4, std::uint32_t{0xcdef1234});
    const auto object = readWorldFixture<RF455ObjectRefresh>(refresh);
    check(object.objectKind == 1 && object.objectType == 2 &&
          object.groundIndex == 0x89ab && object.serial == 0xcdef1234, "object refresh layout");
}

class PositionProbeNetwork : public CNetworkMgr {
public:
    using CNetworkMgr::PositionMsg_ObjectRefresh455;
};

void refreshOwners() {
    auto* previousManager = g_pCharacterMgr;
    auto* previousAvatar = g_pAvatar;
    auto manager = std::make_unique<CCharacterMgr>();
    manager->CreateAvatar();
    auto network = std::make_unique<PositionProbeNetwork>();

    constexpr DWORD monsterSerial = 0x12345678;
    constexpr DWORD parkedSerial = 0x89abcdef;
    constexpr WORD groundIndex = 4321;
    auto* monster = manager->AddMonster(monsterSerial);
    auto* parked = manager->AddUnit(parkedSerial);
    auto* ground = _GetGroundItemMgr()->AddItem();
    monster->SetIndex(monsterSerial);
    parked->SetCharTypeID(CTI_UNIT);
    parked->SetIndex(parkedSerial);
    ground->SetObjectTypeID(OTI_ITEM);
    ground->SetIndex(groundIndex);

    const RF455ObjectRefresh monsterUpdate{0, 1, groundIndex, monsterSerial};
    const auto* bytes = reinterpret_cast<const char*>(&monsterUpdate);
    check(!network->PositionMsg_ObjectRefresh455(bytes, sizeof monsterUpdate - 1) &&
          !monster->IsReceiveFixPositionMsg(), "malformed refresh leaves the monster untouched");
    const RF455ObjectRefresh missing{0, 1, groundIndex, 1};
    check(network->PositionMsg_ObjectRefresh455(reinterpret_cast<const char*>(&missing), sizeof missing) &&
          !monster->IsReceiveFixPositionMsg(), "unknown monster does not refresh a different owner");

    const auto apply = [&](const RF455ObjectRefresh& packet, CResObject& owner) {
        owner.SetReceiveFixPositionMsg(FALSE);
        const auto* position = owner.GetPosition();
        const std::array<float, 3> beforePosition{position[0], position[1], position[2]};
        const DWORD beforeTime = timeGetTime();
        check(network->PositionMsg_ObjectRefresh455(reinterpret_cast<const char*>(&packet), sizeof packet),
              "owner refresh is accepted");
        check(owner.IsReceiveFixPositionMsg() &&
              owner.GetReceiveFixPositionMsgTime() - beforeTime <= timeGetTime() - beforeTime,
              "owner refresh writes the current tick");
        check(std::equal(beforePosition.begin(), beforePosition.end(), owner.GetPosition()),
              "owner refresh leaves coordinates unchanged");
    };
    apply(monsterUpdate, *monster);
    apply({0, 8, groundIndex, parkedSerial}, *parked);
    apply({1, 2, groundIndex, parkedSerial}, *parked);
    apply({1, 0, groundIndex, monsterSerial}, *ground);

    _GetGroundItemMgr()->Clear();
    network.reset();
    manager.reset();
    g_pAvatar = previousAvatar;
    g_pCharacterMgr = previousManager;
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
    store();
    worldUpdates();
    refreshOwners();
    std::puts("{\"status\":\"PASS\",\"base_bytes\":431,\"inventory_stride\":30,\"force_stride\":11,"
              "\"mastery_minimum\":322,\"quest_stride\":14,\"unit_stride\":67,\"animus_stride\":18,\"miner_stride\":5,"
              "\"linker_bytes\":157,\"macro_bytes\":954,\"shout_bytes\":650,\"store_stride\":16,"
              "\"world_spawn_bytes\":17,\"world_move_bytes\":14,\"world_status_bytes\":12,\"world_refresh_bytes\":8,"
              "\"refresh_owner_routes\":4,\"empty_and_error_results\":true,\"bad_sizes_rejected\":true}");
}
