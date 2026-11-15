#include "client455_client_items.h"
#include "client455_item_payloads.h"
#include "client455_shop_transactions.h"
#include <cstdint>
#include <cstring>

namespace {
template<class T>
T RF455_ShopReplyValue(const char* data, std::size_t offset)
{
    T value{};
    std::memcpy(&value, data + offset, sizeof(value));
    return value;
}

bool RF455_ReceiveShopReply(BYTE subtype, const char* data, std::size_t size)
{
    using Kind = RF455ShopPending455::Kind;
    auto* shop = _GetShopTradeBoard();
    if (!shop || !data) return false;
    const auto pending = shop->PendingTransaction455();
    const bool sale = subtype == 5;
    if (!pending.sent || pending.kind != (sale ? Kind::Sell : Kind::Buy)) return false;
    if (size < (sale ? 35u : subtype == 2 ? 66u : 37u)) return false;
    if (subtype == 2 && (static_cast<BYTE>(data[65]) != 1 || size < 73)) return false;

    auto* inventory = _GetInventoryBoard();
    auto* avatar = _GetAvatar();
    if (!inventory || !avatar) return false;
    const bool accepted = sale ? data[0] == 1 : subtype == 2;
    bool applied = false;
    if (accepted && sale) {
        auto* object = inventory->GetObject(pending.pack, pending.socket);
        auto* item = object ? dynamic_cast<RF455BasicItem*>(object->GetItem455()) : nullptr;
        if (item && item->header().serial == pending.ownedSerial &&
            item->quantity455() == pending.observedQuantity)
            applied = inventory->Remove(pending.pack, pending.socket, pending.quantity) != FALSE;
    } else if (accepted) {
        const auto serial = RF455_ShopReplyValue<std::uint16_t>(data, 66);
        BYTE pack = pending.pack;
        BYTE socket = pending.socket;
        if (!inventory->GetObject(pack, socket) || inventory->FindEmptySocket(pack, socket)) {
            CBoardObject object;
            auto& items = RF455_GameItems();
            auto* item = static_cast<RF455BasicItem*>(items.create(0, pending.itemKind, pending.itemIndex));
            if (item) {
                item->header().serial = serial;
                item->header().field8 = serial;
                if (item->IsStackable455()) item->SetDownloadValue455(pending.quantity, 0);
                const auto modifier = static_cast<BYTE>(data[68]);
                if (modifier > 0 && modifier < 3)
                    item->SetDownloadModifiers455(modifier, RF455_ShopReplyValue<std::uint32_t>(data, 69),
                                                 false, 0);
                object.SetItem455(item);
                applied = inventory->Add(pack, socket, &object) != FALSE;
            }
        }
    }

    if (!sale || accepted) {
        const std::size_t balance = sale ? 1 : 0;
        avatar->SetDalant(RF455_ShopReplyValue<std::int64_t>(data, balance));
        avatar->SetGold(RF455_ShopReplyValue<std::int64_t>(data, balance + 8));
    }

    const BYTE error = sale ? static_cast<BYTE>(data[34]) :
                       subtype == 3 ? static_cast<BYTE>(data[36]) : 0;
    RF455_ObserveProtocol("shop-result", subtype, accepted, applied ? pending.quantity : 0);
    if (!accepted) RF455_ObserveProtocol("shop-rejected", subtype, error, 0);
    shop->FinishTransaction455();
    if (sale) shop->RebuildSellChoices455();
    return true;
}
}
