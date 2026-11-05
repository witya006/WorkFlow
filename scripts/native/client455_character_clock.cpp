#include "client455_character_clock.h"
#include <cstring>

extern "C" DWORD RF455_UpdateCharacterClock(RF455CharacterClock* state,const RF455CharacterClockProviders* api){
    // The original ignores QPC's BOOL. A provider that fails without writing
    // leaves unspecified stack data there; our zero seed is outside that domain.
    LARGE_INTEGER value={};
    if(!state->initialized){
        state->initialized=1;state->performanceAvailable=api->frequency(&value);
        if(state->performanceAvailable){state->frequency=static_cast<std::uint64_t>(value.QuadPart);api->counter(&value);state->previousCounter=static_cast<std::uint64_t>(value.QuadPart);}
    }
    if(state->performanceAvailable){
        api->counter(&value);const auto now=static_cast<std::uint64_t>(value.QuadPart);
        const auto product=(now-state->previousCounter)*1000ull;state->previousCounter=now;
        long long numerator,denominator;std::memcpy(&numerator,&product,8);std::memcpy(&denominator,&state->frequency,8);
        float* delta=&state->deltaMilliseconds;float* elapsed=&state->elapsedMilliseconds;
        __asm{fild numerator
            fild denominator
            fdivp st(1),st
            mov eax,delta
            fstp dword ptr[eax]
            mov edx,elapsed
            fld dword ptr[edx]
            fadd dword ptr[eax]
            fstp dword ptr[edx]}
        return static_cast<DWORD>(product);
    }
    const DWORD now=api->milliseconds();++state->samples;
    state->windowMilliseconds+=now-state->previousTick;
    if(state->windowMilliseconds>200){
        const auto total=state->windowMilliseconds,count=state->samples;
        const float unsignedBias=4294967296.0f;float* delta=&state->deltaMilliseconds;
        __asm{fild total
            test total,80000000h
            jz positiveTotal
            fadd unsignedBias
        positiveTotal:
            fild count
            test count,80000000h
            jz positiveCount
            fadd unsignedBias
        positiveCount:
            fdivp st(1),st
            mov eax,delta
            fstp dword ptr[eax]}
        state->samples=0;state->windowMilliseconds=0;
    }
    // No elapsed accumulation on this branch in 91EA80. Preserve that quirk.
    state->previousTick=now;return now;
}
