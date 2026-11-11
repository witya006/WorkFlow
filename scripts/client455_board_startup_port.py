"""Restore the measured MainGame Linker startup sequence, retaining other gaps."""

from client455_trade_ore_port import patch_method, replace


def port_board_startup(raw, relative, section, native):
    if relative == 'gameobject/board/common/clinkboard.h':
        anchor = b'\tCLinkBoard();'
        if raw.count(anchor) != 1:
            raise ValueError('Linker startup declaration boundary')
        return raw.replace(anchor, anchor + b'\r\n\tvoid InitializeMainGame455();'), True
    if relative == 'gameobject/board/common/clinkboard.cpp':
        return raw + b'\n' + (native / 'client455_linker_startup.inc').read_bytes(), True
    if relative == 'userinterface/gamewindow/guihotkeyboard.h':
        return replace(raw, b'SetBeltWindow( CGUIItemBeltWindow * pi_pPotionWin, CGUIForceBeltWindow * pi_pSFWin );',
                       b'SetLinkWindow455(CGUIForceBeltWindow* link);'), True
    if relative == 'userinterface/gamewindow/guihotkeyboard.cpp':
        raw = patch_method(raw, section, b'CGUIHotKeyBoard', b'SetBeltWindow', lambda _: b'''CGUIHotKeyBoard::SetLinkWindow455(CGUIForceBeltWindow* link)
{
    if (m_pSFWin && m_pSFWin != link) Remove(m_pSFWin);
    m_pSFWin = link;
    if (!link) return;
    const double scale = double(gScreen.GetSizeX()) / 1024.0;
    link->SetPos(static_cast<LONG>(GetPosX() + scale * 272.0),
                 static_cast<LONG>(GetPosY() + GetSizeY() - scale * 13.0 - link->GetSizeY()));
    Add(link);
    gScreen.Remove(link);
}''')
        raw = replace(raw, b'm_uiAvatarCtrlBoard.Show( IsShow() );',
                      b'm_uiAvatarCtrlBoard.Show( IsShow() );\n\tif (m_pSFWin) m_pSFWin->Show(IsShow());')
        return replace(raw, b'if( !g_pUiItemBeltWindow->ProcNumInputDlg(',
                       b'if( g_pUiItemBeltWindow && !g_pUiItemBeltWindow->ProcNumInputDlg('), True
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
                   b'm_uiFunctionKeyWindow.SetLinkWindow455(static_cast<CGUIForceBeltWindow*>(_GetLinkBoard()->GetWindow()));')
    body = replace(body, b'static_cast< CGUIItemBeltWindow * >( _GetBeltBoard()->GetWindow() );', b'nullptr;')
    raw = raw[:first] + body + raw[last:]
    raw = patch_method(raw, section, b'CGP_MainGame', b'Destroy_UI', lambda method: method.replace(
        b'{', b'{\n\tm_uiFunctionKeyWindow.SetLinkWindow455(nullptr);', 1))
    return replace(raw, b'_GetItemBeltWindow()->UseItem( wParam % VK_F1 );',
                   b'if (_GetItemBeltWindow()) _GetItemBeltWindow()->UseItem(wParam % VK_F1);'), True
