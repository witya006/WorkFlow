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
#include "client455_resource_io.h"
#include "r3d3dtex.h"
#include "r3util.h"
#include "commonutil.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
extern CMainApp g_MainApp;
extern CEffectList* GetEffectListFromID(DWORD);
static unsigned checks=0,warnings=0;
static void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
static void warning(char* message){++warnings;std::fprintf(stderr,"warning:%s\n",message);}
static void error(char* message){throw std::runtime_error(message);}
static unsigned capture(const char* name){
    auto* d=GetD3dDevice();IDirect3DSurface9 *target=nullptr,*copy=nullptr;
    check(SUCCEEDED(d->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc;target->GetDesc(&desc);
    check(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr)),"readback surface");
    check(SUCCEEDED(d->GetRenderTargetData(target,copy)),"readback");D3DLOCKED_RECT lock;check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"readback lock");
    FILE* file=std::fopen(name,"wb");check(file!=nullptr,"capture file");unsigned pixels=0;
    for(unsigned y=0;y<480;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch);std::fwrite(row,4,640,file);for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(file);copy->UnlockRect();copy->Release();target->Release();return pixels;
}
static void draw(){auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0)),"clear");check(SUCCEEDED(d->BeginScene()),"begin");RenderAllEffectsList();check(SUCCEEDED(d->EndScene()),"end");}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warning);SetErrorMessageProc(error);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");R3SetViewPort(0,0,640,480);state->mDynamicLight=16;state->mIsFog=FALSE;
    D3DXVECTOR3 eye(0,120,-220),focus(0,0,0),up(0,1,0);D3DXMatrixLookAtLH(&state->mMatView,&eye,&focus,&up);D3DXMatrixInverse(&state->mInvMatView,nullptr,&state->mMatView);
    D3DXMatrixPerspectiveFovLH(&state->mMatProj,D3DX_PI/3,640.0f/480.0f,1,5000);D3DXMatrixMultiply(&state->mMatViewProj,&state->mMatView,&state->mMatProj);
    auto* d=GetD3dDevice();d->SetTransform(D3DTS_VIEW,&state->mMatView);d->SetTransform(D3DTS_PROJECTION,&state->mMatProj);
    const auto baseline=GetDmallocSize();CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");
    check(GetEffectQuality455()==2,"target default quality2");float pos[3]={};
    R3SetLoopTime(1.0/30.0);unsigned pixels=0,lightTicks=0;
    const DWORD id=StartMagicEffect(pos,0,1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);check(id!=0,"ordinary real aiming cue");
    for(unsigned tick=1;tick<=90;++tick){R3SetTime(tick/30.0);ClearDynamicLight();FrameMoveAllEffectsList();lightTicks+=GetDynamicLightNum()!=0;
        if(tick==1)check(GetEffectListCnt()==2,"two zero-time tracks");
        if(tick==15)check(GetEffectListCnt()==6&&GetLoadedEffectEntityNum()==6,"all six actual scheduled resources");
        if(tick==30||tick==60||tick==90){draw();char name[64];std::sprintf(name,"aiming-%03u.bgra",tick);pixels+=capture(name);}
    }
    check(pixels>20&&lightTicks==90,"visible particles and ordinary dynamic-light insertion");
    check(SetDisapearTimeMagicEffect(id,0),"ordinary effect cancellation");
    unsigned drain=0;while((GetEffectListCnt()||GetMagicListCnt())&&drain<360){++drain;R3SetTime(3+drain/30.0);ClearDynamicLight();FrameMoveAllEffectsList();}
    check(!GetEffectListCnt()&&!GetMagicListCnt()&&drain<360,"cancel drains children and master");draw();check(capture("aiming-cleared.bgra")==0,"cancel clears rendered pixels");
    ApplyEffectOption455(TRUE,0);check(GetEffectQuality455()==0,"option0 quality0");
    auto hidden=StartMagicEffect(pos,0,1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);check(hidden!=0,"retained targeting master at low quality");
    FrameMoveAllEffectsList();check(GetEffectListCnt()==0,"target low quality suppresses aiming children");DeleteMagicList(0,TRUE);
    ApplyEffectOption455(TRUE,3);check(GetEffectQuality455()==1,"option3 quality1");ApplyEffectOption455(FALSE,0);check(GetEffectQuality455()==2,"disabled quality filter restores2");
    D3DXMATRIX matrix;D3DXMatrixIdentity(&matrix);const DWORD entity=GetRealID(90063);
    for(unsigned i=0;i<513;++i)StartEffect(reinterpret_cast<float(*)[4]>(&matrix),entity,_EF_STATE_ALWAYS_LIVE,0xffffffff,1,_MT_FLAG_PARTICLE,0,0x100000+i);
    check(GetEffectListCnt()==512&&!GetEffectListFromID(0x100000)&&GetEffectList()[0].mUniqueID==0x100001,"513th particle evicts and releases oldest at capacity512");
    while(GetEffectListCnt())check(SetDisapearTimeEffect(GetEffectList()[0].mUniqueID,-1),"negative disappear releases clone");
    const auto oldest=StartMagicEffect(reinterpret_cast<float(*)[4]>(&matrix),1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);
    FrameMoveAllEffectsList();check(oldest&&GetEffectListCnt()==2,"oldest master owns real live children");
    DWORD survivors[256];
    for(unsigned i=0;i<256;++i)survivors[i]=StartMagicEffect(reinterpret_cast<float(*)[4]>(&matrix),1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);
    check(GetMagicListCnt()==256&&!GetMagicListFromID(oldest)&&!GetEffectListCnt(),"257th master force-releases oldest children before compaction");
    bool allSurvived=true;for(auto current:survivors)allSurvived=allSurvived&&current&&GetMagicListFromID(current)!=nullptr;
    check(allSurvived,"all256 distinct surviving master IDs remain present after compaction");
    while(GetMagicListCnt())DeleteMagicList(0,TRUE);
    check(!GetMagicListCnt()&&!GetEffectListCnt(),"master boundary phase completely released");
    DestroyEffectsList();DestroyMagicSptList();
    check(!GetEffectResourceGroup455()->archives&&!GetEffectResourceGroup455()->count,"ordinary archive owner released");
    for(int i=1;i<GetNowR3D3DTexCnt();++i)check(!R3GetSurface(i),"ordinary cached texture released");
    const auto retained=GetDmallocSize()-baseline;check(retained==9728,"only process-owned texture tables retained");
    R3ReleasePreTextures();const auto after=GetDmallocSize();check(after==baseline,"all lab allocations released");
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"warnings\":%u,\"real_RPK_cue_tracks\":6,\"real_models\":6,\"particle_recipes\":5,\"ordinary_FrameMove_ticks\":90,\"dynamic_light_ticks\":%u,\"particle_pixels\":%u,\"GPU_frames\":4,\"cancellation_drain_ticks\":%u,\"ordinary_effect_cancellation\":true,\"cleared_pixels\":0,\"effect_capacity\":512,\"overflow_eviction\":true,\"master_capacity\":256,\"master_overflow_eviction\":true,\"quality_owner\":true,\"negative_disappear_releases\":true,\"explicit_global_texture_table_teardown\":true,\"retained_global_texture_cache_bytes\":%d,\"memory_before\":%d,\"memory_after\":%d,\"all_lab_allocations_released\":true,\"full_dynamic_light_compositing\":false,\"full_world_pass_order\":false,\"full_nuclear_owner\":false,\"full_effect_runtime\":false,\"full_client\":false}\n",checks,warnings,lightTicks,pixels,drain,retained,baseline,after);
    std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"effect-runtime:%s\n",e.what());return 1;}}
