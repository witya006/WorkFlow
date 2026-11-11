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
#include "addcodebyjang/playerspecialeffect.h"
#include "client455_player_equipment.h"
#include "client455_equipment_conditions.h"
#include "client455_effect_positions.h"
#include "client455_normal_item_copy.h"
#include <new>
#include <stdexcept>
extern CMainApp g_MainApp;

namespace {
RF455LoopSoundRegistry equipmentLoops455;
RF455EquipmentSoundGate actorEffectSoundGate455;
bool pendingEquipmentLift455=false; //C0C090 BSS;no verified nonzero writer yet.
RF455BasicItem& basicOwner455(RF455ManagedItem* item){
    auto* result=dynamic_cast<RF455BasicItem*>(item);
    if(!result)throw std::logic_error("455 player owner requires a normal payload");return *result;
}
template<class T>T ownerField455(RF455ItemDataSpan row,unsigned offset){
    if(!row.data||offset>row.size||sizeof(T)>row.size-offset)throw std::out_of_range("455 owner metadata extent");
    T value;std::memcpy(&value,row.data+offset,sizeof value);return value;
}
}
void RF455_OpenEquipmentSounds455(){equipmentLoops455.open();}
void RF455_CloseEquipmentSounds455(){equipmentLoops455.close();}

void RF455_PlayActorEffectSound(std::uint32_t id, const float* position, std::uint32_t loop) {
    actorEffectSoundGate455.play(id, position, loop, [] { return double(R3GetTime()); },
        [](std::uint32_t key, const float* at, std::uint32_t repeat) {
            g_MainApp.TaggedAudio455().Play(key, repeat, 0, at);
        });
}

// Actual source owner for the embedded processor. Source object layouts are
// independent of the private455ABI;no old CNormalItem/ITEM_DATA overlay is used.
class RF455PlayerProcState:public RF455EquipmentCallbacks,public RF455EquipmentAnimationCallbacks,
                           public RF455EquipmentConditionHost,public RF455EquipmentEffectBackend {
public:
    CPlayerProc& proc;RF455PlayerEquipment equipment;RF455EquipmentConditions ownedConditions;
    RF455EquipmentConditions& conditions;
    RF455EffectPositionView view;std::array<RF455EquipmentDummyPoints,10> points;
    explicit RF455PlayerProcState(CPlayerProc& value):proc(value),equipment(*this),conditions(ownedConditions){}
    RF455PlayerProcState(CPlayerProc& value,const RF455PlayerProcState& source):proc(value),equipment(*this,source.equipment),conditions(source.conditions){
        //404A40 copies12members;405A40 copies the old actor/bone/box links.
        //The target condition block belongs to that borrowed actor,not Proc.
        //Callback/view pointers are source implementation details and must
        //refer to this copy's adapter while retaining the same target actor.
        if(proc.m_pPlayer)refreshView();
        for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i){auto& object=equipment.physical455(BYTE(i));object.BindAnimationOwner455(this);object.BindFrameOwner455(&view);}
    }
    CPlayer& actor()const{if(!proc.m_pPlayer)throw std::logic_error("455 player processor has no actor");return *proc.m_pPlayer;}
    void refreshView(){
        view.actor=&actor();
        for(unsigned part=0;part<view.parts.size();++part){auto& object=equipment.physical455(BYTE(part));
            for(unsigned n=0;n<10;++n)points[part].set(n,object.GetDummy455(n));
            view.parts[part]={!object.IsEmpty(),object.GetMesh455(),&points[part]};object.BindFrameOwner455(&view);
        }
    }
    void syncLegacyTotals(){
        //Explicit source field transfer for remaining old consumers,not an ABI
        //cast. Full455UI metrics/SF writers andother legacy consumers stay open.
        auto& out=actor().m_stConditionInfo;
        out.m_dwTotalStrikingPower[0]=conditions.total.minimumPower;out.m_dwTotalStrikingPower[1]=conditions.total.maximumPower;
        out.m_dwTotalForcePower[0]=conditions.total.minimumForce;out.m_dwTotalForcePower[1]=conditions.total.maximumForce;
        out.m_dwTotalDefencePower=conditions.total.defence;out.m_fTotalHitProb=conditions.total.hit;
    }
    BYTE race()const override{return actor().GetRace();}
    void* player()const override{return &actor();}
    RF455ManagedItem* createPayload(BYTE type,DWORD index)override{return RF455_GameItems().create(0,type,index);}
    std::unique_ptr<RF455ManagedItem> clonePayload(RF455ManagedItem* item)override{
        return std::unique_ptr<RF455ManagedItem>(new(std::nothrow) RF455DetachedNormalItem(basicOwner455(item)));
    }
    void specialSlotByte(BYTE value)override{actor().m_specialEquipmentByte455=value;}
    void animation(RF455PlayerEquipmentObject& object,DWORD mode)override{refreshView();object.BindFrameOwner455(&view);object.SetEquipmentAnimation455(mode,*this);}
    bool weaponScaleEnabled()const override{return race()==4;}
    void weaponScale(RF455PlayerEquipmentObject& object,float value)override{object.SetScale(value);}
    bool hasBone()const override{return proc.m_pBone!=nullptr;}
    void rematch(CMesh* mesh)override{if(proc.m_pBone&&mesh)_GetCharIF()->RematchParent(proc.m_pBone,mesh);}
    bool combatMode()const override{return actor().GetCombatMode()!=0;}
    bool isFade(RF455PlayerEquipmentObject& object,BYTE value)override{return object.GetFade455()==value;}
    void fade(RF455PlayerEquipmentObject& object,BYTE value,BYTE maximum)override{object.SetFade455(value,maximum);}
    void repeatAction()override{actor().SetAction(actor().GetAction(),FALSE);}
    void itemEffect(RF455ManagedItem* item,bool add)override{conditions.apply(item,add,*this);syncLegacyTotals();}
    void detachedEffect(RF455PlayerEquipmentObject& object,DWORD mode)override{itemAnimationEffect(object,mode);}
    bool actionTypeOne()const override{return (actor().GetAction()>>28)==1;}
    void itemAnimationEffect(RF455PlayerEquipmentObject& object,DWORD mode)override{
        refreshView();RF455EquipmentEffectOwner owner;owner.object=&actor();owner.index=actor().GetIndex();owner.race=race();owner.position=actor().GetPosition();owner.yaw=actor().GetRotY();
        object.ProcessAnimationEffect455(mode,*this,owner);
    }
    CAniData* findItemAnimation(DWORD id)override{return _GetAniMgr()->GetAni(5,id);}
    void adjustOwnerHeight(RF455PlayerEquipmentObject&,bool add)override{
        auto* worn=actor().GetNormalItem455(46);DWORD mesh=ID_INVALID;
        if(worn&&worn->header().data16)mesh=ownerField455<DWORD>(basicOwner455(worn).rawMetadata(),72);
        const float amount=RF455_MountingHeight455(race(),mesh);actor().SetPosition(actor().GetPosX(),actor().GetPosY()+(add?amount:-amount),actor().GetPosZ());
    }
    bool pendingOwnerLift()const override{return pendingEquipmentLift455;}
    void clearPendingOwnerLift()override{pendingEquipmentLift455=false;}
    bool hasActor()const override{return proc.m_pPlayer!=nullptr;}
    std::uint32_t actorType()const override{return actor().GetCharTypeID();}
    bool mountedState2()const override{return actor().IsEqualUnitMountState(2)!=FALSE;}
    bool profileByte17796IsOne()const override{return actor().m_profile17796_455==1;}
    bool globalBonusEnabled()const override{return _GetNetworkMgr()->PremiumState455()!=0;}
    std::array<float,2> globalAvatarBonuses()const override{
        auto* local=_GetAvatar();if(!local)throw std::logic_error("455 premium condition has no global Avatar");return local->PremiumBenefits455().combatBonuses();
    }
    RF455ManagedItem* basePlayerItem(std::uint8_t part)override{return actor().m_clsPlayerProc.GetNormalItem455(part);}
    void skillLevelChanged(std::uint32_t value)override{actor().EquipmentSkillLevel455(BYTE(value));}
    void refreshGlobalAvatarInfo()override{
        syncLegacyTotals();auto* local=_GetAvatar();if(!local)throw std::logic_error("455 condition refresh has no global Avatar");
        //This is the real existing UI owner. Its complete455metric/layout and
        //remaining state producers are explicitly still outside acceptance.
        local->UI_RefreshCharInfoWindow(FALSE);
    }
    bool effectExists(std::uint32_t id)override{return IsExistFromMagicSpt(id)!=FALSE;}
    void expireMagic(std::uint32_t id,float delay)override{SetDisapearTimeMagicEffect(id,delay);}
    std::uint32_t startMagic(const RF455EquipmentEffectOwner& owner,std::uint32_t id,bool render)override{
        refreshView();float position[3];std::memcpy(position,owner.position,12);return RF455_StartMagicAtActor(view,position,owner.yaw,id,nullptr,render?1:0);
    }
    RF455EquipmentEffectLocal localActor()override{
        auto* local=_GetAvatar();if(!local)return {};RF455EquipmentEffectLocal result;
        result.index=local->GetIndex();result.action=local->GetAction();result.walkMode=local->GetWalkMode();return result;
    }
    void playWave(std::uint32_t id,const float* position,std::uint32_t loop)override{
        RF455_PlayActorEffectSound(id, position, loop);
    }
    void stopWave(std::uint32_t id,std::uint32_t tag)override{g_MainApp.TaggedAudio455().Stop(id,tag);}
    void trackLoop(std::uint32_t id,std::uint32_t tag)override{equipmentLoops455.add(id,tag);}
    void untrackLoop(std::uint32_t id,std::uint32_t tag)override{equipmentLoops455.remove(id,tag,[this](std::uint32_t key,std::uint32_t token){stopWave(key,token);});}
};

void CPlayerProc::InitEquipment455(){m_owner455=new RF455PlayerProcState(*this);}
CPlayerProc::CPlayerProc(const CPlayerProc& source):CBaseProc(source),m_owner455(new RF455PlayerProcState(*this,*source.m_owner455)),
    m_dwEquipmentVersion(source.m_dwEquipmentVersion),m_dwEquipmentRequestTime(source.m_dwEquipmentRequestTime),m_pData(source.m_pData){}
void CPlayerProc::DestroyEquipment455(){delete m_owner455;m_owner455=nullptr;}
RF455PlayerEquipment& CPlayerProc::Equipment455(){if(!m_owner455)throw std::logic_error("455 equipment owner is not initialized");return m_owner455->equipment;}
RF455EquipmentConditions& CPlayerProc::EquipmentConditions455(){if(!m_owner455)throw std::logic_error("455 condition owner is not initialized");return m_owner455->conditions;}
RF455PlayerEquipmentObject* CPlayerProc::GetEquipItem455(BYTE part){return Equipment455().get(part);}
RF455ManagedItem* CPlayerProc::GetNormalItem455(BYTE part){return Equipment455().payload(part);}
BOOL CPlayerProc::PutOnTypedEquipment455(CItemObject* source,bool equipped){return equipped?Equipment455().putOnEquipment(source):Equipment455().putOnBoard(source);}
BOOL CPlayerProc::CreateTypedEquipment455(CItemObject* source,bool requireNonempty){return Equipment455().createFrom455(source,requireNonempty);}
void CPlayerProc::WeaponAndShield455(BYTE part){Equipment455().weaponAndShield455(part);}
void CPlayerProc::SetItemAnimation455(RF455PlayerEquipmentObject& object,DWORD mode){m_owner455->animation(object,mode);}
void CPlayerProc::SetItemAnimation455(BYTE part,DWORD mode){if(auto* object=GetEquipItem455(part))SetItemAnimation455(*object,mode);}
void CPlayerProc::RenderEquipment455(){
    auto& state=*m_owner455;auto& actor=state.actor();
    for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i){if(!state.equipment.canRender(BYTE(i),actor.GetRace()))continue;
        auto& object=state.equipment.physical455(BYTE(i));auto* mesh=object.GetMesh455();if(!actor.PSetVertexBlending(i,mesh,FALSE))continue;
        object.PrepareOverlaySlot455(BYTE(i));
        if(i==9)throw std::logic_error("455 Siege draw branch still requires its live actor flags/provider");
        object.SetPosition(actor.GetPosition());object.SetRotY(actor.GetRotY(),FALSE);object.SetScale(actor.GetScale());object.Render();
    }
}
void CPlayerProc::AnimateEquipment455(){
    auto& state=*m_owner455;auto& actor=state.actor();state.refreshView();
    for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i){auto& object=state.equipment.physical455(BYTE(i));auto* mesh=object.GetMesh455();
        //4512C0/4513C0 returnsfalse thisframe on missing mesh;the target's
        //default assignment helper itself is a real empty return1 function.
        if(!mesh)continue;
        if((i==6||i==7)&&!object.IsEmpty()&&m_pBone){_GetCharIF()->RematchParent(m_pBone,mesh);_GetCharIF()->AnimationReset(mesh);}
        object.BindFrameOwner455(&state.view);object.FrameMove();object.Animation();actor.PSetVertexBlending(i,mesh,TRUE);
    }
    CPlayerSpecialEffectFrameMove(&actor);
}
void CPlayerProc::ShadowEquipment455(){
    auto& state=*m_owner455;auto& actor=state.actor();
    //Existing shadow consumer is migrated to typed ownership;complete455
    //shadow-pass behavior remains a separately tracked requirement.
    for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i){auto* object=state.equipment.get(BYTE(i));if(!object)continue;
        if((i==6||i==7)&&!actor.GetCombatMode())continue;auto* mesh=object->GetMesh455();if(!mesh)continue;
        actor.PSetVertexBlending(i,mesh,FALSE);_GetCharIF()->DrawCharacterShadow(mesh,actor.GetPosition(),actor.GetRotY(),.8f*actor.GetAlphaDensity(),1.0f);
    }
}
void CPlayerProc::RematchEquipment455(BYTE part){if(part!=6&&part!=7)return;auto* object=GetEquipItem455(part);if(object&&m_pBone&&object->GetMesh455()){_GetCharIF()->RematchParent(m_pBone,object->GetMesh455());_GetCharIF()->AnimationReset(object->GetMesh455());}}
void CPlayerProc::FlagsEquipment455(DWORD flags,bool enable){for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i)if(auto* object=GetEquipItem455(BYTE(i))){if(enable)object->Enable(flags);else object->Disable(flags);}}
void CPlayerProc::LightEquipment455(DWORD color,BYTE flag){for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i)if(auto* object=GetEquipItem455(BYTE(i)))object->SetLightColor(color,flag);}
void CPlayerProc::MaterialEquipment455(){for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i)if(auto* object=GetEquipItem455(BYTE(i)))object->SetMaterial(&m_pPlayer->m_d3dMaterial);}
void CPlayerProc::AlphaEquipment455(float value){for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i)if(auto* object=GetEquipItem455(BYTE(i)))object->SetAlphaDensity(value);}
void CPlayerProc::ApplyTypedItemEffect455(RF455ManagedItem* item,bool add){m_owner455->itemEffect(item,add);}
void CPlayerProc::RefreshEquipmentConditions455(){
    auto& state=*m_owner455;state.conditions.resetEquipment();
    for(unsigned i=0;i<RF455PlayerEquipment::PhysicalSlots;++i)if(auto* item=GetNormalItem455(BYTE(i)))state.conditions.apply(item,true,state);
    state.syncLegacyTotals();
}
RF455PlayerEquipmentObject* CPlayer::GetEquipItem455(BYTE part){if(m_pResProc!=&m_clsPlayerProc)throw std::logic_error("455 active unit equipment provider is not restored");return m_clsPlayerProc.GetEquipItem455(part);}
RF455ManagedItem* CPlayer::GetNormalItem455(BYTE part){if(m_pResProc!=&m_clsPlayerProc)throw std::logic_error("455 active unit payload provider is not restored");return m_clsPlayerProc.GetNormalItem455(part);}
RF455EquipmentConditions& CPlayer::EquipmentConditions455(){return m_clsPlayerProc.EquipmentConditions455();}
BOOL CPlayer::PutOnEquipment455(CItemObject* source,bool alreadyEquipped){if(m_pResProc!=&m_clsPlayerProc)throw std::logic_error("455 active unit equipment transfer provider is not restored");return m_clsPlayerProc.PutOnTypedEquipment455(source,alreadyEquipped);}
void CPlayer::EquipmentSkillLevel455(BYTE){/*43E600 is a proven empty base callback.*/}
void CAvatar::EquipmentSkillLevel455(BYTE value){auto* board=_GetSkillBoard();if(!board)throw std::logic_error("455 equipment skill callback has no skill board");board->ApplyEquipmentLevel455(value);}
BOOL CAvatar::PutOffEquipment455(BYTE part){
    if(!CPlayer::PutOffEquipment(part))return FALSE;
    if(part<5)return CPlayer::PutOnEquipment455(&m_defaultItems455[part],true);
    if(part==27)UI_RefreshCharInfoWindow(FALSE);
    if((part==8||part==46)&&_GetSkillBoard()){
        auto* wrapper=_GetSkillBoard()->GetObject(2,part==8?0:1);
        if(!wrapper)return FALSE; //419BB0:removal already happened.
        if(wrapper->GetItem455())throw std::logic_error("455 cloak/Siege skill unlink owners andicon state require migration");
        auto* local=_GetAvatar();if(!local)throw std::logic_error("455 equipment removal has no global Avatar");
        if(local->GetWalkMode()==(part==8?2:4))throw std::logic_error("455 equipment removal movement-mode transition requires migration");
    }
    return TRUE;
}
void CSkillBoard::ApplyEquipmentLevel455(BYTE value){
    for(unsigned pack=0;pack<GetMaxPackNum();++pack)for(unsigned socket=0;socket<GetMaxSocketNum455(BYTE(pack));++socket){auto* wrapper=GetObject(BYTE(pack),BYTE(socket));if(!wrapper)continue;
        auto* item=dynamic_cast<RF455SkillForceItem*>(wrapper->GetItem455());if(!item)throw std::logic_error("455 skill board still contains a legacy/mixed payload");item->SetEquipmentLevel455(value);
    }
}
void RF455_UpdateSkillIconLevel455(void* icon,BYTE value){static_cast<CGUISkFcUnit*>(icon)->SetLevel(value);}
