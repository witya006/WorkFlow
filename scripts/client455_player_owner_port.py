"""Migrate embedded player equipment ownership without legacy payload casts."""
def port_player_owner(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1 and b'\r\n' in old and raw.count(old.replace(b'\r\n',b'\n'))==1:old=old.replace(b'\r\n',b'\n')
        if raw.count(old)!=1:raise ValueError('Player owner anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    def body(signature,replacement):
        nonlocal raw
        first,last=section(raw,signature,signature);raw=raw[:first]+replacement+raw[last:]
    if relative=='character/player/cbaseplayer.h':
        raw=b'#include "client455_player_equipment.h"\n#include "client455_equipment_conditions.h"\nclass RF455PlayerProcState;\n'+raw
        once(b'class CBaseProc\r\n{',b'class CBaseProc\r\n{\n\tfriend class RF455PlayerProcState;')
        once(b'class CPlayerProc : public CBaseProc\r\n{',b'class CPlayerProc : public CBaseProc\r\n{\n\tfriend class RF455PlayerProcState;')
        first=raw.index(b'\tCNormalItem\t\tm_listNormalItem[');last=raw.index(b'\tDWORD\t\t\tm_dwEquipmentVersion',first)
        raw=raw[:first]+b'\tRF455PlayerProcState* m_owner455;\n\n'+raw[last:]
        once(b'\tCPlayerProc();',b'''    CPlayerProc();
    CPlayerProc(const CPlayerProc&);CPlayerProc& operator=(const CPlayerProc&)=delete;
    void InitEquipment455();void DestroyEquipment455();
    RF455PlayerEquipment& Equipment455();RF455EquipmentConditions& EquipmentConditions455();
    RF455PlayerEquipmentObject* GetEquipItem455(BYTE);RF455ManagedItem* GetNormalItem455(BYTE);
    BOOL PutOnTypedEquipment455(CItemObject*,bool);BOOL CreateTypedEquipment455(CItemObject*,bool);
    void WeaponAndShield455(BYTE);void SetItemAnimation455(BYTE,DWORD);
    void SetItemAnimation455(RF455PlayerEquipmentObject&,DWORD);
    void RenderEquipment455();void AnimateEquipment455();void ShadowEquipment455();void RematchEquipment455(BYTE);
    void FlagsEquipment455(DWORD,bool);void LightEquipment455(DWORD,BYTE);void MaterialEquipment455();void AlphaEquipment455(float);
    void ApplyTypedItemEffect455(RF455ManagedItem*,bool);void RefreshEquipmentConditions455();''')
        return raw,True
    if relative=='character/player/cplayer.h':
        once(b'friend class CPlayerProc;',b'friend class CPlayerProc;\n\tfriend class RF455PlayerProcState;')
        once(b'\tBYTE\t\t\tm_byUserGrade;',b'\tBYTE m_profile17796_455=0,m_specialEquipmentByte455=0;\n\tBYTE\t\t\tm_byUserGrade;')
        once(b'\tCPlayer();',b'''\tCPlayer();
    RF455PlayerEquipmentObject* GetEquipItem455(BYTE);RF455ManagedItem* GetNormalItem455(BYTE);
    RF455EquipmentConditions& EquipmentConditions455();
    BOOL PutOnEquipment455(CItemObject*,bool alreadyEquipped=false);
    void RefreshEquipmentConditions455(){m_clsPlayerProc.RefreshEquipmentConditions455();}
    virtual void EquipmentSkillLevel455(BYTE);''')
        return raw,True
    if relative=='character/avatar/cavatar.h':
        once(b'\tCAvatar();',b'\tCAvatar();\n\tvoid EquipmentSkillLevel455(BYTE) override;\n\tBOOL PutOffEquipment455(BYTE);')
        return raw,True
    if relative=='character/player/cplayer.cpp':
        body(b'CPlayer::SetAction_SwitchingCombatMode(',b'''CPlayer::SetAction_SwitchingCombatMode(){
    //44BE00 uses embedded5200 even while mounted;the old UMS guard is absent.
    if(m_byPrevCombatMode==m_byCombatMode)return;
    if(m_byCombatMode>1)throw std::logic_error("455 combat mode outside verified table domain");
    static const BYTE animation[2]={2,1},fade[2]={1,2};
    auto* weapon=m_clsPlayerProc.GetEquipItem455(6);
    auto* shield=m_clsPlayerProc.GetEquipItem455(7);
    if(weapon){m_clsPlayerProc.SetItemAnimation455(*weapon,animation[m_byCombatMode]);weapon->SetFade455(fade[m_byCombatMode],static_cast<BYTE>(static_cast<int>(_GetFPS())));}
    if(shield){m_clsPlayerProc.SetItemAnimation455(*shield,animation[m_byCombatMode]);shield->SetFade455(fade[m_byCombatMode],static_cast<BYTE>(static_cast<int>(_GetFPS())));}
}''')
        raw=b'#include <stdexcept>\n'+raw
        return raw,True
    if relative=='gameprogress/cgp_login.cpp':
        raw=b'#include "addcodebyjang/foreffect.h"\n'+raw
        #53BBCD calls effects init afterLoadData,before created=1.53BC1F
        #destroys effects afterbase Destroy,beforecamera andUnloadData.
        first,last=section(raw,b'CGP_LogIn::Create(',b'CGP_LogIn::Create(');fragment=raw[first:last]
        anchor=b'\tm_bIsCreated = TRUE;'
        if fragment.count(anchor)!=1:raise ValueError('Login effects startup boundary changed')
        fragment=fragment.replace(anchor,b'\tCreateEffect();\n'+anchor);raw=raw[:first]+fragment+raw[last:]
        first,last=section(raw,b'CGP_LogIn::Destroy(',b'CGP_LogIn::Destroy(');fragment=raw[first:last]
        anchor=b'\tD3DXMATRIX mat;'
        if fragment.count(anchor)!=1:raise ValueError('Login effects teardown boundary changed')
        fragment=fragment.replace(anchor,b'\tDestroyEffect();\n'+anchor);raw=raw[:first]+fragment+raw[last:]
        #The transitional Login shell still owns its legacy load scheduling.
        #Migrate actual object accesses;do not claim the whole455stage policy.
        first,last=section(raw,b'LoadDummyResouce(',b'LoadDummyResouce(');fragment=raw[first:last]
        for old,new in [
            (b'CEquipItem *',b'RF455PlayerEquipmentObject *'),
            (b'j < MAX_EQUIP_PART',b'j < RF455PlayerEquipment::PhysicalSlots'),
            (b'->GetEquipItem( j )',b'->GetEquipItem455( j )'),
            (b'pEquipItem->GetMesh()',b'pEquipItem->GetMesh455()')]:
            if fragment.count(old)!=1:raise ValueError('Login dummy equipment anchor '+repr(old))
            fragment=fragment.replace(old,new)
        raw=raw[:first]+fragment+raw[last:]
        first,last=section(raw,b'CGP_LogIn::Render(',b'CGP_LogIn::Render(');fragment=raw[first:last]
        for old,new in [
            (b'CEquipItem * pWeapon = _GetAvatarDummy(i)->GetEquipItem( IEPT_WEAPON );',b'auto* pWeapon=_GetAvatarDummy(i)->GetEquipItem455(IEPT_WEAPON);'),
            (b'CEquipItem * pShield = _GetAvatarDummy(i)->GetEquipItem( IEPT_SHIELD );',b'auto* pShield=_GetAvatarDummy(i)->GetEquipItem455(IEPT_SHIELD);'),
            (b'pWeapon->SetFadeMode( FRM_NONE );',b'pWeapon->SetFade455(0);'),
            (b'pShield->SetFadeMode( FRM_NONE );',b'pShield->SetFade455(0);')]:
            if fragment.count(old)!=1:raise ValueError('Login render equipment anchor '+repr(old))
            fragment=fragment.replace(old,new)
        raw=raw[:first]+fragment+raw[last:]
        return raw,True
    if relative=='character/avatar/cavatar_etc.cpp':
        body(b'CAvatar::PutOffEquipment(',b'CAvatar::PutOffEquipment(BYTE part){return PutOffEquipment455(part);}')
        return raw,True
    if relative=='gameobject/board/skillforceboard/cskillboard.h':
        once(b'\tCSkillBoard();',b'\tCSkillBoard();\n\tvoid ApplyEquipmentLevel455(BYTE);')
        return raw,True
    if relative=='mainapp.cpp':
        #Tagged-audio port adds the actual Close later in preparation.
        first,last=section(raw,b'CMainApp::Destroy(',b'CMainApp::Destroy(');at=raw.index(b'{',first)+1
        raw=raw[:at]+b'\n\tRF455_CloseEquipmentSounds455();'+raw[at:]
        raw=b'#include "client455_equipment_effects.h"\n'+raw;return raw,True
    if relative=='character/player/cbaseplayer.cpp':
        first,last=section(raw,b'CPlayerProc::CPlayerProc(',b'CPlayerProc::CPlayerProc(');at=raw.index(b'{',first)+1
        raw=raw[:at]+b'\n\tInitEquipment455();'+raw[at:]
        body(b'CPlayerProc::~CPlayerProc(',b'CPlayerProc::~CPlayerProc(){DestroyEquipment455();}')
        replacements=[
            (b'CPlayerProc::Render( void )',b'CPlayerProc::Render(){RenderEquipment455();}'),
            (b'CPlayerProc::Animation( void )',b'CPlayerProc::Animation(){AnimateEquipment455();}'),
            (b'CPlayerProc::CreateShadow( void )',b'CPlayerProc::CreateShadow(){ShadowEquipment455();}'),
            (b'CPlayerProc::RematchItemToBone(',b'CPlayerProc::RematchItemToBone(BYTE part){RematchEquipment455(part);}'),
            (b'CPlayerProc::PutOnEquipment( BYTE',b'CPlayerProc::PutOnEquipment(BYTE part,DWORD index){return Equipment455().putOn(part,index);}'),
            (b'CPlayerProc::PutOnEquipment( CBoardItem',b'CPlayerProc::PutOnEquipment(CBoardItem* source){return PutOnTypedEquipment455(source,false);}'),
            (b'CPlayerProc::PutOnEquipment( CEquipItem',b'CPlayerProc::PutOnEquipment(CEquipItem* source){if(!source)return FALSE;throw std::logic_error("455 legacy equipment source must migrate to the typed wrapper API");}'),
            (b'CPlayerProc::PutOffEquipment(',b'CPlayerProc::PutOffEquipment(BYTE part){return Equipment455().putOff(part);}'),
            (b'CPlayerProc::CreateEquipment( BYTE',b'CPlayerProc::CreateEquipment(BYTE part,DWORD index){return Equipment455().create(part,index);}'),
            (b'CPlayerProc::CreateEquipment( CBoardItem',b'CPlayerProc::CreateEquipment(CBoardItem* source){return CreateTypedEquipment455(source,false);}'),
            (b'CPlayerProc::CreateEquipment( CEquipItem',b'CPlayerProc::CreateEquipment(CEquipItem* source){if(!source)return FALSE;throw std::logic_error("455 legacy equipment factory input has no typed payload");}'),
            (b'CPlayerProc::PutOnEquipment_SetWeaponAndShield(',b'CPlayerProc::PutOnEquipment_SetWeaponAndShield(BYTE part){WeaponAndShield455(part);}'),
            (b'CPlayerProc::SetEquipItemAnimation(',b'CPlayerProc::SetEquipItemAnimation(BYTE part,BYTE mode){SetItemAnimation455(part,mode);}'),
            (b'CPlayerProc::SetLightColor( DWORD',b'CPlayerProc::SetLightColor(DWORD color,BYTE flag){LightEquipment455(color,flag);}'),
            (b'CPlayerProc::SetLightColorFromMap(',b'CPlayerProc::SetLightColorFromMap(){MaterialEquipment455();}'),
            (b'CPlayerProc::SetAlphaDensity(',b'CPlayerProc::SetAlphaDensity(float value){AlphaEquipment455(value);}'),
            (b'CPlayerProc::Enable(',b'CPlayerProc::Enable(DWORD flags){FlagsEquipment455(flags,true);}'),
            (b'CPlayerProc::Disable(',b'CPlayerProc::Disable(DWORD flags){FlagsEquipment455(flags,false);}'),
            (b'CPlayerProc::GetEquipItem(',b'CPlayerProc::GetEquipItem(BYTE part){if(GetEquipItem455(part))throw std::logic_error("455 legacy equipment consumer is not migrated");return NULL;}'),
            (b'CPlayerProc::GetNormalItem(',b'CPlayerProc::GetNormalItem(BYTE part){if(GetNormalItem455(part))throw std::logic_error("455 legacy normal-item consumer is not migrated");return NULL;}')]
        for signature,replacement in replacements:body(signature,replacement)
        first,last=section(raw,b'CPlayerProc::GetAnimationData_Normal(',b'CPlayerProc::GetAnimationData_Normal(')
        fragment=raw[first:last]
        old=b'CEquipItem * pWeapon = GetEquipItem( IEPT_WEAPON );'
        if fragment.count(old)!=1 or fragment.count(b'pWeapon->GetMeshID()')!=1:raise ValueError('Typed player animation weapon anchor')
        fragment=fragment.replace(old,b'auto* pWeapon=GetEquipItem455(IEPT_WEAPON);').replace(b'pWeapon->GetMeshID()',b'pWeapon->GetPlan455().meshID')
        raw=raw[:first]+fragment+raw[last:]
        if b'm_listEquipItem' in raw or b'm_listNormalItem' in raw:raise ValueError('Unmigrated direct player equipment array')
        return raw,True
    if relative=='character/character/ccharacter_etc.cpp':
        first,last=section(raw,b'CCharacter::RefreshConditionInfo(',b'CCharacter::RefreshConditionInfo(');at=raw.index(b'{',first)+1
        raw=raw[:at]+b'\n\tif(GetCharTypeID()==0||GetCharTypeID()==15){static_cast<CPlayer*>(this)->RefreshEquipmentConditions455();return;}'+raw[at:]
        return raw,True
    return raw,False
