#pragma once
#include <cstdint>
struct _sprite_info;
bool RF455_ItemAtlasPage(std::uint32_t classification,std::uint32_t& spriteID,std::uint8_t& page);
bool RF455_ItemSpriteSearch455(std::uint32_t,std::uint32_t,int,_sprite_info&);
bool RF455_UnitPartsSearch455(std::uint32_t,std::uint32_t,int,_sprite_info&);
bool RF455_DefaultSpriteSearch455(std::uint32_t,_sprite_info&);
