"""Use the 455 monster Force result in the ordinary client dispatcher."""

from client455_trade_ore_port import replace


def port_monster_force(raw, relative, native):
    if relative == 'item/citemdata.h':
        position = raw.index(b'class CSFItem :')
        prefix, raw = raw[:position], raw[position:]
        prefix += b'BYTE RF455WeaponHoldType(DWORD meshID);\n'
        raw = replace(raw, b'\tSF_DATA *\t\tm_pData;', b'\tDWORD m_typedSFRow455 = ID_INVALID;\n\tBOOL CreateTyped455(BYTE type, DWORD index, BYTE level);\n\tSF_DATA *\t\tm_pData;')
        raw = replace(raw, b'if( m_pData ) return m_pData->dwDTIndex; else return ID_INVALID;',
                      b'if( m_pData ) return m_pData->dwDTIndex; '
                      b'else return m_typedSFRow455;')
        raw = replace(raw, b'inline\tDWORD\t\t\tGetDTCode( void )\t\t\t\t\t'
                      b'{ if( m_pData ) return m_pData->dwDTCode; else return ID_INVALID; }',
                      b'DWORD\t\t\t\tGetDTCode( void );')
        raw = replace(raw, b'inline\tBYTE\t\t\tGetRangeTypeForEffect( void )\t\t'
                      b'{ if( m_pData ) return m_pData->byRangeType_For_Effect; else return 0xFF; }',
                      b'BYTE\t\t\t\tGetRangeTypeForEffect( void );')
        raw = replace(raw, b'virtual\tBOOL\t\t\tCreate( BYTE pi_bySFType, DWORD pi_dwDTIndex );',
                      b'virtual\tBOOL\t\t\tCreate( BYTE pi_bySFType, DWORD pi_dwDTIndex );\n'
                      b'\tBOOL CreateForce455(DWORD index, BYTE level);\n'
                      b'\tBOOL CreateSkill455(DWORD index, BYTE level);\n'
                      b'\tbool HasForceRow455() const { return m_bySFType == CAT_FORCE && m_typedSFRow455 != ID_INVALID; }')
        return prefix + raw, True
    if relative == 'item/citemdata.cpp':
        hold_start = raw.index(b'BYTE\nCBaseItem::GetHoldType( void )')
        switch_start = raw.index(b'\t\tswitch( dwWeaponKind )\n', hold_start)
        switch_end = raw.index(b'\n\t\t}\n\t}\n\telse if', switch_start) + len(b'\n\t\t}')
        weapon_cases = raw[switch_start:switch_end].replace(b'dwWeaponKind', b'(meshID & 0x0000ff00) >> 8')
        weapon_cases = b'\n'.join(line[1:] if line.startswith(b'\t') else line for line in weapon_cases.split(b'\n'))
        raw = (raw[:hold_start] + b'BYTE RF455WeaponHoldType(DWORD meshID)\n{\n' + weapon_cases + b'\n}\n\n' +
               raw[hold_start:switch_start].split(b'\n\t\tDWORD dwWeaponKind')[0] +
               b'\n\t\treturn RF455WeaponHoldType(GetMeshID());' + raw[switch_end:])
        raw = replace(raw, b'CSFItem::Init( void )\n{', b'CSFItem::Init( void )\n{\n\tm_typedSFRow455 = ID_INVALID;')
        raw = replace(raw, b'CSFItem::SetData( SF_DATA * pi_pData )\n{',
                      b'CSFItem::SetData( SF_DATA * pi_pData )\n{\n\tm_typedSFRow455 = ID_INVALID;')
        raw = replace(raw, b'CSFItem::IsAttackable( void )\n{',
                      b'CSFItem::IsAttackable( void )\n{\n'
                      b'\tif (m_typedSFRow455 != ID_INVALID)\n'
                      b'\t\treturn RF455_GameItems().skillForce.hasAttackEffect(m_bySFType, m_typedSFRow455);')
        raw = replace(raw, b'CSFItem::GetRangeType( void )\n{', b'''CSFItem::GetRangeType( void )
{
    if (m_typedSFRow455 != ID_INVALID) {
        const auto row = RF455_GameItems().skillForce.get(m_bySFType, m_typedSFRow455);
        const unsigned effect = 144u + m_byLevel;
        return m_byLevel >= 1 && m_byLevel <= 7 && IsAttackable() && row.size > effect ? row.data[effect] : 0;
    }''')
        return (b'#include "client455_client_items.h"\n' + raw + b'\n' +
                (native / 'client455_monster_force_result.inc').read_bytes()), True
    if relative == 'character/player/cbaseplayer.cpp':
        raw = replace(raw,
                      b'CNormalItem *\tpWeapon\t\t= GetNormalItem( IEPT_WEAPON );\n\t\tif( pWeapon )\n\t\t\tbyHoldType = pWeapon->GetHoldType();',
                      b'const auto* weapon = GetEquipItem455(IEPT_WEAPON);\n\t\tif (weapon)\n'
                      b'\t\t\tbyHoldType = RF455WeaponHoldType(weapon->GetPlan455().meshID);')
        raw = replace(raw, b'\tDWORD dwAniTypeID;\n\n\tswitch( pi_dwActionID )',
                      b'\tDWORD dwAniTypeID = ID_INVALID;\n\n\tswitch( pi_dwActionID )')
        begin = raw.index(b'CPlayerProc::GetAnimationData_Skill(')
        raw = raw[:begin] + replace(raw[begin:],
                      b'CNormalItem * pWeapon = GetNormalItem( IEPT_WEAPON );',
                      b'auto* pWeapon = GetEquipItem455(IEPT_WEAPON);')
        begin = raw.index(b'CPlayerProc::GetAnimationData_Skill(')
        return raw[:begin] + replace(raw[begin:], b'pWeapon->GetMeshID() & 0x0000FF00',
                                     b'pWeapon->GetPlan455().meshID & 0x0000FF00'), True
    if relative == 'character/character/ccharacter_relationinfo2.h':
        raw = replace(raw, b'\tDWORD\t\t\tm_dwCurDamagePoint;',
                      b'\tDWORD m_originalDamage455;\n\tbool m_specialHit455;\n\tDWORD\t\t\tm_dwCurDamagePoint;')
        raw = replace(raw, b'\tCAttackerInfo();', b'\tCAttackerInfo();\n'
                      b'\tvoid SetDamage455(LONG damage);\n\tvoid AdvanceDamage455();\n'
                      b'\tDWORD GetOriginalDamage455() const { return m_originalDamage455; }\n'
                      b'\tbool IsSpecialHit455() const { return m_specialHit455; }')
        return raw, True
    if relative == 'character/character/ccharacter_relationinfo2.cpp':
        anchor = b'\t\t\tl_pAttackerInfo->SetProcessedDamage( TRUE );'
        raw = replace(raw, anchor, anchor + b'''
            auto* force = l_pAttackerInfo->GetSFItem();
            if (!force->IsEmpty() && force->HasForceRow455()) {
                if (force->IsAttackable() && l_pAttackerInfo->GetTotalDamagePoint())
                    l_pAttackerInfo->AdvanceDamage455();
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
