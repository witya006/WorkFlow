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
#include "commonutil.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>

extern CMainApp g_MainApp;
static unsigned checks=0,warnings=0;
static void check(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
static void warning(char* message){++warnings;std::fprintf(stderr,"warning:%s\n",message);}
static void error(char* message){throw std::runtime_error(message);}
static void phase(const char* message){std::fprintf(stderr,"phase:%s\n",message);std::fflush(stderr);}

static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    InitR3Engine();SetWarningMessageProc(warning);SetErrorMessageProc(error);
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"actual D3D device");
    phase("device");const auto baseline=GetDmallocSize();
    auto* own=GetEffectResourceGroup455();check(own&&!own->archives&&!own->count,"static group begins empty");
    RF455_RpkGroup other;auto* original=RF455_GetResourceGroup();
    check(RF455_SetResourceGroup(&other)==&other,"setter returns new group");
    CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");
    check(GetEffectResourceGroup455()==own&&own->count==1&&own->archives,"ordinary table owns archive indexes");
    check(RF455_GetResourceGroup()==&other,"table load does not select group");
    check(GetLoadedEffectEntityNum()==0,"no eagerly loaded entities");
    const auto loaded=GetDmallocSize();LoadEffectEntityList(".\\Effect\\EffectEntityList.spt");
    check(GetDmallocSize()==loaded&&own->count==1,"table-only reload releases prior table and indexes");
    phase("group");
    float pos[3]={1,2,3};const DWORD instance=StartMagicEffect(pos,0,1358041136,nullptr,_EF_STATE_ALWAYS_LIVE);
    auto* magic=GetMagicListFromID(instance);
    check(instance&&magic&&magic->mEntityUniqueIDCnt==6,"ordinary cache reads archived cue without manual group setup");
    check(RF455_GetResourceGroup()==own,"ordinary start selects persistent effect group");
    RF455_SetResourceGroup(&other);
    auto* model=GetEntityFromEffectEntityList(GetRealID(90061));
    check(model&&model->IsLoadedEntity()&&model->mTextureSize,"actual archived R3E model and textures");
    check(RF455_GetResourceGroup()==own&&GetLoadedEffectEntityNum()==1,"lazy entity selects group");
    RF455_SetResourceGroup(&other);
    check(GetEntityFromEffectEntityList(GetRealID(90061))==model&&RF455_GetResourceGroup()==&other,
          "entity cache hit preserves caller active group");
    phase("model");
    const DWORD ids[5]={90063,90062,90066,90065,90064};
    D3DXMATRIX matrix;D3DXMatrixRotationY(&matrix,.3f);matrix._41=7;matrix._42=8;matrix._43=9;
    for(auto id:ids){
        RF455_SetResourceGroup(&other);
        std::unique_ptr<CParticle> first(GetParticleFromEffectEntityList(GetRealID(id),reinterpret_cast<float(*)[4]>(&matrix)));
        check(first&&first->mEntity&&first->mEntity->IsLoadedEntity()&&first->mNum==1,"real archived particle recipe/entity");
        check(RF455_GetResourceGroup()==own,"first particle load selects effect group");
        RF455_SetResourceGroup(&other);
        std::unique_ptr<CParticle> second(GetParticleFromEffectEntityList(GetRealID(id),reinterpret_cast<float(*)[4]>(&matrix)));
        check(second&&second.get()!=first.get()&&second->mEntity==first->mEntity,"clones share cached entity");
        check(first->mElement&&second->mElement&&first->mElement!=second->mElement,"clones own separate elements");
        check(RF455_GetResourceGroup()==&other,"particle cache hit preserves active group");
        check(first->GetParticleAttr()&_PARTICLE_ATTR_ALWAYS_LIVE,"actual always-live recipe retained");
        check(!first->mRotMat[3][0]&&!first->mRotMat[3][1]&&!first->mRotMat[3][2]
              &&first->mRotMat[0][0]==matrix._11&&first->mRotMat[2][2]==matrix._33,"clone rotation copied and translation cleared");
        check(first->GetParticleState()==_PARTICLE_STATE_START&&second->GetParticleState()==_PARTICLE_STATE_START,
              "clones initialized and started");
        std::fprintf(stderr,"particle:%lu flags=%08lx entity=%p elements=%p/%p\n",id,first->GetParticleAttr(),first->mEntity,first->mElement,second->mElement);
    }
    check(GetLoadedEffectEntityNum()==6&&GetAllEffectEntityTextureSize()>0,"six actual cached entity owners");
    check(SetDisapearTimeMagicEffect(instance,0),"ordinary disappear");ResetEffectManager();
    RF455_SetResourceGroup(own);DestroyEffectsList();DestroyMagicSptList();
    check(!own->count&&!own->archives&&GetLoadedEffectEntityNum()==0,"release clears indexes and templates");
    check(!RF455_GetResourceGroup()&&!RF455_GetResourceArchiveEnabled(),"released group is no longer selected");
    ReleaseEffectEntityList();check(!own->count&&!own->archives,"empty release remains valid");
    const auto retained=GetDmallocSize()-baseline;
    std::fprintf(stderr,"global_texture_cache:%d records=%d surfaces=%d\n",retained,GetNowR3TexCnt(),GetNowR3D3DTexCnt());
    check(retained==9728&&GetNowR3TexCnt()==7&&GetNowR3D3DTexCnt()==7,"only initial process-owned texture tables remain");
    for(int i=1;i<GetNowR3D3DTexCnt();++i)check(R3GetSurface(i)==nullptr,"ordinary owner released real D3D texture");
    // This lab owns the otherwise process-global texture manager. Its public
    // teardown is separate from destroying the effect table/cache.
    R3ReleasePreTextures();const auto after=GetDmallocSize();
    check(after==baseline,"effect allocations released after explicit global texture-table teardown");RF455_SetResourceGroup(original);
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result file");
    std::fprintf(out,"{\"status\":\"PASS\",\"checks\":%u,\"warnings\":%u,\"ordinary_archive_owner\":true,\"ordinary_start_selects_group\":true,\"real_RPK_cue_tracks\":6,\"real_R3E_models\":6,\"real_particle_recipes\":5,\"real_particle_clones\":10,\"real_D3D_textures\":true,\"cache_hit_selection_preserved\":true,\"table_only_reload_balanced\":true,\"static_empty_group_remains_valid\":true,\"all_allocations_released\":true,\"explicit_global_texture_table_teardown\":true,\"retained_global_texture_cache_bytes\":%d,\"memory_before\":%d,\"memory_after\":%d,\"GPU_effect_drawn\":false,\"full_effect_runtime\":false,\"full_nuclear_aiming\":false,\"full_client\":false}\n",checks,warnings,retained,baseline,after);
    std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* p){if(p->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",p->ExceptionRecord->ExceptionCode,DWORD(p->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"effect-resources:%s\n",e.what());return 1;}}
