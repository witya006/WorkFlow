// Own-client samples after the accepted starting-position response.
#include <d3dx9.h>

LPDIRECT3DDEVICE9 GetD3dDevice();

static void RF455_ObserveWorldFrame(const float* avatar, const float* camera,
                                    float yaw, float pitch, float distance,
                                    unsigned action, BOOL inputEnabled) {
    auto& state = RF455_WorldObservation();
    const unsigned sample = 3 - state.remaining;
    constexpr ULONGLONG delays[] = {0, 1000, 3000};
    const auto elapsed = GetTickCount64() - state.acceptedAt;
    if (elapsed < delays[sample]) return;
    --state.remaining;

    char message[384];
    std::snprintf(message, sizeof(message),
                  "RF455 WorldSample:%u:%llu:%u:%d:%.6g,%.6g,%.6g:%.6g,%.6g,%.6g:%.6g,%.6g,%.6g",
                  sample, elapsed, action, inputEnabled != FALSE,
                  avatar[0], avatar[1], avatar[2], camera[0], camera[1], camera[2],
                  yaw, pitch, distance);
    OutputDebugStringA(message);

    if (sample == 1) return;
    const char* filename = sample == 0 ? "world-post-position.png" : "world-post-position-settled.png";
    IDirect3DSurface9* target = nullptr;
    IDirect3DSurface9* memory = nullptr;
    D3DSURFACE_DESC desc = {};
    auto* device = GetD3dDevice();
    HRESULT result = device ? device->GetRenderTarget(0, &target) : E_FAIL;
    if (SUCCEEDED(result)) result = target->GetDesc(&desc);
    if (SUCCEEDED(result)) {
        result = device->CreateOffscreenPlainSurface(desc.Width, desc.Height, desc.Format,
                                                     D3DPOOL_SYSTEMMEM, &memory, nullptr);
    }
    if (SUCCEEDED(result)) result = device->GetRenderTargetData(target, memory);
    if (SUCCEEDED(result)) {
        result = D3DXSaveSurfaceToFileA(filename, D3DXIFF_PNG, memory, nullptr, nullptr);
    }
    if (memory) memory->Release();
    if (target) target->Release();
    std::snprintf(message, sizeof(message), "RF455 WorldCapture:%u:%ld:%ux%u",
                  sample, result, desc.Width, desc.Height);
    OutputDebugStringA(message);
}
