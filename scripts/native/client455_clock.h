#pragma once
#include <windows.h>

// Win32 clock API. Fractions use a 86400-second day; HMS inputs wrap separately.
// The simulation rate does not affect the independent real-time counter.
extern "C" {
float RF455_GetDayRate();
void RF455_SetDayRate(float);
float RF455_GetDayFraction();
void RF455_SetDayFraction(float);
void RF455_SetDayTime(unsigned hours,unsigned minutes,unsigned seconds);
void RF455_GetDayTime(unsigned* hours,unsigned* minutes,unsigned* seconds);
float RF455_GetRealDayFraction();
void RF455_SetRealDayFraction(float);
void RF455_AdvanceDayClock();

// Named storage and clock provider permit deterministic component tests. The
// production provider is GetTickCount; no test override is installed by the game.
extern float RF455_DayRate,RF455_DayFraction,RF455_RealDayFraction;
extern DWORD RF455_DayBase,RF455_RealDayBase;
extern DWORD (WINAPI* RF455_ClockTickSource)();
}
