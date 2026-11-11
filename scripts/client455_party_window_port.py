"""Use the 455 party panel and advance the ordinary base download request."""
from client455_trade_ore_port import patch_method, remove_methods, replace


PARTY = 'userinterface/gamewindow/group/guipartywindow'


def header(raw):
    raw = replace(raw, b'MAX_PARTY_MEMBER_NUM\t\t\t7', b'MAX_PARTY_MEMBER_NUM\t\t\t11')
    start = raw.index(b'\tCGUIObjectEx\tm_uiHPGauge;')
    end = raw.index(b'\tCGUIButton\t\tm_uiRemoveButton;', start)
    raw = raw[:start] + b'''    CGUIObjectEx m_uiGauge455[3], m_uiClassIcon455;
    CGUIObject m_uiRowSkin455;
    float m_rates455[3] = {};
    BYTE m_classIcon455 = 0xff;
    bool m_compact455 = false, m_localLeader455 = false, m_first455 = false;
    void SetGauge455(unsigned index, float rate);

''' + raw[end:]
    for name in (b'm_uiDamageSF', b'm_uiHelpSF', b'sfHelp'):
        raw = replace(raw, name + b'[5]', name + b'[8]')
    raw = replace(raw, b'} sfDamage[5]', b'} sfDamage[8]')
    begin = raw.index(b'\tint\t\t\t\tm_nGaugeSizeX;')
    end = raw.index(b'// < Member Function >', begin)
    raw = raw[:begin] + b'    CGUIObject m_uiEventCover;\n\n' + raw[end:]
    raw = replace(raw, b'\tvoid\t\tClearMemberInfo( void );',
                  b'\tvoid\t\tClearMemberInfo( void );\n'
                  b'    void SetClassIcon455(BYTE index);\n'
                  b'    void Layout455(bool compact, bool localLeader, bool first);')
    raw = replace(raw, b'char\tpCharName[20];', b'char\tpCharName[20] = {};\n\tBYTE byClassIcon455 = 0xff;')
    raw = replace(raw, b'\tCGUIObject\t\tm_uiTitleBoard;',
                  b'\tCGUIObject\t\tm_uiTitleBoard;\n'
                  b'    CGUIObject m_uiViewToggle455, m_uiDistribution455, m_uiLeaderMark455;\n'
                  b'    BYTE m_distribution455 = 0;\n'
                  b'    DWORD m_leader455 = 0xffffffff;\n'
                  b'    bool m_compact455 = false;\n'
                  b'    void Layout455(bool initial = false);')
    return replace(raw, b'\tvoid\t\tLock( BOOL pi_bLock );',
                   b'\tvoid\t\tLock( BOOL pi_bLock );\n    void SetDistribution455(BYTE mode);\n'
                   b'    void Show(BOOL show) override;')


def source(raw, section, native):
    row = b'CGUIPartyMemberInfo'
    raw = patch_method(raw, section, row, row,
                       lambda body: replace(body, b'\tm_bCreated = FALSE;', b''))
    names = (b'Init', b'SetSprite', b'ClearMemberInfo', b'SetLevel', b'SetHPGauge', b'SetFPGauge', b'SetSPGauge',
             b'AddDamageSF', b'AddHelpSF', b'RemoveDamageSF', b'RemoveHelpSF', b'RemoveAllSF')
    raw = remove_methods(raw, section, row, [(name, b'void') for name in names])
    window = b'CGUIPartyWindow'
    names = (b'Init', b'SetSprite', b'SetWindowType', b'RemoveMember', b'RemoveAllMember', b'Lock',
             b'EnableLockNLeaveButton', b'MouseEvent', b'SetTotalMemberNum')
    raw = remove_methods(raw, section, window, [(name, b'void') for name in names] + [(b'AddMember', b'BOOL')])
    signature = b'CGUIPartyWindow::SetLeader( DWORD'
    start, end = section(raw, signature, signature)
    declaration = raw.rfind(b'void', 0, start)
    if raw[declaration:start].strip() != b'void':
        raise ValueError('Party leader declaration changed')
    raw = raw[:declaration] + raw[end:]
    raw = patch_method(raw, section, window, b'SetMember', lambda body: body.replace(
        b'{', b'{\n    if (m_leader455 == pi_dwMemberID) { m_leader455 = NONE_MEMBER_ID; Layout455(); }', 1))
    raw = patch_method(raw, section, window, b'SetLeader', lambda body: body.replace(
        b'{', b'{\n    if (!pi_pMemberInfo) return;', 1))
    return raw + b'\n' + (native / 'client455_party_window.inc').read_bytes()


def port_party_window(raw, relative, section, native):
    if relative == PARTY + '.h':
        return header(raw), True
    if relative == PARTY + '.cpp':
        return source(raw, section, native), True
    if relative == 'gameobject/board/general/cpartyboard.h':
        return replace(raw, b'MAX_PLAYER_IN_PARTY\t( 8 )', b'MAX_PLAYER_IN_PARTY\t( 12 )'), True
    if relative == 'network/protocol/pt_zone_client.h':
        return replace(raw, b'#define base_download_request_clzo 5', b'#define base_download_request_clzo 3'), True
    return raw, False
