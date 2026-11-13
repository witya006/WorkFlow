#include "client455_multisampling.h"
#include <wrl/client.h>
#include <cstdio>
#include <stdexcept>

using Microsoft::WRL::ComPtr;

static void require(bool value, const char* message) {
    if (!value) throw std::runtime_error(message);
}

// Deterministic driver contract: Reset overwrites these in/out fields.
// Physical driver behavior varies, so exercise refusal and device-loss explicitly.
struct RefusingDevice {
    HRESULT first, second;
    unsigned calls = 0;
    D3DPRESENT_PARAMETERS inputs[2]{};
    HRESULT Reset(D3DPRESENT_PARAMETERS* mode) {
        require(calls < 2, "unexpected reset retry");
        inputs[calls] = *mode;
        mode->BackBufferWidth = mode->BackBufferHeight = mode->BackBufferCount = 0;
        mode->BackBufferFormat = D3DFMT_UNKNOWN;
        return calls++ == 0 ? first : second;
    }
};

static bool geometry(const D3DPRESENT_PARAMETERS& mode, D3DFORMAT format) {
    return mode.BackBufferWidth == 1920 && mode.BackBufferHeight == 1080 &&
        mode.BackBufferCount == 1 && mode.BackBufferFormat == format;
}

int main() {
    try {
        const auto instance = GetModuleHandleW(nullptr);
        WNDCLASSW cls{};
        cls.lpfnWndProc = DefWindowProcW;
        cls.hInstance = instance;
        cls.lpszClassName = L"RF455PresentationResetProbe";
        require(RegisterClassW(&cls) != 0, "window registration");
        const HWND window = CreateWindowExW(0, cls.lpszClassName, cls.lpszClassName,
            WS_POPUP, 0, 0, 1920, 1080, nullptr, nullptr, instance, nullptr);
        require(window != nullptr, "1920x1080 test window");
        struct Window { HWND value; ~Window() { DestroyWindow(value); } } windowOwner{window};
        ComPtr<IDirect3D9> api;
        api.Attach(Direct3DCreate9(D3D_SDK_VERSION));
        D3DDISPLAYMODE desktop{};
        require(api && SUCCEEDED(api->GetAdapterDisplayMode(0, &desktop)), "hardware adapter");
        D3DPRESENT_PARAMETERS mode{};
        mode.BackBufferWidth = 1920;
        mode.BackBufferHeight = 1080;
        mode.BackBufferCount = 1;
        mode.BackBufferFormat = desktop.Format;
        mode.SwapEffect = D3DSWAPEFFECT_DISCARD;
        mode.hDeviceWindow = window;
        mode.Windowed = TRUE;
        mode.EnableAutoDepthStencil = TRUE;
        mode.AutoDepthStencilFormat = D3DFMT_D24S8;
        mode.MultiSampleType = D3DMULTISAMPLE_4_SAMPLES;
        const auto original = mode;
        RefusingDevice fallback{D3DERR_INVALIDCALL, S_OK};
        require(SUCCEEDED(RF455_ResetPresentation(fallback, mode)) && fallback.calls == 2,
                "fallback succeeds once");
        require(geometry(fallback.inputs[1], desktop.Format) && geometry(mode, desktop.Format) &&
                mode.MultiSampleType == D3DMULTISAMPLE_NONE, "fallback keeps requested geometry");
        mode = original;
        RefusingDevice failed{D3DERR_INVALIDCALL, D3DERR_OUTOFVIDEOMEMORY};
        require(RF455_ResetPresentation(failed, mode) == D3DERR_OUTOFVIDEOMEMORY &&
                geometry(mode, desktop.Format) && mode.MultiSampleType == original.MultiSampleType,
                "failed reset retains requested configuration");
        RefusingDevice lost{D3DERR_DEVICELOST, S_OK};
        require(RF455_ResetPresentation(lost, mode) == D3DERR_DEVICELOST && lost.calls == 1 &&
                geometry(mode, desktop.Format), "device lost waits without another reset");
        mode.MultiSampleType = D3DMULTISAMPLE_NONE;
        RefusingDevice plain{D3DERR_INVALIDCALL, S_OK};
        require(FAILED(RF455_ResetPresentation(plain, mode)) && plain.calls == 1,
                "disabled multisampling does not retry");

        ComPtr<IDirect3DDevice9> device;
        require(SUCCEEDED(api->CreateDevice(0, D3DDEVTYPE_HAL, window,
            D3DCREATE_SOFTWARE_VERTEXPROCESSING, &mode, &device)), "hardware device creation");
        for (unsigned iteration = 0; iteration < 3; ++iteration) {
            mode.MultiSampleType = RF455_SelectMultisampling(*api.Get(), 0, D3DDEVTYPE_HAL, mode);
            const auto selected = mode.MultiSampleType;
            require(SUCCEEDED(RF455_ResetPresentation(*device.Get(), mode)), "actual device reset");
            require(geometry(mode, desktop.Format) && mode.MultiSampleType == selected,
                    "success preserves next reset settings");
            ComPtr<IDirect3DSurface9> back, depth;
            D3DSURFACE_DESC color{}, z{};
            require(SUCCEEDED(device->GetBackBuffer(0, 0, D3DBACKBUFFER_TYPE_MONO, &back)) &&
                    SUCCEEDED(device->GetDepthStencilSurface(&depth)), "reset surfaces");
            require(SUCCEEDED(back->GetDesc(&color)) && SUCCEEDED(depth->GetDesc(&z)) &&
                    color.Width == 1920 && color.Height == 1080 &&
                    color.MultiSampleType == selected && z.MultiSampleType == selected,
                    "actual surface dimensions and antialiasing survive repeated reset");
            require(SUCCEEDED(device->Clear(0, nullptr, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER,
                    0xff204060, 1.f, 0)) && SUCCEEDED(device->Present(nullptr, nullptr, nullptr, nullptr)),
                    "frame presentation after reset");
            std::printf("reset=%u width=%u height=%u msaa=%u present=OK\n", iteration + 1,
                        color.Width, color.Height, unsigned(selected));
        }
        std::puts("PASS: repeated hardware reset and four driver-error contracts");
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n", error.what());
        return 1;
    }
}
