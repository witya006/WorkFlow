#pragma once
#include <cstdint>
#include <stdexcept>

// Logical storage/board identities recovered from455, not a packet-layout
// replacement. GetBoard aliases Embellishment to Equipment; GetObject does not.
enum class RF455StorageCode : std::uint8_t {
    Inventory=0, Equipment=1, Embellishment=2, Force=3,
    Animus=4, Trunk=5, Linker=6
};
constexpr unsigned RF455_BOARD_COUNT=56;
constexpr unsigned RF455_STORAGE_COUNT=6;
constexpr unsigned RF455_STORAGE_POSITION_COUNT=7;

// 4FEF50 is used by ordinary ReturnItemToItemBoard4FEF90. Other item-transfer
// and protocol rules remain separate reconstruction work.
inline bool RF455_IsPhysicalItemStorage(std::uint8_t value) {
    return value==0 || value==1 || value==5;
}

// The old potion belt has no slot in455. Keep an INVALID migration marker so
// unrecovered old callers cannot alias Force3 or be registered in the table.
constexpr std::uint8_t RF455_REMOVED_LEGACY_BELT=0xff;
class CBeltBoard;
[[noreturn]] inline CBeltBoard* RF455_RejectRemovedLegacyBelt() {
    throw std::logic_error("Legacy potion-belt storage is absent in455;this caller requires migration");
}
