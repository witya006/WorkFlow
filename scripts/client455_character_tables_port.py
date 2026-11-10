"""Load455character tables through the normal manager;legacy typed consumers open."""
def port_character_tables(raw,relative,section):
    if relative=='datatable/ccharacterdatamgr.h':
        raw=b'#include "client455_character_tables.h"\n'+raw
        anchor=b'\tDT_PlayerList \t\tm_listPlayer;'
        if raw.count(anchor)!=1:raise ValueError('Character data owner boundary changed')
        raw=raw.replace(anchor,b'\tRF455CharacterTables m_tables455;\n'+anchor)
        anchor=b'\tCCharacterDataMgr();'
        if raw.count(anchor)!=1:raise ValueError('Character data public boundary changed')
        raw=raw.replace(anchor,anchor+b'\n\tconst RF455CharacterTables& Tables455()const{return m_tables455;}\n\tRF455ItemDataSpan GetClassData455(const char*);\n\tRF455ItemDataSpan GetClassData455ByIndex(DWORD);')
        return raw,True
    if relative!='datatable/ccharacterdatamgr.cpp':return raw,False
    anchor=b'#include "CCharacterDataMgr.h"'
    if raw.count(anchor)!=1:raise ValueError('Character includes changed')
    raw=raw.replace(anchor,anchor+b'\n#include "client455_client_items.h"\n#include "client455_nation_paths.h"\n#include "client455_language.h"\n#include "network/cnetworkmgr.h"\n#include <string>')
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
        return result?TRUE:FALSE;
    }''')
    # File IO lives in the shared source owner;the manager never casts rows to
    # the old CPlayerClass/DT_CNMInfo/SF structures.
    raw+=b'''
RF455ItemDataSpan CCharacterDataMgr::GetClassData455(const char* code){return RF455_GameItems().data.classByCode(code);}
RF455ItemDataSpan CCharacterDataMgr::GetClassData455ByIndex(DWORD index){return RF455_GameItems().data.classByIndex(index);}
'''
    return raw,True
