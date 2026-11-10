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
#include "client455_equipment_object.h"
#include "client455_player_equipment.h"
#include "client455_normal_item_copy.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>
#include <map>
#include <cmath>

extern CMainApp g_MainApp;
static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static unsigned word(FILE* f){unsigned n;require(std::fread(&n,4,1,f)==1,"Expected word");return n;}
struct PlanCase{unsigned type,index,mesh,tableType,race,group,resultMesh,resultIndex;};
struct RealCase{unsigned type,index,mesh,race,group,resultMesh,parts;};
class AnimationHost146:public RF455EquipmentAnimationCallbacks {
    CAvatar& actor;
public:
    bool liftPending=true;unsigned effects=0,loaded=0,lifts=0;std::vector<DWORD> requested;
    explicit AnimationHost146(CAvatar& value):actor(value){}
    void itemAnimationEffect(RF455PlayerEquipmentObject&,DWORD)override{require(requested.empty(),"Effect callback precedes every lookup");++effects;}
    CAniData* findItemAnimation(DWORD id)override{
        requested.push_back(id);auto* ani=_GetAniMgr()->GetAni(5,id);
        if(ani){if(!(ani->m_Load&&ani->imported))std::fprintf(stderr,"ANI %08x loaded%u imported%p maximum%u name%s\n",id,ani->m_Load,ani->imported,ani->maximum,ani->m_Name);require(ani->m_Load&&ani->imported,"Actual item ANI loaded");++loaded;}return ani;
    }
    void adjustOwnerHeight(RF455PlayerEquipmentObject& object,bool add)override{
        require(object.GetOwner455()==&actor,"Real own player for mount lift");
        const float amount=RF455_MountingHeight455(actor.GetRace(),object.GetTableIndex455());
        actor.SetPosition(actor.GetPosX(),actor.GetPosY()+(add?amount:-amount),actor.GetPosZ());++lifts;
    }
    bool pendingOwnerLift()const override{return liftPending;}
    void clearPendingOwnerLift()override{liftPending=false;}
};
class AnimationObject146:public RF455PlayerEquipmentObject {
public:
    void seedFrames(){m_dwOldBoneFrame=77;m_dwBoneFrame=999;}
};
struct AnimationCase146{unsigned type,index,race,mode,effective,id,found,parts,maximum,tracks;};
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    FILE* file=std::fopen("expected.bin","rb");require(file,"Animation expected");char magic[4];require(std::fread(magic,1,4,file)==4&&!std::memcmp(magic,"EA46",4),"Animation fixture signature");
    unsigned count=word(file);std::vector<AnimationCase146> cases(count);require(std::fread(cases.data(),sizeof(AnimationCase146),count,file)==count&&std::fgetc(file)==EOF,"Animation fixture extent");std::fclose(file);
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Nation/language");
    InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Own D3D");
    require(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Actual resource owners");
    require(RF455_GameItems().loadItemFiles(),"Real Item tables");unsigned successes=0,failures=0,poses=0,lookups=0,lifts=0;
    {
        CCharResDataMgr resources;require(resources.LoadData(),"Actual resource catalog");CAvatar actor;
        for(const auto& c:cases){
            actor.SetRace(BYTE(c.race));actor.SetPosition(1,100,2);AnimationHost146 host(actor);AnimationObject146 object;
            require(object.Create455(BYTE(c.type),(c.race<<28)|c.index),"Actual animated equipment");
            require(object.GetMesh455()&&object.GetMesh455()->m_Load&&object.GetMesh455()->m_MaxObj==c.parts,"Actual selected model geometry");
            auto* item=RF455_GameItems().create(0,BYTE(c.type),c.index);require(item,"Actual animation item payload");
            item->header().serial=object.GetIndex();item->header().field8=object.GetServerIndex();object.SetItem455(item);object.SetOwner455(&actor);object.seedFrames();
            const bool selected=object.SetMeshAnimation455(c.mode,host);require(selected==bool(c.found)&&host.effects==1,"Real ANI selection/failure and effect order");
            require(object.GetAnimationID()==(c.found?c.effective:c.id),"Selected mode versus failed final lookup ID");
            if(c.found){
                auto* ani=object.GetAnimation()->GetAniData();require(ani&&ani->m_Ident==c.id&&ani->maximum==c.maximum&&object.GetOldBoneFrame()==0&&object.GetBoneFrame()==160&&object.GetAnimation()->IsAnimating(),"Actual selected ANI/state reset");
                require(object.CResObject::Animation(320),"Actual model animation through normal CResObject");++poses;++successes;
            }else{require(!object.GetAnimation()->GetAniData()&&object.GetOldBoneFrame()==77&&object.GetBoneFrame()==999,"Failed selection retains frame state");++failures;}
            lookups+=unsigned(host.requested.size());host.requested.clear();const float before=actor.GetPosY();
            require(object.SetEquipmentAnimation455(c.mode,host)&&host.effects==2,"Public equipment wrapper returns true even when inner selection fails");
            const bool special=c.type==8||c.type==46;
            if(special)require(bool(object.IsEnable(256))==(c.mode==0||c.mode==3),"Special animation render flag");
            float expected=before;if(c.type==46){const float h=RF455_MountingHeight455(BYTE(c.race),object.GetTableIndex455());if(c.mode==1||c.mode==3||c.mode==4)expected+=h;else if(c.mode==2||c.mode==5)expected-=h;}
            require(std::abs(actor.GetPosY()-expected)<0.0001f,"Actual mount owner height change");
            if(c.type==46&&c.mode==3)require(!host.liftPending,"Mode3 consumes pending lift");lifts+=host.lifts;
        }
        AnimationObject146 fade;fade.SetFade455(1,3);fade.AdvanceFade455();require(fade.GetFade455()==1&&fade.GetFadeFrame455()==2&&fade.IsEnable(4)&&std::abs(fade.GetAlphaDensity()-2.0f/3)<0.00001f,"Real fade-out intermediate");
        fade.AdvanceFade455();fade.AdvanceFade455();require(fade.GetFade455()==3&&!fade.IsEnable(4)&&fade.GetAlphaDensity()==0,"Real fade-out end");
        fade.SetFade455(2,3);fade.AdvanceFade455();fade.AdvanceFade455();fade.AdvanceFade455();require(fade.GetFade455()==4&&fade.GetFadeFrame455()==3&&!fade.IsEnable(4)&&fade.GetAlphaDensity()==1,"Real fade-in end");
        fade.SetFade455(2,0);for(unsigned i=0;i<60;++i)fade.AdvanceFade455();require(fade.GetFade455()==4&&fade.GetFadeFrame455()==60,"Zero duration selects60frames");
    }
    require(RF455_GameItems().manager.size()==0,"All animated equipment payloads released");
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF(),"Resource teardown");g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* output=std::fopen("result.json","wb");require(output,"Output");std::fprintf(output,"{\"status\":\"PASS\",\"cases\":%u,\"animation_successes\":%u,\"animation_failures\":%u,\"actual_pose_calls\":%u,\"lookups\":%u,\"owner_lifts\":%u,\"fade_actual_source\":true,\"animation_selection_actual_source\":true,\"item_effect_callback_is_recorder\":true,\"ordinary_player_connected\":false,\"full_appearance\":false}\n",unsigned(cases.size()),successes,failures,poses,lookups,lifts);std::fclose(output);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Equipment providers146: %s\n",error.what());return 2;}}
