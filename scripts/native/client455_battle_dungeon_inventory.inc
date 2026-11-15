#include "client455_battle_dungeon_panel.h"
#include "client455_item_payloads.h"

namespace {
constexpr DWORD NoBattleDungeonKey455 = 0xffffffffu;

RF455BasicItem* BattleDungeonKey455(CBoardObject* object)
{
    auto* item = object ? dynamic_cast<RF455BasicItem*>(object->GetItem455()) : nullptr;
    if (!item || item->header().kind != 0 || item->header().flag21 ||
        item->header().serial == NoBattleDungeonKey455 || !item->quantity455()) return nullptr;
    const auto row = item->rawMetadata();
    if (!row.data || row.size <= 152 || (row.data[88] != 23 && row.data[88] != 29)) return nullptr;
    return item;
}

bool HasBattleDungeonGateSpace455(CLevel& level, const float* position)
{
    // RVA 0x3E24D0 probes eight horizontal segments from 15 units above the avatar.
    constexpr float offsets[][2] = {
        {70, 0}, {70, 70}, {0, 70}, {-70, 70}, {-70, 0}, {-70, -70}, {0, -70}, {70, -70},
    };
    Vector3f origin = {position[0], position[1] + 15.0f, position[2]};
    for (const auto& offset : offsets) {
        Vector3f endpoint = {origin[0] + offset[0], origin[1], origin[2] + offset[1]};
        if (level.mBsp->IsCollisionFace(origin, endpoint)) return false;
    }
    return true;
}

BOOL OpenBattleDungeon455(DWORD serial, bool requiresParty)
{
    auto* land = _GetLand();
    auto* avatar = _GetAvatar();
    auto* network = _GetNetworkMgr();
    auto* party = _GetPartyBoard();
    auto* level = land ? land->GetLevel() : nullptr;
    if (!avatar || !network || !level || !level->IsLoadedBsp() || !level->mBsp) return FALSE;

    unsigned error = 0;
    const auto map = land->GetMapIndex();
    if (requiresParty && (!party || !party->IsPartyMember(avatar->GetIndex()))) error = 0x77;
    else if (map == 14 || map == 16 || map == 23 || _GetDungeonInfo()->IsInDungeon()) error = 0x164;
    else if (map == 15) error = 0x6f3;
    else if (map == 0xff) return FALSE;
    else if (!HasBattleDungeonGateSpace455(*level, avatar->GetPosition())) error = 0x8bb;
    if (error) {
        RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(error));
        return FALSE;
    }

    auto* dungeon = static_cast<CNetMsgProcessor_Dungeon*>(network->GetNetMsgProcessor(NMP_DUNGEON));
    return dungeon && dungeon->RequestBattleDungeonOpen455(serial);
}
}

BOOL CInventoryBoard::StageBattleDungeonKey455(BYTE pack, BYTE slot)
{
    if (m_dungeonGateKey455 != NoBattleDungeonKey455) return FALSE;
    auto* object = GetObject(pack, slot);
    auto* item = BattleDungeonKey455(object);
    if (!item || object->IsUsing()) return FALSE;

    m_dungeonGatePack455 = pack;
    m_dungeonGateSlot455 = slot;
    m_dungeonGateKey455 = item->header().serial;
    object->SetUsingState(TRUE);
    if (auto* icon = object->GetIcon()) icon->SetLock455(TRUE);
    m_dungeonGatePanel455.Bind455(this,
        [](void* owner) { static_cast<CInventoryBoard*>(owner)->ConfirmBattleDungeonKey455(); },
        [](void* owner) {
            auto* board = static_cast<CInventoryBoard*>(owner);
            if (!board->m_dungeonGatePending455) board->CancelBattleDungeonKey455();
        });
    m_dungeonGatePanel455.Present455(RF455_ReadBasicIconMetadata(*item), m_uiInventoryWindow);
    return TRUE;
}

void CInventoryBoard::ConfirmBattleDungeonKey455()
{
    if (m_dungeonGateKey455 == NoBattleDungeonKey455 || m_dungeonGatePending455) return;
    auto* object = GetObject(m_dungeonGatePack455, m_dungeonGateSlot455);
    auto* item = BattleDungeonKey455(object);
    if (!item || item->header().serial != m_dungeonGateKey455 || !object->IsUsing()) {
        CancelBattleDungeonKey455();
        return;
    }
    const auto row = item->rawMetadata();
    if (OpenBattleDungeon455(m_dungeonGateKey455, row.data[152] == 1)) {
        m_dungeonGatePending455 = true;
        m_dungeonGatePanel455.SetPending455(true);
    }
}

void CInventoryBoard::CompleteBattleDungeonKey455(bool accepted)
{
    if (!m_dungeonGatePending455) return;
    m_dungeonGatePending455 = false;
    if (!accepted) {
        m_dungeonGatePanel455.SetPending455(false);
        return;
    }

    const BYTE pack = m_dungeonGatePack455, slot = m_dungeonGateSlot455;
    auto* object = GetObject(pack, slot);
    auto* item = BattleDungeonKey455(object);
    const bool consume = item && item->header().serial == m_dungeonGateKey455 && object->IsUsing();
    CancelBattleDungeonKey455();
    if (consume) Remove(pack, slot, 1);
}

void CInventoryBoard::CancelBattleDungeonKey455()
{
    if (m_dungeonGateKey455 != NoBattleDungeonKey455) {
        auto* object = GetObject(m_dungeonGatePack455, m_dungeonGateSlot455);
        auto* item = object ? object->GetItem455() : nullptr;
        if (item && item->header().serial == m_dungeonGateKey455) {
            object->SetUsingState(FALSE);
            object->RefreshLock455();
        }
    }
    m_dungeonGateKey455 = NoBattleDungeonKey455;
    m_dungeonGatePack455 = m_dungeonGateSlot455 = 0xff;
    m_dungeonGatePending455 = false;
    m_dungeonGatePanel455.Hide455();
}
