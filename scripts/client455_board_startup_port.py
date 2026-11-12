"""Restore the measured MainGame Linker startup sequence, retaining other gaps."""

from client455_trade_ore_port import patch_method, remove_methods, replace


def port_board_startup(raw, relative, section, native):
    if relative == 'gameobject/board/common/clinkboard.h':
        anchor = b'\tCLinkBoard();'
        if raw.count(anchor) != 1:
            raise ValueError('Linker startup declaration boundary')
        return raw.replace(anchor, anchor + b'\r\n\tvoid InitializeMainGame455();'), True
    if relative == 'gameobject/board/common/clinkboard.cpp':
        return raw + b'\n' + (native / 'client455_linker_startup.inc').read_bytes(), True
    if relative == 'userinterface/gamewindow/guihotkeyboard.h':
        raw = replace(raw, b'class CGUIForceBeltWindow;', b'class CGUILinkWindow455;')
        raw = replace(raw, b'CGUIForceBeltWindow\t*\tm_pSFWin;', b'CGUILinkWindow455* m_pSFWin;')
        raw = replace(raw, b'CGUIObjectAni\t\t\tm_uiBoardAni;', b'float m_boardScale455 = 1.0f;')
        return replace(raw, b'SetBeltWindow( CGUIItemBeltWindow * pi_pPotionWin, CGUIForceBeltWindow * pi_pSFWin );',
                       b'SetLinkWindow455(CGUILinkWindow455* link);'), True
    if relative == 'userinterface/gamewindow/guihotkeyboard.cpp':
        raw = remove_methods(raw, section, b'CGUIHotKeyBoard',
                             [(b'Init', b'void'), (b'SetSprite', b'void'), (b'SetBeltWindow', b'void')])
        raw = replace(raw, b'm_uiAvatarCtrlBoard.Show( IsShow() );',
                      b'm_uiAvatarCtrlBoard.Show( IsShow() );\n\tif (m_pSFWin) m_pSFWin->Show(IsShow());')
        raw = replace(raw, b'if( !g_pUiItemBeltWindow->ProcNumInputDlg(',
                      b'if( g_pUiItemBeltWindow && !g_pUiItemBeltWindow->ProcNumInputDlg(')
        raw = patch_method(raw, section, b'CGUIHotKeyBoard', b'ChangeAttackMode', lambda method: replace(
            method, b'if( pi_eMode == Manual )', b'if( pi_eMode == Auto )'))
        raw = b'#include "client455_linker_window.h"\n#include <algorithm>\n#include <stdexcept>\n' + raw
        return raw + b'\n' + (native / 'client455_hotkey_hud.inc').read_bytes(), True
    if relative != 'gameprogress/cgp_maingame.cpp':
        return raw, False
    first, last = section(raw, b'CGP_MainGame::Create_Board(', b'CGP_MainGame::Create_Board(')
    body = raw[first:last]
    start = body.index(b'\t// init link board')
    end = body.index(b'\t// init unit tuning board', start)
    old = body[start:end]
    if old.count(b'_GetBeltBoard()') != 4 or old.count(b'_GetLinkBoard()') != 4:
        raise ValueError('Legacy MainGame Linker/Belt startup boundary')
    # 455 goes straight from Linker Open(1) to UnitTuning.
    body = body[:start] + (
        b'\t//455 RVA147832..1478CB: five ten-slot Linker banks, window3.\r\n'
        b'\t_GetLinkBoard()->InitializeMainGame455();\r\n\r\n'
    ) + body[end:]
    body = replace(body, b'm_uiFunctionKeyWindow.SetBeltWindow( (CGUIItemBeltWindow *)_GetBeltBoard()->GetWindow(), (CGUIForceBeltWindow *)_GetLinkBoard()->GetWindow() );',
                   b'm_uiFunctionKeyWindow.SetLinkWindow455(&_GetLinkBoard()->LinkerWindow455());')
    body = replace(body, b'static_cast< CGUIItemBeltWindow * >( _GetBeltBoard()->GetWindow() );', b'nullptr;')
    raw = raw[:first] + body + raw[last:]
    raw = patch_method(raw, section, b'CGP_MainGame', b'Destroy_UI', lambda method: method.replace(
        b'{', b'{\n\tm_uiFunctionKeyWindow.SetLinkWindow455(nullptr);', 1))
    return replace(raw, b'_GetItemBeltWindow()->UseItem( wParam % VK_F1 );',
                   b'if (_GetItemBeltWindow()) _GetItemBeltWindow()->UseItem(wParam % VK_F1);'), True
