// 455 base, inventory and Force handlers at RVA 16BEA0, 16D080 and 16DF30.
#include "client455_initial_download.h"
#include "client455_protocol_observation.h"

namespace {
constexpr unsigned SupportedItemTables = 26;

bool CreateDownloadedItem(CBoardItem& item, BYTE table, WORD index, DWORD serial)
{
    if (table >= SupportedItemTables || !item.Create(IEPT_SERVER_TO_CLIENT[table], index)) return false;
    item.SetIndex(serial);
    item.SetServerIndex(serial);
    return true;
}

bool PutDownloadedAccessory(CEquipBoard& board, CBoardItem& item, int wireSlot)
{
    BYTE first;
    switch (item.GetItemKind()) {
    case IEPT_RING: first = UIPT_RING_LEFT; break;
    case IEPT_AMULET: first = UIPT_AMULET_LEFT; break;
    case IEPT_BULLET: first = UIPT_BULLET_LEFT; break;
    default: return false;
    }
    const BYTE preferred = first + (wireSlot % 2 != 0);
    const BYTE other = first + (preferred == first);
    return board.Add(0, board.GetObject(0, preferred) ? other : preferred, &item) != FALSE;
}
}

bool CNetworkMgr::InitMsg_BaseDownloadResult_zocl(const char* bytes, std::size_t size)
{
    RF455BaseDownload packet{};
    if (m_initialDownload455 != RF455DownloadStep::Base || !RF455_ReadBaseDownload(bytes, size, packet)) return false;
    if (packet.result) {
        RF455_ObserveProtocol("base-rejected", packet.result, 0, 0);
        return true;
    }
    auto* land = _GetLand();
    auto* avatar = _GetAvatar();
    auto* equipment = _GetEquipBoard();
    if (!land || !avatar || !equipment || !_GetCamera() || packet.mapIndex >= land->GetMaxMapNum()) {
        RF455_ObserveProtocol("base-owner-unavailable", packet.mapIndex, land ? land->GetMaxMapNum() : 0, 0);
        return false;
    }

    land->SetMapIndex(static_cast<BYTE>(packet.mapIndex));
    avatar->SetServerIndex(packet.zoneIndex);
    std::memcpy(m_vecAvatarStartPos, packet.startPosition, sizeof packet.startPosition);
    auto* camera = _GetCamera();
    if (avatar->GetObserverInfo()->m_bIsObserver && avatar->GetObserverInfo()->m_byObserverMode == OMI_FLY)
        camera->SetPosition(m_vecAvatarStartPos);
    else
        camera->GetR3Camera()->SetPos(m_vecAvatarStartPos[0], m_vecAvatarStartPos[1], m_vecAvatarStartPos[2]);

    m_dwItemIndexForFirstItemSetting = 0;
    static constexpr BYTE sockets[] = {UIPT_UPPER_PART, UIPT_LOWER_PART, UIPT_GLOVES, UIPT_SHOES,
                                       UIPT_HELMET, UIPT_SHIELD, UIPT_WEAPON, UIPT_CLOAK};
    for (unsigned i = 0; i < sizeof sockets; ++i) {
        const auto& entry = packet.equipment[i];
        if (entry.table == 0xff) {
            equipment->Remove(0, sockets[i], 1);
            continue;
        }
        CBoardItem item;
        if (!CreateDownloadedItem(item, entry.table, entry.index, m_dwItemIndexForFirstItemSetting)) continue;
        item.SetQuantity(1);
        item.InsertTalikFromServerFlag(entry.upgrade);
        equipment->Add(0, sockets[i], &item);
        ++m_dwItemIndexForFirstItemSetting;
    }
    for (const auto& entry : packet.accessories) {
        CBoardItem item;
        if (!CreateDownloadedItem(item, entry.table, entry.index, m_dwItemIndexForFirstItemSetting)) continue;
        item.SetDurability(entry.durability);
        item.SetQuantity(1);
        PutDownloadedAccessory(*equipment, item, entry.slot);
        ++m_dwItemIndexForFirstItemSetting;
    }

    avatar->SetExp(packet.experienceMillionths / 1000000.0f);
    avatar->SetMaxHP(packet.maxHP);
    avatar->SetHP(packet.hp);
    avatar->SetMaxFP(packet.maxFP);
    avatar->SetFP(packet.fp);
    avatar->SetMaxSP(packet.maxSP);
    avatar->SetSP(packet.sp);
    for (BYTE i = 0; i < 3; ++i)
        if (packet.classes[i] != 0xffff) avatar->SetClassDTIndex(i + 1, packet.classes[i]);

    auto* data = _GetCharDataMgr()->GetPlayer(avatar->GetDTIndex());
    if (data) {
        avatar->SetData(data);
        avatar->SetSpeed(CMM_MOVE_WALK, CHAR_SPEED_DEFAULT * data->m_fMoveWalkRate);
        avatar->SetSpeed(CMM_MOVE_RUN, CHAR_SPEED_DEFAULT * data->m_fMoveRunRate);
    }
    RF455_ObserveProtocol("base-applied", packet.mapIndex, m_dwItemIndexForFirstItemSetting, 0);
    m_initialDownload455 = RF455DownloadStep::Inventory;
    return InitMsg_InvenDownloadRequest_clzo() != FALSE;
}

bool CNetworkMgr::InitMsg_InvenDownloadResult_zocl(const char* bytes, std::size_t size)
{
    RF455InventoryDownload packet{};
    if (m_initialDownload455 != RF455DownloadStep::Inventory || !RF455_ReadInventoryDownload(bytes, size, packet)) return false;
    if (packet.result) {
        RF455_ObserveProtocol("inventory-rejected", packet.result, 0, 0);
        return true;
    }
    auto* inventory = _GetInventoryBoard();
    if (!inventory) return false;
    for (BYTE bag = 0; bag < packet.bags; ++bag) inventory->AddPack(bag);

    bool placed[100] = {};
    unsigned placedCount = 0;
    for (unsigned pass = 0; pass < 2; ++pass) {
        for (unsigned i = 0; i < packet.count; ++i) {
            if (placed[i]) continue;
            const auto& entry = packet.items[i];
            BYTE bag, slot;
            if (pass == 0) {
                if (entry.slot < 0) continue;
                bag = static_cast<BYTE>(entry.slot / MAX_INVENTORY_SOCKET);
                slot = static_cast<BYTE>(entry.slot % MAX_INVENTORY_SOCKET);
                if (bag >= packet.bags || inventory->GetObject(bag, slot)) continue;
            } else if (!inventory->FindEmptySocket(bag, slot)) {
                continue;
            }

            const DWORD serial = m_dwItemIndexForFirstItemSetting + i;
            CBoardItem item;
            if (!CreateDownloadedItem(item, entry.table, entry.index, serial)) continue;
            if (item.GetItemKind() == IEPT_ANIMUS) {
                item.SetCurMaxDurability(entry.countOrDurability);
                item.SetDurability(entry.upgrade);
            } else {
                if (item.IsSplitable()) item.SetQuantity(static_cast<BYTE>(entry.countOrDurability));
                else item.SetDurability(entry.countOrDurability);
                if (item.GetItemKind() != IEPT_UNIT) item.InsertTalikFromServerFlag(entry.upgrade);
            }
            if (inventory->Add(bag, slot, &item)) {
                placed[i] = true;
                ++placedCount;
                if (item.GetItemKind() == IEPT_UNIT)
                    _GetUnitStorehouseBoard()->AddUnitByIndex(static_cast<BYTE>(entry.upgrade), serial);
            }
        }
    }

    m_dwItemIndexForFirstItemSetting += packet.count;
    RF455_ObserveProtocol("inventory-applied", packet.bags, packet.count, placedCount);
    m_initialDownload455 = RF455DownloadStep::Force;
    return InitMsg_ForceDownloadRequest_clzo() != FALSE;
}

bool CNetworkMgr::InitMsg_ForceDownloadResult_zocl(const char* bytes, std::size_t size)
{
    RF455ForceDownload packet{};
    if (m_initialDownload455 != RF455DownloadStep::Force || !RF455_ReadForceDownload(bytes, size, packet)) return false;
    if (packet.result) {
        RF455_ObserveProtocol("force-rejected", packet.result, 0, 0);
        return true;
    }
    auto* board = _GetForceBoard();
    if (!board || !_GetAvatar() || !_GetLinkBoard()) return false;
    unsigned applied = 0;
    for (unsigned i = 0; i < packet.count; ++i, ++m_dwItemIndexForFirstItemSetting) {
        const auto& entry = packet.items[i];
        auto* data = static_cast<FORCE_ITEM_DATA*>(_GetItemDataMgr()->GetData(IEPT_FORCE, entry.index));
        if (!data) continue;
        auto* force = static_cast<CSFItem*>(board->GetSFByDTCode(data->dwForceDTCode));
        if (!force) continue;
        force->SetItemDTIndex(entry.index);
        force->SetIndex(m_dwItemIndexForFirstItemSetting);
        force->SetSuccessCount(entry.mastery);
        force->CalculateSuccessCount();
        force->SetHave(TRUE);
        if (!_GetAvatar()->IsUsableItem(force)) force->SetState(CSFItem::SFS_DEACTIVE);
        else if (_GetLinkBoard()->IsExistObject(force)) force->SetState(CSFItem::SFS_LINK);
        else force->SetState(CSFItem::SFS_ACTIVE);
        ++applied;
    }
    RF455_ObserveProtocol("force-applied", packet.count, applied, 0);
    m_initialDownload455 = RF455DownloadStep::Mastery;
    return InitMsg_CumDownloadRequest_clzo() != FALSE;
}
