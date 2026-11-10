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
#include "client455_nation_paths.h"
#include "client455_language.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>

extern CMainApp g_MainApp;
static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static unsigned word(FILE* f){unsigned n;require(std::fread(&n,4,1,f)==1,"Expected word");return n;}
struct PlanCase{unsigned type,index,mesh,tableType,race,group,resultMesh,resultIndex;};
struct RealCase{unsigned type,index,mesh,race,group,resultMesh,parts;};
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    FILE* f=std::fopen("expected.bin","rb");require(f,"Expected file");char magic[4];require(std::fread(magic,1,4,f)==4&&!std::memcmp(magic,"EQ45",4),"Expected signature");
    unsigned count=word(f);std::vector<PlanCase> plans(count);require(std::fread(plans.data(),sizeof(PlanCase),count,f)==count,"Expected plans");
    count=word(f);std::vector<RealCase> cases(count);require(std::fread(cases.data(),sizeof(RealCase),count,f)==count,"Expected real cases");
    count=word(f);std::vector<std::string> textures;for(unsigned i=0;i<count;++i){unsigned bytes=word(f);require(bytes&&bytes<256,"Texture name bounds");std::string name(bytes,'\0');require(std::fread(&name[0],1,bytes,f)==bytes,"Texture name bytes");textures.push_back(name);}
    require(std::fgetc(f)==EOF,"Expected extent");std::fclose(f);
    for(const auto& c:plans){const auto p=RF455_PlanEquipment(BYTE(c.type),c.index,c.mesh);require(p.tableType==c.tableType&&p.race==c.race&&p.resourceGroup==c.group&&p.meshID==c.resultMesh&&p.tableIndex==c.resultIndex,"Independent mesh/race/group plan");}
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Nation/language");
    InitR3Engine();auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Own D3D");
    require(_CreateCharIF(GetD3dDevice())&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Actual resource owners");
    require(RF455_GameItems().loadItemFiles(),"Ordinary Item47/localized names");unsigned loaded=0,defaults=0;
    {
        CCharResDataMgr catalog;require(catalog.LoadData(),"Ordinary nine-group resource catalog");
        CAvatar avatar;
        require(!avatar.GetDefaultItem455(0)&&!avatar.GetDefaultItem455(6)&&!avatar.GetDefaultItem455(255),"Fresh default slots and bounds");
        require(!avatar.SetDefaultItem(BYTE(6),DWORD(0))&&!avatar.SetDefaultItem(BYTE(255),DWORD(0)),"Default setter bounds");
        for(const auto& c:cases){
            {
                RF455EquipmentObject object;require(object.Create455(BYTE(c.type),c.index),"Actual typed equipment creation");
                const auto p=object.GetPlan455();require(p.race==c.race&&p.resourceGroup==c.group&&p.meshID==c.resultMesh,"Actual resource selection");
                auto* mesh=object.GetMesh455();if(!mesh){std::fprintf(stderr,"Missing actual mesh type%u/index%u/id%08x\n",c.type,c.index,c.resultMesh);throw std::runtime_error("Real mesh did not load");}
                require(mesh->m_Load&&mesh->m_MaxObj==c.parts&&mesh->m_pMesh&&object.GetOriginalMesh455()==mesh&&object.GetBone455()==mesh,"Actual loaded mesh parts and borrowed bindings");++loaded;
                auto* item=RF455_GameItems().create(0,BYTE(c.type),c.index);require(item,"Real basic payload");
                item->header().serial=object.GetIndex();item->header().field8=object.GetServerIndex();object.SetItem455(item);
                require(item->header().references==1&&object.GetTableIndex455()==c.index&&object.GetIndex()==(c.index|0xf0000000)&&object.GetServerIndex()==object.GetIndex(),"Payload IDs/retain/table index");
                {RF455EquipmentObject copy(object);require(copy.GetItem455()==item&&item->header().references==2&&copy.GetMesh455()==mesh,"Own copied resource wrapper retains payload");}
                require(item->header().references==1,"Copy releases one reference");
            }
            if(c.type<6){
                require(avatar.SetDefaultItem(BYTE(c.type),DWORD(c.index)),"Ordinary Avatar default setter");auto* object=avatar.GetDefaultItem455(BYTE(c.type));
                require(object&&object->GetItem455()&&object->GetTableIndex455()==c.index&&object->GetItem455()->header().serial==(c.index|0xf0000000)&&object->GetItem455()->header().field8==(c.index|0xf0000000)&&object->GetMesh455(),"Actual default Avatar slot/payload/resource");++defaults;
            }
        }
        require(defaults==30&&loaded==32&&RF455_GameItems().manager.size()==6,"Six default owners survive replacement;temporary owners released");
        {RF455EquipmentObject missing;require(missing.Create455(6,32)&&missing.GetPlan455().meshID==0x00a10320&&!missing.GetMesh455()&&!missing.GetBone455()&&!missing.GetOriginalMesh455(),"Real valid item metadata with no registered mesh still creates successfully");}
        for(const auto& name:textures){auto* texture=RF455_GetTextureByName(_GetCharIF()->m_TM.native,name.c_str());
            if(!texture){std::fprintf(stderr,"Missing real GPU texture %s\n",name.c_str());throw std::runtime_error("Actual material texture missing");}
            D3DSURFACE_DESC desc={};require(SUCCEEDED(texture->GetLevelDesc(0,&desc))&&desc.Width&&desc.Height,"Real GPU texture surface");}
        require(!avatar.SetDefaultItem(BYTE(1),DWORD(0x0fffffff))&&!avatar.GetDefaultItem455(1),"Failed metadata replacement leaves slot empty");
        require(RF455_GameItems().manager.size()==5,"Replacement releases retired payload");
    }
    require(RF455_GameItems().manager.size()==0,"Avatar teardown releases all default payloads");
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr()&&_DestroyCharIF(),"Resource teardown");
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");require(out,"Output");std::fprintf(out,"{\"status\":\"PASS\",\"plan_cases\":%u,\"real_models_loaded\":%u,\"actual_default_creations\":%u,\"gpu_texture_entries\":%u,\"default_payload_owners\":6,\"payloads_after_teardown\":0,\"actual_resource_bindings\":true,\"ordinary_Avatar_default_setter\":true,\"full_player_appearance_or_draw\":false}\n",unsigned(plans.size()),loaded,defaults,unsigned(textures.size()));std::fclose(out);return 0;
}
#ifndef RF455_EQUIPMENT_NO_MAIN
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Equipment: %s\n",error.what());return 2;}}
#endif
