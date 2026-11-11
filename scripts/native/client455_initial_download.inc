// 455 base, inventory and Force handlers at RVA 16BEA0, 16D080 and 16DF30.
#include "client455_initial_download.h"
#include "client455_client_items.h"
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

bool CNetworkMgr::InitMsg_CumDownloadResult_zocl(const char* bytes, std::size_t size)
{
    RF455MasteryDownload packet{};
    if (m_initialDownload455 != RF455DownloadStep::Mastery || !RF455_ReadMasteryDownload(bytes, size, packet)) return false;
    if (packet.result) {
        RF455_ObserveProtocol("mastery-rejected", packet.result, 0, 0);
        return true;
    }
    auto* avatar = _GetAvatar();
    auto* skills = _GetSkillBoard();
    auto* force = _GetForceBoard();
    if (!avatar || !skills || !force || !_GetLinkBoard() || !_GetOreProcBoard()) return false;

    avatar->SetExpertness(EVT_NEAR, packet.weapon[0]);
    avatar->SetExpertness(EVT_FAR, packet.weapon[1]);
    avatar->SetExpertness(EVT_RACE_SKILL, packet.racial);
    avatar->SetExpertness(EVT_SHIELD, packet.shield);
    avatar->SetExpertness(EVT_DEFENCE, packet.defence);
    for (BYTE i = 0; i < 3; ++i) avatar->SetExpertness(EVT_MAKE_WEAPON + i, packet.crafting[i]);

    unsigned skillsApplied = 0;
    for (unsigned i = 0; i < 48; ++i) {
        auto* skill = skills->GetSFByDTIndex(i);
        if (!skill || !skill->GetData()) continue;
        skill->SetHave(TRUE);
        if (!avatar->IsUsableItem(skill)) skill->SetState(CSFItem::SFS_DEACTIVE);
        else if (_GetLinkBoard()->IsExistObject(skill)) skill->SetState(CSFItem::SFS_LINK);
        else skill->SetState(CSFItem::SFS_ACTIVE);
        avatar->SetSFSuccessCount(CAT_SKILL, skill->GetIndex(), packet.skill[i]);
        ++skillsApplied;
    }
    for (DWORD index : {48u, 83u}) {
        if (auto* skill = skills->GetSFByDTIndex(index))
            avatar->SetSFSuccessCount(CAT_SKILL, skill->GetIndex(), 1);
    }
    for (BYTE i = 0; i < 24; ++i)
        force->SetSuccessCountOfMastery(i, i % 4, packet.force[i], FALSE);

    unsigned oresApplied = 0;
    for (BYTE i = 0; i < packet.oreCount; ++i) {
        CBoardItem item;
        if (!item.Create(IEPT_INGOT, packet.oreIndex[i])) continue;
        item.SetIndex(i);
        item.SetServerIndex(i);
        item.SetDurability(1);
        item.SetQuantity(packet.oreQuantity[i]);
        if (_GetOreProcBoard()->Add(0, i, &item)) ++oresApplied;
    }
    RF455_ObserveProtocol("mastery-applied", skillsApplied, packet.oreCount, oresApplied);
    m_initialDownload455 = RF455DownloadStep::Quest;
    BYTE type[] = {init_msg, 11};
    return SendNetMessage(NST_GAME_SERVER, type, nullptr, 0) != FALSE;
}

bool CNetworkMgr::InitMsg_QuestDownloadResult455(const char* bytes, std::size_t size)
{
    RF455QuestDownload packet{};
    if (m_initialDownload455 != RF455DownloadStep::Quest || !RF455_ReadQuestDownload(bytes, size, packet)) return false;
    auto* avatar = _GetAvatar();
    if (!avatar) return false;
    unsigned resolved = 0;
    auto& items = RF455_GameItems();
    if (packet.count && items.loadQuestFile()) {
        for (unsigned i = 0; i < packet.count; ++i)
            if (items.data.getQuest(packet.quests[i].index).data) ++resolved;
    }
    RF455_ObserveProtocol("quest-decoded", packet.result, packet.count, resolved);

    // The target continues even if a quest record cannot be attached.
    if (avatar->IsAccretia()) {
        m_initialDownload455 = RF455DownloadStep::Miner;
        BYTE type[] = {init_msg, 54};
        return SendNetMessage(NST_GAME_SERVER, type, nullptr, 0) != FALSE;
    }
    m_initialDownload455 = RF455DownloadStep::Special;
    return InitMsg_SpecialDownloadRequest_clzo() != FALSE;
}

bool CNetworkMgr::InitMsg_SpecialDownloadResult455(BYTE subtype, const char* bytes, std::size_t size)
{
    if (m_initialDownload455 != RF455DownloadStep::Special) return false;
    unsigned applied = 0;
    if (subtype == 14) {
        if (!RF455_MatchDownloadList<RF455UnitDownloadEntry>(bytes, size, 1)) return false;
        auto* board = _GetUnitStorehouseBoard();
        if (!board) return false;
        for (unsigned i = 0; i < static_cast<BYTE>(bytes[0]); ++i) {
            RF455UnitDownloadEntry record;
            std::memcpy(&record, bytes + 1 + i * sizeof record, sizeof record);
            if (record.frame == 0xff || record.slot >= unit_storage_num) continue;
            auto* original = board->GetUnit(record.slot);
            if (!original) continue;
            CUnitItem unit;
            if (!unit.AddFrame(record.frame)) continue;
            unit.SetIndex(original->GetIndex());
            unit.SetDurability(record.durability);
            unit.SetHave(TRUE);
            for (BYTE j = 0; j < 6; ++j) {
                if (record.parts[j] == 0xff) continue;
                if (auto* part = unit.AddParts(IEPT_UNIT_HELMET + j, record.parts[j])) part->SetHave(TRUE);
            }
            for (BYTE j = 0; j < 2; ++j) {
                if (record.ammunition[j].index == 0xffff) continue;
                if (auto* part = unit.AddBullet(IEPT_UNIT_ARMS + j, record.ammunition[j].index)) {
                    part->SetDurability(record.ammunition[j].remaining);
                    part->SetHave(TRUE);
                }
            }
            for (BYTE j = 0; j < 8 && j < MAX_BACKPACK_BULLET_NUM; ++j) {
                if (record.spare[j].index == 0xffff) continue;
                if (auto* part = unit.AddBackpackBullet(j, record.spare[j].index)) {
                    part->SetDurability(record.spare[j].remaining);
                    part->SetHave(TRUE);
                }
            }
            unit.SetTractionDebt(record.tractionDebt);
            if (board->ReplaceUnit(record.slot, &unit)) ++applied;
        }
    } else if (subtype == 15) {
        if (!RF455_MatchDownloadList<RF455AnimusDownloadEntry>(bytes, size, 1)) return false;
        auto* board = _GetAnimusBoard();
        if (!board || !_GetLinkBoard()) return false;
        for (unsigned i = 0; i < static_cast<BYTE>(bytes[0]); ++i) {
            RF455AnimusDownloadEntry record;
            std::memcpy(&record, bytes + 1 + i * sizeof record, sizeof record);
            if (record.index == 0xff || record.experience > 0xffffffffu) continue;
            auto* item = board->GetAnimusByDTIndex(record.index);
            auto* data = static_cast<ANIMUS_DATA*>(_GetItemDataMgr()->GetData(IEPT_ANIMUS, record.index));
            if (!item || !data) continue;
            const auto exp = static_cast<DWORD>(record.experience);
            auto* actor = _GetCharDataMgr()->GetAnimusByExp(record.index, exp);
            if (!actor) continue;
            item->SetData(data);
            item->SetCharData(actor);
            item->SetIndex(m_dwItemIndexForFirstItemSetting++);
            item->SetExp(exp);
            item->SetHP(record.hp);
            item->SetState(_GetLinkBoard()->IsExistObject(item) ? CAnimusItem::AIS_LINK : CAnimusItem::AIS_ACTIVE);
            ++applied;
        }
    } else {
        return false;
    }
    RF455_ObserveProtocol("special-decoded", subtype, static_cast<BYTE>(bytes[0]), applied);
    m_initialDownload455 = RF455DownloadStep::Miner;
    BYTE type[] = {init_msg, 54};
    return SendNetMessage(NST_GAME_SERVER, type, nullptr, 0) != FALSE;
}

bool CNetworkMgr::InitMsg_MinerDownloadResult455(const char* bytes, std::size_t size)
{
    if (m_initialDownload455 != RF455DownloadStep::Miner ||
        !RF455_MatchDownloadList<RF455MinerDownloadEntry>(bytes, size, 2)) return false;
    RF455_ObserveProtocol("miner-decoded", static_cast<BYTE>(bytes[0]), static_cast<BYTE>(bytes[1]), 0);
    m_initialDownload455 = RF455DownloadStep::Linker;
    BYTE type[] = {init_msg, 46};
    return SendNetMessage(NST_GAME_SERVER, type, nullptr, 0) != FALSE;
}
