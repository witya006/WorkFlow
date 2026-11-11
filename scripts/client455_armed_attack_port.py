"""Connect the ordinary attack to the typed weapon and ammunition owners."""

import re

from client455_trade_ore_port import patch_method, replace


def port_armed_attack(raw, relative, section):
    def edit(owner, method, transform):
        nonlocal raw
        raw = patch_method(raw, section, owner, method, transform)

    if relative == 'character/avatar/cavatar_combat.cpp':
        def weapon_condition(body):
            body = replace(body, b'CNormalItem * pWeapon = GetNormalItem( IEPT_WEAPON );',
                           b'const RF455ConditionItem weapon(GetNormalItem455(IEPT_WEAPON));')
            body = body.replace(b'if( pWeapon )', b'if (weapon.valid)')
            return body.replace(b'pWeapon->GetWeaponCategoryID()', b'weapon.weaponCategory()')

        owner = b'CAvatar'
        def can_attack(body):
            first = body.index(b'\tCNormalItem * pWeapon')
            last = body.index(b'\n\tif( !CheckCorrespondenceOfWeaponWithBullet()', first)
            return body[:first] + b'''    if (!IsEqualUnitMountState(UMS_MOUNT)) {
        const RF455ConditionItem weapon(GetNormalItem455(IEPT_WEAPON));
        RF455_ObserveProtocol("combat-weapon", weapon.kind(), weapon.weaponCategory(), weapon.requiresAmmunition());
        if (weapon.weaponCategory() == IWCT_MINE) return ARC_FAIL_STOP;
    }
''' + body[last:]

        edit(owner, b'CheckAvatarConditionForAttack', can_attack)
        def observe_attack(body):
            for method, event in [(b'CheckAvatarConditionForAttack()', b'combat-avatar-check'),
                                  (b'CheckDistanceAndDelayForAttack( pi_pTarget )', b'combat-range-check')]:
                anchor = b'l_nResult = ' + method + b';'
                body = replace(body, anchor, anchor + b'\n    RF455_ObserveProtocol("' + event +
                               b'", l_nResult, GetCombatMode(), 0);')
            return body

        edit(owner, b'NormalAttack', observe_attack)
        edit(owner, b'Attack', lambda body: replace(
            body, b'\tif( _GetGGI()->IsRequestProcess() || !IsEnable( ROSF_MOVABLE ) )',
            b'''    RF455_ObserveProtocol("combat-input", _GetGGI()->IsRequestProcess(), IsEnable(ROSF_MOVABLE), GetCombatMode());
\tif( _GetGGI()->IsRequestProcess() || !IsEnable( ROSF_MOVABLE ) )'''))
        edit(owner, b'GetAttackRange', weapon_condition)
        edit(owner, b'GetAttackDelay', lambda body: replace(
            body, b'CNormalItem * pWeapon\t= GetNormalItem( IEPT_WEAPON );\n\t\t\tif( pWeapon )\n\t\t\t\tdwAttackDelay += pWeapon->GetAttackDelay();',
            b'const RF455ConditionItem weapon(GetNormalItem455(IEPT_WEAPON));\n'
            b'\t\t\tif (weapon.kind() == IEPT_WEAPON) dwAttackDelay += weapon.delay();'))

        def combined_delay(body):
            body = replace(body, b'\tCNormalItem *\tpWeapon\t\t\t= GetNormalItem( IEPT_WEAPON );\n', b'')
            body = replace(body, b'\t\t\tcase CAT_NORMAL :', b'''            case CAT_NORMAL: {
                const RF455ConditionItem weapon(GetNormalItem455(IEPT_WEAPON));''')
            body = replace(body, b'if( pWeapon )', b'if (weapon.valid)')
            body = replace(body, b'pWeapon->GetWeaponCategoryID()', b'weapon.weaponCategory()')
            return replace(body, b'\t\t\t\tbreak;\n\n\t\t\tcase CAT_SKILL',
                           b'\t\t\t\tbreak;\n            }\n\n\t\t\tcase CAT_SKILL')

        edit(owner, b'CalculateAttackDelayWithAllEffect', combined_delay)

        def bullet_condition(body):
            at = body.index(b'{') + 1
            return body[:at] + b'''
    const RF455ConditionItem weapon(GetNormalItem455(IEPT_WEAPON));
    if (!weapon.requiresAmmunition()) return TRUE;
    auto* board = _GetEquipBoard();
    for (BYTE socket = UIPT_BULLET_LEFT; socket <= UIPT_BULLET_RIGHT; ++socket) {
        auto* entry = board->GetObject(0, socket);
        const RF455ConditionItem ammunition(entry ? entry->GetItem455() : nullptr);
        if (ammunition.kind() != IEPT_BULLET ||
            ammunition.field<BYTE>(232) != weapon.field<BYTE>(268)) continue;
        SetBulletDTIndex(ammunition.field<DWORD>(0));
        board->SetUsingBulletSocketNo(socket);
        return TRUE;
    }
''' + body[body.index(b'\t\t_SetSystemMsg(', at):body.index(b'\n\t}', body.index(b'\t\t_SetSystemMsg(', at))].replace(
                b'\t\t', b'    ') + b'\n}\n'

        edit(owner, b'CheckCorrespondenceOfWeaponWithBullet_WhenDismount', bullet_condition)
        return b'#include "client455_protocol_observation.h"\n' + raw, True

    if relative == 'character/player/cbaseplayer.cpp':
        def attack_range(body):
            first = body.index(b'\t\tif( !m_pData )')
            last = body.index(b'\n\t}', first)
            return body[:first] + b'''        if (!m_pData) return fAttackRange;
        fAttackRange += m_pData->m_fWidth / 2.0f;
        const RF455ConditionItem device(GetNormalItem455(27));
        const RF455ConditionItem weapon(GetNormalItem455(IEPT_WEAPON));
        fAttackRange += device.attackRange();
        fAttackRange += weapon.valid ? weapon.attackRange() : m_pData->m_fAttackRange;''' + body[last:]

        edit(b'CPlayerProc', b'GetAttackRange', attack_range)
        edit(b'CPlayerProc', b'SetEffectInfo_Combat', lambda body: replace(
            body, b'GetItemEffectID( GetNormalItem( IEPT_WEAPON ), IET_ATTACK_NORMAL )',
            b'''ID_INVALID;
        if (auto* weapon = GetEquipItem455(IEPT_WEAPON))
            po_stEffectInfo.dwID = (weapon->GetPlan455().meshID & 0xffffff00u) |
                                   (IET_ATTACK_NORMAL << 4) | weapon->EffectGrade455()'''))
        return raw, True

    if relative == 'character/player/cplayer.cpp':
        edit(b'CPlayer', b'GetAttackDistanceType', lambda body: replace(
            body, b'CEquipItem * pEquipItem = GetEquipItem( IEPT_WEAPON );\n\tif( pEquipItem )\n\t\treturn pEquipItem->GetAttackDistanceType();',
            b'''const RF455ConditionItem weapon(GetNormalItem455(IEPT_WEAPON));
    if (weapon.kind() == IEPT_WEAPON)
        return weapon.requiresAmmunition() || weapon.weaponCategory() == IWCT_THROW ? ADT_FAR : ADT_NEAR;'''))
        return raw, True

    if relative == 'gameobject/board/itemboard/cequipboard.cpp':
        edit(b'CEquipBoard', b'GetUsingBulletIndex', lambda body: replace(
            body, b'\tCBoardItem * pWeaponItem = GetItem( UIPT_WEAPON );',
            b'''    if (auto* wornWeapon = GetObject(0, UIPT_WEAPON)) {
        if (auto* payload = wornWeapon->GetItem455()) {
            const RF455ConditionItem weapon(payload);
            if (!weapon.requiresAmmunition() || m_byUsingBulletSocketNo < UIPT_BULLET_LEFT ||
                m_byUsingBulletSocketNo > UIPT_BULLET_RIGHT) return ID_INVALID;
            auto* entry = GetObject(0, m_byUsingBulletSocketNo);
            auto* item = entry ? entry->GetItem455() : nullptr;
            const RF455ConditionItem ammunition(item);
            return ammunition.kind() == IEPT_BULLET &&
                   ammunition.field<BYTE>(232) == weapon.field<BYTE>(268)
                   ? item->header().serial : ID_INVALID;
        }
    }
\tCBoardItem * pWeaponItem = GetItem( UIPT_WEAPON );'''))
        return raw, True

    if relative == 'network/netmsgprocessor/combat/cnetmsgprocessor_combat.cpp':
        def request(body):
            at = body.index(b'{') + 1
            return body[:at] + b'''
    if (!pi_pVictim) return FALSE;

    // 455 5/1 uses two ammunition words. The second is absent in the
    // ordinary non-alternate ammunition state.
    BYTE payload[8]{};
    payload[0] = pi_pVictim->GetCharTypeID();
    const WORD zoneIndex = static_cast<WORD>(pi_pVictim->GetServerIndex());
    std::memcpy(payload + 1, &zoneIndex, sizeof zoneIndex);
    if (pi_pVictim->IsEqualCharType(CTI_PLAYER)) {
        static const int thresholds[] = {23, 45, 63, 80, 100};
        const int roll = std::rand() % 100;
        while (roll > thresholds[payload[3]]) ++payload[3];
    }
    const WORD ammunition = static_cast<WORD>(_GetEquipBoard()->GetUsingBulletIndex());
    std::memcpy(payload + 4, &ammunition, sizeof ammunition);
    payload[6] = payload[7] = 0xff;

    SetAvatarAttackState(CAT_NORMAL, pi_pVictim);
    _GetGGI()->SetRequestProcessState(TRUE);
    return SendNetMessage(1, payload, sizeof payload);
}
'''

        edit(b'CNetMsgProcessor_Combat', b'AttackGenRequest_clzo', request)
        return raw, True

    if relative == 'addcodebyjang/playerspecialeffect.cpp':
        raw = raw.replace(b'CEquipItem *item = pl->GetEquipItem( IEPT_WEAPON );',
                          b'auto* item = pl->GetEquipItem455(IEPT_WEAPON);')
        raw = raw.replace(b'item->GetMeshID()', b'item->GetPlan455().meshID')
        raw = raw.replace(b'item->GetMesh()', b'item->GetMesh455()')
        raw = raw.replace(b'item->GetDummyIndex(', b'item->GetDummy455(')
        raw = replace(raw, b'if( pl->GetEquipItem( CEPT_WEAPON ) )',
                      b'if (auto* weapon = pl->GetEquipItem455(CEPT_WEAPON))')
        raw = re.sub(rb'\t+DWORD l_dwMeshIDEff = EFUtil_GetAttackMaterial\(pl\);\n', b'', raw)
        raw = replace(raw, b'pl->GetEquipItem( CEPT_WEAPON )->GetMeshID()', b'weapon->GetPlan455().meshID')
        return raw, True

    return raw, False
