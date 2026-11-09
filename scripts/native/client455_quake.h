#pragma once
#include <cstdint>

// Own process state,not an overlay of the original's separate global addresses.
struct RF455QuakeState {
    std::uint32_t phase=0,period=5;
    float duration=0,remaining=0,density=0,amplitude[3]={},verticalScale=1;
    float swayDensity=0,swayPeriod=0,swayRemaining=0,previous[3]={},next[3]={};
    bool swayEnabled=false;
};
const RF455QuakeState& RF455_QuakeState();
void RF455_StartCameraSway(float density,float period);
void RF455_StopCameraSway();
bool RF455_IsCameraSwayActive();
