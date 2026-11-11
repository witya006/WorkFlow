"""Connect the 455 monster's received and displayed health fractions."""

from client455_trade_ore_port import replace


def port_monster_health(raw, relative, native):
    if relative == 'character/npc/cmonster.h':
        raw = replace(raw, b'\tCMonsterData *\tm_pMonsterData;',
                      b'\tCMonsterData *\tm_pMonsterData;\n'
                      b'\tfloat m_displayedHealth455 = 1.0f;\n\tfloat m_targetHealth455 = -1.0f;')
        return replace(raw, b'\tCMonster();',
                       b'\tCMonster();\n\tfloat GetHPRate() override { return m_displayedHealth455; }\n'
                       b'\tvoid ReceiveHealth455(WORD tenThousandths);\n'
                       b'\tvoid ApplyForceHealthImpact455(DWORD currentDamage, DWORD originalDamage, BYTE frames);'), True
    if relative == 'character/npc/cmonster.cpp':
        raw = replace(raw, b'\tSetScale( m_pMonsterData->m_fScale );',
                      b'\tif (m_targetHealth455 == -1.0f) m_displayedHealth455 = 1.0f;\n'
                      b'\tSetScale( m_pMonsterData->m_fScale );')
        return raw + b'\n' + (native / 'client455_monster_health.inc').read_bytes(), True
    if relative == 'character/character/ccharacter_relationinfo2.h':
        return replace(raw, b'\tvoid AdvanceForceDamage455();',
                       b'\tvoid AdvanceForceDamage455();\n'
                       b'\tDWORD GetOriginalForceDamage455() const { return m_forceOriginalDamage455; }'), True
    if relative == 'character/character/ccharacter_relationinfo2.cpp':
        return replace(raw, b'''                if (force->IsAttackable() && l_pAttackerInfo->GetTotalDamagePoint())
                    l_pAttackerInfo->AdvanceForceDamage455();''',
                       b'''                if (force->IsAttackable() && l_pAttackerInfo->GetTotalDamagePoint()) {
                    const BYTE frames = l_pAttackerInfo->GetEffectFrameNum();
                    l_pAttackerInfo->AdvanceForceDamage455();
                    if (m_pOwner->IsEqualCharType(CTI_MONSTER))
                        static_cast<CMonster*>(m_pOwner)->ApplyForceHealthImpact455(
                            l_pAttackerInfo->GetCurDamagePoint(),
                            l_pAttackerInfo->GetOriginalForceDamage455(), frames);
                }'''), True
    if relative == 'network/netmsgprocessor/item/cnetmsgprocessor_itemarrangement.h':
        anchor = b'\t\t\t\tbool\tAnalysisServerPacket( _MSG_HEADER * pMsgHeader, char* pi_pMsg );'
        return replace(raw, anchor, anchor + b'\nprivate:\n'
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
