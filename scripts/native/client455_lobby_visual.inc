#include "client455_lobby_post.h"
#include "client455_lobby_material.h"
#include "client455_lobby_sky.h"
#include "client455_lobby_shadow.h"
#include "userinterface/gamewindow/etcwin/guioptionwindow.h"
#include <cstdio>
#include <cstdlib>
#include <memory>
static HRESULT RF455_SaveLoginBackbuffer(const char*,D3DSURFACE_DESC&);
void RF455_ObserveLobbySlots();

namespace {
std::unique_ptr<CGUIOptionWindow> lobbyOptions455;
CGUIOptionWindow* RF455_LobbyOptions(){return lobbyOptions455.get();}
bool RF455_LobbyReferenceMode() {
    static const bool value=[] {char text[8]{};return GetEnvironmentVariableA("RF455_LOBBY_REFERENCE",text,sizeof(text))&&text[0]=='1';}();
    return value;
}
float RF455_LobbyReferenceSeconds() {
    char text[32]{};
    const float value=GetEnvironmentVariableA("RF455_LOBBY_CAMERA_SECONDS",text,sizeof(text))?float(std::atof(text)):3.2f;
    return value>=0&&value<=30?value:3.2f;
}
void RF455_InstallLobbyVisual(CGUIScreen& screen) {
    RF455_SetLobbyPostEnabled(GetPrivateProfileIntA("RenderState","LobbyPost",1,".\\R3Engine.ini")!=0);
    lobbyOptions455=std::make_unique<CGUIOptionWindow>();
    lobbyOptions455->SetActions455({});
    lobbyOptions455->Init();
    lobbyOptions455->SetLogoutRestricted455(TRUE);
    screen.Add(lobbyOptions455.get());
}
void RF455_RemoveLobbyVisual(CGUIScreen& screen) {
    RF455_InvalidateLobbyShadows(true);
    if(!lobbyOptions455)return;
    if(lobbyOptions455->IsShow())lobbyOptions455->Close();
    if(screen.GetCapture455()==lobbyOptions455.get())screen.SetCapture455(nullptr);
    screen.Remove(lobbyOptions455.get());
    lobbyOptions455.reset();
}
void RF455_OpenLobbySettings() {
    auto* options=RF455_LobbyOptions();if(!options)return;
    if(options->IsShow()){options->Close();return;}
    options->Open();
    options->SetPos((_GetUIScreen()->GetSizeX()-options->GetSizeX())/2,
                    (_GetUIScreen()->GetSizeY()-options->GetSizeY())/2);
    options->SetPage455(CGUIOptionWindow::GraphicsPage);
    _GetUIScreen()->SetCapture455(options);
}
struct RF455LobbyFrameSample {
    LARGE_INTEGER started{},frequency{};
    double total=0,intervalTotal=0;unsigned frames=0,intervals=0;
    void begin(){LARGE_INTEGER now;QueryPerformanceFrequency(&frequency);QueryPerformanceCounter(&now);if(started.QuadPart){intervalTotal+=double(now.QuadPart-started.QuadPart)*1000/double(frequency.QuadPart);++intervals;}started=now;}
    void end(){LARGE_INTEGER ended;QueryPerformanceCounter(&ended);total+=double(ended.QuadPart-started.QuadPart)*1000/double(frequency.QuadPart);++frames;}
} lobbyFrameSample455;
void RF455_SaveLobbyVisualMetadata() {
    static const bool diagnostics=[] {char text[8]{};return GetEnvironmentVariableA("RF455_LOBBY_DIAGNOSTICS",text,sizeof(text))&&text[0]=='1';}();
    if(!RF455_LobbyReferenceMode()&&!diagnostics)return;
    // One fixed receipt per preview; updated at most once per second.
    static DWORD previous=0;const DWORD now=GetTickCount();if(now-previous<1000)return;previous=now;
    const auto post=RF455_GetLobbyPostTelemetry();const auto material=RF455_GetLobbyMaterialTelemetry();const auto sky=RF455_GetLobbySkyTelemetry();const auto shadow=RF455_GetLobbyShadowTelemetry();
    if(FILE* file=std::fopen("lobby-visual.json","wb")) {
        std::fprintf(file,"{\"post_enabled\":%s,\"post_available\":%s,\"post_frames\":%llu,\"passes\":%u,\"format\":%u,\"msaa\":%u,\"estimated_post_vram_bytes\":%llu,\"post_error\":%ld,\"post_stage\":\"%s\",\"material_binds\":%llu,\"material_skips\":%llu,\"material_errors\":%llu,\"cpu_render_submission_ms_mean\":%.4f,\"camera_seconds\":%.3f,\"camera_view\":[",
            post.enabled?"true":"false",post.available?"true":"false",post.completedFrames,post.passCount,unsigned(post.colorFormat),post.multisampleCount,
            post.estimatedVideoBytes,long(post.error),post.errorStage,material.binds,material.skips,material.errors,
            lobbyFrameSample455.frames?lobbyFrameSample455.total/lobbyFrameSample455.frames:0,RF455_LobbyReferenceSeconds());
        const float* matrix=&GetR3State()->mMatView._11;for(unsigned i=0;i<16;++i)std::fprintf(file,"%s%.8g",i?",":"",matrix[i]);
        std::fprintf(file,"],\"frame_interval_ms_mean\":%.4f,\"material_error\":%ld,\"material_stage\":\"%s\",\"sky_ready\":%s,\"sky_draws\":%llu,\"sky_errors\":%llu,\"sky_error\":%ld,\"sky_stage\":\"%s\",\"sky_volume_bytes\":%llu,\"shadow_ready\":%s,\"shadow_resolution\":%u,\"shadow_bsp_draws\":%u,\"shadow_actor_draws\":%u,\"shadow_errors\":%llu,\"shadow_stage\":\"%s\"}\n",
            lobbyFrameSample455.intervals?lobbyFrameSample455.intervalTotal/lobbyFrameSample455.intervals:0,long(material.error),material.errorStage,
            sky.ready?"true":"false",sky.draws,sky.errors,long(sky.error),sky.stage,sky.volumeTextureBytes,
            shadow.ready?"true":"false",shadow.resolution,shadow.bspDraws,shadow.actorDraws,shadow.errors,shadow.stage);std::fclose(file);
    }
}
void RF455_ObserveLobbySettings(){
    static const bool enabled=[] {char text[8]{};return GetEnvironmentVariableA("RF455_LOBBY_SETTINGS_TEST",text,sizeof(text))&&text[0]=='1';}();
    if(!enabled||!RF455_LobbyReferenceMode()||!lobbyOptions455)return;
    static DWORD first=GetTickCount(),next=first+2200;static unsigned phase=0;
    static bool passed=true,initial=false;const auto now=GetTickCount();
    if(phase>=6||now<next)return;next=now+500;
    auto& options=*lobbyOptions455;
    auto click=[&](CGUIObject& button){_mouse_event event{};event.source=&button;event.id=MOUSE_CLICKED;options.MouseEvent(event);};
    auto capture=[&](const char* name){D3DSURFACE_DESC desc{};return SUCCEEDED(RF455_SaveLoginBackbuffer(name,desc))&&desc.Width==1920&&desc.Height==1080;};
    bool ok=true;
    switch(phase){
    case 0:
        initial=RF455_LobbyPostEnabled();
        SendMessage(_GetUIScreen()->GetHWND(),WM_SYSKEYDOWN,VK_F10,0);
        ok=options.IsShow()&&options.SelectedPage455()==CGUIOptionWindow::GraphicsPage;
        break;
    case 1:
        ok=capture("lobby-settings.png");
        click(options.LobbyQuality455(initial?0:1));
        ok=ok&&RF455_LobbyPostEnabled()==initial;
        click(options.CancelButton455());
        ok=ok&&!options.IsShow()&&RF455_LobbyPostEnabled()==initial;
        options.Open();options.SetPage455(CGUIOptionWindow::GraphicsPage);
        click(options.LobbyQuality455(initial?0:1));
        ok=options.Apply455()&&ok;options.Close();
        ok=ok&&RF455_LobbyPostEnabled()!=initial&&
            bool(GetPrivateProfileIntA("RenderState","LobbyPost",-1,".\\R3Engine.ini"))!=initial;
        break;
    case 2:
        ok=capture("lobby-switched.png");
        options.Open();click(options.LobbyQuality455(initial?1:0));
        ok=options.Apply455()&&ok;options.Close();
        break;
    case 3:
        ok=capture("lobby-restored.png")&&RF455_LobbyPostEnabled()==initial&&
            bool(GetPrivateProfileIntA("RenderState","LobbyPost",-1,".\\R3Engine.ini"))==initial;
        RF455_ReleaseLobbyShadows();RF455_ReleaseLobbySky();RF455_ReleaseLobbyMaterial();RF455_ReleaseLobbyPost();
        break;
    case 4:
        {const auto post=RF455_GetLobbyPostTelemetry();const auto sky=RF455_GetLobbySkyTelemetry();ok=!initial||(post.available&&post.error==S_OK&&post.passCount==11&&sky.ready&&sky.errors==0);}
        break;
    case 5:
        ok=!options.IsShow();break;
    }
    passed=passed&&ok;++phase;
    if(FILE* file=std::fopen("lobby-settings-test.json","wb")){
        std::fprintf(file,"{\"completed_phases\":%u,\"passed\":%s,\"last_phase_passed\":%s,\"initial_enhanced\":%s}\n",phase,passed?"true":"false",ok?"true":"false",initial?"true":"false");std::fclose(file);
    }
}
}
