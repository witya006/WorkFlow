#include "addcodebyjang/cmagicscript.h"
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
#include "client455_resource_io.h"
#include "client455_equipment_object.h"
#include "client455_effect_positions.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include <cstdio>
#include <cmath>
#include <memory>
#include <vector>
extern CMainApp g_MainApp;
static unsigned contracts=0;
static void require(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static void point(const float* value,float x,float y,float z,const char* reason){
    if(!std::isfinite(value[0])||!std::isfinite(value[1])||!std::isfinite(value[2])||std::abs(value[0]-x)>0.0002f||std::abs(value[1]-y)>0.0002f||std::abs(value[2]-z)>0.0002f){
        std::fprintf(stderr,"%s:actual %.9g %.9g %.9g expected %.9g %.9g %.9g\n",reason,value[0],value[1],value[2],x,y,z);throw std::runtime_error(reason);}
    ++contracts;
}
class PositionActor146:public CAvatar {
public:void bind(CBone* model,BBOX* box){m_pBone=model;m_pBBox=box;}void type(DWORD type){m_dwCharTypeID=type;}
};
static void frozenContracts(){
    PositionActor146 actor;BBOX box={};box.pMin[1]=-1;box.pMax[1]=2;actor.bind(nullptr,&box);actor.SetPosition(20,40,60);actor.SetScale(2);actor.SetRotY(0,FALSE);actor.SetRace(4);actor.SetDummyIndex(8,255);
    RF455EffectPositionView view;view.actor=&actor;float out[3]={9,8,7};
    require(!RF455_ResolveEffectPosition(out,{},17).targetReturn,"Null actor returns0");point(out,9,8,7,"Null actor leaves output");
    for(BYTE type:{BYTE(0),BYTE(10),BYTE(18),BYTE(255)}){auto r=RF455_ResolveEffectPosition(out,view,type);require(r.targetReturn&&r.defined,"Default branch defined");point(out,20,40,60,"Unrecognised/default type retains position");}
    auto result=RF455_ResolveEffectPosition(out,view,1);require(result.defined,"World bounds");point(out,20,44,60,"Type1 uses world maximumY");
    result=RF455_ResolveEffectPosition(out,view,7);require(result.defined,"Scaled world bounds");point(out,20,55.6f,60,"Type7 preserves second scale multiplication");
    result=RF455_ResolveEffectPosition(out,view,2);require(result.defined,"Damage bound fallback");point(out,20,48.64f,60,"Damage fallback72percent");
    result=RF455_ResolveEffectPosition(out,view,3);require(result.targetReturn&&!result.defined,"Missing named bone target copies indeterminate data");
    result=RF455_ResolveEffectPosition(out,view,5);require(result.targetReturn&&!result.defined,"Missing weapon target copies indeterminate data");
    auto nodes=std::unique_ptr<ObjectMesh[]>(new ObjectMesh[8]);std::memset(nodes.get(),0,8*sizeof(ObjectMesh));
    const char* names[]={"Bip01 R Hand","Bip01 L Hand","Bip01 R Foot","Bip01 L Foot","Bip01 Spine","Bip01 Spine1","unused","unused"};
    auto parents=std::unique_ptr<ObjectMesh[]>(new ObjectMesh[8]);std::memset(parents.get(),0,8*sizeof(ObjectMesh));
    CMesh mesh={};mesh.m_MaxObj=8;mesh.m_pMesh=nodes.get();
    for(unsigned i=0;i<8;++i){std::strcpy(parents[i].m_Name,names[i]);nodes[i].m_pParent=&parents[i];D3DXMatrixIdentity(&nodes[i].m_MatResult);nodes[i].m_MatResult.m[3][0]=2;nodes[i].m_MatResult.m[3][1]=3;nodes[i].m_MatResult.m[3][2]=4;}
    nodes[5].m_MatResult.m[3][2]=8;
    require(actor.PSetVertexBlending(1,&mesh,TRUE),"Actual actor cached pose matrices");view.parts[1]={true,&mesh,nullptr};
    for(BYTE type:{BYTE(3),BYTE(4),BYTE(8),BYTE(9),BYTE(17)}){result=RF455_ResolveEffectPosition(out,view,type);require(result.defined,"Named position");point(out,16,48,54,"Hand/foot/spine actual cached matrix");}
    actor.SetRotY(90,FALSE);result=RF455_ResolveEffectPosition(out,view,17);require(result.defined,"Yaw position");point(out,14,48,64,"Yaw90changesworldaxes");actor.SetRotY(0,FALSE);
    actor.SetRace(0);result=RF455_ResolveEffectPosition(out,view,2);require(result.defined,"Damage midpoint");point(out,16,52,54,"Race0damagebetweenSpineandSpine1");actor.SetRace(2);
    result=RF455_ResolveEffectPosition(out,view,2);require(result.defined,"Other race spine");point(out,16,48,54,"Race2retainsSpinewithoutmidpoint");
    //The binding-name matcher returns the blend index,but7E07B0 then uses the
    //part's FIRST cached matrix ratherthan selecting that contribution.
    nodes[4].m_pParent=nullptr;nodes[4].m_BlendNum=2;const char* other="other";const char* spine="Bip01 Spine";
    std::memcpy(nodes[4].bytes+526,&other,4);std::memcpy(nodes[4].bytes+530,&spine,4);
    result=RF455_ResolveEffectPosition(out,view,17);require(result.defined&&RF455_EffectMeshBinding(nodes[4],spine)==3,"Blend-name lookup");point(out,16,48,54,"Binding indexdoesnotselectanothercachedmatrix");nodes[4].m_BlendNum=0;
    result=RF455_ResolveEffectPosition(out,view,17);require(result.defined,"Spine1fallback");point(out,16,56,54,"SpinefailureusesSpine1");
    RF455EquipmentDummyPoints points;require(points.get(0)==0&&points.get(10)==255,"Dummy constructor/get bounds");
    const char* dummyNames[]={"Effect1","effect2","FIRE1","fire2","Fire3","fire4","effect1","fire4x"};
    for(unsigned i=0;i<8;++i)std::strcpy(nodes[i].m_Name,dummyNames[i]);points.bind(mesh);
    require(points.get(0)==6&&points.get(1)==1&&points.get(2)==2&&points.get(5)==5&&points.get(6)==255,"Actual dummy marker scan case/truncation/last wins");
    require(actor.PSetVertexBlending(6,&mesh,TRUE),"Actual weapon pose cache");view.parts[6]={true,&mesh,&points};
    for(BYTE type:{BYTE(5),BYTE(6),BYTE(11),BYTE(12),BYTE(13),BYTE(14)}){result=RF455_ResolveEffectPosition(out,view,type);require(result.defined,"Weapon point");point(out,16,type==14?56.0f:48.0f,54,"Weapon mapped point");}
    for(BYTE type:{BYTE(15),BYTE(16)}){result=RF455_ResolveEffectPosition(out,view,type);require(result.defined,"Unused weapon point fallback");point(out,20,47.92f,60,"Weapon fallback66percent");}
    points.set(0,0);result=RF455_EffectWeaponPosition(out,view,0,true);require(!result.targetReturn&&result.defined,"Weapondummy0invalidwithdefinedfallback");point(out,20,47.92f,60,"Weapon index0fallback");
    //NPCs match their own mesh names and use m_MatResult,without player bindings.
    actor.type(1);actor.bind(&mesh,&box);std::strcpy(nodes[0].m_Name,"Bip01 Spine");nodes[0].m_MatResult.m[3][2]=10;
    result=RF455_ResolveEffectPosition(out,view,17);require(result.defined,"NPCnamedmesh");point(out,16,60,54,"NPCusesownmodelmatrix");
    actor.type(2);result=RF455_ResolveEffectPosition(out,view,17);require(!result.defined&&result.targetReturn,"UnsupportedNPCtype remains indeterminate");actor.bind(nullptr,nullptr);
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Nation/language");InitR3Engine();auto* engine=GetR3State();engine->mScreenXsize=640;engine->mScreenYsize=480;engine->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Own D3D");
    require(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Actual resource owners");require(RF455_GameItems().loadItemFiles(),"Real Item tables");
    frozenContracts();
    RF455_RpkGroup group;group.LoadDirectory(".\\Effect\\");auto* previous=RF455_GetResourceGroup();RF455_SetResourceGroup(&group);CreateEffectsList(".\\Effect\\EffectEntityList.spt");CreateMagicSptList(".\\Effect\\MagicSptList.spt");
    unsigned models=0,realPositions=0,magicStarts=0;std::vector<float> positions;
    {
        CCharResDataMgr resources;require(resources.LoadData(),"Real Resource catalog");
        for(unsigned race=0;race<5;++race){PositionActor146 actor;actor.SetRace(BYTE(race));actor.SetPosition(20,40,60);actor.SetRotY(90,FALSE);actor.SetScale(1.25f);
            auto* bone=_GetBoneMgr()->GetBone(0,race);require(bone&&bone->m_Load,"Real player skeleton");actor.bind(bone,_GetBBoxMgr()->GetBoundBox(0,race));
            if(race==4){auto* ani=_GetAniMgr()->GetAni(0,1090849056);require(ani&&ani->m_Load,"Real archived AccretiaANI");_GetCharIF()->MatchAnimationToMesh(ani,bone);bone->m_Frame=320;}
            _GetCharIF()->FrameMove(bone);RF455EffectPositionView view;view.actor=&actor;
            std::array<RF455EquipmentObject,5> pieces;
            for(unsigned part=0;part<5;++part){require(pieces[part].Create455(BYTE(part),race*16),"Real body part");auto* mesh=pieces[part].GetMesh455();require(mesh&&mesh->m_Load,"Real body mesh");
                _GetCharIF()->RematchParent(bone,mesh);_GetCharIF()->FrameMove(mesh);require(actor.PSetVertexBlending(part,mesh,TRUE),"Actual per-part pose cache");view.parts[part]={true,mesh,nullptr};++models;
            }
            for(BYTE type:{BYTE(3),BYTE(4),BYTE(8),BYTE(9),BYTE(17)}){float out[3];const auto result=RF455_ResolveEffectPosition(out,view,type);
                if(!result.defined)std::fprintf(stderr,"Missing real bone race%u/type%u\n",race,type);require(result.targetReturn&&result.defined,"Real complete named attachment");
                require(std::isfinite(out[0])&&std::isfinite(out[1])&&std::isfinite(out[2]),"Finite real attachment");positions.insert(positions.end(),out,out+3);++realPositions;
            }
            float original[3];actor.GetPosition(original);const DWORD id=RF455_StartMagicAtActor(view,original,actor.GetRotY(),0x50006004,nullptr,1);auto* effect=GetMagicListFromID(id);require(effect&&effect->mMagicPtr,"Actual cloak magic");
            auto* script=static_cast<CProcessMagic*>(effect->mMagicPtr);require(script->mCreateType==17,"Real cloak requests Spine attachment");float expected[3];require(RF455_ResolveEffectPosition(expected,view,17).defined,"Actual cloak expectedposition");
            require(!std::memcmp(effect->mMat[3],expected,12),"Real magic translationusesactualassembledparts");SetDisapearTimeMagicEffect(id,0);++magicStarts;actor.bind(nullptr,nullptr);
        }
    }
    ResetEffectManager();DestroyEffectsList();DestroyMagicSptList();RF455_SetResourceGroup(previous);group.Release();
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF(),"Resource teardown");g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* output=std::fopen("result.json","wb");require(output,"Output");std::fprintf(output,"{\"status\":\"PASS\",\"frozen_position_contracts\":%u,\"real_models\":%u,\"real_named_positions\":%u,\"real_attached_magic\":%u,\"races\":5,\"archived_player_animation\":true,\"missing_target_temporaries_indeterminate\":true,\"ordinary_player_connected\":false,\"full_appearance\":false,\"positions\":[",contracts,models,realPositions,magicStarts);
    for(unsigned i=0;i<positions.size();++i)std::fprintf(output,"%s%.9g",i?",":"",positions[i]);std::fprintf(output,"]}\n");std::fclose(output);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Equipment attachment146:%s\n",error.what());return 2;}}
