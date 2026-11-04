// Included in the original commonutil.cpp TU; existing OS-provider pointers stay.
#include "client455_loop_clock.h"
static RF455LoopClock rf455EngineLoopClock;
extern "C" RF455LoopClock* RF455_GetEngineLoopClockState(){return &rf455EngineLoopClock;}
extern "C" void RF455_SetEngineLoopTimeScale(float scale){rf455EngineLoopClock.timeScale=scale;}
void R3CalculateTime(){RF455_UpdateLoopClock(&rf455EngineLoopClock,pQueryPerformanceFrequency,&QueryPerformanceCounter,ptimeGetTime);}
float GetDuration(){return RF455_GetLoopDuration(&rf455EngineLoopClock,&QueryPerformanceCounter,ptimeGetTime);}
float R3GetLoopTime(){return rf455EngineLoopClock.loopSeconds;}
void R3SetLoopTime(float value){rf455EngineLoopClock.loopSeconds=value;}
float R3GetTime(){return rf455EngineLoopClock.realSeconds;}
void R3SetTime(float value){rf455EngineLoopClock.realSeconds=value;}
void R3SetMinFPS(float fps){float result;__asm {fld fps
    fld1
    fdivrp st(1),st
    fstp result}rf455EngineLoopClock.maximumSeconds=result;}
LONG R3GetToggle30fps(){return rf455EngineLoopClock.toggles[0];}
LONG R3GetToggle15fps(){return rf455EngineLoopClock.toggles[1];}
LONG R3GetToggle7fps(){return rf455EngineLoopClock.toggles[2];}
