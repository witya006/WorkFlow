#include "client455_avatar_movement.h"
#include "client455_client_items.h"
#include "client455_language.h"
#include "client455_message_dispatch.h"
#include "client455_protocol_observation.h"
#include "client455_world_updates.h"
#include <cstring>

void EP_DisconnectedFromServer();

namespace {
#pragma pack(push, 1)
struct PortalRequest455 {
    BYTE portal;
    WORD itemSerials[3];
};
struct PortalResult455 {
    BYTE result;
    BYTE map;
    float position[3];
    BYTE zone;
};
#pragma pack(pop)
static_assert(sizeof(PortalRequest455) == 7);
static_assert(sizeof(PortalResult455) == 15);

const RF455MapInfo* FindPortalMap455(const CLand& land, DWORD map)
{
    const auto& catalog = land.MapData455();
    return catalog.maps && map < catalog.count ? &catalog.maps[map] : nullptr;
}

WORD FindPortalItemInPack455(CInventoryBoard& inventory, BYTE pack, BYTE category,
                            DWORD index, BYTE quantity)
{
    for (BYTE slot = 0; slot < inventory.GetMaxSocketNum455(pack); ++slot) {
        auto* object = inventory.GetObject(pack, slot);
        auto* item = object ? dynamic_cast<RF455BasicItem*>(object->GetItem455()) : nullptr;
        if (!item || item->header().kind != 0 || item->tableIndex() != index ||
            item->quantity455() < quantity)
            continue;
        const auto data = item->rawMetadata();
        const auto serial = static_cast<WORD>(item->header().serial);
        if (data.size > 88 && data.data[88] == category && serial != 0xffff) return serial;
    }
    return 0xffff;
}

bool ResolvePortalItems455(const RF455PortalAccess& access, PortalRequest455& request)
{
    if (!access.itemCount) return true;
    auto* inventory = _GetInventoryBoard();
    if (!inventory || access.itemCount > _countof(request.itemSerials)) return false;
    const auto& items = RF455_GameItems().data;
    auto* language = RF455_GetNormalLanguagePack();
    for (BYTE i = 0; i < access.itemCount; ++i) {
        const auto table = access.itemTables[i];
        std::uint32_t index = 0;
        if (!items.findItemByCode(table, access.itemCodes[i], index)) {
            RF455_ShowSystemMessage("%s", language->get(0x866));
            return false;
        }
        const auto row = items.getItem(table, index);
        if (row.size <= 88) return false;
        const auto category = row.data[88];
        const auto active = inventory->GetActivePackNo();
        const auto required = access.itemQuantities[i];
        auto serial = FindPortalItemInPack455(*inventory, active, category, index, required);
        for (BYTE pack = 0; serial == 0xffff && pack < inventory->GetMaxPackNum(); ++pack) {
            if (pack != active)
                serial = FindPortalItemInPack455(*inventory, pack, category, index, required);
        }
        if (serial == 0xffff) {
            char name[65]{};
            std::memcpy(name, row.data + 8, sizeof name - 1);
            RF455_ShowSystemMessage(language->get(0xc20), name);
            return false;
        }
        request.itemSerials[i] = serial;
    }
    return true;
}

void ShowPortalRefusal455(BYTE code)
{
    static constexpr unsigned messages[] = {
        0, 0x702, 0x703, 0x704, 0x705, 0x706, 0x707, 0x708,
        0x709, 0x70a, 0x70b, 0x70c, 0x70d, 0x70f, 0x70e, 0x832,
        0x833, 0x834, 0x835, 0x906, 0xc42, 0xc43, 0, 0x907, 0x18af,
    };
    auto* language = RF455_GetNormalLanguagePack();
    if (code < _countof(messages) && messages[code])
        RF455_ShowSystemMessage("%s", language->get(messages[code]));
    else
        RF455_ShowSystemMessage(language->get(0x710), static_cast<int>(code));
}
}

BOOL CNetMsgProcessor_Map::MovePotalRequest_clzo(BYTE portal)
{
    auto* avatar = _GetAvatar();
    auto* move = avatar ? avatar->GetMoveMapInfo() : nullptr;
    auto* land = _GetLand();
    auto* boards = _GetGBM();
    if (m_portalPending455 || !boards || boards->IsRequestProcess() || !land || !move ||
        move->m_bIsMoved || move->m_byMoveStep != MOVEMAP_INFO::MMS_NONE)
        return FALSE;

    const auto sourceIndex = land->GetMapIndex();
    const auto* source = FindPortalMap455(*land, sourceIndex);
    if (!source || !source->pPortalInfo || portal >= source->byPortalNum) return FALSE;
    auto& entry = source->pPortalInfo[portal];
    if (!entry.byLinkedPortal || !entry.byLinkedPortalNum) return FALSE;
    const auto& link = entry.byLinkedPortal[0];
    const auto* destination = FindPortalMap455(*land, link[0]);
    if (!destination || !destination->pPortalInfo || link[1] >= destination->byPortalNum ||
        (link[0] != sourceIndex && !land->CanLoadMap455(static_cast<BYTE>(link[0]))))
        return FALSE;

    const auto level = entry.access.minimumLevel;
    if (level != 0xffffffff && level > avatar->GetLevel()) {
        char portalName[sizeof entry.pName + 1]{};
        std::memcpy(portalName, entry.pName, sizeof entry.pName);
        RF455_ShowSystemMessage(RF455_GetNormalLanguagePack()->get(0xc41), portalName, level);
        return FALSE;
    }
    PortalRequest455 request{portal, {0xffff, 0xffff, 0xffff}};
    if (level != 0xffffffff && !ResolvePortalItems455(entry.access, request)) return FALSE;
    if (!SendNetMessage(move_potal_request_clzo, &request, sizeof request)) return FALSE;

    m_portalPending455 = true;
    move->m_bIsMoved = TRUE;
    move->m_pEnterPortalInfo = &entry;
    move->m_pExitPortalInfo = &destination->pPortalInfo[link[1]];
    move->m_byEnterMapIndex = sourceIndex;
    move->m_byExitMapIndex = static_cast<BYTE>(link[0]);
    boards->SetRequestProcessState(TRUE);
    return TRUE;
}

void CNetMsgProcessor_Map::CancelPortalRequest455()
{
    if (!m_portalPending455) return;
    m_portalPending455 = false;
    _GetGBM()->SetRequestProcessState(FALSE);
    if (auto* avatar = _GetAvatar()) {
        if (auto* move = avatar->GetMoveMapInfo()) {
            move->m_bIsMoved = FALSE;
            move->m_pEnterPortalInfo = move->m_pExitPortalInfo = nullptr;
        }
    }
}

bool CNetMsgProcessor_Map::ReceivePortalResult455(const char* bytes, std::size_t size)
{
    if (!bytes || (size != 1 && size != sizeof(PortalResult455))) return false;
    const BYTE result = static_cast<BYTE>(bytes[0]);
    PortalResult455 reply{};
    if (!result && (!RF455_ReadWorldRecord(bytes, size, reply) || !RF455_FinitePosition(reply.position)))
        return false;
    if (!m_portalPending455) return true;
    auto* avatar = _GetAvatar();
    if (avatar) avatar->SetAction(CAI_MOVE_STOP);
    if (result) {
        CancelPortalRequest455();
        ShowPortalRefusal455(result);
        return true;
    }

    auto* move = avatar ? avatar->GetMoveMapInfo() : nullptr;
    auto* land = _GetLand();
    if (!move || !land || !_GetMapLoadingWindow() || !move->m_pExitPortalInfo ||
        land->GetMapIndex() != move->m_byEnterMapIndex ||
        reply.zone != 0 || reply.map != move->m_byExitMapIndex ||
        (reply.map != move->m_byEnterMapIndex && !land->CanLoadMap455(reply.map))) {
        CancelPortalRequest455();
        RF455_ObserveProtocol("portal-result-unavailable", reply.map, reply.zone, 0);
        EP_DisconnectedFromServer();
        return true;
    }

    m_portalPending455 = false;
    _GetGBM()->SetRequestProcessState(FALSE);
    std::memcpy(move->m_vecPosition, reply.position, sizeof reply.position);
    move->MoveToPortal_Result(GST_PORTAL);
    return true;
}

void CNetworkMgr::CancelPendingMapRequests455()
{
    CancelBasePortalRequest455();
    if (auto* processor = static_cast<CNetMsgProcessor_Map*>(GetNetMsgProcessor(NMP_MAP)))
        processor->CancelPortalRequest455();
}
