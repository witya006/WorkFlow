#pragma once
#include <windows.h>
struct RF455IMWaveView {
    unsigned count,capacity,loopCount;
    unsigned short sample2D,used;
    void* handle;void* memory;
};
RF455IMWaveView RF455_GetIMWaveView(unsigned id);
