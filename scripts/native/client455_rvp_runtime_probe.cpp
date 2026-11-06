#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "Character.h"
#include "client455_rvp_runtime.h"
#include "client455_movie_state.h"
#include "client455_fullscreen_effect.h"
#include <client455_normal_renderer_math.h>
#include "RTMovie.h"
#include "r3enginekernel.h"
#include "jmalloc.h"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;

static unsigned warnings=0;
static void check(bool value,const char* message){if(!value)throw std::runtime_error(message);}
static void message(char* text){std::fprintf(stderr,"RVP engine:%s\n",text);}
static void warning(char* text){++warnings;message(text);}
static void capture(const char* name) {
    auto* device=GetD3dDevice();IDirect3DSurface9* surface=nullptr;IDirect3DSurface9* copy=nullptr;
    check(SUCCEEDED(device->GetBackBuffer(0,0,D3DBACKBUFFER_TYPE_MONO,&surface)),"framebuffer");
    D3DSURFACE_DESC desc;surface->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr)),"readback allocation");
    check(SUCCEEDED(device->GetRenderTargetData(surface,copy)),"GPU readback");
    D3DLOCKED_RECT lock;check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"readback lock");
    FILE* file=std::fopen(name,"wb");check(file!=nullptr,"capture file");
    for(unsigned y=0;y<480;++y)check(std::fwrite(static_cast<char*>(lock.pBits)+y*lock.Pitch,4,640,file)==640,"capture row");
    std::fclose(file);copy->UnlockRect();copy->Release();surface->Release();
}
static void draw(CLevel& level) {
    check(R3BeginScene()!=FALSE,"scene begin");R3ClearFrameBuffer();
    level.DrawSkyBoxRender();level.DrawMapRender();level.DrawMapEntitiesRender();
    FullScreenEffect();DrawFadeScreen();R3EndScene();
}
static int run(const char* race) {
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    InitR3Engine();SetErrorMessageProc(message);SetWarningMessageProc(warning);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;
    state->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(state->MapPath,".\\Map\\");
    std::strcpy(state->EntityPath,".\\Map\\Entity\\");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    state->mScreenXsize=640;state->mScreenYsize=480;R3SetViewPort(0,0,640,480);
    unsigned selected=0,fadeIns=0,fadeOuts=0,ticks=0;int before=0,after=0;
    {
        ChInterface outer;outer.InitCharacter(GetD3dDevice());
        before=GetDmallocSize();
        {
            CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);check(land->Create()!=0,"land create");
            char path[256];std::sprintf(path,".\\Map\\%s\\%s.bsp",race,race);
            R3SetTime(0);RTMoviePause(FALSE);check(land->LoadLevel(path)!=0,"world load");
            check(IsLoadedRTMovie()&&IsLoadedRTCamera()&&IsRTMoviePlaying(),"ordinary CLevel created actual RVP");
            auto initial=RF455_RvpView();check(!initial.limitation[0]&&initial.tracks>20&&RF455_GetMovieState()==4,"loaded RVP contract");
            auto* level=land->GetLevel();check(level!=nullptr,"level owner");
            //Real float setter reproduces8D1D90, including its subtraction of
            //playStart/30 (and therefore the observed double-start offset).
            auto& ani=level->mAutoAniCam;ani.SetPrePlayCamera(0,31,361,1);R3SetTime(20);
            ani.SetNowFrame(1.75f);R3SetTime(20.125f);float matrix[4][4];ani.PlayAniCamera(matrix,1,FALSE);
            check(std::abs(ani.GetNowFrame()-(1.75f+.125f+2.f*31.f/30.f))<0.00001f,"float setter and455 start-offset rule");
            R3SetTime(0);RF455_SetMovieState(0);RTMovieStartPlay(TRUE);
            check(RF455_RvpView().cameraSelections>0,"prepare executes actual camera event");
            FILE* trace=std::fopen("rvp-trace.jsonl","wb");check(trace!=nullptr,"trace");
            for(unsigned tick=0;tick<800&&IsRTMoviePlaying();++tick) {
                R3SetTime(tick*.25f);R3SetLoopTime(.25f);level->FrameMove();++ticks;
                const auto view=RF455_RvpView();
                std::fprintf(trace,"{\"tick\":%u,\"seconds\":%.9g,\"cursor\":%zu,\"selected\":%u,\"playing\":%s,\"flags\":%u}\n",tick,view.seconds,view.cursor,view.cameraSelections,view.playing?"true":"false",RF455_GetMovieState());
                draw(*level);if(tick==20)capture("rvp-scene.bgra");
            }
            std::fclose(trace);const auto done=RF455_RvpView();
            check(!done.playing&&done.movieLoaded&&(RF455_GetMovieState()&4),"camera final-stop ends player");
            check(done.cursor==done.tracks,"all stock tracks consumed");
            check(RF455_GetFullScreenEffectDensity()==.25f,"completion resets density");
            selected=done.cameraSelections;fadeIns=done.fadeIns;fadeOuts=done.fadeOuts;draw(*level);capture("rvp-last.bgra");
            R3SetTime(0);RF455_SetMovieState(4);RTMovieStartPlay(TRUE);RTMoviePause(TRUE);
            R3SetTime(4.25f);RTMovieFrameMove();check(!IsRTMoviePlaying()&&RF455_RvpView().paused,"pause marks play false455");
            RTMoviePause(FALSE);RTMovieStartPlay(FALSE);check(IsRTMoviePlaying(),"explicit resume");
            RF455_AddMovieFlags(16);const auto suspended=RF455_RvpView();R3SetTime(9);RTMovieFrameMove();
            check(RF455_RvpView().seconds==suspended.seconds&&RF455_RvpView().cursor==suspended.cursor,"flag16 gate");
            RF455_RemoveMovieFlags(16);RTMovieFrameMove();check(RF455_RvpView().seconds!=suspended.seconds,"gate release");
            float view[4][4];Vector3f position;RTMoiveGetCameraMatrix(view);RTMoiveGetCameraPos(position);
            check(!std::memcmp(position,view[3],sizeof(position)),"real camera position/matrix getters");
            RTMovieRelease();check(&CRender::GetRender()==&outer,"renderer release before failed loads");
            char originalCamera[256];std::sprintf(originalCamera,".\\Map\\%s\\%s.cam",race,race);
            check(CopyFileA(originalCamera,"missing.cam",FALSE)!=FALSE,"camera-only fixture");
            RTMovieCreate("missing.rvp",level);check(!IsLoadedRTMovie()&&IsLoadedRTCamera(),"CAM exists without RVP");
            RTMovieStartPlay(TRUE);check(IsRTMoviePlaying(),"camera-only Start sets play before loaded check");
            SetStateFullScreenEffect(0x80000000u);RTMovieFrameMove();
            check(GetStateFullScreenEffect()==0x80000000u,"unloaded RVP cannot change render mode");RTMovieRelease();
            check(CopyFileA(originalCamera,"actors-open.cam",FALSE)!=FALSE,"actor fixture camera");
            FILE* unsupported=std::fopen("actors-open.rvp","wb");check(unsupported!=nullptr,"actor fixture");
            std::fputs("[Object] *unit unit.msh bone unit.bn collision [PrepareTrack] no_camera [Track]",unsupported);std::fclose(unsupported);
            RTMovieCreate("actors-open.rvp",level);
            check(!IsLoadedRTMovie()&&IsLoadedRTCamera()&&RF455_RvpView().limitation[0],"unfinished actor provider explicitly refused");
            RTMovieRelease();SetStateFullScreenEffect(0);
            //A final successful load makes the sticky-loaded Release case
            //observable through the actual CLand.Destroy path as well.
            char originalRvp[256];std::sprintf(originalRvp,".\\Map\\%s\\%s.rvp",race,race);
            RTMoviePause(FALSE);RTMovieCreate(originalRvp,level);check(IsLoadedRTMovie(),"reload after explicit refusal");
            check(land->Destroy()!=0&&!g_pLevel,"destroy actual level");g_pCamera=nullptr;
            check(!IsLoadedRTCamera()&&IsLoadedRTMovie(),"455 release keeps loaded scalar");
            check(&CRender::GetRender()==&outer,"nested renderer restores active outer owner");
        }
        after=GetDmallocSize();check(before==after,"world/camera Dmalloc release balance");
    }
    RF455_ReleaseNormalCharacterSharedResources();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* file=std::fopen("result.json","wb");check(file!=nullptr,"result");
    std::fprintf(file,"{\"status\":\"PASS\",\"selected\":%u,\"fade_ins\":%u,\"fade_outs\":%u,\"ticks\":%u,\"warnings\":%u,\"memory_before\":%d,\"memory_after\":%d,\"ordinary_RVP_created\":true,\"float_pause_clock\":true,\"flag16_gate\":true,\"nested_renderer_restored\":true,\"camera_only_and_explicit_refusal\":true,\"full_RVP_actor_audio\":false,\"full_Tutorial\":false}\n",selected,fadeIns,fadeOuts,ticks,warnings,before,after);
    std::fclose(file);return 0;
}
int main(int argc,char** argv){try{check(argc==2,"race argument");return run(argv[1]);}catch(const std::exception& error){std::fprintf(stderr,"RVP runtime:%s\n",error.what());return 1;}}
