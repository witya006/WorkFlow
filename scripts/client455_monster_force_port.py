"""Use the 455 monster Force result in the ordinary client dispatcher."""

from client455_trade_ore_port import replace


def port_monster_force(raw, relative, native):
    if relative == 'item/citemdata.h':
        position = raw.index(b'class CSFItem :')
        prefix, raw = raw[:position], raw[position:]
        raw = replace(raw, b'\tSF_DATA *\t\tm_pData;', b'\tDWORD m_forceRow455 = ID_INVALID;\n\tSF_DATA *\t\tm_pData;')
        raw = replace(raw, b'if( m_pData ) return m_pData->dwDTIndex; else return ID_INVALID;',
                      b'if( m_pData ) return m_pData->dwDTIndex; '
                      b'else return HasForceRow455() ? m_forceRow455 : ID_INVALID;')
        raw = replace(raw, b'virtual\tBOOL\t\t\tCreate( BYTE pi_bySFType, DWORD pi_dwDTIndex );',
                      b'virtual\tBOOL\t\t\tCreate( BYTE pi_bySFType, DWORD pi_dwDTIndex );\n'
                      b'\tBOOL CreateForce455(DWORD index, BYTE level);\n'
                      b'\tbool HasForceRow455() const { return m_bySFType == CAT_FORCE && m_forceRow455 != ID_INVALID; }')
        return prefix + raw, True
    if relative == 'item/citemdata.cpp':
        raw = replace(raw, b'CSFItem::Init( void )\n{', b'CSFItem::Init( void )\n{\n\tm_forceRow455 = ID_INVALID;')
        raw = replace(raw, b'CSFItem::SetData( SF_DATA * pi_pData )\n{',
                      b'CSFItem::SetData( SF_DATA * pi_pData )\n{\n\tm_forceRow455 = ID_INVALID;')
        raw = replace(raw, b'CSFItem::IsAttackable( void )\n{',
                      b'CSFItem::IsAttackable( void )\n{\n'
                      b'\tif (HasForceRow455())\n'
                      b'\t\treturn RF455_GameItems().skillForce.hasAttackEffect(CAT_FORCE, m_forceRow455);')
        return (b'#include "client455_client_items.h"\n' + raw + b'\n' +
                (native / 'client455_monster_force_result.inc').read_bytes()), True
    if relative == 'character/character/ccharacter_relationinfo2.h':
        raw = replace(raw, b'\tDWORD\t\t\tm_dwCurDamagePoint;',
                      b'\tDWORD m_forceOriginalDamage455;\n\tbool m_forceSpecialHit455;\n\tDWORD\t\t\tm_dwCurDamagePoint;')
        raw = replace(raw, b'\tCAttackerInfo();', b'\tCAttackerInfo();\n'
                      b'\tvoid SetForceDamage455(LONG damage);\n\tvoid AdvanceForceDamage455();\n'
                      b'\tbool IsForceSpecialHit455() const { return m_forceSpecialHit455; }')
        return raw, True
    if relative == 'character/character/ccharacter_relationinfo2.cpp':
        anchor = b'\t\t\tl_pAttackerInfo->SetProcessedDamage( TRUE );'
        raw = replace(raw, anchor, anchor + b'''
            auto* force = l_pAttackerInfo->GetSFItem();
            if (!force->IsEmpty() && force->HasForceRow455()) {
                if (force->IsAttackable() && l_pAttackerInfo->GetTotalDamagePoint())
                    l_pAttackerInfo->AdvanceForceDamage455();
                continue;
            }
''')
        return b'#include <cstdlib>\n' + raw + b'\n' + (native / 'client455_monster_force_damage.inc').read_bytes(), True
    if relative == 'character/npc/cbasenpc.cpp':
        raw = replace(raw, b'CBaseNpc::SetEffectInfo_Force( EffectInfo & po_stEffectInfo, DWORD pi_dwActionID )\n{',
                      b'CBaseNpc::SetEffectInfo_Force( EffectInfo & po_stEffectInfo, DWORD pi_dwActionID )\n{\n'
                      b'\t// Typed 455 Force effects have their own IDs.\n'
                      b'\tif (m_clSFItem.HasForceRow455()) return;')
        return raw, True
    if relative == 'network/netmsgprocessor/combat/cnetmsgprocessor_combat.h':
        return replace(raw, b'\t\t\t\tbool\tAnalysisServerPacket( _MSG_HEADER * pMsgHeader, char* pi_pMsg );',
                       b'\t\t\t\tbool\tAnalysisServerPacket( _MSG_HEADER * pMsgHeader, char* pi_pMsg );\n'
                       b'private:\n\tbool MonsterForceResult455(const char* bytes, std::size_t size);\npublic:'), True
    if relative == 'network/netmsgprocessor/combat/cnetmsgprocessor_combat.cpp':
        raw = replace(raw, b'\t\tcase attack_force_result_zocl\t:',
                      b'\t\tcase 9:\n\t\t\treturn pMsgHeader->m_wSize >= 4 &&\n'
                      b'\t\t\t       MonsterForceResult455(pi_pMsg, pMsgHeader->m_wSize - 4);\n\n'
                      b'\t\tcase attack_force_result_zocl\t:')
        anchor = b'#include "CNetMsgProcessor_Combat.h"'
        return replace(raw, anchor, anchor + b'\n#include "client455_monster_force_result.h"\n'
                       b'#include "client455_protocol_observation.h"\n\n' +
                       (native / 'client455_monster_force_dispatch.inc').read_bytes()), True
    return raw, False
