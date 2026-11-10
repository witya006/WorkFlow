#pragma once
#include "client455_equipment_object.h"
#include <array>
#include <cstring>
#include <memory>
#include <stdexcept>

// The reference call at4539BD passes the EQUIPMENT object as this and its
// player as arg0. The misleading decompiler call is not Player.SetPrevAction.
class RF455PlayerEquipmentObject;
inline float RF455_MountingHeight455(BYTE race,DWORD meshID=ID_INVALID){
    float height=race<2?5.8f:race<4?5.0f:8.0f;
    if(meshID!=ID_INVALID&&((meshID&0xff00)>>8)==1)height=static_cast<float>(height*0.75);
    return height;
}
class RF455EquipmentAnimationCallbacks {
public:
    virtual ~RF455EquipmentAnimationCallbacks()=default;
    virtual void itemAnimationEffect(RF455PlayerEquipmentObject&,DWORD)=0;
    virtual CAniData* findItemAnimation(DWORD)=0; //resource group5,5E12C0
    virtual void adjustOwnerHeight(RF455PlayerEquipmentObject&,bool)=0;
    virtual bool pendingOwnerLift()const=0;
    virtual void clearPendingOwnerLift()=0;
};
class RF455PlayerEquipmentObject:public RF455EquipmentObject {
    BYTE fadeMode455=0,fadeMaximum455=60,fadeCurrent455=0;
    BYTE itemKind455()const{
        if(!GetItem455())return 255;
        auto* item=dynamic_cast<RF455BasicItem*>(GetItem455());
        if(!item)throw std::logic_error("455 equipment animation requires a normal payload");
        const auto row=item->rawMetadata();if(row.size<=88)throw std::out_of_range("455 equipment animation metadata");
        return row.data[88];
    }
    CAniData* findAnimation455(DWORD mode,RF455EquipmentAnimationCallbacks& host){
        if(!GetItem455())return nullptr;
        auto* item=dynamic_cast<RF455BasicItem*>(GetItem455());
        if(!item)throw std::logic_error("455 equipment animation requires a normal payload");
        const auto row=item->rawMetadata();if(row.size<76)throw std::out_of_range("455 mesh animation metadata");
        DWORD mesh;std::memcpy(&mesh,row.data+72,4);
        const BYTE category=BYTE((mesh>>16)&15),user=BYTE(mesh>>20),part=BYTE(mesh>>8);
        if((category==0||category==8)&&user!=10&&part!=7)mesh=(mesh&0xff0fffff)|(DWORD(GetPlan455().race)<<20);
        const DWORD id=(mesh<<4)|mode;m_Animation.SetAnimationID(id);
        return host.findItemAnimation(id);
    }
public:
    void SetOwner455(void* owner){m_dwItemField588455=static_cast<DWORD>(reinterpret_cast<std::uintptr_t>(owner));}
    void* GetOwner455()const{return reinterpret_cast<void*>(m_dwItemField588455);}
    //46D2F0:the effect precedes all animation mutation,including failure.
    bool SetMeshAnimation455(DWORD mode,RF455EquipmentAnimationCallbacks& host){
        host.itemAnimationEffect(*this,mode);m_Animation.SetAnimationID(ID_INVALID);m_Animation.SetAniData(nullptr);
        auto* data=findAnimation455(mode,host);
        if(!data&&mode){mode=0;data=findAnimation455(0,host);}
        if(!data)return false;
        m_Animation.SetAniData(data);m_Animation.SetAnimationID(mode);
        m_dwOldBoneFrame=0;m_dwBoneFrame=160;m_Animation.Animating(TRUE);ResetAnimation(data);return true;
    }
    //46DF10 deliberately ignores the inner animation result and returns true.
    bool SetEquipmentAnimation455(DWORD mode,RF455EquipmentAnimationCallbacks& host){
        const BYTE kind=itemKind455();
        if(kind==8||kind==46){
            if(mode==0||mode==3)Enable(256);
            else if(mode==1||mode==2||mode==4||mode==5)Disable(256);
        }
        SetMeshAnimation455(mode,host);
        if(kind==46){
            if(mode==1||mode==4)host.adjustOwnerHeight(*this,true);
            else if(mode==2||mode==5)host.adjustOwnerHeight(*this,false);
            else if(mode==3&&host.pendingOwnerLift()){host.adjustOwnerHeight(*this,true);host.clearPendingOwnerLift();}
        }
        return true;
    }
    void SetFade455(BYTE mode,BYTE maximum=60){
        fadeMode455=mode;fadeMaximum455=maximum?maximum:60;fadeCurrent455=mode==1?fadeMaximum455:0;
    }
    BYTE GetFade455()const{return fadeMode455;}
    BYTE GetFadeFrame455()const{return fadeCurrent455;}
    void AdvanceFade455(){
        if(fadeMode455!=1&&fadeMode455!=2)return;
        if(fadeMode455==1&&fadeCurrent455){
            if(!--fadeCurrent455){Disable(4);SetAlphaDensity(0);fadeMode455=3;return;}
        }else if(fadeMode455==2&&fadeCurrent455<fadeMaximum455&&++fadeCurrent455>=fadeMaximum455){
            fadeCurrent455=fadeMaximum455;Disable(4);fadeMode455=4;SetAlphaDensity(1);return;
        }
        SetAlphaDensity(static_cast<float>(static_cast<double>(fadeCurrent455)/fadeMaximum455));Enable(4);
    }
};

// Required owner operations. No default/no-op implementations: production
// integration must supply the actual animation,condition/effect and actor
// routes. A recorded callback in a probe is not acceptance of that route.
class RF455EquipmentCallbacks {
public:
    virtual ~RF455EquipmentCallbacks()=default;
    virtual BYTE race()const=0;
    virtual void* player()const=0;
    virtual RF455ManagedItem* createPayload(BYTE,DWORD)=0;
    virtual std::unique_ptr<RF455ManagedItem> clonePayload(RF455ManagedItem*)=0;
    virtual void specialSlotByte(BYTE)=0;
    virtual void animation(RF455PlayerEquipmentObject&,DWORD)=0;
    virtual bool weaponScaleEnabled()const=0;
    virtual void weaponScale(RF455PlayerEquipmentObject&,float)=0;
    virtual bool hasBone()const=0;
    virtual void rematch(CMesh*)=0;
    virtual bool combatMode()const=0;
    virtual bool isFade(RF455PlayerEquipmentObject&,BYTE)=0;
    virtual void fade(RF455PlayerEquipmentObject&,BYTE,BYTE)=0;
    virtual void repeatAction()=0;
    virtual void itemEffect(RF455ManagedItem*,bool)=0;
    virtual void detachedEffect(RF455PlayerEquipmentObject&,DWORD)=0;
    virtual bool actionTypeOne()const=0;
};

// Source reconstruction of453030/453100/4531E0/453550/453760/453AF0/453C40
// and their getters/rematch rules. Storage has13slots;target render/animation
// loops separately iterate12. This controller does not invent the missing
// ordinary render or condition providers.
class RF455PlayerEquipment {
    RF455EquipmentCallbacks& host;
    std::array<RF455PlayerEquipmentObject,13> slots;
    static BYTE alias(BYTE kind){return kind==27?11:kind==46?9:kind;}
    static RF455BasicItem& basic(RF455ManagedItem* item){
        auto* value=dynamic_cast<RF455BasicItem*>(item);
        if(!value)throw std::logic_error("455 player equipment requires a basic payload");
        return *value;
    }
    static BYTE kind(RF455ManagedItem* item){
        const auto row=basic(item).rawMetadata();
        if(row.size<=88)throw std::out_of_range("455 equipment kind outside metadata");
        return row.data[88]; //410FA0,not CItem::kind at12
    }
    void weaponAndShield(BYTE type){
        if(type!=6&&type!=7&&type!=27)return;
        const BYTE part=alias(type);auto& object=slots[part];
        if(host.hasBone()&&object.GetMesh455())host.rematch(object.GetMesh455());
        if(host.combatMode()){
            if(!host.isFade(object,4)&&!host.isFade(object,2))host.fade(object,4,60);
        }else if(!host.isFade(object,3)&&!host.isFade(object,1))host.fade(object,3,60);
        if(part!=7)host.repeatAction();
    }
    void postCreate(BYTE type,DWORD index,bool equipOverload){
        if(!equipOverload&&type==27&&index>=30)host.rematch(slots[11].GetMesh455());
        else weaponAndShield(type);
        if(type==8&&host.hasBone()&&slots[8].GetMesh455())host.rematch(slots[8].GetMesh455());
        else if(type==46&&host.hasBone()&&slots[9].GetMesh455())host.rematch(slots[9].GetMesh455());
    }
    bool createFrom(CItemObject* source,bool requireNonempty){
        if(!source||(requireNonempty&&source->IsEmpty()))return false;
        auto* item=source->GetItem455();const BYTE type=kind(item);
        if(!create(type,basic(item).tableIndex()))return false;
        auto& object=slots[alias(type)];
        object.SetIndex(source->GetIndex());object.SetServerIndex(source->GetServerIndex());
        object.SetItem455(item);
        if(alias(type)==6&&host.weaponScaleEnabled())host.weaponScale(object,1.5f);
        return true;
    }
public:
    explicit RF455PlayerEquipment(RF455EquipmentCallbacks& callbacks):host(callbacks){}
    virtual ~RF455PlayerEquipment()=default;
    virtual RF455PlayerEquipmentObject* get(BYTE type){
        const BYTE part=alias(type);return part<=12&&!slots[part].IsEmpty()?&slots[part]:nullptr;
    }
    RF455ManagedItem* payload(BYTE type){auto* object=get(type);return object?object->GetItem455():nullptr;}
    bool create(BYTE type,DWORD index){
        if((type==9||type==10||type==11)&&(type!=10||index>=80))return false;
        if(type>12&&type!=27&&type!=46)return false;
        BYTE part=alias(type);if(part==5&&index<80)part=10;
        auto& object=slots[part];if(!object.IsEmpty())putOff(part);
        const BYTE factoryType=part==10?5:part==11?27:part==9?46:part;
        if(!object.Create455(factoryType,index|(DWORD(host.race())<<28))){object.Clear();return false;}
        auto* item=host.createPayload(factoryType,index);if(!item)return false;
        if(part==9){const auto data=basic(item).rawMetadata();
            if(data.data){if(data.size<=176)throw std::out_of_range("455 special-slot metadata");host.specialSlotByte(data.data[176]);}}
        item->header().serial=object.GetIndex();item->header().field8=object.GetServerIndex();
        object.SetItem455(item);object.SetOwner455(host.player());
        if(part==8)host.animation(object,0);else if(part!=9)host.animation(object,1);
        if(part==6&&host.weaponScaleEnabled())host.weaponScale(object,1.5f);
        return true;
    }
    bool putOn(BYTE type,DWORD index){
        if(!create(type,index))return false;
        postCreate(type,index,false);host.itemEffect(payload(type),true);return true;
    }
    bool putOnBoard(CItemObject* source){
        if(!createFrom(source,false))return false;
        auto* item=source->GetItem455();const BYTE type=kind(item);
        postCreate(type,basic(item).tableIndex(),false);host.itemEffect(item,true);return true;
    }
    bool putOnEquipment(CItemObject* source){
        if(!createFrom(source,true))return false;
        const BYTE type=kind(source->GetItem455());
        postCreate(type,basic(source->GetItem455()).tableIndex(),true);
        host.itemEffect(payload(type),true);return true;
    }
    virtual bool putOff(BYTE type){
        const BYTE part=alias(type);if(part>12)return false;
        auto& object=slots[part];auto* item=object.GetItem455();if(!item)return false;
        auto clone=host.clonePayload(item);const BYTE itemType=kind(item);
        if(itemType==8||itemType==46)host.detachedEffect(object,2);
        object.Clear();host.itemEffect(clone.get(),false);clone.reset();
        if((part==6||part==11)&&host.actionTypeOne())host.repeatAction();
        return true;
    }
};
