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
#include "addcodebyjang/effectcore.h"
#include "addcodebyjang/effectentitylist.h"
#include "client455_nuclear_aiming.h"
#include "client455_rvp_effects.h"
#include <client455_normal_renderer_math.h>
#include "RTMovie.h"
#include "mss.h"
#include "jmalloc.h"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
extern CMainApp g_MainApp;
extern CEffectList* GetEffectListFromID(DWORD);
static unsigned checks=0,warnings=0;
static void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
static void warning(char* message){++warnings;std::fprintf(stderr,"warning:%s\n",message);}
static void error(char* message){throw std::runtime_error(message);}
static void phase(const char* value){std::fprintf(stderr,"phase:%s\n",value);std::fflush(stderr);}
static bool same(const float* a,const float* b){return std::memcmp(a,b,12)==0;}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warning);SetErrorMessageProc(error);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");R3SetViewPort(0,0,640,480);
    RF455_PrepareTaggedAudio(state->SoundPath);check(InitR3SoundSystem(".\\Snd\\WaveList.spt")!=0,"real Miles driver");SetGlobalWavVolume(0);
    auto& audio=g_MainApp.TaggedAudio455();check(audio.Open(".\\Snd\\WaveList.spt",state->SoundPath),"real tagged provider/listener");
    unsigned drain=0;int before=0,after=0;
    {
        ChInterface renderer;renderer.InitCharacter(GetD3dDevice());before=GetDmallocSize();
        CCamera camera;g_pCamera=&camera;std::unique_ptr<CLand> land(new CLand);
        check(land->Create()!=0,"ordinary land owner");phase("load-world");check(land->LoadLevel(".\\Map\\neutralAS1\\neutralAS1.bsp")!=0,"actual455 world");phase("world");
        auto* level=land->GetLevel();check(level==g_pLevel&&level->IsLoadedBsp(),"actual global level binding");
        D3DXVECTOR3 eye(0,120,-220),focus(0,0,0),up(0,1,0);D3DXMatrixLookAtLH(&state->mMatView,&eye,&focus,&up);
        D3DXMatrixInverse(&state->mInvMatView,nullptr,&state->mMatView);D3DXMatrixPerspectiveFovLH(&state->mMatProj,D3DX_PI/3,640.0f/480,1,30000);
        D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);
        gMouse.x=320;gMouse.y=240;Vector3f picked;check(level->GetPointFromScreenRay(gMouse.x,gMouse.y,&picked)!=0,"actual BSP cursor ray");
        check(std::isfinite(picked[0])&&std::isfinite(picked[1])&&std::isfinite(picked[2]),"finite actual cursor");
        CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");
        auto& aiming=RF455_NuclearAiming();unsigned char zero[20]={};check(!std::memcmp(&aiming,zero,20),"actual MainApp owner starts with target20bytes");
        float command[3]={7,8,9};aiming.SetPosition(command);check(same(aiming.position,command),"command position setter");
        state->mSoundOn=TRUE;state->mDynamicLight=9;aiming.SetPending(1);const auto first=aiming.effectHandle;
        check(first&&aiming.pending==1&&same(aiming.position,command)&&state->mDynamicLight==3,"actual effect/sound start preserves command position andforces light3");
        auto* master=GetMagicListFromID(first);check(master&&same(master->mMat[3],picked),"null-character start preserves real world cursor");
        auto wave=audio.Inspect(277034);check(wave.sample&&wave.tag==1&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_PLAYING,"real radar tagged sample playing");
        state->mDynamicLight=9;aiming.SetPending(1);check(aiming.effectHandle==first&&state->mDynamicLight==9&&audio.Inspect(277034).sample==wave.sample,"repeated pending doesnot restart visual/audio orlight");
        R3SetLoopTime(.05f);for(unsigned i=0;i<16;++i){R3SetTime(i*.05f);FrameMoveAllEffectsList();}
        check(GetEffectListCnt()==6,"actual six children ready");
        gMouse.x=340;check(level->GetPointFromScreenRay(gMouse.x,gMouse.y,&picked)!=0,"second real cursor ray");aiming.FrameMove();
        auto* process=static_cast<CProcessMagic*>(master->mMagicPtr);bool moved=true;
        for(unsigned j=0;j<6;++j){auto* child=GetEffectListFromID(master->mEntityUniqueID[j]);float expected[3];for(unsigned k=0;k<3;++k)expected[k]=picked[k]+process->mMagicTrack[j].Pos[k];moved=moved&&child&&same(child->mMat[3],expected);}
        check(moved,"actual frame moves all children with their local offsets");
        float held[3];std::memcpy(held,GetEffectList()[0].mMat[3],12);aiming.SetPending(0);gMouse.x=360;aiming.FrameMove();
        check(!aiming.pending&&aiming.effectHandle==first&&same(held,GetEffectList()[0].mMat[3])&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_PLAYING,"pending1to0 retains handles andstops cursor updates");
        aiming.SetPending(1);check(aiming.pending==1&&aiming.effectHandle&&aiming.effectHandle!=first&&GetMagicListFromID(first)->mState==2,"fresh pending replaces visual andstarts old disappear");
        check(audio.Inspect(277034).sample==wave.sample,"replacement preserves duplicate sound tag suppression");
        aiming.Clear();check(!aiming.effectHandle&&!aiming.pending&&!std::memcmp(aiming.position,zero,12),"clear resets handle/pending/command position");
        check(AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_DONE,"clear with handle stops actual radar tag");
        while((GetEffectListCnt()||GetMagicListCnt())&&drain<300){++drain;FrameMoveAllEffectsList();}
        check(!GetEffectListCnt()&&!GetMagicListCnt()&&drain<300,"replaced andcurrent effects drain");audio.Collect();
        DestroyMagicSptList();CreateMagicSptList("missing-cue.spt");aiming.SetPending(1);
        check(!aiming.effectHandle&&aiming.pending&&state->mDynamicLight==3,"missing effect stillsets pending/light3");wave=audio.Inspect(277034);
        check(wave.sample&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_PLAYING,"missing effect stillplays actual sound");
        aiming.Clear();check(!aiming.effectHandle&&!aiming.pending&&AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample))==SMP_PLAYING,"clear without effect handle doesnot stop sound");
        audio.Stop(277034,1);audio.Collect(); // explicit fixture cleanup of target quirk
        DestroyEffectsList();DestroyMagicSptList();check(land->Destroy()!=0,"ordinary world teardown");RTMovieRelease();g_pCamera=nullptr;
        after=GetDmallocSize();std::fprintf(stderr,"memory:%d/%d\n",before,after);check(before==after,"scoped world/effect allocations released");
    }
    RF455_ReleaseNormalCharacterSharedResources();audio.Close();ReleaseR3SoundSystem();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"warnings\":%u,\"owner_bytes\":20,\"actual_MainApp_owner\":true,\"real_world_cursor\":true,\"real_Miles_radar\":true,\"real_effect_children\":6,\"track_offsets_preserved\":true,\"repeated_pending_retains\":true,\"pending_zero_retains_visual_and_sound\":true,\"clear_stops_with_handle\":true,\"missing_effect_sound_quirk\":true,\"scoped_memory_balanced\":true,\"memory_before\":%d,\"memory_after\":%d,\"drain_ticks\":%u,\"muted_lab\":true,\"C1A_message\":false,\"full_nuclear_owner\":false,\"full_world_frame_order\":false,\"full_client\":false}\n",checks,warnings,before,after,drain);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"nuclear:%s\n",e.what());return 1;}}
