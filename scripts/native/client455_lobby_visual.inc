#include "client455_lobby_post.h"
#include "client455_lobby_material.h"
#include "client455_lobby_sky.h"
#include "client455_lobby_shadow.h"
#include "client455_render_diagnostics.h"
#include "userinterface/gamewindow/etcwin/guioptionwindow.h"
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
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
    void begin(){RF455_DiagnosticsBeginFrame(GetD3dDevice());LARGE_INTEGER now;QueryPerformanceFrequency(&frequency);QueryPerformanceCounter(&now);if(started.QuadPart){intervalTotal+=double(now.QuadPart-started.QuadPart)*1000/double(frequency.QuadPart);++intervals;}started=now;}
    void end(){RF455_DiagnosticsCpuEnd();LARGE_INTEGER ended;QueryPerformanceCounter(&ended);total+=double(ended.QuadPart-started.QuadPart)*1000/double(frequency.QuadPart);++frames;}
} lobbyFrameSample455;
void RF455_DrawLobbyDiagnostics(){
    const auto info=RF455_GetRenderDiagnostics();const auto shadow=RF455_GetLobbyShadowTelemetry();
    const auto post=RF455_GetLobbyPostTelemetry();
    // User-requested debug HUD, default visible. No session/account information.
    static DWORD checked=0;static bool visible=true;const DWORD now=GetTickCount();
    if(now-checked>1000){visible=GetPrivateProfileIntA("HUD","LobbyDiagnostics",1,".\\R3Engine.ini")!=0;checked=now;}
    if(!visible||RF455_LobbyReferenceMode())return;
    wchar_t adapter[512]{};MultiByteToWideChar(CP_ACP,0,info.adapter,-1,adapter,512);
    wchar_t lines[7][640]{};
    swprintf_s(lines[0],L"FPS: %.1f   Frame: %.2f ms",info.fps,info.frameMs);
    swprintf_s(lines[1],L"%ls  [%ls]",adapter,info.hardware?L"Hardware":L"Software");
    swprintf_s(lines[2],L"%u x %u   MSAA %ux   CPU submit: %.2f ms",info.width,info.height,post.multisampleCount,info.cpuSubmissionMs);
    if(info.samples)swprintf_s(lines[3],L"GPU: %.2f ms   Space: %.2f   Shadows: %.2f   Post: %.2f",info.gpuMs[0],info.gpuMs[1],info.gpuMs[2],info.gpuMs[3]);
    else swprintf_s(lines[3],L"GPU timing: %ls",info.gpuTimingSupported?L"warming up":L"unavailable");
    swprintf_s(lines[4],L"Shadow %u: BSP %u / actor %u   Pose age: %u frames",shadow.resolution,shadow.bspDraws,shadow.actorDraws,shadow.actorPoseAgeFramesMax);
    swprintf_s(lines[5],L"Shadow fit changes: %llu   GPU query errors: %llu",shadow.lightMatrixChanges,info.queryErrors);
    const DWORD outline=RF455_GetTextOutline();RF455_SetTextOutline(0xff091422);
    for(unsigned i=0;i<6;++i){float position[4]={18.f,float(info.height)*.5f-68.f+i*23.f,0,1};RF455_DrawText(position,lines[i],i?0xffc9dfed:0xff80e7ff,0x10,1.1f);}
    RF455_SetTextOutline(outline);
}
void RF455_SaveLobbyVisualMetadata() {
    static const bool diagnostics=[] {char text[8]{};return GetEnvironmentVariableA("RF455_LOBBY_DIAGNOSTICS",text,sizeof(text))&&text[0]=='1';}();
    if(!RF455_LobbyReferenceMode()&&!diagnostics)return;
    // One fixed receipt per preview; updated at most once per second.
    static DWORD previous=0;const DWORD now=GetTickCount();if(now-previous<1000)return;previous=now;
    const auto diag=RF455_GetRenderDiagnostics();const auto shadows=RF455_GetLobbyShadowTelemetry();
    if(FILE* file=std::fopen("lobby-diagnostics.json","wb")){
        // Driver descriptions normally contain ASCII letters; escape JSON delimiters.
        std::string adapter;for(const char*c=diag.adapter;*c;++c){if(*c=='"'||*c=='\\')adapter+='\\';if(static_cast<unsigned char>(*c)>=32)adapter+=*c;}
        std::fprintf(file,"{\"adapter\":\"%s\",\"vendor\":%u,\"device\":%u,\"hardware\":%s,\"width\":%u,\"height\":%u,\"fps\":%.3f,\"frame_ms\":%.4f,\"cpu_submit_ms\":%.4f,",
            adapter.c_str(),diag.vendorId,diag.deviceId,diag.hardware?"true":"false",diag.width,diag.height,diag.fps,diag.frameMs,diag.cpuSubmissionMs);
        std::fprintf(file,"\"section_names\":[\"frame\",\"sky\",\"shadow\",\"post\",\"land_including_sky\",\"land_alpha\",\"actors_effects\",\"ui\"],\"gpu_ms\":[");
        for(unsigned i=0;i<8;++i)std::fprintf(file,"%s%.4f",i?",":"",diag.gpuMs[i]);
        std::fprintf(file,"],\"cpu_ms\":[");for(unsigned i=0;i<8;++i)std::fprintf(file,"%s%.4f",i?",":"",diag.cpuMs[i]);
        std::fprintf(file,"],\"game_loop_ms\":%.4f,\"present_cpu_ms\":%.4f,\"lobby_update_ms\":%.4f,",diag.outsideMs[0],diag.outsideMs[1],diag.outsideMs[2]);
        std::fprintf(file,"\"present\":{\"result\":%ld,\"interval\":%u,\"windowed\":%s,\"swap_effect\":%u,\"back_buffers\":%u,\"refresh_hz\":%u},",
            diag.presentParametersResult,diag.presentInterval,diag.windowed?"true":"false",diag.swapEffect,diag.backBuffers,diag.refreshHz);
        std::fprintf(file,"\"gpu_samples\":%llu,\"query_errors\":%llu,\"discarded_frames\":%llu,\"shadow_matrix_changes\":%llu,\"shadow_fit_expansions\":%llu,\"actor_pose_age_frames\":%u,\"actor_pose_age_ms\":%u}\n",
            diag.samples,diag.queryErrors,diag.discardedFrames,shadows.lightMatrixChanges,shadows.fitExpansions,shadows.actorPoseAgeFramesMax,shadows.actorPoseAgeMsMax);std::fclose(file);
    }
    const auto post=RF455_GetLobbyPostTelemetry();const auto material=RF455_GetLobbyMaterialTelemetry();const auto sky=RF455_GetLobbySkyTelemetry();const auto shadow=RF455_GetLobbyShadowTelemetry();
    if(FILE* file=std::fopen("lobby-visual.json","wb")) {
        std::fprintf(file,"{\"authored_material_ready\":%s,\"authored_material_binds\":%llu,\"authored_material_bytes\":%llu,",
            material.authoredReady?"true":"false",material.authoredBinds,material.authoredTextureBytes);
        std::fprintf(file,"\"authored_wall_binds\":%llu,\"authored_panel_binds\":%llu,\"authored_hull_binds\":%llu,",
            material.authoredSetBinds[0],material.authoredSetBinds[1],material.authoredSetBinds[2]);
        std::fprintf(file,"\"sky_detail_bytes\":%llu,",sky.detailTextureBytes);
        std::fprintf(file,"\"post_enabled\":%s,\"post_available\":%s,\"post_frames\":%llu,\"passes\":%u,\"format\":%u,\"msaa\":%u,\"estimated_post_vram_bytes\":%llu,\"post_error\":%ld,\"post_stage\":\"%s\",\"material_binds\":%llu,\"material_skips\":%llu,\"material_errors\":%llu,\"cpu_render_submission_ms_mean\":%.4f,\"camera_seconds\":%.3f,\"camera_view\":[",
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
        // Require fresh assignments after recreation, not historical counters.
        RF455_ResetLobbyMaterialTelemetry();
        break;
    case 4:
        {const auto post=RF455_GetLobbyPostTelemetry();const auto sky=RF455_GetLobbySkyTelemetry();
        const auto material=RF455_GetLobbyMaterialTelemetry();
        ok=!initial||(post.available&&post.error==S_OK&&post.passCount==11&&sky.ready&&sky.detailTextureBytes>0&&sky.errors==0&&
            material.authoredReady&&material.authoredTextureBytes>0&&
            material.authoredSetBinds[0]>0&&material.authoredSetBinds[1]>0&&material.authoredSetBinds[2]>0&&material.errors==0);}
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
