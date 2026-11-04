#pragma once
#include "client455_pose.h"

struct RF455SecondaryState {
    float value[5];int direction[5];float minimum[5],maximum[5];unsigned lastTick;
};
static_assert(sizeof(RF455SecondaryState)==84,"455 borrowed secondary state");
// Shared across characters,as reference globals1189738..1189750 are.
struct RF455SecondaryGlobals {unsigned leftTick,rightTick;float ponyPosition[3];unsigned ponyTick;float phase;};
struct RF455SecondaryMath {
    RF455PoseMath pose;
    void* (__stdcall *rotationX)(void*,float);
    void* (__stdcall *rotationY)(void*,float);
    void* (__stdcall *rotationZ)(void*,float);
    void* (__stdcall *quaternionMatrix)(void*,const void*);
    void* (__stdcall *quaternionAxis)(void*,const void*,float);
    unsigned (__stdcall *ticks)(); // Actual timeGetTime or explicit deterministic test clock.
    // Reference calls static __CIsin then stores m32. Provider must write m32;
    // matching an unrelated CRT's sine is not a reference bit-parity claim.
    void (__cdecl *sineFloat)(float* result,const float* angle);
};
struct RF455SecondaryContext {RF455SecondaryMath math;RF455SecondaryGlobals* globals;};
extern "C" RF455PoseStatus RF455_ApplySecondaryMotion(RF455CharacterStorage*,RF455MeshStorage*,const RF455SecondaryContext*);
