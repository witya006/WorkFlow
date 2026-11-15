#pragma once
#include <cstdint>

// One ordinary transaction, source-owned metadata only. Catalog slots, table
// indices and server serials are intentionally distinct. No borrowed item owner.
struct RF455ShopPending455 {
    enum Kind { None, Buy, Sell };
    Kind kind = None;
    bool sent = false;
    std::uint32_t merchant = 0, catalogSlot = 0, itemIndex = 0, ownedSerial = 0;
    std::uint8_t itemKind = 0, quantity = 1, observedQuantity = 0;
    std::uint8_t pack = 255, socket = 255, storage = 0;
};
