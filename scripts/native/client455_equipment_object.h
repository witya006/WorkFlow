#pragma once
#include "client455_item_object.h"
#include "r3material.h"
#include <array>
#include <memory>

// Source-owned resources for7E88F0/7E8970/7E89E0/7E8B60.
// The material is the recovered54/526-byte engine record,not an EFF record.
class RF455GradeOverlayResources {
    struct State;
    std::unique_ptr<State> state;
public:
    RF455GradeOverlayResources();
    ~RF455GradeOverlayResources();
    bool Load455();
    void Release455();
    const _R3MATERIAL& Material455(unsigned)const;
    IDirect3DTexture9* Texture455(unsigned)const;
    void Begin455(BYTE grade);
    void End455();
};
RF455GradeOverlayResources& RF455_GradeOverlays455();

struct RF455EquipmentPlan {
    DWORD tableIndex=0,meshID=0;BYTE tableType=0,race=255,resourceGroup=5;
};
RF455EquipmentPlan RF455_PlanEquipment(BYTE type,DWORD encodedIndex,DWORD meshID);

// Source-owned creation/resource/payload part of CEquipObject. Its target
// private644-byte layout is not a C++ overlay. Render wrappers use actual
// source providers;ordinary player/controller integration is still required.
class RF455EquipmentObject:public CItemObject {
    BYTE race455=255;
    CMesh* mesh455=nullptr;
    CMesh* originalMesh455=nullptr;
    DWORD field608455=0;
    float random455;
    RF455EquipmentPlan plan455;
    BYTE renderMode455=255;
    BYTE overlayGrade455; //The target constructor does not initialize604.
    bool overlayGradeKnown455=false;
    std::array<BYTE,10> dummy455{};
    bool CanRender455();
    void DrawWithEffect455(BYTE,const D3DXMATRIX*);
public:
    RF455EquipmentObject();
    RF455EquipmentObject(const RF455EquipmentObject&);
    bool Create455(BYTE type,DWORD encodedIndex);
    void SetItem455(RF455ManagedItem*) override;
    DWORD GetTableIndex455()const;
    float GetRandom455()const{return random455;}
    BOOL Render() override;
    virtual BOOL Render455(const D3DXMATRIX&);
    BOOL RenderWithShadow455();
    BYTE EffectGrade455()const;
    BYTE UnitPart455()const;
    DWORD EffectListKey455()const;
    void SetOverlayGrade455(BYTE grade){overlayGrade455=grade;overlayGradeKnown455=true;}
    BYTE GetOverlayGrade455()const;
    //450330/450710:metadata152 only for slots6/7;all other slots write0.
    void PrepareOverlaySlot455(BYTE slot);
    void SetRenderMode455(BYTE mode){renderMode455=mode;}
    void SetDummy455(unsigned index,BYTE node){if(index<dummy455.size())dummy455[index]=node;}
    BYTE GetDummy455(unsigned index)const{return index<dummy455.size()?dummy455[index]:255;}
    bool GetTracePositions455(Vector3f*)const;
    CMesh* GetMesh455()const{return mesh455;}
    CMesh* GetOriginalMesh455()const{return originalMesh455;}
    CBone* GetBone455()const{return m_pBone;}
    BBOX* GetBox455()const{return m_pBBox;}
    const RF455EquipmentPlan& GetPlan455()const{return plan455;}
};

//527E70/528090/528190 retain a source-owned mesh wrapper and shared payload.
//The target's four-matrix node stride is preserved,including aliases across
//nodes/slots. Out-of-allocation writes are reported rather than silently fixed.
class RF455EquipmentEffectQueue {
    struct State;
    std::unique_ptr<State> state;
public:
    RF455EquipmentEffectQueue();
    ~RF455EquipmentEffectQueue();
    void Add455(const RF455EquipmentObject*);
    void Clear455();
    BOOL Render455();
    unsigned Count455()const;
    unsigned Start455()const;
};
RF455EquipmentEffectQueue& RF455_EquipmentEffects455();
