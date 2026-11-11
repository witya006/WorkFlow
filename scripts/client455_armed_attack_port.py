"""Connect the ordinary attack to the typed weapon and ammunition owners."""

import re

from client455_trade_ore_port import patch_method, replace


def port_armed_attack(raw, relative, section, native):
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
    auto* board = _GetEquipBoard();
    auto* wornWeapon = board->GetObject(0, UIPT_WEAPON);
    const RF455ConditionItem weapon(wornWeapon ? wornWeapon->GetItem455() : nullptr);
    if (!weapon.valid) return TRUE;
    const auto& items = RF455_GameItems();
    const auto classType = [&items](DWORD index) {
        const auto row = items.data.classByIndex(index);
        return row.data ? row.data[0] : BYTE(0);
    };
    if (!weapon.allowsAttackClass(classType(GetInitialClassIndex455())) &&
        !weapon.allowsAttackClass(classType(GetClassDTIndex(0)))) return FALSE;
    if (!weapon.requiresAmmunition()) return TRUE;

    constexpr DWORD SpecialWeaponID = 0x00a11107;
    constexpr DWORD SpecialProjectileIndex = 20;
    const bool specialWeapon = weapon.field<DWORD>(72) == SpecialWeaponID;
    for (BYTE socket = UIPT_BULLET_LEFT; socket <= UIPT_BULLET_RIGHT; ++socket) {
        auto* entry = board->GetObject(0, socket);
        auto* payload = entry ? entry->GetItem455() : nullptr;
        const RF455ConditionItem ammunition(payload);
        if (ammunition.kind() != IEPT_BULLET) continue;
        const bool specialProjectile =
            items.skillForce.projectileEffectIndex(ammunition.field<DWORD>(216)) == SpecialProjectileIndex;
        if (specialWeapon != specialProjectile) {
            if (specialWeapon && socket == UIPT_BULLET_RIGHT)
                _SetSystemMsg("%s", RF455_GetNormalLanguagePack()->get(0xc00));
            continue;
        }
        if (payload->header().flag21 || !weapon.matchesPrimaryAmmunition(ammunition)) continue;
        SetBulletDTIndex(ammunition.field<DWORD>(0));
        board->SetUsingBulletSocketNo(socket);
        RF455_ObserveProtocol("combat-ammunition", socket, ammunition.field<DWORD>(0), payload->header().serial);
        return TRUE;
    }
    _SetSystemMsg("%s", RF455_GetNormalLanguagePack()->get(0x97));
    return FALSE;
}
'''

        edit(owner, b'CheckCorrespondenceOfWeaponWithBullet_WhenDismount', bullet_condition)
        return (b'#include "client455_protocol_observation.h"\n#include "client455_client_items.h"\n'
                b'#include "client455_language.h"\n' + raw), True

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
            return item ? item->header().serial : ID_INVALID;
        }
    }
\tCBoardItem * pWeaponItem = GetItem( UIPT_WEAPON );'''))
        return raw, True

    if relative == 'network/netmsgprocessor/combat/cnetmsgprocessor_combat.h':
        anchor = b'\tbool MonsterForceResult455(const char* bytes, std::size_t size);'
        return replace(raw, anchor, anchor +
                       b'\n\tbool NormalAttackResult455(const char* bytes, std::size_t size);'
                       b'\n\tbool AmmunitionRemaining455(const char* bytes, std::size_t size);'), True

    if relative == 'character/character/ccharacter_relationinfo2.cpp':
        edit(b'CCombatState', b'ProcessDamage', lambda body: replace(
            body, b'ProcessDamage_SetDamageEffect( l_pAttackerInfo );',
            b'''ProcessDamage_SetDamageEffect( l_pAttackerInfo );
                if (l_pAttackerInfo->GetDamageType_AT() == CAT_NORMAL &&
                    l_pAttackerInfo->GetEnemyCharTypeID() == CTI_AVATAR)
                    RF455_RecordCombatImpact(m_pOwner->GetIndex(), l_pAttackerInfo->GetCurDamagePoint(),
                                             m_pOwner->GetHPRate());'''))
        edit(b'CCombatState', b'ProcessDamage', lambda body: replace(
            body, b'm_pOwner->SetEffectInfo( CAI_DAMAGED_MISS );',
            b'''if (l_pAttackerInfo->GetDamageType_AT() == CAT_NORMAL)
                    m_pOwner->SetEffectInfo(l_pAttackerInfo->IsSpecialHit455()
                        ? CAI_DAMAGED_SPECIAL_HIT455 : CAI_DAMAGED_MISS455);
                else
                    m_pOwner->SetEffectInfo(CAI_DAMAGED_MISS);'''))
        return b'#include "client455_protocol_observation.h"\n' + raw, True

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
        anchor = b'\t\tcase attack_gen_result_zocl\t:'
        raw = replace(raw, anchor, b'''        case 6:
            _GetGGI()->SetRequestProcessState(FALSE);
            return true;
        case 7:
            return pMsgHeader->m_wSize >= 4 &&
                   NormalAttackResult455(pi_pMsg, pMsgHeader->m_wSize - 4);
        case 21:
            return pMsgHeader->m_wSize >= 4 &&
                   AmmunitionRemaining455(pi_pMsg, pMsgHeader->m_wSize - 4);

''' + anchor)
        anchor = b'#include "client455_monster_force_result.h"'
        raw = replace(raw, anchor, anchor + b'\n#include "client455_normal_attack_result.h"'
                      b'\n#include "client455_equipment_conditions.h"')
        anchor = b'#include "client455_protocol_observation.h"'
        raw = replace(raw, anchor, anchor + b'\n\n' + (native / 'client455_normal_attack_dispatch.inc').read_bytes())
        return raw, True

    if relative == 'addcodebyjang/effectutil.h':
        anchor = b'BOOL EFUtil_GetCharTransformFromIndex(Vector3f *get_pos,CCharacter *c_char,CEquipItem *item,DWORD id);'
        return replace(raw, anchor, b'''class RF455PlayerEquipmentObject;
struct RF455EffectEquipment {
    RF455PlayerEquipmentObject* typed;
    CEquipItem* legacy;
    explicit operator bool() const { return typed || legacy; }
    DWORD meshID() const;
    DWORD material() const;
    BYTE dummy(DWORD index) const;
};
RF455EffectEquipment EFUtil_Equipment455(CCharacter* actor, BYTE part);
BOOL EFUtil_GetCharTransformFromIndex(Vector3f* position, CCharacter* actor,
                                    const RF455EffectEquipment& item, DWORD id);
''' + anchor), True

    if relative == 'addcodebyjang/effectutil.cpp':
        signature = b'BOOL EFUtil_GetCharTransformFromIndex(Vector3f *get_pos,CCharacter *c_char,CEquipItem *item,DWORD id)'
        start = raw.index(signature)
        end = raw.index(b'\nBOOL EFUtil_IsCollisionFarAttack', start)
        body = raw[start:end]
        body = replace(body, signature, b'static BOOL RF455_WeaponTransform(Vector3f *get_pos, CCharacter *c_char, int m)')
        body = replace(body, b'\n\tint m;\n', b'')
        at = body.index(b'\tif( !item )')
        stop = body.index(b'\n\tppp3.x=0;', at)
        body = body[:at] + b'''    if (m == 255 || m == 0)
        goto EFUtil_GetCharTransformFromIndexError;
''' + body[stop:]
        body = replace(body, b'\tBBOX bbox;', b'\tBBOX bbox{};')
        raw = raw[:start] + body + (native / 'client455_weapon_effect_owner.inc').read_bytes() + raw[end:]

        for part in (b'CEPT_WEAPON', b'CEPT_UPPER_PART'):
            marker = b'CEquipItem *pio_pItem = pl->GetEquipItem( ' + part + b' );'
            start = raw.index(marker)
            end = raw.index(b'\n\t}', start)
            raw = raw[:start] + b'return EFUtil_Equipment455(pl, ' + part + b').material();' + raw[end:]

        start = raw.index(b'static CEquipItem *GetEquipItem(CCharacter *ch)')
        end = raw.index(b'BOOL EFUTIL_GetPosType(', start)
        raw = raw[:start] + raw[end:]
        end = raw.index(b'\n}', start)
        body = raw[start:end]
        body = replace(body, b'\tCEquipItem *item;', b'\tRF455EffectEquipment item{};')
        body = body.replace(b'item = GetEquipItem(ch);', b'item = EFUtil_Equipment455(ch, CEPT_WEAPON);')
        body = re.sub(rb'(_DUMMY_(?:TRACE|FIRE)[12]\);)\n\t\tVector3fCopy\(temp,pos\);',
                      rb'\1\n\t\tif (item) Vector3fCopy(temp,pos);', body)
        raw = raw[:start] + body + raw[end:]
        return b'#include "client455_equipment_conditions.h"\n' + raw, True

    if relative == 'addcodebyjang/foreffect.cpp':
        for owner in (b'mSrc', b'mTar'):
            raw = replace(raw, b'CEquipItem *' + owner + b'Item;', b'RF455EffectEquipment ' + owner + b'Item;')
            raw = replace(raw, owner + b'Item = ((CPlayer*)' + owner + b')->GetEquipItem( CEPT_WEAPON );',
                          owner + b'Item = EFUtil_Equipment455(' + owner + b', CEPT_WEAPON);')
            raw = raw.replace(owner + b'Item->GetMeshID()', owner + b'Item.meshID()')
        raw = replace(raw, b'CEquipItem *item = mSrcItem;', b'const auto& item = mSrcItem;')
        raw = raw.replace(b'mSrcItem == NULL', b'!mSrcItem')
        raw = replace(raw, b'((CPlayer *)mSrc)->GetEquipItem( CEPT_WEAPON )->GetMeshID()', b'mSrcItem.meshID()')
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
