#pragma once
#ifndef RF455_NUCLEAR_AIMING_H
#define RF455_NUCLEAR_AIMING_H
#include <windows.h>
#include <cstddef>

// The inline20-byte aiming member of the target's separate container owner.
// Stored command position is independent of the live cursor used by visuals.
struct RF455NuclearAiming {
    DWORD effectHandle=0,pending=0;
    float position[3]={};
    void SetPending(DWORD value);
    void SetVisualState(DWORD value);
    void SetPosition(const float* value);
    void FrameMove();
    void Clear();
};
static_assert(sizeof(RF455NuclearAiming)==20&&offsetof(RF455NuclearAiming,pending)==4
              &&offsetof(RF455NuclearAiming,position)==8,"455 aiming member20");
RF455NuclearAiming& RF455_NuclearAiming();
#endif
