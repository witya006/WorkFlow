#include "client455_battle_dungeon_map.h"
#include "client455_language.h"
#include "client455_message_dispatch.h"
#include "client455_protocol_observation.h"
#include "addcodebyjang/cmagicscript.h"
#include "addcodebyjang/effectcore.h"
#include "character/avatar/cavatar_relationinfo.h"
#include "gameobject/board/itemboard/cinventoryboard.h"
#include "userinterface/gamewindow/etcwin/guimaploadingwindow.h"

void EP_DisconnectedFromServer();

bool CNetMsgProcessor_Dungeon::HasBattleDungeonGate455(CGroundItem* item) const
{
    return RF455_IsBattleDungeonGateValid455(m_battleDungeonGate455) &&
           (!item || (m_battleDungeonGate455.word == item->GetServerIndex() &&
                      m_battleDungeonGate455.serial == item->GetIndex()));
}

void CNetMsgProcessor_Dungeon::ClearBattleDungeonGate455()
{
    m_battleDungeonGate455 = {};
}

void CNetMsgProcessor_Dungeon::StartBattleDungeonGateEffect455()
{
    auto* avatar = _GetAvatar();
    auto* land = _GetLand();
    if (!HasBattleDungeonGate455(nullptr) || !avatar || !land) return;
    const auto* observer = avatar->GetObserverInfo();
    if (observer && observer->m_bIsObserver) return;
    const unsigned race = avatar->GetRace();
    const DWORD effectId = RF455_BattleDungeonGateEffectId455(race);
    if (!effectId) return;

    const BYTE mapIndex = land->GetMapIndex();
    const auto& catalog = land->MapData455();
    if (mapIndex == 0xff || !catalog.maps || mapIndex >= catalog.count) return;
    const auto& map = catalog.maps[mapIndex];
    if (!map.pPortalInfo) return;
    for (DWORD index = 0; index < map.byPortalNum; ++index) {
        const auto& portal = map.pPortalInfo[index];
        if (!portal.bIsMovable || !portal.byUsableRace[race] ||
            !RF455_IsBattleDungeonPortal455(portal.pName, race)) continue;
        if (!IsExistFromMagicSpt(effectId)) return;

        const auto* active = m_battleDungeonGateEffect455 ? GetMagicListFromID(m_battleDungeonGateEffect455) : nullptr;
        if (active && active->mMagicID == effectId && active->mState == _EF_STATE_ALWAYS_LIVE) return;
        StopBattleDungeonGateEffect455(0.f);

        Vector3f center;
        for (unsigned axis = 0; axis < 3; ++axis)
            center[axis] = (portal.vecMin[axis] + portal.vecMax[axis]) * 0.5f;
        m_battleDungeonGateEffect455 = StartMagicEffect(center, avatar->GetRotY(), effectId, nullptr, _EF_STATE_ALWAYS_LIVE);
        return;
    }
}

void CNetMsgProcessor_Dungeon::StopBattleDungeonGateEffect455(float delay)
{
    if (!m_battleDungeonGateEffect455) return;
    const auto* active = GetMagicListFromID(m_battleDungeonGateEffect455);
    if (!active) {
        m_battleDungeonGateEffect455 = 0;
        return;
    }
    if (delay > 0.f && active->mState == _EF_STATE_START_DISAPEAR) return;
    const BOOL scheduled = SetDisapearTimeMagicEffect(m_battleDungeonGateEffect455, delay);
    if (!scheduled || delay <= 0.f) m_battleDungeonGateEffect455 = 0;
}

void CNetMsgProcessor_Dungeon::CancelBattleDungeonEntry455()
{
    ClearBattleDungeonGate455();
    if (m_battleDungeonOpenPending455) {
        m_battleDungeonOpenPending455 = false;
        if (auto* inventory = _GetInventoryBoard()) inventory->CancelBattleDungeonKey455();
        if (auto* boards = _GetGBM()) boards->SetRequestProcessState(FALSE);
    }
    if (!m_battleDungeonEntryPending455) return;
    m_battleDungeonEntryPending455 = false;

    auto* avatar = _GetAvatar();
    auto* move = avatar ? avatar->GetMoveMapInfo() : nullptr;
    if (move && move->m_byMoveStep != MOVEMAP_INFO::MMS_NONE) return;
    if (auto* boards = _GetGBM()) boards->SetRequestProcessState(FALSE);
    if (move) {
        move->m_bIsMoved = FALSE;
        move->m_pEnterPortalInfo = move->m_pExitPortalInfo = nullptr;
    }
}

BOOL CNetMsgProcessor_Dungeon::RequestBattleDungeonOpen455(DWORD serial)
{
    auto* boards = _GetGBM();
    auto* network = _GetNetworkMgr();
    if (serial == static_cast<DWORD>(ID_INVALID) || !boards || !network || boards->IsRequestProcess() ||
        m_battleDungeonOpenPending455 || m_battleDungeonEntryPending455) return FALSE;

    // RVA 0x1828C0 sends only the item serial.
    BYTE type[] = {35, 201};
    auto payload = RF455_EncodeBattleDungeonOpen455(serial);
    if (!network->SendNetMessage(NST_GAME_SERVER, type, payload.data(), static_cast<int>(payload.size())))
        return FALSE;
    m_battleDungeonOpenPending455 = true;
    boards->SetRequestProcessState(TRUE);
    return TRUE;
}

BOOL CNetMsgProcessor_Dungeon::RequestBattleDungeonEntry455(CGroundItem* item)
{
    auto* boards = _GetGBM();
    auto* avatar = _GetAvatar();
    auto* move = avatar ? avatar->GetMoveMapInfo() : nullptr;
    auto* land = _GetLand();
    auto* network = _GetNetworkMgr();
    if (!HasBattleDungeonGate455(item) || m_battleDungeonEntryPending455 || m_battleDungeonOpenPending455 ||
        !network || !land || !boards ||
        boards->IsRequestProcess() ||
        !move || move->m_bIsMoved || move->m_byMoveStep != MOVEMAP_INFO::MMS_NONE) return FALSE;
    const BYTE source = land->GetMapIndex();
    const auto& catalog = land->MapData455();
    if (source == 0xff || !catalog.maps || source >= catalog.count) return FALSE;

    // RVA 0x182A00 sends only the staged gate pair.
    BYTE type[] = {35, 203};
    auto payload = RF455_EncodeBattleDungeonEntry455(m_battleDungeonGate455);
    if (!network->SendNetMessage(NST_GAME_SERVER, type, payload.data(), static_cast<int>(payload.size())))
        return FALSE;
    m_battleDungeonEntryPending455 = true;
    boards->SetRequestProcessState(TRUE);
    _GetDungeonInfo()->SetDungeonData(item);
    move->m_bIsMoved = TRUE;
    move->m_pEnterPortalInfo = move->m_pExitPortalInfo = nullptr;
    move->m_byEnterMapIndex = source;
    move->m_byExitMapIndex = 0xff;
    return TRUE;
}

bool CNetMsgProcessor_Dungeon::ReceiveBattleDungeonMap455(BYTE message, const char* bytes, std::size_t size)
{
    if (message == 102) {
        ClearBattleDungeonGate455();
        StopBattleDungeonGateEffect455(3.f);
        RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(0x9a9));
        return true;
    }
    if (message == 104 || message == 202) {
        std::uint8_t status;
        RF455BattleDungeonGate gate;
        if (!RF455_ReadBattleDungeonGate455(message, bytes, size, status, gate)) return false;
        if (message == 202) {
            if (m_battleDungeonOpenPending455) {
                m_battleDungeonOpenPending455 = false;
                if (auto* boards = _GetGBM()) boards->SetRequestProcessState(FALSE);
                if (auto* inventory = _GetInventoryBoard()) inventory->CompleteBattleDungeonKey455(status == 0);
            }
            const auto index = status ? RF455_BattleDungeonEntryRefusal455(status) : 0x9aa;
            RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(index));
        }
        if (!status) {
            m_battleDungeonGate455 = gate;
            if (RF455_IsBattleDungeonGateValid455(gate)) StartBattleDungeonGateEffect455();
            else StopBattleDungeonGateEffect455(0.f);
        }
        return true;
    }

    RF455BattleDungeonMap reply;
    if (!RF455_ReadBattleDungeonMap455(message, bytes, size, reply)) return false;

    const bool entering = message == 204;
    if (reply.status && !entering) return true;
    const bool pending = entering && m_battleDungeonEntryPending455;
    if (entering) {
        ClearBattleDungeonGate455();
        m_battleDungeonEntryPending455 = false;
    }
    auto* boards = _GetGBM();
    auto* avatar = _GetAvatar();
    auto* move = avatar ? avatar->GetMoveMapInfo() : nullptr;
    const bool pendingCanStop = pending && (!move || move->m_byMoveStep == MOVEMAP_INFO::MMS_NONE);
    if (!reply.status || pendingCanStop) {
        if (boards) boards->SetRequestProcessState(FALSE);
        if (avatar) avatar->SetAction(CAI_MOVE_STOP);
    }
    if (reply.status) {
        if (move && pendingCanStop) {
            move->m_bIsMoved = FALSE;
            move->m_pEnterPortalInfo = move->m_pExitPortalInfo = nullptr;
        }
        RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(RF455_BattleDungeonEntryRefusal455(reply.status)));
        return true;
    }

    auto* land = _GetLand();
    auto* loading = _GetMapLoadingWindow();
    const BYTE source = land ? land->GetMapIndex() : 0xff;
    const auto* catalog = land ? &land->MapData455() : nullptr;
    auto* network = _GetNetworkMgr();
    if (network) network->CancelPendingMapRequests455();
    if (!move || !land || !land->GetLevel() || !loading || !catalog || !catalog->maps ||
        source == 0xff || source >= catalog->count || reply.destination >= 0xff ||
        reply.destination >= catalog->count ||
        (reply.destination != source && !land->CanLoadMap455(static_cast<BYTE>(reply.destination)))) {
        if (loading && loading->IsShow()) loading->Close();
        RF455_ObserveProtocol("battle-dungeon-map-unavailable", message, reply.destination, source);
        EP_DisconnectedFromServer();
        return true;
    }

    if (loading->IsShow()) loading->Close();
    if (!entering) _GetDungeonInfo()->ExitDungeon();
    move->m_pEnterPortalInfo = move->m_pExitPortalInfo = nullptr;
    move->m_bIsMoved = TRUE;
    move->m_byEnterMapIndex = source;
    move->m_byExitMapIndex = static_cast<BYTE>(reply.destination);
    for (unsigned axis = 0; axis < 3; ++axis) move->m_vecPosition[axis] = reply.position[axis];
    move->MoveToPortal_Result(GST_DUNGEON);
    return true;
}
