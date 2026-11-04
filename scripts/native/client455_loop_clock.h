#pragma once
#include <windows.h>
#include <cstdint>

// Owned source state, not a binary overlay of the reference globals.
struct RF455LoopClock {
    std::uint32_t initialized=0,oldTick=0,loopCount=0,loopMilliseconds=0;
    float loopSeconds=0,realSeconds=0,maximumSeconds=1,timeScale=1;
    float toggleSeconds[3]={0,0,0};
    std::int32_t toggles[3]={1,1,1};
    std::uint64_t frequency=0,ticksPerFrame=0,startTicks=0,ticks=0;
    float frequencyFloat=0,initialSecondsPerFrame=0;
};
using RF455QueryPerformance=BOOL (WINAPI*)(LARGE_INTEGER*);
using RF455MillisecondTimer=DWORD (WINAPI*)();
extern "C" {
std::uint64_t RF455_GetLoopTicks(RF455QueryPerformance,RF455MillisecondTimer);
void RF455_UpdateLoopClock(RF455LoopClock*,RF455QueryPerformance frequency,RF455QueryPerformance counter,RF455MillisecondTimer);
float RF455_GetLoopDuration(const RF455LoopClock*,RF455QueryPerformance,RF455MillisecondTimer);
// Engine bridge ownership remains in commonutil.cpp.
RF455LoopClock* RF455_GetEngineLoopClockState();
void RF455_SetEngineLoopTimeScale(float);
}
