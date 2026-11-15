// Pinned 455 x86 b1b5febf..., RVA1981D0/198AD0. Only one ordinary
// bag transaction is enabled; inventory/currency publication belongs to replies.
#include <cstring>
#include <limits>

namespace {
bool OrdinaryShopKind455(BYTE kind)
{
    return (kind >= 1 && kind <= 17) || kind == 20 || kind == 22;
}

BYTE ShopItemKind455(const RF455BasicItem& item)
{
    const auto row = item.rawData();
    return row.data && row.size > 88 ? row.data[88] : 255;
}

bool ShopBagSlot455(CInventoryBoard* bag, BYTE pack, BYTE socket)
{
    return bag && pack < bag->GetMaxPackNum() && socket < bag->GetMaxSocketNum455(pack);
}
}

void CShopTradeBoard::FinishTransaction455()
{
    const bool sent = m_pending455.sent;
    m_pending455 = RF455ShopPending455{};
    m_uiShopWindow.SetSelection455(nullptr, FALSE);
    m_uiShopWindow.SetDalant(0);
    m_uiShopWindow.SetGold(0);
    if (sent) if (auto* boards = _GetGBM()) boards->SetRequestProcessState(FALSE);
}

void CShopTradeBoard::CloseWindow()
{
    if (m_pending455.sent) return;
    FinishTransaction455();
    CObjectBoard::CloseWindow();
}

void CShopTradeBoard::RebuildSellChoices455()
{
    m_sellChoices455.clear();
    m_uiShopWindow.ClearTradeItemList();
    auto* bag = _GetInventoryBoard();
    if (!bag) return;
    for (BYTE pack = 0; pack < bag->GetMaxPackNum(); ++pack) {
        for (BYTE socket = 0; socket < bag->GetMaxSocketNum455(pack); ++socket) {
            auto* object = bag->GetObject(pack, socket);
            auto* item = object ? dynamic_cast<RF455BasicItem*>(object->GetItem455()) : nullptr;
            if (!item || item->header().kind != 0 || object->IsUsing() || item->header().flag21 ||
                object->GetIndex() > 65535 || !OrdinaryShopKind455(ShopItemKind455(*item)) ||
                !item->quantity455()) continue;
            try {
                const auto icon = RF455_ReadBasicIconMetadata(*item);
                RF455ShopPending455 choice;
                choice.kind = RF455ShopPending455::Sell;
                choice.merchant = m_dwNpcIndex;
                choice.itemKind = ShopItemKind455(*item);
                choice.itemIndex = item->tableIndex();
                choice.ownedSerial = object->GetIndex();
                choice.observedQuantity = item->quantity455();
                choice.pack = pack;
                choice.socket = socket;
                choice.storage = IBT_INVENTORY;
                m_uiShopWindow.TakeInTradeItem(choice.ownedSerial, icon.itemID, icon.spriteID, icon.quantity);
                m_sellChoices455.push_back(choice);
            } catch (const std::out_of_range&) {
                // A malformed icon must not expose a mismatched selectable row.
            }
        }
    }
}

BOOL CShopTradeBoard::SelectTransaction455(unsigned index)
{
    if (!m_catalogActive455 || m_pending455.sent || !IsTrading()) return FALSE;
    auto* boards = _GetGBM();
    auto* bag = _GetInventoryBoard();
    if (!boards || boards->IsRequestProcess() || boards->HaveHoverObject() || !bag) return FALSE;
    const auto& choices = m_byTradeMode == STM_BUY ? m_buyChoices455 : m_sellChoices455;
    if ((m_byTradeMode != STM_BUY && m_byTradeMode != STM_SELL) || index >= choices.size()) return FALSE;
    auto selected = choices[index];
    if (!OrdinaryShopKind455(selected.itemKind)) return FALSE;
    const char* name = nullptr;
    RF455StorePreview preview;
    if (selected.kind == RF455ShopPending455::Buy) {
        if (!bag->FindEmptySocket(selected.pack, selected.socket)) return FALSE;
        selected.storage = IBT_INVENTORY; // RVA0790E0: non-equipment lane unchanged.
        RF455StoreNpcView store;
        if (!_GetCharDataMgr() || !_GetCharDataMgr()->Tables455().storeNpcByIndex(m_dwNpcIndex, store) ||
            !RF455_GameItems().makeStorePreview(selected.itemKind, selected.itemIndex, preview,
                                               store.upgradeCode, store.priceMultiplier)) return FALSE;
        // Premium, points and special store branches are outside this package.
        if (preview.currency > 1) return FALSE;
        std::uint64_t price = 0;
        if (!RF455_CurrentShopUnitPrice(preview, price) ||
            price > static_cast<std::uint64_t>((std::numeric_limits<__int64>::max)())) return FALSE;
        m_uiShopWindow.SetDalant(preview.currency == 0 ? static_cast<__int64>(price) : 0);
        m_uiShopWindow.SetGold(preview.currency == 1 ? static_cast<__int64>(price) : 0);
        name = preview.name.c_str();
    } else {
        if (!ShopBagSlot455(bag, selected.pack, selected.socket)) return FALSE;
        auto* object = bag->GetObject(selected.pack, selected.socket);
        auto* item = object ? dynamic_cast<RF455BasicItem*>(object->GetItem455()) : nullptr;
        if (!item || item->header().kind != 0 || object->GetIndex() != selected.ownedSerial || object->IsUsing() ||
            item->header().flag21 || ShopItemKind455(*item) != selected.itemKind ||
            item->tableIndex() != selected.itemIndex || !item->quantity455()) return FALSE;
        selected.observedQuantity = item->quantity455();
        name = item->name();
        // Sale proceeds are server-owned; do not show an invented price.
        m_uiShopWindow.SetDalant(0);
        m_uiShopWindow.SetGold(0);
    }
    m_pending455 = selected;
    m_uiShopWindow.SetSelection455(name, TRUE);
    return TRUE;
}

BOOL CShopTradeBoard::RequestSelected455()
{
    auto* boards = _GetGBM();
    auto* bag = _GetInventoryBoard();
    auto& pending = m_pending455;
    if (!m_catalogActive455 || pending.kind == RF455ShopPending455::None || pending.sent ||
        !IsTrading() || pending.merchant != m_dwNpcIndex || !m_pNMP_ItemTrade ||
        !boards || boards->IsRequestProcess() || boards->HaveHoverObject() ||
        !ShopBagSlot455(bag, pending.pack, pending.socket)) return FALSE;
    if (pending.kind == RF455ShopPending455::Buy) {
        if (bag->GetObject(pending.pack, pending.socket)) {
            if (!bag->FindEmptySocket(pending.pack, pending.socket)) return FALSE;
        }
    } else {
        auto* object = bag->GetObject(pending.pack, pending.socket);
        auto* item = object ? dynamic_cast<RF455BasicItem*>(object->GetItem455()) : nullptr;
        if (!item || item->header().kind != 0 || object->GetIndex() != pending.ownedSerial || object->IsUsing() ||
            item->header().flag21 || ShopItemKind455(*item) != pending.itemKind ||
            item->tableIndex() != pending.itemIndex || !item->quantity455()) return FALSE;
        pending.observedQuantity = item->quantity455();
    }
    BYTE bytes[15] = {}; // Zero unused DWORD at +5; count and every field bounded.
    std::memcpy(bytes, &pending.merchant, 4);
    bytes[4] = 1;
    bytes[9] = pending.storage;
    BYTE subtype;
    int size;
    if (pending.kind == RF455ShopPending455::Buy) {
        subtype = 1; size = 15;
        std::memcpy(bytes + 10, &pending.catalogSlot, 4);
        bytes[14] = pending.quantity;
    } else {
        subtype = 4; size = 13;
        const WORD serial = static_cast<WORD>(pending.ownedSerial);
        std::memcpy(bytes + 10, &serial, 2);
        bytes[12] = pending.quantity;
    }
    if (!m_pNMP_ItemTrade->SendNetMessage(subtype, bytes, size)) return FALSE;
    pending.sent = true;
    boards->SetRequestProcessState(TRUE);
    m_uiShopWindow.SetEnableTrade(FALSE);
    return TRUE;
}
