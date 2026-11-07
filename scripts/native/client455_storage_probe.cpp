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
#include "client455_storage.h"
#include <cstdio>
#include <stdexcept>
#include <typeinfo>

extern CMainApp g_MainApp;
template<class Tag, typename Tag::Type Member> struct MemberAccess {
    friend typename Tag::Type access(Tag) { return Member; }
};
struct NetworkMember { using Type=CNetworkMgr CMainApp::*; friend Type access(NetworkMember); };
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
struct NetworkScope {
    CNetworkMgr& network=g_MainApp.*access(NetworkMember{});
    NetworkScope(){if(!network.Create())throw std::runtime_error("network owner");}
    ~NetworkScope(){network.Destroy();}
};
static void check(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
static int measure(){
    NetworkScope context;
    CBoardManager manager;manager.Create();
    check(_STORAGE_POS::INVEN==0&&_STORAGE_POS::EQUIP==1&&_STORAGE_POS::EMBELLISH==2&&
          _STORAGE_POS::FORCE==3&&_STORAGE_POS::ANIMUS==4&&_STORAGE_POS::TRUNK==5&&
          _STORAGE_POS::LINKER==6&&_STORAGE_POS::BELT==255,"source storage identities");
    check(MAX_BOARD_TYPE==56&&_STORAGE_POS::POS_NUM==7&&_STORAGE_POS::STORAGE_NUM==6,"source capacities");
    auto* force=dynamic_cast<CForceBoard*>(manager.GetBoard(3));
    auto* animus=dynamic_cast<CAnimusBoard*>(manager.GetBoard(4));
    auto* inventory=dynamic_cast<CInventoryBoard*>(manager.GetBoard(0));
    auto* equipment=dynamic_cast<CEquipBoard*>(manager.GetBoard(1));
    check(force&&animus&&inventory&&equipment,"actual registered classes");
    check(manager.GetBoard(2)==equipment&&!manager.GetBoard(5),"equipment alias and missing Trunk");
    force->Create(IBT_FORCE,6,20);animus->Create(IBT_ANIMUS,1,10);
    inventory->Create(IBT_INVENTORY,5,20);equipment->Create(IBT_EQUIP,1,16);
    check(force->IsEqual(3)&&animus->IsEqual(4)&&force->GetMaxPackNum()==6&&
          inventory->GetMaxPackNum()==5,"actual base creation identities/capacities");
    for(BYTE i=0;i<6;++i)check(force->AddPack(i)!=0,"real Force pack activation");
    check(animus->AddPack(0)&&inventory->AddPack(0)&&equipment->AddPack(0),"real pack activation");
    check(!manager.GetObject(3,0,0)&&!manager.GetObject(4,0,0)&&!manager.GetObject(2,0,0),"ordinary object lookup");
    bool retired=false;
    try{(void)_GetBeltBoard();}catch(const std::logic_error&){retired=true;}
    check(retired,"old belt callers must not select Force or Trunk");
    FILE* cases=std::fopen("storage-cases.txt","rb");check(cases!=nullptr,"reference fixture");
    unsigned id,physical,checked=0,present=0,objects=0;
    while(std::fscanf(cases,"%u %u",&id,&physical)==2){
        check(id<256&&RF455_IsPhysicalItemStorage(BYTE(id))==bool(physical),"reference physical-item predicate");
        auto* board=manager.GetBoard(BYTE(id));present+=board!=nullptr;++checked;
        if(!physical||id==5)check(!manager.ReturnItemToItemBoard(BYTE(id),0,0,reinterpret_cast<CBoardItem*>(1)),"ordinary ReturnItem guard/unregistered owner");
    }
    std::fclose(cases);check(checked==256&&present==18,"complete byte lookup domain");
    std::printf("{\"status\":\"PASS\",\"registry_limit\":56,\"physical_codes_checked\":256,\"public_present\":%u,\"boards\":[",present);
    for(unsigned i=0;i<56;++i){if(i==2)continue;auto* board=manager.GetBoard(BYTE(i));if(!board)continue;
        std::printf("%s{\"id\":%u,\"class\":\"%s\"}",objects?",":"",i,typeid(*board).name());++objects;}
    std::printf("],\"registered\":%u,\"source_storage_ids\":[0,1,2,3,4,5,6],\"legacy_belt_invalid\":255,"
                "\"actual_Force_Animus_packs\":true,\"legacy_belt_rejected\":true,\"Trunk_missing\":true,"
                "\"full_factory\":false,\"full_item_protocol\":false,\"actual_Tutorial\":false}\n",objects);
    return 0;
}
static LONG recordFailure(EXCEPTION_POINTERS* info){
    if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;
    std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",info->ExceptionRecord->ExceptionCode,
                 DWORD(info->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));
    return EXCEPTION_EXECUTE_HANDLER;
}
static int guarded(){__try{return measure();}__except(recordFailure(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Storage:%s\n",error.what());return 1;}}
