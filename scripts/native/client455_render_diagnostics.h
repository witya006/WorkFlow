#pragma once
#ifndef RF455_RENDER_DIAGNOSTICS_H
#define RF455_RENDER_DIAGNOSTICS_H
#include <d3d9.h>
#include <cstdint>
struct RF455RenderDiagnostics {
    char adapter[512];
    unsigned adapterOrdinal, vendorId, deviceId, width, height;
    bool hardware, gpuTimingSupported;
    double fps, frameMs, cpuSubmissionMs, gpuMs[4];
    std::uint64_t frames, samples, queryErrors;
};
// Timings use a bounded asynchronous ring; never flush/spin on the GPU.
void RF455_DiagnosticsBeginFrame(IDirect3DDevice9*);
void RF455_DiagnosticsEndFrame();
void RF455_DiagnosticsCpuEnd();
void RF455_GpuSectionBegin(unsigned section); // 0 frame, 1 sky, 2 shadow, 3 post
void RF455_GpuSectionEnd(unsigned section);
RF455RenderDiagnostics RF455_GetRenderDiagnostics();
void RF455_ReleaseRenderDiagnostics();
struct RF455GpuSection {
    unsigned section;
    explicit RF455GpuSection(unsigned value):section(value){RF455_GpuSectionBegin(section);}
    ~RF455GpuSection(){RF455_GpuSectionEnd(section);}
};
#endif
