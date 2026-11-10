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

extern CMainApp g_MainApp;
static void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
static unsigned word(FILE* f){unsigned n;require(std::fread(&n,4,1,f)==1,"Expected word");return n;}
struct PlanCase{unsigned type,index,mesh,tableType,race,group,resultMesh,resultIndex;};
struct RealCase{unsigned type,index,mesh,race,group,resultMesh,parts;};
class EquipmentHost146:public RF455EquipmentCallbacks {
    CAvatar& actor;
public:
    CBone* bone=nullptr;bool combat=false,scale=false,actionOne=true,failFactory=false;
    unsigned clones=0,rematches=0,adds=0,removes=0;std::vector<std::string> events;
    DWORD detachedSerial=0,detachedServer=0,detachedData=0;BYTE detachedReferences=0;std::string detachedName;
    std::map<RF455PlayerEquipmentObject*,BYTE> fades;
    explicit EquipmentHost146(CAvatar& value):actor(value){}
    BYTE race()const override{return actor.GetRace();}
    void* player()const override{return &actor;}
    RF455ManagedItem* createPayload(BYTE type,DWORD index)override{
        events.push_back("factory"+std::to_string(type));return failFactory?nullptr:RF455_GameItems().create(0,type,index);
    }
    std::unique_ptr<RF455ManagedItem> clonePayload(RF455ManagedItem* item)override{
        events.push_back("clone");++clones;auto* value=dynamic_cast<RF455BasicItem*>(item);require(value,"Actual basic equipment payload");
        detachedSerial=item->header().serial;detachedServer=item->header().field8;detachedData=item->header().data16;detachedReferences=item->header().references;detachedName=item->name();
        return std::unique_ptr<RF455ManagedItem>(new(std::nothrow) RF455DetachedNormalItem(*value));
    }
    void specialSlotByte(BYTE)override{events.push_back("special-byte");}
    void animation(RF455PlayerEquipmentObject& object,DWORD id)override{
        require(object.GetOwner455()==&actor,"Actual owner set before animation callback");events.push_back("animation"+std::to_string(id));
    }
    bool weaponScaleEnabled()const override{return scale;}
    void weaponScale(RF455PlayerEquipmentObject&,float value)override{require(value==1.5f,"Weapon scale constant");events.push_back("scale");}
    bool hasBone()const override{return bone!=nullptr;}
    void rematch(CMesh* mesh)override{events.push_back("rematch");if(bone&&mesh){_GetCharIF()->RematchParent(bone,mesh);++rematches;}}
    bool combatMode()const override{return combat;}
    bool isFade(RF455PlayerEquipmentObject& object,BYTE mode)override{return fades[&object]==mode;}
    void fade(RF455PlayerEquipmentObject& object,BYTE mode,BYTE frames)override{
        require(frames==60,"Target fade duration");fades[&object]=mode;events.push_back("fade"+std::to_string(mode));
    }
    void repeatAction()override{events.push_back("repeat-action");}
    void itemEffect(RF455ManagedItem* item,bool add)override{
        if(add){++adds;events.push_back(item?"add":"add-null");}
        else{++removes;require(dynamic_cast<RF455DetachedNormalItem*>(item),"Detached snapshot survives slot release");
            require(item->header().serial==detachedSerial&&item->header().field8==detachedServer&&item->header().data16==detachedData&&item->header().references==detachedReferences&&std::string(item->name())==detachedName,"Detached consumer reads original IDs/metadata/name/reference byte after release");events.push_back("remove");}
    }
    void detachedEffect(RF455PlayerEquipmentObject&,DWORD id)override{require(id==2,"Detach event2");events.push_back("detach2");}
    bool actionTypeOne()const override{return actionOne;}
};
static unsigned playerEquipment146(const std::vector<RealCase>& cases){
    CAvatar actor;actor.SetRace(0);EquipmentHost146 host(actor);host.bone=_GetBoneMgr()->GetBone(0,0);require(host.bone,"Actual player bone");
    RF455PlayerEquipment equipment(host);unsigned real=0;
    for(const auto& c:cases){
        if(c.type>=6)continue;actor.SetRace(BYTE(c.index/16));host.bone=_GetBoneMgr()->GetBone(0,actor.GetRace());
        require(equipment.create(BYTE(c.type),c.index),"Real13-slot creation");const BYTE slot=c.type==5?10:BYTE(c.type);
        auto* value=equipment.get(slot);require(value&&value->GetItem455()&&value->GetMesh455()&&value->GetPlan455().meshID==c.resultMesh&&value->GetOwner455()==&actor,"Actual13-slot/race/model/owner binding");++real;
    }
    require(!equipment.create(9,0)&&!equipment.create(11,0)&&!equipment.create(10,80)&&!equipment.create(13,0)&&!equipment.create(255,0),"Reserved and external slot bounds");
    actor.SetRace(0);host.bone=_GetBoneMgr()->GetBone(0,0);host.events.clear();host.scale=true;
    require(equipment.putOn(6,0),"Actual weapon create/rematch/controller");
    require(host.events==std::vector<std::string>({"factory6","animation1","scale","rematch","fade3","repeat-action","add"}),"Weapon callback order from target ASM");
    host.events.clear();require(equipment.putOff(6),"Actual weapon removal");
    require(host.events==std::vector<std::string>({"clone","remove","repeat-action"})&&!equipment.get(6),"Clone-before-clear/effect/remove order");
    host.events.clear();host.combat=true;require(equipment.putOn(7,0),"Actual shield create");
    require(host.events==std::vector<std::string>({"factory7","animation1","rematch","fade4","add"}),"Combat shield order without action reset");
    require(equipment.putOff(7),"Actual shield removal");
    host.events.clear();require(equipment.create(8,0),"Actual special item metadata");
    require(host.events==std::vector<std::string>({"factory8","animation0"}),"Slot8 uses animation0");
    host.events.clear();require(equipment.putOff(8),"Special item removal");
    require(host.events==std::vector<std::string>({"clone","detach2","remove"}),"Special detach before release/effect");
    host.events.clear();require(equipment.create(46,0)&&equipment.get(46)==equipment.get(9),"Type46 aliases slot9");
    require(host.events==std::vector<std::string>({"factory46","special-byte"}),"Slot9 special byte and no animation callback");
    require(equipment.putOff(46),"Type46 removal alias");
    host.events.clear();require(equipment.create(27,0)&&equipment.get(27)==equipment.get(11),"Type27 aliases slot11");
    require(equipment.putOff(27),"Type27 removal alias");
    require(equipment.create(12,0)&&equipment.get(12),"Thirteenth storage slot");require(equipment.putOff(12),"Thirteenth removal");
    require(equipment.create(10,0)&&equipment.get(10)&&!equipment.get(5),"Explicit hair slot maps to factory5 but getter does not remap5");
    require(equipment.putOff(10),"Hair removal");
    {
        RF455EquipmentObject source;require(source.Create455(6,0),"Shared source resource");
        auto* item=RF455_GameItems().create(0,6,0);require(item,"Shared source payload");item->header().serial=0x12345678;item->header().field8=0x87654321;source.SetItem455(item);
        host.events.clear();require(equipment.putOnBoard(&source),"Board wrapper overload");
        require(equipment.payload(6)==item&&item->header().references==2&&equipment.get(6)->GetIndex()==0x12345678&&equipment.get(6)->GetServerIndex()==0x87654321,"Shared source retains actual payload and IDs");
        require(host.events==std::vector<std::string>({"factory6","animation1","scale","scale","rematch","fade4","repeat-action","add"}),"Board overload scale and callback order");
        require(equipment.putOff(6)&&item->header().references==1,"Overload removal releases one shared reference");
        require(equipment.putOnEquipment(&source)&&equipment.payload(6)==item,"Equipment wrapper overload");
        require(equipment.putOff(6)&&item->header().references==1,"Equipment overload lifetime");
    }
    host.failFactory=true;require(!equipment.create(0,0),"Factory failure retained");auto* retained=equipment.get(0);
    require(retained&&!retained->GetItem455()&&retained->GetMesh455(),"Factory failure retains successful resource creation");
    host.failFactory=false;require(!equipment.create(1,0x0fffffff)&&!equipment.get(1),"Metadata failure clears slot");
    require(!equipment.putOff(255)&&!equipment.get(255),"Getter/remove bounds");
    for(unsigned part=0;part<13;++part)equipment.putOff(BYTE(part));
    require(host.clones==host.removes&&host.rematches>=2,"All controller detach snapshots consumed");
    require(real==30,"Five races/six base models through actual controller");return real;
}
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
        require(playerEquipment146(cases)==30,"Player equipment controller146");
        require(RF455_GameItems().manager.size()==0,"13-slot controller teardown");
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
    FILE* out=std::fopen("result.json","wb");require(out,"Output");std::fprintf(out,"{\"status\":\"PASS\",\"plan_cases\":%u,\"real_models_loaded\":%u,\"actual_default_creations\":%u,\"gpu_texture_entries\":%u,\"default_payload_owners\":6,\"payloads_after_teardown\":0,\"actual_resource_bindings\":true,\"ordinary_Avatar_default_setter\":true,\"player_controller_real_creations\":30,\"player_controller_production_connected\":false,\"condition_animation_callbacks_are_probe_recorders\":true,\"full_player_appearance_or_draw\":false}\n",unsigned(plans.size()),loaded,defaults,unsigned(textures.size()));std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"Player equipment146: %s\n",error.what());return 2;}}
