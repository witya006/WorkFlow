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
#include "client455_tutorial_intro.h"
#include "client455_fullscreen_effect.h"
#include "jerror.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <memory>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct ScreenMember{using Type=CGUIScreen CMainApp::*;friend Type access(ScreenMember);};template struct MemberAccess<ScreenMember,&CMainApp::m_cScreen>;
static void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
static unsigned warnings=0;
static void errorMessage(char* text){std::fprintf(stderr,"engine-error:%s\n",text);std::exit(2);}
static void warningMessage(char* text){if(warnings++<16)std::fprintf(stderr,"engine-warning:%s\n",text);}
static void phase(const char* text){std::fprintf(stderr,"phase:%s\n",text);std::fflush(stderr);}
static unsigned capture(const char* name){
    auto* device=GetD3dDevice();IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");
    D3DVIEWPORT9 viewport={};device->GetViewport(&viewport);check(viewport.Width==640&&viewport.Height==480,"viewport");FILE* output=std::fopen(name,"wb");check(output!=nullptr,"capture file");unsigned changed=0;
    for(unsigned y=viewport.Y;y<viewport.Y+480;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+viewport.X;std::fwrite(row,4,640,output);for(unsigned x=0;x<640;++x)changed+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(output);memory->UnlockRect();memory->Release();target->Release();return changed;
}
struct Selection{unsigned ordinal,start,end;float tick;};
struct Fade{bool out;float seconds;};
// Stage/QBI/follow/camera-control callbacks remain explicit recordings. Fullscreen
// mode/density now call the real engine backend;camera/fade/UI/world are real.
struct Host final : RF455TutorialIntroCameraHost {
    CGUIScreen& screen;bool blocked=false;unsigned scripts=0,follows=0,applied=0,engineFlag=0,control=6;float engineFloat=0;
    std::vector<Selection> selections;std::vector<Fade> fades;std::vector<unsigned> finishOrder;
    explicit Host(CGUIScreen& value):screen(value){}
    void selectCamera(std::uint32_t ordinal,std::uint32_t start,std::uint32_t end,std::uint32_t flag)override{check(flag==1,"final-stop");selections.push_back({ordinal,start,end,R3GetTime()});RF455TutorialIntroCameraHost::selectCamera(ordinal,start,end,flag);}
    void applyCameraMatrix(float matrix[4][4])override{++applied;RF455TutorialIntroCameraHost::applyCameraMatrix(matrix);for(unsigned i=0;i<16;++i){check(std::isfinite(viewMatrix()[i]),"finite real camera matrix");check(std::fabs(viewMatrix()[i]-matrix[i/4][i%4])<0.00001f,"camera backend engine layout/zero-rotation view");}if(applied<=2)std::fprintf(stderr,"camera:%u raw=%.6g,%.6g,%.6g,%.6g actual=%.6g,%.6g,%.6g,%.6g pos=%.6g,%.6g,%.6g\n",applied,matrix[0][0],matrix[1][1],matrix[2][2],matrix[3][3],viewMatrix()[0],viewMatrix()[5],viewMatrix()[10],viewMatrix()[15],position()[0],position()[1],position()[2]);}
    void fadeIn(std::uint32_t color,float seconds,float density)override{check(!color&&density==1,"fade-in arguments");fades.push_back({false,seconds});if(seconds==5)finishOrder.push_back(2);RF455TutorialIntroCameraHost::fadeIn(color,seconds,density);}
    void fadeOut(std::uint32_t color,float seconds,float density)override{check(!color&&density==1,"fade-out arguments");fades.push_back({true,seconds});if(!seconds)finishOrder.push_back(1);RF455TutorialIntroCameraHost::fadeOut(color,seconds,density);}
    void setEngineRenderFlag(std::uint32_t flag)override{RF455TutorialIntroCameraHost::setEngineRenderFlag(flag);engineFlag=flag;check(GetStateFullScreenEffect()==flag,"real fullscreen mode binding");if(!flag)finishOrder.push_back(8);}
    void setEngineFloat8CE9D0(float value)override{RF455TutorialIntroCameraHost::setEngineFloat8CE9D0(value);engineFloat=value;check(RF455_GetFullScreenEffectDensity()==value,"real fullscreen density binding");if(value==0.25f)finishOrder.push_back(9);}
    std::uint32_t cameraControlFlags()override{return control;}
    void setCameraControlFlags(std::uint32_t value)override{control=value;if(!(value&1))finishOrder.push_back(10);}
    void blockStageInput(bool value)override{blocked=value;if(!value)finishOrder.push_back(3);}
    void showScreen(bool value)override{screen.Show(value?TRUE:FALSE);if(value)finishOrder.push_back(4);}
    void showMouse(bool value)override{screen.GetMouse()->Show(value?TRUE:FALSE);if(value)finishOrder.push_back(5);}
    void startBoardScript()override{check(blocked==false&&screen.IsShow()&&screen.GetMouse()->IsShow(),"finish ordering before script");++scripts;finishOrder.push_back(6);}
    void followAvatarCamera()override{++follows;finishOrder.push_back(11);}
};
static void draw(CLevel& level,Host& host){
    Vector3f position;std::memcpy(position,host.position(),sizeof(position));D3DXMATRIX matrix;std::memcpy(&matrix,host.viewMatrix(),64);level.SetCameraPos(position);level.SetViewMatrix(&matrix);level.FrameMove();
    check(R3BeginScene()!=FALSE,"real R3BeginScene");R3ClearFrameBuffer();level.DrawSkyBoxRender();level.DrawMapRender();level.DrawMapEntitiesRender();FullScreenEffect();DrawFadeScreen();R3EndScene();
}
static void drawFadeOnly(){auto* device=GetD3dDevice();check(SUCCEEDED(device->BeginScene()),"fade begin");DrawFadeScreen();check(SUCCEEDED(device->EndScene()),"fade end");}
static int run(const char* race){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetErrorMessageProc(errorMessage);SetWarningMessageProc(warningMessage);auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(state->MapPath,".\\Map\\");std::strcpy(state->EntityPath,".\\Map\\Entity\\");check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    unsigned raceByte=0;if(!std::strcmp(race,"cora"))raceByte=2;else if(!std::strcmp(race,"accretia"))raceByte=4;else check(!std::strcmp(race,"bellato"),"race");
    CAvatar avatar;auto* savedAvatar=g_pAvatar;avatar.SetRace(BYTE(raceByte));avatar.SetClientStage455(2);g_pAvatar=&avatar;auto& screen=g_MainApp.*access(ScreenMember{});auto* savedScreen=g_pUiScreen;g_pUiScreen=&screen;
    for(unsigned value=0;value<6;++value)check(RF455_GetTutorialIntroSequence(BYTE(value))==RF455_GetTutorialIntroSequence(BYTE(value&~1u)),"race grouping");check(!RF455_GetTutorialIntroSequence(6)&&!RF455_GetTutorialIntroSequence(255),"invalid race domain");
    unsigned captures=0,frames=0,applied=0,selected=0,fadeOuts=0;int memoryBefore=GetDmallocSize(),memoryAfter=0;const auto* sequence=RF455_GetTutorialIntroSequence(avatar.GetRace());FILE* trace=std::fopen("trace.jsonl","wb");check(trace!=nullptr,"trace");
    {
        CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);check(land->Create()!=0,"land create");char path[260];std::sprintf(path,".\\Map\\%s\\%s.bsp",race,race);check(land->LoadLevel(path)!=0,"real land load");phase("world-loaded");
        Host host(screen);RF455TutorialIntro intro;R3SetTime(0);R3SetLoopTime(0.25f);SetFadeIn(0,2,1);check(intro.load(avatar.GetRace(),host),"real intro load");check(host.blocked&&!screen.IsShow()&&!screen.GetMouse()->IsShow()&&host.control==7&&host.engineFlag==0x80000000u&&host.engineFloat==0.15f,"intro start bindings");
        std::vector<bool> captured(sequence->count,false);bool skip=false;
        for(unsigned tick=0;tick<800&&intro.active();++tick){
            R3SetTime(tick*0.25f);intro.frame(host,skip);++frames;
            std::fprintf(trace,"{\"tick\":%.9g,\"ordinal\":%u,\"pending\":%u,\"camera_seconds\":%.9g,\"fading\":%s,\"active\":%s,\"applied\":%u}\n",double(R3GetTime()),intro.ordinal(),intro.pending(),double(host.cameraSeconds()),host.fading()?"true":"false",intro.active()?"true":"false",host.applied);
            draw(*land->GetLevel(),host);if(!tick)capture("debug-first.bgra");
            if(intro.active()&&intro.ordinal()<sequence->count&&!captured[intro.ordinal()]&&host.cameraSeconds()*30.0>=sequence->segments[intro.ordinal()].start+30){std::sprintf(path,"cut-%02u.bgra",intro.ordinal());check(capture(path)>100,"real cut pixels");captured[intro.ordinal()]=true;++captures;}
        }
        check(!intro.active()&&host.scripts==1&&host.follows==1&&intro.ordinal()==sequence->count,"natural intro completion");check(captures==sequence->count&&host.selections.size()==sequence->count,"all real cameras reached and captured");
        for(unsigned index=0;index<sequence->count;++index){const auto& row=host.selections[index];const auto& expected=sequence->segments[index];check(row.ordinal==index&&row.start==expected.start&&row.end==expected.end,"ordinal and interval,not record label");}
        for(const auto& fade:host.fades)fadeOuts+=fade.out&&fade.seconds==2;check(fadeOuts==sequence->count,"one fade-out per cut");check(host.finishOrder==std::vector<unsigned>({1,2,3,4,5,6,8,9,10,11}),"full finish call order and same-frame follow");check(host.control==6&&host.engineFloat==0.25f,"unrelated control bits preserved");applied=host.applied;selected=unsigned(host.selections.size());
        Host skipped(screen);RF455TutorialIntro skipIntro;R3SetTime(250);check(skipIntro.load(avatar.GetRace(),skipped),"skip intro load");skip=true;skipIntro.frame(skipped,skip);check(skipIntro.active()&&!skip&&skipIntro.ordinal()==0xffff&&skipped.scripts==0,"skip consumed after camera,completion deferred");skipIntro.frame(skipped,skip);check(!skipIntro.active()&&skipped.scripts==1&&skipped.follows==1,"skip finish on following tick");
        check(skipIntro.load(avatar.GetRace(),skipped)&&skipIntro.ordinal()==0xffff,"reload retains counters");skipIntro.frame(skipped,skip);check(!skipIntro.active()&&skipped.scripts==2,"retained sentinel finishes reloaded intro");skipIntro.initCounters();check(!skipIntro.ordinal()&&!skipIntro.pending(),"explicit init resets only counters");
        // Drive the actual fade-out wait/completion on a controlled engine clock.
        R3SetTime(300);SetFadeOut(0,2,1);check(IsFading(),"fade starts");R3SetTime(301);drawFadeOnly();check(IsFading(),"fade wait");R3SetTime(303);drawFadeOnly();check(!IsFading(),"real fade completion");
        check(land->Destroy()!=0&&!g_pLevel,"real level release");g_pCamera=nullptr;
    }
    std::fclose(trace);memoryAfter=GetDmallocSize();check(memoryBefore==memoryAfter,"world and intro camera Dmalloc balance");g_pAvatar=savedAvatar;g_pUiScreen=savedScreen;g_MainApp.ReleaseR3D3D();ReleaseR3Engine();phase("released");
    FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result");std::fprintf(output,"{\"status\":\"PASS\",\"selected\":%u,\"captures\":%u,\"frames\":%u,\"applied\":%u,\"fade_outs\":%u,\"warnings\":%u,\"memory_before\":%d,\"memory_after\":%d,\"real_camera_fade_screen_mouse_avatar_world\":true,\"deferred_skip\":true,\"reload_retains_counters\":true,\"full_stage_QBI_engine_controls\":false}\n",selected,captures,frames,applied,fadeOuts,warnings,memoryBefore,memoryAfter);std::fclose(output);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception:%08lX RVA:%08lX\n",info->ExceptionRecord->ExceptionCode,reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress)-reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(const char* race){__try{return run(race);}__except(filter(GetExceptionInformation())){return 99;}}
int main(int argc,char** argv){try{check(argc==2,"race argument");return guarded(argv[1]);}catch(const std::exception& error){std::fprintf(stderr,"Tutorial intro:%s\n",error.what());return 1;}}
