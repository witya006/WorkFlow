"""Apply 455 health updates and zero-damage Force reactions to monsters."""

from client455_trade_ore_port import replace


def port_monster_health(raw, relative, native):
    if relative == 'character/npc/cmonster.h':
        raw = replace(raw, b'\tCMonsterData *\tm_pMonsterData;',
                      b'\tCMonsterData *\tm_pMonsterData;\n'
                      b'\tfloat m_displayedHealth455 = 1.0f;\n\tfloat m_targetHealth455 = -1.0f;')
        return replace(raw, b'\tCMonster();',
                       b'\tCMonster();\n\tfloat GetHPRate() override { return m_displayedHealth455; }\n'
                       b'\tvoid ReceiveHealth455(WORD tenThousandths);\n'
                       b'\tvoid ApplyFinalHealthImpact455();\n'
                       b'\tvoid ApplyHealthImpact455(DWORD currentDamage, DWORD originalDamage, BYTE frames);'), True
    if relative == 'character/npc/cmonster.cpp':
        anchor = b'\t\tcase CAI_DAMAGED_MISS\t\t: return MET_DAMAGE_MISS;'
        raw = replace(raw, anchor, anchor + b'\n\t\tcase CAI_DAMAGED_MISS455\t: return MET_DAMAGE_MISS;\n'
                      b'\t\tcase CAI_DAMAGED_SPECIAL_HIT455: return 13;')
        raw = replace(raw, b'\tSetScale( m_pMonsterData->m_fScale );',
                      b'\tif (m_targetHealth455 == -1.0f) m_displayedHealth455 = 1.0f;\n'
                      b'\tSetScale( m_pMonsterData->m_fScale );')
        raw = replace(raw, b'\t\tm_pCombatState->SetRemainHP( 0 );',
                      b'\t\tm_targetHealth455 = 0.0f;\n\t\tm_pCombatState->SetRemainHP( 0 );')
        raw = replace(raw, b'\tif( IsEqualActionCategory( CAI_DEATH ) )\n\t{',
                      b'\tif( IsEqualActionCategory( CAI_DEATH ) )\n\t{\n'
                      b'\t\tif (m_byDestroyType == mon_destroy_code_die) ApplyFinalHealthImpact455();')
        return raw + b'\n' + (native / 'client455_monster_health.inc').read_bytes(), True
    if relative == 'character/character/ccharacter_relationinfo2.h':
        raw = replace(raw, b'class CAttackerInfo :',
                      b'constexpr DWORD CAI_DAMAGED_MISS455 = 0x60000005;\n'
                      b'constexpr DWORD CAI_DAMAGED_SPECIAL_HIT455 = 0x60000006;\n\n'
                      b'class CAttackerInfo :')
        anchor = b'\t\t\tvoid\tProcessDamage_SetDamage( CAttackerInfo * pi_pAttackerInfo );'
        return replace(raw, anchor, anchor + b'\n\tvoid AdvanceImpact455(CAttackerInfo& attack);'), True
    if relative == 'character/character/ccharacter_relationinfo2.cpp':
        raw = replace(raw, b'''\t\t\t\tProcessDamage_SetDamage( l_pAttackerInfo );
\t\t\t\tProcessDamage_SetHP( l_pAttackerInfo );''',
                      b'''                const bool monster = m_pOwner->IsEqualCharType(CTI_MONSTER);
                if (l_pAttackerInfo->GetDamageType_AT() == CAT_NORMAL && l_pAttackerInfo->GetOriginalDamage455()) {
                    AdvanceImpact455(*l_pAttackerInfo);
                    if (!monster) ProcessDamage_SetHP(l_pAttackerInfo);
                } else {
                    ProcessDamage_SetDamage(l_pAttackerInfo);
                    if (monster && !l_pAttackerInfo->GetEffectFrameNum())
                        static_cast<CMonster*>(m_pOwner)->ApplyFinalHealthImpact455();
                    else
                        ProcessDamage_SetHP(l_pAttackerInfo);
                }''')
        return replace(raw, b'''                if (force->IsAttackable() && l_pAttackerInfo->GetTotalDamagePoint())
                    l_pAttackerInfo->AdvanceDamage455();''',
                       b'''                if (!force->IsAttackable()) continue;
                if (l_pAttackerInfo->GetTotalDamagePoint()) {
                    AdvanceImpact455(*l_pAttackerInfo);
                    m_pOwner->SetEffectInfo(CAI_DAMAGED_BY_FORCE);
                } else if (m_pOwner->IsEqualCharType(CTI_MONSTER)) {
                    m_pOwner->SetEffectInfo(l_pAttackerInfo->IsSpecialHit455()
                        ? CAI_DAMAGED_SPECIAL_HIT455 : CAI_DAMAGED_MISS455);
                }'''), True
    if relative == 'network/netmsgprocessor/item/cnetmsgprocessor_itemarrangement.h':
        anchor = b'\t\t\t\tbool\tAnalysisServerPacket( _MSG_HEADER * pMsgHeader, char* pi_pMsg );'
        return replace(raw, anchor, anchor + b'\n\tBOOL RequestMonsterTarget455(CCharacter& target);\n'
                       b'\tBOOL CancelMonsterTarget455();\nprivate:\n'
                       b'\tbool MonsterHealth455(BYTE opcode, const char* bytes, std::size_t size);\npublic:'), True
    if relative == 'network/netmsgprocessor/item/cnetmsgprocessor_itemarrangement.cpp':
        anchor = b'\t\tcase potionsocket_separation_result_zocl:'
        raw = replace(raw, anchor, b'\t\tcase 27:\n\t\tcase 29:\n'
                      b'\t\t\treturn pMsgHeader->m_wSize >= 4 &&\n'
                      b'\t\t\t       MonsterHealth455(pMsgHeader->m_byType[1], pi_pMsg, pMsgHeader->m_wSize - 4);\n\n'
                      + anchor)
        anchor = b'#include "CNetMsgProcessor_ItemArrangement.h"'
        return replace(raw, anchor, anchor + b'\n#include "../../../GameObject/Manager/CCharacterMgr.h"\n'
                       b'#include "client455_protocol_observation.h"\n#include <cstring>\n\n'
                       + (native / 'client455_monster_health_dispatch.inc').read_bytes()), True
    return raw, False
