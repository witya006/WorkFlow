"""Load 455 character tables and adapt NPC and monster consumers."""

from client455_trade_ore_port import replace


def port_character_tables(raw,relative,section):
    if relative=='datatable/ccharacterdatamgr.h':
        raw=b'#include "client455_character_tables.h"\n'+raw
        raw=replace(raw,b'class CMonsterData : public BASE_DATA\n{',
                    b'class CMonsterData : public BASE_DATA\n{\n\tfriend class CCharacterDataMgr;')
        raw=replace(raw,b'CDataMgr \t\t\tm_listMonster;',b'std::vector<CMonsterData> m_monsters455;')
        raw=replace(raw,b'( CMonsterData * )m_listMonster.GetData( pi_dwIndex )',
                    b'pi_dwIndex < m_monsters455.size() ? &m_monsters455[pi_dwIndex] : nullptr')
        raw=replace(raw,b'return m_listMonster.GetTotalNum();',
                    b'return static_cast<DWORD>(m_monsters455.size());')
        raw=replace(raw,b'DWORD\t\t\t\tm_dwMaxMerchant;\n\tDT_CNMInfo *\t\tm_listMarchant;',
                    b'std::vector<DT_CNMInfo> m_merchants455;')
        raw=replace(raw,b'return ( DT_CNMInfo * )&m_listMarchant[pi_dwIndex];',
                    b'return pi_dwIndex < m_merchants455.size() ? &m_merchants455[pi_dwIndex] : nullptr;')
        raw=replace(raw,b'return m_dwMaxMerchant;',
                    b'return static_cast<DWORD>(m_merchants455.size());')
        raw=replace(raw,b'float\tfYAngle;',b'float\tfYAngle;\n\tfloat fScale455;')
        anchor=b'\tDT_PlayerList \t\tm_listPlayer;'
        if raw.count(anchor)!=1:raise ValueError('Character data owner boundary changed')
        raw=raw.replace(anchor,b'\tRF455CharacterTables m_tables455;\n'+anchor)
        anchor=b'\tCCharacterDataMgr();'
        if raw.count(anchor)!=1:raise ValueError('Character data public boundary changed')
        raw=raw.replace(anchor,anchor+b'\n\tconst RF455CharacterTables& Tables455()const{return m_tables455;}\n\tRF455ItemDataSpan GetClassData455(const char*);\n\tRF455ItemDataSpan GetClassData455ByIndex(DWORD);')
        return raw,True
    if relative=='character/npc/cnpc.h':
        raw=replace(raw,b'DT_CNMInfo *\t\tm_pData;',b'DT_CNMInfo m_ownedStoreData455;\n\tDT_CNMInfo* m_pData;')
        raw=replace(raw,b'\tCMerchantItemMgr\tm_cItemList;',b'''    enum class MeshPose455 : BYTE { Drawable, Failed, FailureReported };
    MeshPose455 m_meshPose455 = MeshPose455::Drawable;
\tCMerchantItemMgr\tm_cItemList;''')
        raw=replace(raw,b'{ m_pData = pi_pData; }',b'''{
        if (pi_pData) m_ownedStoreData455 = *pi_pData;
        m_pData = pi_pData ? &m_ownedStoreData455 : nullptr;
    }''')
        raw=replace(raw,b'\t\t\tDWORD\t\t\tGetMeshID( void );',b'''    bool IsMeshPoseDrawable455() const { return m_meshPose455 == MeshPose455::Drawable; }
\t\t\tDWORD\t\t\tGetMeshID( void );''')
        return raw,True
    if relative=='character/npc/cnpc.cpp':
        raw=replace(raw,b'if( !_GetAvatar()->IsEqualRace( m_pData->byRace * 2 ) )',
                    b'if (m_pData->byRace != 0xff && !_GetAvatar()->IsEqualRace(m_pData->byRace * 2))')
        raw=replace(raw,b'return ( dynamic_cast< CCharacter * >( new CNpc( *this ) ) );',
                    b'''auto* npc = new CNpc(*this);
    npc->SetData(m_pData);
    if (npc->m_meshPose455 == MeshPose455::FailureReported)
        npc->m_meshPose455 = MeshPose455::Failed;
    return npc;''')
        signature=b'CNpc::Animation('
        first,last=section(raw,signature,signature)
        body=replace(raw[first:last],b'\t_GetCharIF()->FrameMove( m_pMesh );',b'''    const auto pose = _GetCharIF()->UpdatePose455(m_pMesh);
    if (pose != RF_POSE_OK) {
        if (m_meshPose455 != MeshPose455::FailureReported) {
            RF455_ObserveProtocol("npc-pose-failure", static_cast<unsigned>(pose), GetMeshID(), 0);
            m_meshPose455 = MeshPose455::FailureReported;
        }
        return TRUE;
    }
    m_meshPose455 = MeshPose455::Drawable;''')
        raw=raw[:first]+body+raw[last:]
        signature=b'CNpc::Render('
        first,last=section(raw,signature,signature)
        fade=b'\t\t\tm_fAlphaDensity -= 0.01f;'
        body=replace(raw[first:last],fade,fade+b'''
        if (!IsMeshPoseDrawable455()) return TRUE;''')
        raw=raw[:first]+body+raw[last:]
        signature=b'CNpc::CreateShadow('
        first,last=section(raw,signature,signature)
        shadow=b'\t_GetCharIF()->DrawCharacterShadow('
        body=replace(raw[first:last],shadow,b'''    if (!IsMeshPoseDrawable455()) return;
'''+shadow)
        raw=raw[:first]+body+raw[last:]
        raw=replace(raw,b'\tm_pMesh = _GetMeshMgr()->GetMesh( RLI_NPC, pi_dwIndex );',b'''    auto* mesh = _GetMeshMgr()->GetMesh(RLI_NPC, pi_dwIndex);
    if (mesh != m_pMesh) m_meshPose455 = MeshPose455::Drawable;
    m_pMesh = mesh;''')
        signature=b'CNpc::OpenShopWindow('
        first,last=section(raw,signature,signature)
        body=replace(raw[first:last],b'if( !m_pData )',
                     b'if (!m_pData || pi_byButtonOrder >= MAX_NPC_BUTTON_NUM)')
        return b'#include "client455_protocol_observation.h"\n'+raw[:first]+body+raw[last:],True
    if relative=='addcodebyjang/effectutil.cpp':
        signature=b'void EFUtil_PushShadow('
        first,last=section(raw,signature,signature)
        opening=raw.index(b'{',first,last)+1
        guard=b'''
    if (ptr->GetCharTypeID() == CTI_NPC &&
        !static_cast<const CNpc*>(ptr)->IsMeshPoseDrawable455()) return;
'''
        return raw[:opening]+guard+raw[opening:],True
    if relative=='character/npc/cmonster.cpp':
        # The 455 attribute initializer sets a health fraction, not a maximum
        # loaded from the record. The legacy integer health owner needs its own port.
        first=raw.index(b'\tSetMaxHP( m_pMonsterData->m_dwMaxHP );')
        last=raw.index(b'\tSetScale( m_pMonsterData->m_fScale );',first)
        raw=raw[:first]+raw[last:]
        raw=replace(raw,b'return MAI_CREATE_CREATE;',b'return 16; // 455 monster creation animation')
        normal=b'CMonster::GetAnimationData_Normal( DWORD pi_dwAniTypeID )'
        first,last=section(raw,normal,normal)
        body=replace(raw[first:last],b'GetMeshID() << 8',b'GetMeshID() << 12')
        body=replace(body,b'return GetAnimationDataByRandom( RLI_MONSTER, dwAniID );',b'''auto* animation = GetAnimationDataByRandom(RLI_MONSTER, dwAniID);
    RF455_ObserveProtocol("monster-animation-key", GetMeshID(), pi_dwAniTypeID,
                          animation ? m_Animation.GetAnimationID() : ID_INVALID);
    return animation;''')
        raw=raw[:first]+body+raw[last:]
        force=b'CMonster::GetAnimationData_Force( DWORD pi_dwAniTypeID )'
        first,last=section(raw,force,force)
        body=force+b'''
{
    if (pi_dwAniTypeID == ID_INVALID) return nullptr;

    const bool attackClip = RF455_GameItems().skillForce.usesMonsterAttackClip(
        m_clSFItem.GetSFType(), m_clSFItem.GetDTIndex(), m_clSFItem.GetLevel());
    const DWORD type = attackClip ? MAI_FORCE_ATTACK : MAI_FORCE_SUPPORT;
    const DWORD animationId = (GetMeshID() << 12) | (type << 4);
    m_Animation.SetAnimationID(animationId);
    return _GetAniMgr()->GetAni(RLI_MONSTER, animationId);
}'''
        return (b'#include "client455_protocol_observation.h"\n#include "client455_client_items.h"\n'
                +raw[:first]+body+raw[last:]),True
    if relative!='datatable/ccharacterdatamgr.cpp':return raw,False
    anchor=b'#include "CCharacterDataMgr.h"'
    if raw.count(anchor)!=1:raise ValueError('Character includes changed')
    raw=raw.replace(anchor,anchor+b'\n#include "client455_client_items.h"\n#include "client455_nation_paths.h"\n#include "client455_language.h"\n#include "network/cnetworkmgr.h"\n#include <cstring>\n#include <string>')
    raw=replace(raw,b'\tm_dwMaxMerchant\t\t\t= 0;\n\tm_listMarchant\t\t\t= NULL;',b'\tm_merchants455.clear();')
    raw=replace(raw,b'_DELETE_ARRAY( m_listMarchant );',b'std::vector<DT_CNMInfo>().swap(m_merchants455);')
    def edit(signature,change):
        nonlocal raw
        first,last=section(raw,signature,signature);raw=raw[:first]+change(raw[first:last])+raw[last:]
    def load(body):
        first=body.index(b'\t// load data');last=body.index(b'\t// make skill/force board')
        body=body[:first]+b'''    m_tables455.playerResult=m_tables455.loadPlayerFile();
    m_tables455.skillResult=LoadSkillForceData();
    m_tables455.storeResult=LoadNpcData();
    m_tables455.characterResult=LoadCharacterData();

'''+body[last:]
        for old,new in [(b'IBT_SKILL, MAX_UI_SKILL_CLASS_TYPE, MAX_SKILL / MAX_UI_SKILL_CLASS_TYPE',b'IBT_SKILL, 7, 20'),
                        (b'MAX_UI_SKILL_CLASS_TYPE, MAX_SKILL_MASTERY_NUM, MAX_SKILL',b'7, 12, 100'),
                        (b'IBT_FORCE, MAX_UI_FORCE_CLASS_TYPE, MAX_FORCE / MAX_UI_FORCE_CLASS_TYPE',b'IBT_FORCE, 6, 20'),
                        (b'MAX_UI_FORCE_CLASS_TYPE, MAX_FORCE_MASTERY_NUM, MAX_FORCE',b'6, 24, 100')]:
            if body.count(old)!=1:raise ValueError('Character board dimensions changed')
            body=body.replace(old,new)
        return body
    edit(b'CCharacterDataMgr::LoadData( void )',load)
    edit(b'CCharacterDataMgr::LoadSkillForceData( void )',lambda _:b'''CCharacterDataMgr::LoadSkillForceData( void ){
        const std::string names=std::string(RF455_GetClientDataRoot())+"\\\\NDSkillForce.edf";
        return RF455_GameItems().skillForce.loadFiles(".\\\\DataTable\\\\SkillForce.edf",names.c_str())?TRUE:FALSE;
    }''')
    edit(b'CCharacterDataMgr::GetNpc( DWORD pi_dwIndex )',lambda _:b'''CCharacterDataMgr::GetNpc( DWORD pi_dwIndex ){
        for (auto& merchant : m_merchants455)
            if (merchant.dwIndex == pi_dwIndex) return &merchant;
        return nullptr;
    }''')
    edit(b'CCharacterDataMgr::LoadNpcData( void )',lambda _:b'''CCharacterDataMgr::LoadNpcData( void ){
        const bool localized = m_tables455.loadStoreFiles(_GetNetworkMgr()->m_worldEntry455.npcShop);
        std::vector<DT_CNMInfo> merchants;
        merchants.reserve(m_tables455.stores.count);
        const auto copyText = [](auto& destination, RF455StoreTextView source) {
            const auto length = (std::min)(sizeof(destination) - 1, source.size);
            if (length) std::memcpy(destination, source.data, length);
            destination[length] = 0;
            if (length && length < source.size &&
                RF455_GetNormalLanguagePack()->isLead(destination, static_cast<int>(length - 1)))
                destination[length - 1] = 0;
        };
        for (DWORD row = 0; row < m_tables455.stores.count; ++row) {
            RF455StoreNpcView view;
            if (!m_tables455.storeNpcAt(row, view)) continue;
            merchants.emplace_back();
            auto& merchant = merchants.back();
            merchant.dwIndex = view.index;
            merchant.dwDTCode = view.model;
            merchant.byRace = view.race;
            merchant.fYAngle = view.orientation;
            merchant.fScale455 = view.scale;
            merchant.byMerchantType = 255;
            copyText(merchant.pName, view.name);
            copyText(merchant.pDescription, view.description);
            unsigned button = 0;
            for (const auto action : view.actions) {
                if (!action || action > NMBT_CLASS_CHANGE) continue;
                merchant.pButtonFunction[button++] = static_cast<BYTE>(action);
                if (button == MAX_NPC_BUTTON_NUM) break;
            }
        }
        m_merchants455.swap(merchants);
        return localized ? TRUE : FALSE;
    }''')
    edit(b'CCharacterDataMgr::LoadCharacterData( void )',lambda _:b'''CCharacterDataMgr::LoadCharacterData( void ){
        auto& data=RF455_GameItems().data;
        const bool result=m_tables455.loadCharacterFiles(data);
        m_byMaxAnimusTypeNum=static_cast<BYTE>(data.characterTables()[6].count/81);

        // The 455 type-1 table is indexed by row order. Own these legacy
        // records for the lifetime of actors that retain a pointer to them.
        const auto& monsters=data.characterTables()[2];
        if (monsters.count && monsters.stride < 68) return FALSE;
        m_monsters455.resize(monsters.count);
        for (DWORD index=0; index<monsters.count; ++index) {
            auto& monster=m_monsters455[index];
            const auto* row=monsters.get(index).data;
            std::memcpy(&monster.m_dwMeshID,row+4,sizeof(monster.m_dwMeshID));
            std::memcpy(monster.m_pName,row+8,sizeof(monster.m_pName)-1);
            std::memcpy(&monster.m_fAttackRange,row+56,sizeof(monster.m_fAttackRange));
            monster.m_byMoveSpeed[0]=row[60];
            monster.m_byMoveSpeed[1]=row[61];
            monster.m_byWidth=row[62];
            std::memcpy(&monster.m_fScale,row+64,sizeof(monster.m_fScale));
            monster.m_dwEffectValue=ID_INVALID;
            monster.m_dwAttackEffectMaterial=ID_INVALID;
            monster.m_dwDefenceEffectMaterial=ID_INVALID;
        }
        return result?TRUE:FALSE;
    }''')
    edit(b'CCharacterDataMgr::GetMonster( DWORD pi_dwIndex )',lambda _:b'''CCharacterDataMgr::GetMonster( DWORD pi_dwIndex ){
        return GetMonsterByOrder(pi_dwIndex);
    }''')
    # File IO lives in the shared source owner. Serialized rows do not alias
    # the legacy C++ objects.
    raw+=b'''
RF455ItemDataSpan CCharacterDataMgr::GetClassData455(const char* code){return RF455_GameItems().data.classByCode(code);}
RF455ItemDataSpan CCharacterDataMgr::GetClassData455ByIndex(DWORD index){return RF455_GameItems().data.classByIndex(index);}
'''
    return raw,True
