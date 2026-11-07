#pragma once
#include <cstdint>
class RF455ManagedItem;
struct RF455BasicIconMetadata {
    std::uint32_t itemID,spriteID;
    std::uint8_t quantity,usableLevel,grade;
};
RF455BasicIconMetadata RF455_ReadBasicIconMetadata(RF455ManagedItem&);
bool RF455_IconUsable455(std::uint32_t itemID,std::uint8_t race,std::uint8_t level,std::uint8_t requiredLevel);
