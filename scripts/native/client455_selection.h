#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

//56B920/56B9D0:1/14 withoneBYTE;1/15 copies22bytes,not the old6byte reply.
constexpr std::size_t RF455CharacterSelectionBytes=22;
struct RF455CharacterSelection {
    std::uint16_t result=255;
    std::uint32_t serial=0xffffffff;
    std::int64_t dalant=0,gold=0;
};
inline bool RF455_ReadCharacterSelection(const void* data,std::size_t bytes,RF455CharacterSelection& out){
    if(!data||bytes<RF455CharacterSelectionBytes)return false;
    const auto* p=static_cast<const std::uint8_t*>(data);RF455CharacterSelection next;
    next.result=std::uint16_t(p[0])|(std::uint16_t(p[1])<<8);
    next.serial=std::uint32_t(p[2])|(std::uint32_t(p[3])<<8)|(std::uint32_t(p[4])<<16)|(std::uint32_t(p[5])<<24);
    std::memcpy(&next.dalant,p+6,8);std::memcpy(&next.gold,p+14,8);out=next;return true;
}
unsigned RF455_SelectedCharacterSlot();
