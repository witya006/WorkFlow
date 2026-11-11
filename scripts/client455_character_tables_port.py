"""Load 455 character tables and adapt the monster records to the normal owner."""

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
        anchor=b'\tDT_PlayerList \t\tm_listPlayer;'
        if raw.count(anchor)!=1:raise ValueError('Character data owner boundary changed')
        raw=raw.replace(anchor,b'\tRF455CharacterTables m_tables455;\n'+anchor)
        anchor=b'\tCCharacterDataMgr();'
        if raw.count(anchor)!=1:raise ValueError('Character data public boundary changed')
        raw=raw.replace(anchor,anchor+b'\n\tconst RF455CharacterTables& Tables455()const{return m_tables455;}\n\tRF455ItemDataSpan GetClassData455(const char*);\n\tRF455ItemDataSpan GetClassData455ByIndex(DWORD);')
        return raw,True
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
    edit(b'CCharacterDataMgr::LoadNpcData( void )',lambda _:b'''CCharacterDataMgr::LoadNpcData( void ){
        return m_tables455.loadStoreFiles(_GetNetworkMgr()->m_worldEntry455.npcShop)?TRUE:FALSE;
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
