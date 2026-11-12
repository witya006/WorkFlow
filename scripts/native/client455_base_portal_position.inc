#include "client455_language.h"
#include "client455_message_dispatch.h"

namespace {
#pragma pack(push, 1)
struct RF455BasePortalResult {
    BYTE result;
    BYTE map;
    std::int16_t position[3];
};
#pragma pack(pop)
static_assert(sizeof(RF455BasePortalResult) == 8);

bool CanEnterBasePortalMap455(CLand& land, BYTE map)
{
    const auto& data = land.MapData455();
    if (!data.maps || map >= data.count || !land.GetLevel()) return false;
    return map == land.GetMapIndex() || land.CanLoadMap455(map);
}
}

BOOL CNetworkMgr::PositionMsg_GotoBaseportalRequest_clzo(DWORD serial)
{
    auto* boards = _GetGBM();
    auto* avatar = _GetAvatar();
    auto* land = _GetLand();
    auto* move = avatar ? avatar->GetMoveMapInfo() : nullptr;
    if (m_basePortalPending455 || !boards || boards->IsRequestProcess() ||
        !move || move->m_bIsMoved || move->m_byMoveStep != MOVEMAP_INFO::MMS_NONE ||
        !land || !CanEnterBasePortalMap455(*land, land->GetMapIndex()))
        return FALSE;

    boards->CloseUnnecessaryWindow();
    boards->SetRequestProcessState(TRUE);
    WORD item = static_cast<WORD>(serial);
    BYTE type[] = {position_msg, 26};
    if (!SendNetMessage(NST_GAME_SERVER, type, &item, sizeof(item))) {
        boards->SetRequestProcessState(FALSE);
        return FALSE;
    }

    m_basePortalSerial455 = serial;
    m_basePortalPending455 = true;
    move->m_bIsMoved = TRUE;
    move->m_byEnterMapIndex = land->GetMapIndex();
    // Legacy world consumers still index the current map during the wait.
    RF455_ObserveProtocol("base-portal-request", position_msg, 26, sizeof(item));
    return TRUE;
}

void CNetworkMgr::CancelBasePortalRequest455()
{
    if (!m_basePortalPending455) return;
    m_basePortalPending455 = false;
    if (auto* boards = _GetGBM()) {
        boards->SetRequestProcessState(FALSE);
        if (auto* inventory = _GetInventoryBoard())
            inventory->CompleteBasePortalUse455(m_basePortalSerial455, false);
    }
    if (auto* avatar = _GetAvatar()) {
        if (auto* move = avatar->GetMoveMapInfo()) move->m_bIsMoved = FALSE;
    }
}

bool CNetworkMgr::PositionMsg_BasePortalResult455(const char* bytes, std::size_t size)
{
    if (!bytes || (size != 1 && size != sizeof(RF455BasePortalResult))) return false;
    const BYTE result = static_cast<BYTE>(bytes[0]);
    const bool succeeded = result == 0 || result == 10;
    RF455BasePortalResult packet{};
    if (succeeded && !RF455_ReadWorldRecord(bytes, size, packet)) return false;
    if (!m_basePortalPending455) return true;

    auto* avatar = _GetAvatar();
    auto* move = avatar ? avatar->GetMoveMapInfo() : nullptr;
    auto* land = _GetLand();
    if (avatar) avatar->SetAction(CAI_MOVE_STOP);
    if (!succeeded || !move || !land || !_GetMapLoadingWindow() ||
        !CanEnterBasePortalMap455(*land, packet.map)) {
        CancelBasePortalRequest455();
        RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(0x340));
        RF455_ObserveProtocol("base-portal-rejected", position_msg, result, size);
        return true;
    }

    m_basePortalPending455 = false;
    _GetGBM()->SetRequestProcessState(FALSE);
    if (_GetDungeonInfo()->IsInDungeon()) {
        _GetDungeonInfo()->SetDungeonExitType(DET_PORTAL);
        _GetDungeonInfo()->ExitDungeon();
    }
    for (unsigned axis = 0; axis < 3; ++axis) move->m_vecPosition[axis] = packet.position[axis];
    move->m_byExitMapIndex = packet.map;
    land->SetPortalIndex(0xff);
    move->MoveToPortal_Result(GST_BASE_PORTAL);
    if (result == 10) RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(0x177d));
    if (auto* inventory = _GetInventoryBoard())
        inventory->CompleteBasePortalUse455(m_basePortalSerial455, true);
    RF455_ObserveProtocol("base-portal-result", position_msg, result, size);
    return true;
}
