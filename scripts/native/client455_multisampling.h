#pragma once

#include <d3d9.h>

// Explicit per-client choice instead of an unspecified D3D9 default.
// Windowed presentation still participates in the desktop compositor.
inline UINT RF455_PresentationInterval() {
    return GetPrivateProfileIntA("RenderState","VSync",0,".\\R3Engine.ini")
        ? D3DPRESENT_INTERVAL_ONE : D3DPRESENT_INTERVAL_IMMEDIATE;
}

inline D3DMULTISAMPLE_TYPE RF455_SelectMultisampling(IDirect3D9& api, UINT adapter,
                                                     D3DDEVTYPE deviceType,
                                                     const D3DPRESENT_PARAMETERS& mode) {
    const UINT requested = GetPrivateProfileIntA("RenderState", "MSAA", 4, ".\\R3Engine.ini");
    const D3DMULTISAMPLE_TYPE candidates[] = {D3DMULTISAMPLE_4_SAMPLES, D3DMULTISAMPLE_2_SAMPLES};
    for (const auto samples : candidates) {
        if (UINT(samples) <= requested &&
            SUCCEEDED(api.CheckDeviceMultiSampleType(adapter, deviceType, mode.BackBufferFormat,
                                                     mode.Windowed, samples, nullptr)) &&
            (!mode.EnableAutoDepthStencil ||
             SUCCEEDED(api.CheckDeviceMultiSampleType(adapter, deviceType, mode.AutoDepthStencilFormat,
                                                      mode.Windowed, samples, nullptr)))) {
            return samples;
        }
    }
    return D3DMULTISAMPLE_NONE;
}

// Reset may overwrite its input even on failure. Keep the selected mode separate
// so another reset (or the no-MSAA retry) retains the requested size and format.
template<class Device>
inline HRESULT RF455_ResetPresentation(Device& device, D3DPRESENT_PARAMETERS& mode) {
    auto requested = mode;
    auto attempt = requested;
    HRESULT result = device.Reset(&attempt);
    if (FAILED(result) && result != D3DERR_DEVICELOST &&
        requested.MultiSampleType != D3DMULTISAMPLE_NONE) {
        requested.MultiSampleType = D3DMULTISAMPLE_NONE;
        requested.MultiSampleQuality = 0;
        attempt = requested;
        result = device.Reset(&attempt);
    }
    if (SUCCEEDED(result)) mode = requested;
    return result;
}

inline HRESULT RF455_ReadRenderTarget(IDirect3DDevice9& device, IDirect3DSurface9& source,
                                      IDirect3DSurface9& memory) {
    D3DSURFACE_DESC desc{};
    HRESULT result = source.GetDesc(&desc);
    if (FAILED(result)) return result;
    if (desc.MultiSampleType == D3DMULTISAMPLE_NONE)
        return device.GetRenderTargetData(&source, &memory);

    IDirect3DSurface9* resolved = nullptr;
    result = device.CreateRenderTarget(desc.Width, desc.Height, desc.Format, D3DMULTISAMPLE_NONE,
                                       0, FALSE, &resolved, nullptr);
    if (SUCCEEDED(result)) {
        result = device.StretchRect(&source, nullptr, resolved, nullptr, D3DTEXF_NONE);
        if (SUCCEEDED(result)) result = device.GetRenderTargetData(resolved, &memory);
        resolved->Release();
    }
    return result;
}
