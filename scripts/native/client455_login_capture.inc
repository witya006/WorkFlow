// Own diagnostic only. The ordinary Login render calls this after EndScene.
// No extra drawing or altered game state;enabled only by the own staged runner.
#include <cstdio>
#include "client455_multisampling.h"
static HRESULT RF455_SaveLoginBackbuffer(const char* name, D3DSURFACE_DESC& desc) {
    IDirect3DSurface9 *target = nullptr, *memory = nullptr;
    auto* device = GetD3dDevice();
    HRESULT result = device ? device->GetBackBuffer(0, 0, D3DBACKBUFFER_TYPE_MONO, &target) : E_FAIL;
    if (SUCCEEDED(result)) result = target->GetDesc(&desc);
    if (SUCCEEDED(result)) result = device->CreateOffscreenPlainSurface(desc.Width, desc.Height, desc.Format, D3DPOOL_SYSTEMMEM, &memory, nullptr);
    if (SUCCEEDED(result)) result = RF455_ReadRenderTarget(*device, *target, *memory);
    if (SUCCEEDED(result)) result = D3DXSaveSurfaceToFileA(name, D3DXIFF_PNG, memory, nullptr, nullptr);
    if (memory) memory->Release();
    if (target) target->Release();
    return result;
}

static void RF455_CaptureLoginFrameIfRequested(){
    static bool attempted=false;static unsigned frames=0;static DWORD firstTick=0;if(attempted)return;
    char enabled[2]={};if(GetEnvironmentVariableA("RF455_CAPTURE_LOGIN",enabled,2)!=1||enabled[0]!='1')return;
    const DWORD now=GetTickCount();if(!frames)firstTick=now;++frames;
    char delayText[16]={};unsigned delay=0;if(GetEnvironmentVariableA("RF455_CAPTURE_LOGIN_DELAY_MS",delayText,sizeof(delayText)))std::sscanf(delayText,"%u",&delay);
    if(now-firstTick<delay)return;
    attempted=true;D3DSURFACE_DESC desc={};
    const HRESULT result=RF455_SaveLoginBackbuffer("login-frame.png", desc);
    if(FILE* output=std::fopen("login-frame.json","wb")){std::fprintf(output,"{\"result\":%ld,\"width\":%u,\"height\":%u,\"format\":%u,\"frame_index\":%u,\"elapsed_ms\":%lu,\"requested_delay_ms\":%u}\n",result,desc.Width,desc.Height,unsigned(desc.Format),frames,now-firstTick,delay);std::fclose(output);}
    char message[128];std::sprintf(message,"RF455 LoginFrame:%08lX:%ux%u",static_cast<unsigned long>(result),desc.Width,desc.Height);OutputDebugStringA(message);
}

static void RF455_CaptureSelectionFadeIfRequested(DWORD elapsedMs, bool complete) {
    static const bool enabled = [] {
        char value[2]{};
        return GetEnvironmentVariableA("RF455_CAPTURE_SELECTION_FADE", value, sizeof(value)) == 1 && value[0] == '1';
    }();
    if (!enabled) return;
    static bool attempted[3]{};
    static const char* const filenames[] = {"selection-fade-start.png", "selection-fade-mid.png", "selection-fade-end.png"};
    const unsigned phase = complete ? 2 : elapsedMs >= 450 ? 1 : 0;
    if (attempted[phase]) return;
    attempted[phase] = true;
    D3DSURFACE_DESC desc{};
    const HRESULT result = RF455_SaveLoginBackbuffer(filenames[phase], desc);
    char event[128];
    std::snprintf(event, sizeof(event), "RF455 SelectionFade:%u:%lu:%08lX:%ux%u", phase, elapsedMs,
                  static_cast<unsigned long>(result), desc.Width, desc.Height);
    OutputDebugStringA(event);
}

static bool RF455_IsLoadingCaptureRequested() {
    static const bool enabled = [] {
        char value[2]{};
        return GetEnvironmentVariableA("RF455_CAPTURE_LOADING_REVEAL", value, sizeof(value)) == 1 && value[0] == '1';
    }();
    return enabled;
}

static void RF455_CaptureGameRatingIfRequested(DWORD elapsedMs) {
    static bool attempted = false;
    if (attempted || !RF455_IsLoadingCaptureRequested()) return;
    attempted = true;
    D3DSURFACE_DESC desc{};
    const HRESULT result = RF455_SaveLoginBackbuffer("lobby-game-rating.png", desc);
    char event[128];
    std::snprintf(event, sizeof(event), "RF455 GameRating:%lu:%08lX:%ux%u", elapsedMs,
                  static_cast<unsigned long>(result), desc.Width, desc.Height);
    OutputDebugStringA(event);
}

static void RF455_CaptureLoadingRevealIfRequested(DWORD elapsedMs, bool complete) {
    if (!RF455_IsLoadingCaptureRequested()) return;
    static bool attempted[3]{};
    static const char* const filenames[] = {"loading-reveal-start.png", "loading-reveal-mid.png", "loading-reveal-end.png"};
    const unsigned phase = complete ? 2 : elapsedMs >= 380 ? 1 : 0;
    if (attempted[phase]) return;
    attempted[phase] = true;
    D3DSURFACE_DESC desc{};
    const HRESULT result = RF455_SaveLoginBackbuffer(filenames[phase], desc);
    char event[128];
    std::snprintf(event, sizeof(event), "RF455 LoadingReveal:%u:%lu:%08lX:%ux%u", phase, elapsedMs,
                  static_cast<unsigned long>(result), desc.Width, desc.Height);
    OutputDebugStringA(event);
}

static void RF455_CaptureLobbyCameraIfRequested(unsigned phase) {
    static const bool enabled = [] {
        char value[2]{};
        return GetEnvironmentVariableA("RF455_CAPTURE_LOBBY_CAMERA", value, sizeof(value)) == 1 && value[0] == '1';
    }();
    if (!enabled) return;
    static bool attempted[4]{};
    static const char* const filenames[] = {"lobby-camera-menu.png", "lobby-camera-flight.png",
                                             "lobby-camera-selection.png", "lobby-camera-credits.png"};
    if (attempted[phase]) return;
    attempted[phase] = true;
    D3DSURFACE_DESC desc{};
    const HRESULT result = RF455_SaveLoginBackbuffer(filenames[phase], desc);
    char event[96];
    std::snprintf(event, sizeof(event), "RF455 LobbyCamera:%u:%08lX:%ux%u", phase,
                  static_cast<unsigned long>(result), desc.Width, desc.Height);
    OutputDebugStringA(event);
}
