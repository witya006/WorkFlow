"""Migrate the target windows without changing the legacy source snapshot."""
from client455_trade_ore_port import patch_method, remove_methods, replace


VIEW = 'userinterface/gamewindow/guiselectedcharwin'
MENU = 'userinterface/gamewindow/guiselectedcharmenu'


def port_target_windows(raw, relative, section, native):
    if relative == VIEW + '.h':
        gauge = b'\tCGUIObjectEx\tm_uiHPGauge;'
        if raw.count(gauge) != 2:
            raise ValueError('Selected target HP declarations changed')
        raw = raw.replace(gauge, b'\tCGUIObjectEx\tm_uiHPGauge, m_uiHPBackdrop455;\n    float m_hpRate455 = 0.0f;', 1)
        raw = replace(raw, b'm_bIsAttackState;', b'm_bIsAttackState = FALSE;')
        raw = replace(raw, b'\tWORD\t\t\tm_wGaugeXLen;\n', b'')
        start = raw.index(b'\tBYTE\t\t\tm_byMaxGaugeLen;')
        end = raw.index(b'\tBOOL\t\t\tm_bIsCreated;', start)
        raw = raw[:start] + b'''    CGUIObjectEx m_uiHPGauge, m_uiHPBackdrop455;
    CGUIText m_uiLevel455;
    float m_hpRate455 = 0.0f;

''' + raw[end:]
        start = raw.index(b'\tvoid\tSetPower(')
        end = raw.index(b'\n', start)
        return raw[:start] + b'    void SetLevel455(unsigned level);' + raw[end:], True
    if relative == VIEW + '.cpp':
        raw = remove_methods(raw, section, b'CGUISelectedCharWin',
                             [(name, b'void') for name in (b'Init', b'SetSprite', b'SetAttackState',
                                                          b'SetSelectState', b'SetHPRate')])
        raw = remove_methods(raw, section, b'CGUISelectedMobInfoWin',
                             [(name, b'void') for name in (b'Init', b'SetSprite', b'SetMobName', b'SetHP', b'SetPower')])
        return raw + b'\n' + (native / 'client455_target_windows.inc').read_bytes(), True
    if relative == MENU + '.h':
        raw = replace(raw, b'\t\tFriend,', b'\t\tSanctionPlayer,\n\t\tFriend,')
        return replace(raw, b'MAX_MENU_NUM = PLAYER_MENU_NUM', b'MAX_MENU_NUM = 10'), True
    if relative == MENU + '.cpp':
        raw = remove_methods(raw, section, b'CGUISelectedCharMenu',
                             [(name, b'void') for name in (b'SetSprite', b'SetMenuType', b'SetPartyMenu')])
        raw = replace(raw, b'SetARGB( 0xC0262626 );', b'SetARGB( 0xD8262626 );')
        return raw + b'\n' + (native / 'client455_target_menu.inc').read_bytes(), True
    if relative == 'userinterface/gamewindow/dungeon/guidungeon.cpp':
        raw = remove_methods(raw, section, b'CGUIKillingCounter', [(b'SetSprite', b'void')])
        return raw + b'\n' + (native / 'client455_dungeon_counter.inc').read_bytes(), True
    if relative == 'gameobject/manager/ctargetmgr.cpp':
        owner = b'CTargetMgr'
        raw = patch_method(raw, section, owner, b'SetTarget_SetEnemyNpcUI', lambda body: replace(
            body, b'm_uiTargetInfoWindow.SetPower( GetResultOfCombatPowerComparisonWithAvatar( pi_pTarget ) );',
            b'''unsigned level = 0;
    if (pi_pTarget->IsEqualCharType(CTI_MONSTER))
        level = static_cast<CMonster*>(pi_pTarget)->GetLevel();
    else if (pi_pTarget->IsEqualCharType(CTI_ANIMUS))
        level = static_cast<CAnimus*>(pi_pTarget)->GetLevel();
    else if (pi_pTarget->IsEqualCharType(CTI_GUARD_TOWER))
        level = static_cast<CGuardTower*>(pi_pTarget)->GetLevel();
    m_uiTargetInfoWindow.SetLevel455(level);'''))
        raw = patch_method(raw, section, owner, b'SetTarget_SetPlayerUI', lambda body: replace(
            body, b'm_uiTargetInfoWindow.SetPower( GetResultOfCombatPowerComparisonWithAvatar( pi_pTarget ) );',
            b'm_uiTargetInfoWindow.SetLevel455(pi_pTarget->GetLevel());'))
        raw = patch_method(raw, section, owner, b'SetTarget_SetMerchantUI', lambda body: replace(
            body, b'm_uiTargetInfoWindow.SetPower( 0xFF );', b'm_uiTargetInfoWindow.SetLevel455(0);'))
        return raw, True
    return raw, False
