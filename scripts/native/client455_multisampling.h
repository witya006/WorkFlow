#pragma once

#include <d3d9.h>

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
