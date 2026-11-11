"""Integrate 455 player exchange and ore processing in the ordinary build."""
import re


TRADE = 'userinterface/gamewindow/player/guitradewindow'
ORE = 'userinterface/gamewindow/npc/guioreprocwindow'


def replace(raw, before, after):
    if raw.count(before) != 1:
        raise ValueError(f'Trade/ore source anchor changed: {before!r}')
    return raw.replace(before, after)


def remove_methods(raw, section, owner, methods):
    for name, return_type in methods:
        anchor = owner + b'::' + name + b'('
        start, end = section(raw, anchor, anchor)
        declaration = re.search(rb'\b' + return_type + rb'[ \t\r\n]*$', raw[:start])
        if declaration is None:
            raise ValueError(f'Trade/ore method declaration changed: {anchor!r}')
        raw = raw[:declaration.start()] + raw[end:]
    return raw


def patch_method(raw, section, owner, name, transform):
    anchor = owner + b'::' + name + b'('
    start, end = section(raw, anchor, anchor)
    return raw[:start] + transform(raw[start:end]) + raw[end:]


def trade_header(raw):
    for before, after in (
        (b'CGUIObjectAni\t\tm_uiAniTitleBar;', b'RF455GuiAnimatedImage m_uiAniTitleBar;'),
        (b'CGUIButton\t\t\tm_uiCloseButton;', b'CGUIButton m_uiCloseButton, m_uiHelpButton455;'),
        (b'BOOL\t\t\t\tm_bIsCreated;', b'BOOL m_avatarLocked455 = FALSE, m_avatarAccepted455 = FALSE;'),
        (b'DWORD\t\t\t\tm_dwAvatarDalant;', b'__int64 m_dwAvatarDalant = 0;'),
        (b'DWORD\t\t\t\tm_dwAvatarGold;', b'__int64 m_dwAvatarGold = 0;'),
        (b'm_bIsLock_Other;', b'm_bIsLock_Other = FALSE;'),
        (b'm_bIsAccept_Other;', b'm_bIsAccept_Other = FALSE;'),
        (b'DWORD\t\tGetAvatarDalant(', b'__int64 GetAvatarDalant('),
        (b'DWORD\t\tGetAvatarGold(', b'__int64 GetAvatarGold('),
    ):
        raw = replace(raw, before, after)
    for name in (b'AvatarDalant', b'AvatarGold', b'OtherDalant', b'OtherGold'):
        raw = replace(raw, b'Set' + name + b'( DWORD ', b'Set' + name + b'( __int64 ')
    return raw


def trade_source(raw, section, native):
    owner = b'CGUITradeWindow'
    names = (b'Init', b'SetSprite', b'SetLock_Avatar', b'SetLock_Other', b'SetAccept_Avatar', b'SetAccept_Other',
             b'SetAvatarDalant', b'SetAvatarGold', b'SetOtherDalant', b'SetOtherGold',
             b'SetEnableSocketNum_Avatar', b'SetEnableSocketNum_Other')
    raw = remove_methods(raw, section, owner, [(name, b'void') for name in names])
    raw = replace(raw, b'\tm_bIsCreated\t= FALSE;', b'')
    for side in (b'Avatar', b'Other'):
        item = b'm_ui' + side + b'Item[pi_bySocketIndex]'
        raw = patch_method(raw, section, owner, b'TakeInItem_' + side,
                           lambda body: replace(body, item + b'.SetItemID',
                                                item + b'.SetIconType455(0);\n\t' + item + b'.SetItemID'))
        for name, error in ((b'TakeInItem_', b'FALSE'), (b'TakeOutItem_', b'FALSE'), (b'GetItem_', b'NULL')):
            if side == b'Other' and name == b'GetItem_':
                continue
            raw = patch_method(raw, section, owner, name + side,
                               lambda body: body.replace(b'{', b'{\n\tif (pi_bySocketIndex >= MAX_TRADE_ITEM_NUM) return ' + error + b';', 1))
    raw = patch_method(raw, section, owner, b'MouseEvent', lambda body: replace(
        replace(replace(body, b'WM_BOARD_ADD_OBJECT, 0', b'WM_PLAYER_TRADE_CHECK_ADD_455, 0'),
                b'WM_BOARD_REMOVE_OBJECT, UI_MOUSE_MSG', b'WM_PLAYER_TRADE_REMOVE_455, UI_MOUSE_MSG'),
        b'WM_CLOSING_WINDOW, 0', b'WM_CLOSE_WINDOW, 1'))
    return raw + b'\n' + (native / 'client455_player_trade_window.inc').read_bytes()


def ore_header(raw):
    for before, after in (
        (b'CGUIObjectAni\t\tm_uiAniTitleBar;', b'RF455GuiAnimatedImage m_uiAniTitleBar;'),
        (b'BOOL\t\t\t\tm_bIsCreated;', b'CGUIText m_uiOreCurrency455, m_uiResultTitle455, m_uiResultHelp455;'),
        (b'SetProcPrice( DWORD ', b'SetProcPrice( __int64 '),
        (b'\tBOOL\t\tDraw( void );', b''),
    ):
        raw = replace(raw, before, after)
    return raw


def ore_source(raw, section, native):
    owner = b'CGUIOreProcWindow'
    raw = remove_methods(raw, section, owner, [(name, b'void') for name in
                         (b'Init', b'SetSprite', b'EnableDisposal', b'SetProcPrice')] + [(b'Draw', b'BOOL')])
    raw = replace(raw, b'\tm_bIsCreated\t\t\t= FALSE;', b'')
    raw = replace(raw, b'\tm_uiInputOreItem.SetItemID', b'\tm_uiInputOreItem.SetIconType455(0);\n\tm_uiInputOreItem.SetItemID')
    raw = replace(raw, b'\tm_uiOutputOreItem[pi_bySocketIndex].SetItemID',
                  b'\tif (pi_bySocketIndex >= MAX_RESULT_ORE_ITEM) return FALSE;\n'
                  b'\tm_uiOutputOreItem[pi_bySocketIndex].SetIconType455(0);\n'
                  b'\tm_uiOutputOreItem[pi_bySocketIndex].SetItemID')
    return raw + b'\n' + (native / 'client455_ore_window.inc').read_bytes()


def port_trade_ore(raw, relative, section, native):
    if relative == TRADE + '.h':
        return trade_header(raw), True
    if relative == TRADE + '.cpp':
        return trade_source(raw, section, native), True
    if relative == ORE + '.h':
        return ore_header(raw), True
    if relative == ORE + '.cpp':
        return ore_source(raw, section, native), True
    if relative == 'define.h':
        # The old IDs overlap the target trade/ore IDs. Move the adjacent owners
        # together using the target Create_UI and Create_Board registrations.
        registrations = (
            (b'FUNC_KEY_WINDOW', 9, 8), (b'CHAR_INFO_WINDOW', 10, 9),
            (b'SELECT_ATTACK_PART_WINDOW', 11, 10), (b'MINING_WINDOW', 12, 11),
            (b'ORE_PROC_WINDOW', 13, 12), (b'EXCHANGE_WINDOW', 14, 13),
            (b'NPC_INTRODUCE_WINDOW', 15, 14), (b'ITEM_WORKING_WINDOW', 16, 15),
            (b'ITEM_UPGRADE_WINDOW', 17, 16), (b'TARGET_INFO_BAR', 18, 17),
            (b'TARGET_INFO_WINDOW', 19, 18), (b'PARTY_WINDOW', 20, 19),
            (b'PLAYER_POPUP_MENU', 21, 20), (b'MOVE_MAP_WINDOW', 22, 21),
            (b'APPLIED_SF_WINDOW', 23, 22), (b'TRADE_WINDOW', 24, 23),
        )
        for name, old, new in registrations:
            pattern = rb'(#define[ \t]+UII_' + name + rb'[ \t]+)' + str(old).encode() + rb'\b'
            raw, count = re.subn(pattern, lambda match: match[1] + str(new).encode(), raw)
            if count != 1:
                raise ValueError(f'Trade/ore window ID changed: {name!r}')
        return raw, True
    if relative == 'definemessage.h':
        at = raw.index(b'#define\tWM_PLAYER_TRADE_BOARD_LOCK')
        return (raw[:at] + b'#define WM_PLAYER_TRADE_CHECK_ADD_455 (WM_USER + 0x0103)\n'
                b'#define WM_PLAYER_TRADE_REMOVE_455 (WM_USER + 0x0104)\n' + raw[at:]), True
    if relative == 'gameobject/board/shopboard/cplayertradeboard.cpp':
        raw = replace(raw, b'case WM_BOARD_ADD_OBJECT', b'case WM_PLAYER_TRADE_CHECK_ADD_455')
        raw = replace(raw, b'case WM_BOARD_REMOVE_OBJECT', b'case WM_PLAYER_TRADE_REMOVE_455')
        raw = replace(raw, b'case WM_CLOSING_WINDOW',
                      b'case WM_CLOSE_WINDOW:\n\t\t\tif (lParam != 1) return 1;\n\t\t\t// fall through\n\t\tcase WM_CLOSING_WINDOW')
        return raw, True
    if relative == 'gameobject/board/common/cboardmanager.cpp':
        anchor = b'case WM_CLOSE_WINDOW\t\t\t:\t'
        return replace(raw, anchor, anchor + b'\n\t\t\tif (wParam == UII_TRADE_WINDOW && lParam == 1)\n'
                       b'\t\t\t\treturn m_listBoard[IBT_PLAYER_TRADE]->MsgProc(hWnd, uMsg, wParam, lParam);'), True
    return raw, False
