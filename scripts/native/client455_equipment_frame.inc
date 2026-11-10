#include "addcodebyjang/effectcore.h"
#include "client455_effect_positions.h"

BOOL RF455EquipmentObject::Animation(DWORD frame){
    if(!CResObject::Animation(frame)||IsDisable(128)||!mesh455)return FALSE;
    _GetCharIF()->FrameMove(mesh455);return TRUE;
}
void RF455EquipmentObject::UpdateAlwaysEffect455(){
    if(!mesh455||(m_dwStatusFlag&0x21000)||IsDisable(2))return;
    if(!field608455){
        field608455=1;RF455EquipmentDummyPoints points;points.bind(*mesh455);
        for(unsigned i=0;i<10;++i)SetDummy455(i,points.get(i));
    }
    //7DBE20 and7F2C50 branch on wrapper virtual120(kind2),not objecttypeBYTE4.
    //4043C0/405040 prove false for both classes implemented here. Thus these
    //classes do not spawn orjiggle ground-item magic. GroundObject remains a
    //separate unported wrapper andcannot silently inherit a fabricated path.
    if(IsMeshWrapperKind455(2))throw std::logic_error("455 ground-wrapper frame provider has not been ported");
    if(m_dwEffectID[0])SetMagicState(m_dwEffectID[0],IsEnable(0x20000)?3:1);
}
void RF455EquipmentObject::FrameMove(){
    UpdateAlwaysEffect455();CResObject::FrameMove();
    if(!animationEffects455.magic||!m_dwItemField588455)return;
    if(IsEnable(256))SetMagicState(animationEffects455.magic,1);
    auto* owner=reinterpret_cast<CCharacter*>(static_cast<std::uintptr_t>(m_dwItemField588455));
    Vector3f position;owner->GetPosition(position);
    auto* entry=GetMagicListFromID(animationEffects455.magic);
    if(entry&&entry->mMagicPtr){
        if(!frameOwner455||frameOwner455->actor!=owner)throw std::logic_error("455 equipment follow has no live actor pose view");
        float resolved[3];auto* process=static_cast<CProcessMagic*>(entry->mMagicPtr);
        const auto result=RF455_ResolveEffectPosition(resolved,*frameOwner455,process->mCreateType);
        if(result.targetReturn){
            if(!result.defined)throw std::logic_error("455 follow position depends on uninitialised target data");
            std::memcpy(entry->mMat[3],resolved,12);std::memcpy(position,resolved,12);
        }
    }
    if(!MovePosMagicEffect(animationEffects455.magic,position,owner->GetRotY()))animationEffects455.magic=0;
}
void RF455EquipmentObject::ProcessAnimationEffect455(DWORD mode,RF455EquipmentEffectBackend& backend,const RF455EquipmentEffectOwner& owner){
    if(owner.object!=reinterpret_cast<void*>(static_cast<std::uintptr_t>(m_dwItemField588455)))
        throw std::logic_error("455 equipment effect owner differs from its assigned actor");
    DWORD mesh=ID_INVALID;BYTE kind=255;
    if(owner.object){
        auto* item=equipmentPayload455(*this);
        if(!item)throw std::logic_error("455 animation effect has no normal payload");
        if(item->header().data16){const auto data=item->rawMetadata();mesh=equipmentField455<DWORD>(data,72);kind=equipmentField455<BYTE>(data,88);}
    }
    //46D3D0:magic starts at actorposition;wave requests use equipment+80.
    animationEffects455.process(owner,m_vecPos,mesh,kind,IsEnable(256)!=0,mode,backend);
}
