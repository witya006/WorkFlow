#pragma once
#include <windows.h>
#include <cstdint>

// Own state. The reference globals interleave unrelated COM pointers; this is
// deliberately not an overlay of that private address range.
#pragma pack(push,4)
struct RF455CharacterClock {
    std::uint32_t initialized=0,performanceAvailable=0;
    std::uint64_t frequency=0,previousCounter=0;
    float elapsedMilliseconds=0,deltaMilliseconds=0;
    std::uint32_t previousTick=0,samples=0,windowMilliseconds=0;
};
#pragma pack(pop)
static_assert(sizeof(RF455CharacterClock)==44,"Own Character clock state");
struct RF455CharacterClockProviders {
    BOOL (WINAPI *frequency)(LARGE_INTEGER*);
    BOOL (WINAPI *counter)(LARGE_INTEGER*);
    DWORD (WINAPI *milliseconds)();
};
extern "C" {
DWORD RF455_UpdateCharacterClock(RF455CharacterClock*,const RF455CharacterClockProviders*);
RF455CharacterClock* RF455_GetNormalCharacterClock();
// Source deployment callbacks, also used for deterministic native verification.
RF455CharacterClockProviders* RF455_GetNormalCharacterClockProviders();
}
