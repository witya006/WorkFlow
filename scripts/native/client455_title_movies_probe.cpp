#include "baseheader.h"
#include "gameprogress/cgp_title.h"
#include "client455_nation_paths.h"

#include <cstdio>
#include <cstring>
#include <stdexcept>

extern HWND g_hWnd;

namespace {
CGP_Title* activeTitle = nullptr;

void require(bool result, const char* message)
{
    if (!result) throw std::runtime_error(message);
}

LRESULT CALLBACK WindowProc(HWND window, UINT message, WPARAM wParam, LPARAM lParam)
{
    if (activeTitle && activeTitle->MsgProc(window, message, wParam, lParam) == 0xffffffff)
        return 0;
    return DefWindowProcW(window, message, wParam, lParam);
}

HWND videoChild(HWND owner)
{
    HWND child = nullptr;
    EnumChildWindows(owner, [](HWND window, LPARAM result) -> BOOL {
        if (!(GetWindowLongPtrW(window, GWL_STYLE) & WS_VISIBLE)) return TRUE;
        RECT bounds{};
        if (!GetClientRect(window, &bounds) || bounds.right <= 100 || bounds.bottom <= 100) return TRUE;
        *reinterpret_cast<HWND*>(result) = window;
        return FALSE;
    }, reinterpret_cast<LPARAM>(&child));
    return child;
}

void pump()
{
    MSG message{};
    while (PeekMessageW(&message, nullptr, 0, 0, PM_REMOVE)) DispatchMessageW(&message);
}

int run(bool waitForPrologue)
{
    require(RF455_InitializeNationPaths(), "actual localized startup configuration");
    const auto module = GetModuleHandleW(nullptr);
    const wchar_t name[] = L"RF455TitleMovieComponent";
    WNDCLASSW registration{};
    registration.lpfnWndProc = WindowProc;
    registration.hInstance = module;
    registration.lpszClassName = name;
    require(RegisterClassW(&registration) != 0, "test window class");
    g_hWnd = CreateWindowExW(0, name, name, WS_POPUP, -2000, -2000, 640, 480,
                            nullptr, nullptr, module, nullptr);
    require(g_hWnd != nullptr, "actual window for the title video renderer");
    ShowWindow(g_hWnd, SW_SHOWNOACTIVATE);
    struct WindowScope {
        ~WindowScope() {
            activeTitle = nullptr;
            DestroyWindow(g_hWnd);
            g_hWnd = nullptr;
        }
    } window;

    CGP_Title title;
    require(title.Create(), "ordinary Title::Create");
    activeTitle = &title;
    const auto deadline = GetTickCount64() + 18000;
    HWND logo = nullptr;
    HWND movie = nullptr;
    while (GetTickCount64() < deadline) {
        pump();
        require(!title.MainLoop(TRUE), "opening movie keeps the ordinary Title stage alive");
        const auto child = videoChild(g_hWnd);
        if (!logo && child) logo = child;
        if (child && logo && (!waitForPrologue || child != logo)) {
            movie = child;
            break;
        }
        Sleep(10);
    }
    require(movie != nullptr && IsWindow(movie), "requested stock movie reaches its actual video child");
    require(PostMessageW(g_hWnd, WM_KEYDOWN, VK_ESCAPE, 1) != 0, "send Escape through the window");
    pump();
    require(title.MainLoop(TRUE) && title.GetNextStage455() == 1 && !videoChild(g_hWnd),
            "Escape closes playback and allows the ordinary transition to Login");
    activeTitle = nullptr;
    require(title.Destroy(), "normal title cleanup after skipping");
    std::printf("{\"status\":\"PASS\",\"skipped\":\"%s\",\"login_stage\":1,\"video_window_closed\":true}\n",
                waitForPrologue ? "prologue" : "logo");
    return 0;
}
}

int main(int argc, char** argv)
{
    try {
        return run(argc == 2 && !std::strcmp(argv[1], "--prologue"));
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n", error.what());
        return 1;
    }
}
