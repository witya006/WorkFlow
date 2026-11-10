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
#include <cstring>
#include <stdexcept>

RF455EquipmentPlan RF455_PlanEquipment(BYTE type,DWORD index,DWORD mesh){
    RF455EquipmentPlan out;out.tableType=type==9?46:type;out.race=BYTE(index>>28);out.tableIndex=index&0x0fffffff;out.meshID=mesh;
    if(out.race==14)out.resourceGroup=6;
    else if(out.race!=15){
        const unsigned category=(mesh>>16)&15,user=(mesh>>20)&255,part=(mesh>>8)&255;
        if((category==0||category==8)&&user!=10&&part!=7)out.meshID=(mesh&0xff0fffff)|(DWORD(out.race)<<20);
    }
    if(out.tableType==8||out.tableType==46)out.resourceGroup=5;
    return out;
}
RF455EquipmentObject::RF455EquipmentObject(){SetObjectTypeID(2);Enable(41218);}
RF455EquipmentObject::RF455EquipmentObject(const RF455EquipmentObject& source):CItemObject(source),race455(source.race455),mesh455(source.mesh455),originalMesh455(source.originalMesh455),field608455(source.field608455),plan455(source.plan455){RetainSharedItem455();}
bool RF455EquipmentObject::Create455(BYTE type,DWORD index){
    race455=BYTE(index>>28);const BYTE tableType=type==9?46:type;const DWORD tableIndex=index&0x0fffffff;
    const auto row=RF455_GameItems().data.getItem(tableType,tableIndex);if(!row.data)return false;
    if(row.size<76)throw std::out_of_range("455 equipment metadata outside row");
    SetIndex(tableIndex|0xf0000000);SetServerIndex(tableIndex|0xf0000000);SetName(const_cast<char*>(reinterpret_cast<const char*>(row.data+8)));
    DWORD mesh;std::memcpy(&mesh,row.data+72,4);plan455=RF455_PlanEquipment(type,index,mesh);
    //5E0A90 checks both the load return and the resulting loaded flag. The
    //legacy public lookup discards that return,so use the registered record.
    const auto loadedMesh=[&](){
        CMesh* value=_GetMeshMgr()->GetMeshMgr(plan455.resourceGroup)->GetCharacter(plan455.meshID);
        if(value&&!value->m_Load){
            if(!_GetCharIF()->LoadRealData(value,&_GetCharIF()->m_TM,true)||!value->m_Load)return static_cast<CMesh*>(nullptr);
        }
        return value;
    };
    m_pBone=loadedMesh();m_pBBox=_GetBBoxMgr()->GetBoundBox(plan455.resourceGroup,plan455.meshID);
    originalMesh455=loadedMesh();mesh455=originalMesh455;field608455=0;return true;
}
void RF455EquipmentObject::SetItem455(RF455ManagedItem* item){
    CItemObject::SetItem455(item);
    if(item){SetIndex(item->header().serial);SetServerIndex(item->header().field8);}
}
DWORD RF455EquipmentObject::GetTableIndex455()const{
    if(!GetItem455())return ID_INVALID;
    auto* item=dynamic_cast<RF455BasicItem*>(GetItem455());
    if(!item)throw std::logic_error("455 equipment requires a real basic item payload");return item->tableIndex();
}
