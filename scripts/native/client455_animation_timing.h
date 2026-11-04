#pragma once
#include <cstdint>
extern "C" {
// Exact selected7CD560 numeric contract: unsigned inputs,x87 arithmetic,
// explicit double spill,truncate to signed64 then retain lowDWORD.
std::uint32_t RF455_AdvanceAnimationFrameValue(std::uint32_t current,std::uint32_t carried,float elapsedSeconds,float speed);
void RF455_InitializeAnimationControl(void* known100);
void RF455_InitializeSecondaryState(void* known84);
}
