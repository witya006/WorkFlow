#define main unusedMovieStateEntry
#include "client455_movie_state_probe.cpp"
#undef main
#include "client455_camera_zoom.h"
#include <wrl/client.h>

template<class Tag, typename Tag::Type Value> struct DisplayMember {
    friend typename Tag::Type member(Tag) { return Value; }
};
struct Loaded { using Type = BOOL CMainApp::*; friend Type member(Loaded); };
struct Stage { using Type = BYTE CMainApp::*; friend Type member(Stage); };
struct Message { using Type = LRESULT(CMainApp::*)(HWND, UINT, WPARAM, LPARAM); friend Type member(Message); };
template struct DisplayMember<Loaded, &CMainApp::m_bLoadedAllData>;
template struct DisplayMember<Stage, &CMainApp::m_byGameProgressID>;
template struct DisplayMember<Message, &CMainApp::MsgProc>;

static int displayChecks() {
    using Microsoft::WRL::ComPtr;
    InitR3Engine();
    auto* state = GetR3State();
    check(std::fabs(state->mAsfectRatio - 16.f / 9) < 1e-6f, "configured 1080p aspect");
    const auto instance = GetModuleHandleW(nullptr);
    WNDCLASSW cls{};
    cls.lpfnWndProc = DefWindowProcW;
    cls.hInstance = instance;
    cls.hCursor = LoadCursorW(nullptr, MAKEINTRESOURCEW(32512));
    cls.lpszClassName = L"RF455DisplayInputProbe";
    check(RegisterClassW(&cls) != 0, "window registration");
    const HWND window = CreateWindowExW(0, cls.lpszClassName, cls.lpszClassName,
        WS_POPUP, 0, 0, 1920, 1080, nullptr, nullptr, instance, nullptr);
    check(window != nullptr, "hidden 1920x1080 window");
    ComPtr<IDirect3D9> api;
    api.Attach(Direct3DCreate9(D3D_SDK_VERSION));
    D3DDISPLAYMODE desktop{};
    check(api && SUCCEEDED(api->GetAdapterDisplayMode(0, &desktop)), "adapter");
    D3DPRESENT_PARAMETERS pp{};
    pp.BackBufferWidth = 1920; pp.BackBufferHeight = 1080; pp.BackBufferCount = 1;
    pp.BackBufferFormat = desktop.Format; pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
    pp.Windowed = TRUE; pp.hDeviceWindow = window;
    ComPtr<IDirect3DDevice9> device;
    check(SUCCEEDED(api->CreateDevice(0, D3DDEVTYPE_HAL, window,
        D3DCREATE_SOFTWARE_VERTEXPROCESSING, &pp, &device)), "hardware device");
    state->mIsUsedVertexShader = FALSE;
    check(SUCCEEDED(D3D_R3InitDevice(device.Get())), "actual engine device binding");
    SetViewPortArea(0, 0, 1920, 1080);
    D3DXMATRIX actual{}, identity{};
    check(SUCCEEDED(device->GetTransform(D3DTS_PROJECTION, &actual)), "actual projection");
    D3DXMatrixIdentity(&identity);
    D3DVIEWPORT9 viewport{};
    check(SUCCEEDED(device->GetViewport(&viewport)), "actual viewport");
    D3DXVECTOR3 left(-1, 0, 10), right(1, 0, 10), top(0, 1, 10), bottom(0, -1, 10);
    D3DXVec3Project(&left, &left, &viewport, &actual, &identity, &identity);
    D3DXVec3Project(&right, &right, &viewport, &actual, &identity, &identity);
    D3DXVec3Project(&top, &top, &viewport, &actual, &identity, &identity);
    D3DXVec3Project(&bottom, &bottom, &viewport, &actual, &identity, &identity);
    const float pixelAspect = (right.x - left.x) / (bottom.y - top.y);
    check(std::fabs(pixelAspect - 1.f) < 1e-5f, "equal world lengths remain equal in screen pixels");
    SetViewPortArea(0, 0, 1920, 0);
    D3DVIEWPORT9 after{};
    device->GetViewport(&after);
    check(after.Width == 1920 && after.Height == 1080, "invalid viewport keeps working projection");
    SetViewPortArea(0, 0, 1920, 1080);

    const HCURSOR previous = SetCursor(cls.hCursor);
    const BOOL wasLoaded = g_MainApp.*member(Loaded{});
    const BYTE wasStage = g_MainApp.*member(Stage{});
    for (BYTE stage : {BYTE(GPI_LOGIN), BYTE(GPI_MAIN_GAME)}) {
        g_MainApp.*member(Loaded{}) = TRUE;
        g_MainApp.*member(Stage{}) = stage;
        SetCursor(cls.hCursor);
        check((g_MainApp.*member(Message{}))(window, WM_SETCURSOR, WPARAM(window),
              MAKELPARAM(HTCLIENT, WM_MOUSEMOVE)) == TRUE && GetCursor() == nullptr,
              "Windows cursor hidden in loaded gameplay client area");
        (g_MainApp.*member(Message{}))(window, WM_SETCURSOR, WPARAM(window),
              MAKELPARAM(HTCAPTION, WM_MOUSEMOVE));
        check(GetCursor() == cls.hCursor, "Windows cursor retained on caption");
    }
    g_MainApp.*member(Loaded{}) = FALSE;
    (g_MainApp.*member(Message{}))(window, WM_SETCURSOR, WPARAM(window), MAKELPARAM(HTCLIENT, WM_MOUSEMOVE));
    check(GetCursor() == cls.hCursor, "cursor available before game UI loads");
    g_MainApp.*member(Loaded{}) = wasLoaded;
    g_MainApp.*member(Stage{}) = wasStage;
    SetCursor(previous);

    check(RF455_CameraWheelDistance(45, -120, 1) == 53.4f, "unchanged wheel step");
    check(RF455_CameraWheelDistance(45, -12000, 1) == 300, "fourfold normal zoom limit");
    check(RF455_CameraWheelDistance(45, -12000, 0) == 240, "fourfold alternative zoom limit");
    check(RF455_CameraWheelDistance(300, 12000, 1) == 10, "unchanged close limit");
    check(std::fabs(RF455_CameraWheelDistance(300, 120, 1) - 291.6f) < 1e-4f,
          "zoom back from extended range");
    D3D_R3DeleteDevice();
    device.Reset();
    DestroyWindow(window);
    ReleaseR3Engine();
    std::printf("PASS: pixel_aspect=%.6f, cursor client/caption/loading, zoom 300/240/min10\n", pixelAspect);
    return 0;
}

int main() {
    try { return displayChecks(); }
    catch (const std::exception& error) { std::fprintf(stderr, "%s\n", error.what()); return 1; }
}
