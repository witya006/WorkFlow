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
#include "gameprogress/cgp_title.h"
#include "addcodebyyun/particlelist.h"
#include <cstdio>
#include <cstring>
#include <string>
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Progress failure line%d: %s\n",__LINE__,#x);return 1;}}while(0)
static_assert(sizeof(CGameProgress)==24,"455stage base:virtualpointer,fourBOOLs,nextDWORD");
struct TraceStage:CGameProgress {
    std::string trace;bool exitInInput=false,exitInFrame=false;
    BOOL InputProcess()override{trace+='I';if(exitInInput)RequestStageExit455();return FALSE;}
    HRESULT FrameMove()override{trace+='F';if(exitInFrame)RequestStageExit455();return E_FAIL;}
    HRESULT Render()override{trace+='R';return E_FAIL;}
    BOOL LoadData()override{trace+='L';return FALSE;}
    BOOL UnloadData()override{trace+='U';return FALSE;}
    HRESULT RestoreDeviceObjects()override{return S_OK;}
    HRESULT InvalidateDeviceObjects()override{return S_OK;}
    LRESULT MsgProc(HWND,UINT,WPARAM,LPARAM)override{return 0;}
    void dirty(){m_bIsCreated=TRUE;m_bIsLoadedData=TRUE;m_bExit=TRUE;m_bRequestExit=TRUE;}
    bool clear()const{return !m_bIsCreated&&!m_bIsLoadedData&&!m_bExit&&!m_bRequestExit;}
};
int main(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    TraceStage stage;REQUIRE(stage.clear());
    for(DWORD value:{0u,1u,2u,3u,0xffffffffu}){stage.SetNextStage455(value);stage.dirty();stage.Init();REQUIRE(stage.clear()&&stage.GetNextStage455()==value);}
    REQUIRE(stage.CGameProgress::Create()==TRUE&&stage.CGameProgress::Destroy()==TRUE&&stage.trace.empty());
    FILE* registry=std::fopen("progress-particles.ini","wb");REQUIRE(registry);
    REQUIRE(std::fputs("[PARTICLE_INFO]\nMAXPARTICLE=3\n[PARTICLE1]\nINDEX=1\nPARTICLE=unused.spt\n"
                       "[PARTICLE2]\nINDEX=31\nPARTICLE=unused.spt\n[PARTICLE3]\nINDEX=2000\nPARTICLE=unused.spt\n",registry)>=0 &&
            std::fclose(registry)==0);
    char registryPath[MAX_PATH];REQUIRE(GetFullPathNameA("progress-particles.ini",MAX_PATH,registryPath,nullptr));
    g_Particle.LoadParticleIni(registryPath);
    auto* first=g_Particle.GetCHParticle(1);
    auto* middle=g_Particle.GetCHParticle(31);
    auto* last=g_Particle.GetCHParticle(2000);
    REQUIRE(first&&middle&&last);
    auto dirty=[&]{first->m_Count=5;middle->m_Count=7;last->m_Count=9;};
    auto reset=[&]{return !first->m_Count&&!middle->m_Count&&!last->m_Count;};
    for(BOOL active:{FALSE,TRUE}){stage.Init();stage.trace.clear();dirty();REQUIRE(stage.MainLoop(active)==FALSE&&stage.trace=="IFR"&&reset());}
    stage.Init();stage.trace.clear();stage.RequestStageExit455();dirty();REQUIRE(stage.MainLoop(FALSE)==TRUE&&stage.trace=="I"&&middle->m_Count==7);
    stage.Init();stage.trace.clear();stage.exitInInput=true;dirty();REQUIRE(stage.MainLoop(TRUE)==TRUE&&stage.trace=="I"&&middle->m_Count==7);stage.exitInInput=false;
    stage.Init();stage.trace.clear();stage.exitInFrame=true;dirty();REQUIRE(stage.MainLoop(FALSE)==FALSE&&stage.trace=="IFR"&&reset());stage.trace.clear();REQUIRE(stage.MainLoop(TRUE)==TRUE&&stage.trace=="I");
    CGP_Title title;REQUIRE(title.GetNextStage455()==1);title.SetNextStage455(3);title.Init();REQUIRE(title.GetNextStage455()==3);
    FILE* out=std::fopen("result.json","wb");REQUIRE(out);std::fputs("{\"status\":\"PASS\",\"actual_base_size\":24,\"next_stage_roundtrips\":5,\"init_retains_next\":true,\"base_create_destroy_no_data_sideeffects\":true,\"actual_virtual_order\":true,\"inactive_still_renders\":true,\"input_exit_shortcircuits\":true,\"frame_exit_observed_next_iteration\":true,\"actual_particle_counters_reset\":true,\"title_constructor_next1\":true,\"full_four_stage_factory\":false,\"tutorial_runtime\":false,\"input_exe_executed\":false}\n",out);std::fclose(out);return 0;
}
