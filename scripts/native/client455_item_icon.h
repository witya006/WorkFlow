#pragma once
#include <cstdint>
std::uint32_t RF455_ItemGradeColor(std::uint8_t);
bool RF455_ItemQuantityVisible(std::uint8_t type,std::uint16_t quantity,bool enabled,bool clipped);
