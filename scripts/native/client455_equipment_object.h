#pragma once
#include "client455_item_object.h"

struct RF455EquipmentPlan {
    DWORD tableIndex=0,meshID=0;BYTE tableType=0,race=255,resourceGroup=5;
};
RF455EquipmentPlan RF455_PlanEquipment(BYTE type,DWORD encodedIndex,DWORD meshID);

// Source-owned creation/resource/payload part of CEquipObject. Its target
// private644-byte layout,fade/animation/draw and gameplay callbacks are not
// represented as complete by this class.
class RF455EquipmentObject:public CItemObject {
    BYTE race455=255;
    CMesh* mesh455=nullptr;
    CMesh* originalMesh455=nullptr;
    DWORD field608455=0;
    RF455EquipmentPlan plan455;
public:
    RF455EquipmentObject();
    RF455EquipmentObject(const RF455EquipmentObject&);
    bool Create455(BYTE type,DWORD encodedIndex);
    void SetItem455(RF455ManagedItem*) override;
    DWORD GetTableIndex455()const;
    CMesh* GetMesh455()const{return mesh455;}
    CMesh* GetOriginalMesh455()const{return originalMesh455;}
    CBone* GetBone455()const{return m_pBone;}
    BBOX* GetBox455()const{return m_pBBox;}
    const RF455EquipmentPlan& GetPlan455()const{return plan455;}
};
