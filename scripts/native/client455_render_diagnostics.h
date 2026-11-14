#pragma once
#ifndef RF455_RENDER_DIAGNOSTICS_H
#define RF455_RENDER_DIAGNOSTICS_H
#include <d3d9.h>
#include <cstdint>
struct RF455RenderDiagnostics {
    char adapter[512];
    unsigned adapterOrdinal, vendorId, deviceId, width, height;
    bool hardware, gpuTimingSupported, windowed;
    unsigned presentInterval, swapEffect, backBuffers, refreshHz;
    long presentParametersResult;
    double fps, frameMs, cpuSubmissionMs, gpuMs[8], cpuMs[8], outsideMs[3];
    std::uint64_t frames, samples, queryErrors, discardedFrames;
};
// Timings use a bounded asynchronous ring; never flush/spin on the GPU.
void RF455_DiagnosticsBeginFrame(IDirect3DDevice9*);
void RF455_DiagnosticsEndFrame();
void RF455_DiagnosticsCpuEnd();
// 0 frame, 1 sky, 2 shadow, 3 post, 4 land (includes sky), 5 land alpha,
// 6 characters/effects, 7 UI. CPU timings accompany sections, without waiting.
void RF455_GpuSectionBegin(unsigned section);
void RF455_GpuSectionEnd(unsigned section);
RF455RenderDiagnostics RF455_GetRenderDiagnostics();
void RF455_ReleaseRenderDiagnostics();
// 0 game loop (includes update/render/Sleep), 1 Present, 2 lobby FrameMove.
struct RF455CpuSection {
    unsigned section;LARGE_INTEGER started;
    explicit RF455CpuSection(unsigned);
    ~RF455CpuSection();
};
struct RF455GpuSection {
    unsigned section;
    explicit RF455GpuSection(unsigned value):section(value){RF455_GpuSectionBegin(section);}
    ~RF455GpuSection(){RF455_GpuSectionEnd(section);}
};
#endif
