"""Apply the 455 critical-impact action, effect ordering and monster flash."""

from client455_trade_ore_port import replace


def port_monster_critical(raw, relative):
    if relative == 'character/character/ccharacter_relationinfo2.cpp':
        raw = replace(raw, b'                    m_pOwner->SetEffectInfo(CAI_DAMAGED_BY_FORCE);',
                      b'                    ProcessDamage_SetDamageEffect(l_pAttackerInfo);')
        start = raw.index(b'CCombatState::ProcessDamage_SetDamageEffect(')
        end = raw.index(b'\n}', start)
        body = replace(raw[start:end], b'\tif( pi_pAttackerInfo->GetDamageType_CT() )',
                       b'\tconst bool force455 = pi_pAttackerInfo->GetSFItem()->HasForceRow455();\n'
                       b'\tif (pi_pAttackerInfo->GetDamageType_CT() && (!force455 || !m_pOwner->IsDeath()))')
        return raw[:start] + body + raw[end:], True
    if relative == 'character/npc/cbasenpc.cpp':
        start = raw.index(b'CBaseNpc::SetAction( DWORD')
        end = raw.index(b'\n}', start)
        anchor = b'\tif( SetAction_IsDuplicateAction( pi_dwActionID, pi_bCheckActionDuplication ) )\n\t\treturn;'
        body = replace(raw[start:end], anchor, anchor + b'\n\n\tm_byPrevCombatMode = m_byCombatMode;')
        raw = raw[:start] + body + raw[end:]
        start = raw.index(b'CBaseNpc::SetAction_IsDuplicateAction(')
        end = raw.index(b'\n}', start)
        anchor = b'\t\t( m_dwActionID == pi_dwActionID )'
        body = replace(raw[start:end], anchor, b'\t\t( m_byPrevCombatMode == m_byCombatMode ) &&\n' + anchor)
        return raw[:start] + body + raw[end:], True
    if relative == 'addcodebyjang/foreffect.cpp':
        anchor = b'\t\t\tif( code1 == MET_DAMAGE_CRITICAL )\n\t\t\t\tMonsterCritical();'
        return replace(raw, anchor, b'''            if (code1 == MET_DAMAGE_CRITICAL) {
                if (CanShowCombatResult()) MonsterCritical();
            }'''), True
    if relative == 'addcodebyjang/monsterspecialeffect.cpp':
        start = raw.index(b'void CMonsterSpecialEffectDamageAction(')
        end = raw.index(b'\n}', start)
        body = raw[start:end]
        body = replace(body, b'\tBBOX bbox;', b'\tBBOX bbox{};')
        body = replace(body, b'\tEFUtil_GetDummyPos( pos, ch,_DUMMY_DAMAGE2);\n\tch->GetBoundBox(bbox);',
                       b'\tEFUTIL_GetPosType(pos, ch, _POS_TYPE_DAMAGE2);')
        body = replace(body, b'\tfloat radious = (bbox.pMax[1]-bbox.pMin[1])*2.0f;\n\n\tch->Set2ndLightRadius(radious);',
                       b'\tconst float radius = ch->GetBoundBox(bbox)\n'
                       b'\t    ? (bbox.pMax[1] - bbox.pMin[1]) * 0.3f : 0.0f;\n\tch->Set2ndLightRadius(radius);')
        return raw[:start] + body + raw[end:], True
    return raw, False
