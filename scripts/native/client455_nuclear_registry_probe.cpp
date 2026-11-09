#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "gameprogress/cgp_maingame.h"
#include "addcodebyjang/effectcore.h"
#include "addcodebyjang/effectentitylist.h"
#include "client455_nuclear_registry.h"
#include "client455_message_dispatch.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_rvp_effects.h"
#include <client455_normal_renderer_math.h>
#include "RTMovie.h"
#include "mss.h"
#include <cstdio>
#include <algorithm>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <vector>
#if defined(RF455_TEXTURE_LIFETIME_PROBE)
#include "client455_texture_lifetime_trace.h"
#endif
#if defined(RF455_QUAKE_PROBE)
#include "client455_quake_trace.h"
#endif
extern CMainApp g_MainApp;
static unsigned checks=0,warnings=0;
static void advanceEffects119(){
    FrameMoveAllEffectsList();
#if defined(RF455_QUAKE_PROBE)
    RF455_QuakeFrame119();
#endif
}
static void check(bool ok,const char* why){++checks;if(!ok)throw std::runtime_error(why);}
static void phase(const char* name){std::fprintf(stderr,"phase:%s checks=%u\n",name,checks);std::fflush(stderr);}
static void warning(char* value){++warnings;
#if defined(RF455_TEXTURE_LIFETIME_PROBE)
    RF455_TextureWarning118(value);
#endif
    std::fprintf(stderr,"warning:%s\n",value);}
static void error(char* value){throw std::runtime_error(value);}
static bool same(const float* a,const float* b){return !std::memcmp(a,b,12);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
struct ProgressMember{using Type=CGameProgress* CMainApp::*;friend Type access(ProgressMember);};
template struct MemberAccess<ProgressMember,&CMainApp::m_pGameProgress>;
struct Scope {
    CMainApp* app=g_pMainApp;CGameProgress* progress=g_MainApp.*access(ProgressMember{});BYTE id=g_MainApp.GetGameProgressID();CGUIChatWindow* chat=g_pUiChatWindow;CGUIScreen* screen=g_pUiScreen;
    Scope(){g_pMainApp=&g_MainApp;g_pUiScreen=&gScreen;check((g_MainApp.*access(NetworkMember{})).Create()!=0,"actual offline network Create");}
    void bind(CGameProgress* object){g_MainApp.SetGameProgressID(object?GPI_MAIN_GAME:0);g_MainApp.*access(ProgressMember{})=object;}
    ~Scope(){g_pUiChatWindow=chat;g_MainApp.*access(ProgressMember{})=progress;g_MainApp.SetGameProgressID(id);g_pMainApp=app;g_pUiScreen=screen;(g_MainApp.*access(NetworkMember{})).Destroy();}
};
static void clockCases(){
    alignas(RF455NuclearRecord) BYTE bytes[32];std::memset(bytes,0xa5,sizeof(bytes));auto* record=new(bytes)RF455NuclearRecord;
    check(!record->launch&&!record->impact&&!record->radar&&!record->countdown,"record known DWORD lanes zero");float zeros[3]={};check(same(record->position,zeros),"record float lanes zero");
    check(bytes[12]==0xa5&&bytes[13]==0xa5&&bytes[14]==0xa5&&bytes[15]==0xa5,"record unknown DWORD12 untouched");record->~RF455NuclearRecord();
    RF455NuclearCountdownClock clock;DWORD now=0,count=0;unsigned calls=0;std::vector<DWORD> emitted;
    auto get=[&](){++calls;return now;};auto emit=[&](DWORD value){emitted.push_back(value);};
    clock.Tick(count,get,emit);count=0xffffffff;clock.Tick(count,get,emit);count=0x80000000;clock.Tick(count,get,emit);check(!clock.initialized&&!calls&&emitted.empty(),"signed nonpositive counts do not initialize or read time");
    count=3;clock.Tick(count,get,emit);check(clock.initialized&&calls==2&&count==3&&emitted.empty(),"first positive count initializes and reads second clock");
    now=999;clock.Tick(count,get,emit);check(count==3&&emitted.empty(),"999ms no decrement");now=1000;clock.Tick(count,get,emit);check(count==2&&emitted.size()==1&&emitted[0]==3,"1000ms decrements once and emits old count");
    now=10000;clock.Tick(count,get,emit);check(count==1&&emitted.size()==2&&emitted.back()==2&&clock.last==10000,"large elapsed does not catch up");
    DWORD later=4;clock.Tick(later,get,emit);check(later==4&&emitted.size()==2,"later record shares consumed tick");
    now=11000;clock.Tick(count,get,emit);clock.Tick(later,get,emit);check(count==0&&later==4&&emitted.back()==1,"first sorted positive record consumes next tick");
    now=12000;clock.Tick(count,get,emit);clock.Tick(later,get,emit);check(!count&&later==3&&emitted.back()==4,"zero first record permits later record");
    clock.last=0xfffffff0;now=0x3d7;clock.Tick(later,get,emit);check(later==3,"wrap 999ms");now=0x3d8;clock.Tick(later,get,emit);check(later==2&&emitted.back()==3,"unsigned clock wrap1000ms");
    count=0x7fffffff;now+=1000;clock.Tick(count,get,emit);check(count==0x7ffffffe&&emitted.back()==0x7fffffff,"signed maximum positive countdown");
    RF455NuclearCountdownClock slow;DWORD times[]={4,1004};unsigned at=0;count=1;slow.Tick(count,[&](){return times[at++];},emit);check(!count&&at==2&&emitted.back()==1,"first two clock reads may themselves cross threshold");
}
static unsigned capture(const char* name,CGUIChatWindow* chat=nullptr,RF455CenterMessages* center=nullptr){
    auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"begin frame");
    RenderAllEffectsList();d->SetRenderState(D3DRS_ZENABLE,FALSE);if(chat)for(unsigned i=0;i<4;++i)chat->GetChatBoard455(i)->Draw();if(center)center->Draw();d->SetRenderState(D3DRS_ZENABLE,TRUE);check(SUCCEEDED(d->EndScene()),"end frame");
    IDirect3DSurface9 *target=nullptr,*copy=nullptr;check(SUCCEEDED(d->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr))&&SUCCEEDED(d->GetRenderTargetData(target,copy)),"readback");
    D3DVIEWPORT9 view={};d->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");D3DLOCKED_RECT lock={};check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");FILE* out=std::fopen(name,"wb");check(out!=nullptr,"capture");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const BYTE* line=static_cast<BYTE*>(lock.pBits)+y*lock.Pitch+view.X*4;std::fwrite(line,4,640,out);for(unsigned x=0;x<640;++x){DWORD pixel;std::memcpy(&pixel,line+4*x,4);pixels+=(pixel&0xffffff)!=0x102030;}}
    std::fclose(out);copy->UnlockRect();copy->Release();target->Release();return pixels;
}
static bool playing(const RF455TaggedWaveView& wave){return wave.sample&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_PLAYING;}
static std::string text(CGUITextBoard* board){std::string value;for(unsigned i=0;i<board->GetFragmentCount455();++i){const auto* entry=board->GetFragment455(i);if(entry)value+=const_cast<CGUITextInfo*>(entry)->GetText();}return value;}
static void messageCheck(CGUIChatWindow& chat,const char* expected,const char* label){auto actual=text(chat.GetChatBoard455(0));actual.erase(std::remove(actual.begin(),actual.end(),'\n'),actual.end());check(actual.find(expected)!=std::string::npos,label);}
static void clear(CGUIChatWindow& chat,RF455CenterMessages& center){for(unsigned i=0;i<4;++i)chat.GetChatBoard455(i)->Clear();center.Clear();}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);clockCases();check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"actual Korean language");InitR3Engine();SetWarningMessageProc(warning);SetErrorMessageProc(error);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device/fonts");R3SetViewPort(0,0,640,480);gScreen.SetSize(640,480);
    Scope scope;auto game=std::unique_ptr<CGP_MainGame>(new CGP_MainGame);auto& chat=game->ChatWindow455();auto& center=game->CenterMessages455();chat.InitializeChat455();g_pUiChatWindow=&chat;scope.bind(game.get());RF455_SystemMessageCounters()={};
    for(unsigned i=0;i<4;++i){auto* board=chat.GetChatBoard455(i);board->SetPos(15+(i%2)*320,25+(i/2)*220);board->SetSize(290,180);board->SetMargin(3,3);board->Show(TRUE);}
    RF455_PrepareTaggedAudio(state->SoundPath);check(InitR3SoundSystem(".\\Snd\\WaveList.spt")!=0,"Miles driver");SetGlobalWavVolume(0);auto& audio=g_MainApp.TaggedAudio455();check(audio.Open(".\\Snd\\WaveList.spt",state->SoundPath),"tagged provider");state->mSoundOn=TRUE;
    unsigned pixels[5]={},drain=0;
    {
        ChInterface renderer;renderer.InitCharacter(GetD3dDevice());CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);
#if defined(RF455_QUAKE_PROBE)
        RF455_QuakeBeforeWorld119();
#endif
        check(land->Create()&&land->LoadLevel(".\\Map\\neutralAS1\\neutralAS1.bsp"),"real BSP");
        D3DXVECTOR3 eye(0,120,-220),focus(0,0,0),up(0,1,0);D3DXMatrixLookAtLH(&state->mMatView,&eye,&focus,&up);D3DXMatrixInverse(&state->mInvMatView,nullptr,&state->mMatView);D3DXMatrixPerspectiveFovLH(&state->mMatProj,D3DX_PI/3,640.f/480,1,30000);D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);GetD3dDevice()->SetTransform(D3DTS_VIEW,&state->mMatView);GetD3dDevice()->SetTransform(D3DTS_PROJECTION,&state->mMatProj);gMouse.x=320;gMouse.y=240;

#if defined(RF455_QUAKE_PROBE)
        RF455_QuakeBegin119(land->GetLevel());
#endif
        CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");R3SetLoopTime(1.0/30);auto& owner=RF455_NuclearContainer();auto& aim=owner.Aiming();check(&aim==&RF455_NuclearAiming()&&owner.Size()==0,"actual MainApp container and existing aiming access share owner");
        float pos[3]={0,0,10},moved[3]={20,0,10},zeros[3]={};
        check(!owner.ClearAll()&&!owner.ResetRecords()&&!owner.Find(0,0)&&!owner.Position(0,0),"empty lookup/clear/reset");
        check(!owner.SetPosition(0,0,pos)&&!owner.Launch(0,0)&&!owner.Impact(0,0)&&!owner.Radar(0,0,1)&&!owner.NotifyRace(0,0)&&!owner.SetCountdown(0,0,5),"missing wrappers false");
        check(owner.Add(255,255)&&owner.Add(0,0)&&owner.Add(0,255)&&owner.Add(255,0)&&owner.Size()==4,"keys cover unsigned WORD boundaries");const auto* original=owner.Find(0,0);check(!owner.Add(0,0)&&owner.Find(0,0)==original&&owner.Size()==4,"duplicate retains same record");
        check(owner.SetPosition(255,255,moved)&&same(owner.Position(255,255),moved)&&same(owner.Position(0,0),zeros),"keys independent");
        state->mDynamicLight=9;const auto messages=RF455_SystemMessageCounters().main;check(owner.Launch(0,0)&&owner.Impact(0,0)&&!owner.Find(0,0)->launch&&!owner.Find(0,0)->impact&&state->mDynamicLight==9&&RF455_SystemMessageCounters().main==messages+2,"all-zero launch/impact emit literal without FX/audio/light");check(text(chat.GetChatBoard455(0)).find("Not Nuclear Posion")!=std::string::npos,"literal routed to real chat");clear(chat,center);
        phase("radar");check(owner.Radar(0,0,7)&&owner.Find(0,0)->radar&&state->mDynamicLight==3,"nonzero radar flag starts at zero position");auto first=owner.Find(0,0)->radar;check(GetMagicListFromID(first)->mState==1&&same(GetMagicListFromID(first)->mMat[3],zeros),"radar persistent master position");auto tag2=audio.Inspect(277034);check(playing(tag2)&&tag2.tag==2,"actual looping radar tag2");
        check(owner.SetPosition(0,0,pos)&&same(GetMagicListFromID(first)->mMat[3],zeros),"setting record position does not move existing radar");check(owner.Radar(0,0,TRUE)&&owner.Find(0,0)->radar!=first&&GetMagicListFromID(first)->mState==2&&audio.Inspect(277034).sample==tag2.sample,"radar replacement disappears old master and suppresses duplicate tag2");
        aim.SetPending(1);auto tag1=audio.Inspect(277034,1);check(playing(tag1)&&tag1.tag==1&&aim.effectHandle,"independent aiming radar tag1");
        first=owner.Find(0,0)->radar;check(owner.Radar(0,0,FALSE)&&!owner.Find(0,0)->radar&&GetMagicListFromID(first)->mState==2&&!playing(tag2)&&playing(tag1),"radar off stops tag2 and retains aiming tag1");
        audio.PlayAtListener(277034,1,2);check(!playing(audio.Inspect(277034))&&playing(tag1),"retained tag2 suppresses restart while aiming keeps shared wave cached");
        check(!owner.Remove(7,7)&&!aim.pending&&aim.effectHandle&&playing(tag1),"missing remove clears pending but keeps aiming visual/audio");aim.Clear();audio.Collect();
        audio.PlayAtListener(277034,1,2);check(playing(audio.Inspect(277034)),"tag2 restarts after entire wave cache collected");check(owner.Radar(0,0,FALSE)&&!playing(audio.Inspect(277034)),"radar off handle0 still stops tag2");
        check(owner.SetCountdown(0,0,5)&&owner.Radar(0,0,TRUE),"live record setup");
        phase("launch-impact");check(owner.Launch(0,0)&&owner.Impact(0,0)&&owner.Find(0,0)->launch&&owner.Find(0,0)->impact,"actual archived launch/impact created");
        const auto launch=owner.Find(0,0)->launch,impact=owner.Find(0,0)->impact;auto* flight=GetMagicListFromID(launch);auto* blast=GetMagicListFromID(impact);check(flight&&blast&&flight->mMagicID==1358041392&&blast->mMagicID==1358041648&&flight->mState==0&&blast->mState==0&&same(flight->mMat[3],pos)&&same(blast->mMat[3],pos),"actual IDs/auto state/record position");
        auto* flightScript=static_cast<CProcessMagic*>(flight->mMagicPtr);auto* blastScript=static_cast<CProcessMagic*>(blast->mMagicPtr);check(flightScript->mTrackNum==1&&blastScript->mTrackNum==15,"real archived track counts");check(flightScript->mMagicTrack[0].Pos[1]==-70,"real missile local offset");
        bool quake=false;for(unsigned i=0;i<blastScript->mTrackNum;++i){const auto& t=blastScript->mMagicTrack[i];if(t.Flag&_MT_FLAG_QUAKE)quake=t.Time==2.6f&&t.QuakeTime==5&&t.QuakeDensity==150;}check(quake,"actual impact quake control track");
        check(playing(audio.Inspect(277036))&&playing(audio.Inspect(277038))&&audio.Inspect(277036).tag==0&&audio.Inspect(277038).tag==0,"real missile/explosion one-shot sound");
        for(unsigned i=1;i<=15;++i){R3SetTime(i/30.0);ClearDynamicLight();advanceEffects119();}check(GetEffectListCnt()>6,"real launch and impact children scheduled");pixels[0]=capture("registry-flight-impact.bgra");check(pixels[0]>20,"visible actual effects");
        const auto beforeReset=GetMagicListCnt();check(owner.ResetRecords()&&owner.Size()==4&&!owner.Find(0,0)->radar&&!owner.Find(0,0)->launch&&!owner.Find(0,0)->impact&&same(owner.Position(0,0),pos)&&owner.Find(0,0)->countdown==5,"reset retains position/countdown and detaches effect handles");check(GetMagicListCnt()==beforeReset&&GetMagicListFromID(launch)->mState==0&&GetMagicListFromID(impact)->mState==0,"reset does not kill launch/impact");
        for(unsigned i=16;i<=90;++i){R3SetTime(i/30.0);ClearDynamicLight();advanceEffects119();}pixels[1]=capture("registry-impact-late.bgra");check(pixels[1]>20,"late actual explosion visible");
        check(owner.ClearAll()&&!owner.Size()&&!owner.ClearAll(),"full clear drops records after reset");
        phase("messages");auto* language=RF455_GetNormalLanguagePack();
        for(BYTE race:{BYTE(0),BYTE(1),BYTE(2),BYTE(255)}){
            check(owner.Add(race,0)&&owner.NotifyRace(race,0),"race notify actual record");
            char expected[512];std::snprintf(expected,sizeof(expected),language->get(0xc15),race<3?language->get(race):"");
            messageCheck(chat,expected,"C15 actual race localization incl empty unknown");clear(chat,center);
        }
        owner.ClearAll();
        phase("real-clock");owner.Add(2,0);owner.Add(0,1);owner.SetCountdown(2,0,3);owner.SetCountdown(0,1,2);const auto beforeClock=RF455_SystemMessageCounters().main;owner.FrameMove();check(owner.Find(0,1)->countdown==2&&owner.Find(2,0)->countdown==3,"first real process clock no decrement");
        Sleep(1050);owner.FrameMove();check(owner.Find(0,1)->countdown==1&&owner.Find(2,0)->countdown==3&&RF455_SystemMessageCounters().main==beforeClock+1,"ascending key consumes shared real tick");char expected[512];std::snprintf(expected,sizeof(expected),language->get(0xc17),2);check(text(chat.GetChatBoard455(0)).find(expected)!=std::string::npos,"real C17 oldcount2 dispatched");center.FrameMoveAt(timeGetTime(),.05f);pixels[2]=capture("registry-countdown.bgra",&chat,&center);clear(chat,center);
        Sleep(1050);owner.ClearAll();owner.Add(1,0);owner.SetCountdown(1,0,4);owner.FrameMove();check(owner.Find(1,0)->countdown==3,"shared clock survives ClearAll/new record");
        std::snprintf(expected,sizeof(expected),language->get(0xc17),4);check(text(chat.GetChatBoard455(0)).find(expected)!=std::string::npos,"real C17 after recreation");owner.ClearAll();clear(chat,center);
        phase("drain");while((GetEffectListCnt()||GetMagicListCnt())&&drain<1200){++drain;R3SetTime(3+drain/30.0);ClearDynamicLight();advanceEffects119();}check(!GetEffectListCnt()&&!GetMagicListCnt()&&drain<1200,"detached flight/explosion/radar naturally drain");pixels[3]=capture("registry-cleared.bgra");check(!pixels[3],"all effect pixels cleared");
        // Destructor follows target ClearAll: pending0, no independent aiming Clear.
        {RF455NuclearContainer local;local.Add(3,0);local.SetPosition(3,0,pos);check(local.Radar(3,0,1)&&local.Find(3,0)->radar,"scoped record radar");}check(!playing(audio.Inspect(277034)),"container destructor stops record radar tag2");
        for(unsigned i=0;i<300&&(GetEffectListCnt()||GetMagicListCnt());++i)advanceEffects119();check(!GetEffectListCnt()&&!GetMagicListCnt(),"destructor radar drains");pixels[4]=capture("registry-destructor-cleared.bgra");check(!pixels[4],"destructor radar pixels cleared");
#if defined(RF455_TEXTURE_LIFETIME_PROBE)
        RF455_TextureBeforeCache118();
#endif
        DestroyEffectsList();DestroyMagicSptList();
#if defined(RF455_TEXTURE_LIFETIME_PROBE)
        RF455_TextureAfterCache118();
#endif
        check(land->Destroy()!=0,"world teardown");RTMovieRelease();g_pCamera=nullptr;
#if defined(RF455_TEXTURE_LIFETIME_PROBE)
        RF455_TextureAfterWorld118();
#endif
    }
    audio.Close();ReleaseR3SoundSystem();gSpriteMgr.UnloadTargetSprites455();RF455_ReleaseNormalCharacterSharedResources();scope.bind(nullptr);g_pUiChatWindow=nullptr;game.reset();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
#if defined(RF455_TEXTURE_LIFETIME_PROBE)
    RF455_TextureAfterEngine118();
#endif
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"warnings\":%u,\"actual_stage_registry\":true,\"record_bytes\":32,\"unknown_DWORD12_untouched\":true,\"unsigned_WORD_keys\":true,\"real_radar_tag2_and_aiming_tag1\":true,\"real_launch_impact_scripts\":true,\"impact_tracks\":15,\"target_reset_detaches_launch_impact\":true,\"real_C15_C17_and_literal\":true,\"shared_process_clock_and_sorted_order\":true,\"clock_survives_clear\":true,\"natural_effect_drain\":%u,\"GPU_frames\":5,\"pixels\":[%u,%u,%u,%u,%u],\"muted_lab\":true,\"ordinary_receiver\":false,\"full_stage_lifecycle\":false,\"full_world_effects\":false,\"full_client\":false}\n",checks,warnings,drain,pixels[0],pixels[1],pixels[2],pixels[3],pixels[4]);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx checks=%u\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)),checks);return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"registry:%s checks=%u\n",e.what(),checks);return 1;}}
