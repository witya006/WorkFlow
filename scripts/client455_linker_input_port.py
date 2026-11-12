"""Route normal 455 keyboard bindings to the current Linker window."""
import re

from client455_trade_ore_port import patch_method, replace


def port_linker_input(raw, relative, section, native):
    if relative == 'gameprogress/cinputprocessmgr.h':
        anchor = b'\tBOOL\tm_bIsPressedKey;'
        raw = replace(raw, anchor, anchor + b'\r\n\tDWORD m_linkerKeyTimes455[10];')
        anchor = b'\tBOOL\tIsPressedKey( DWORD pi_dwKey );'
        return replace(raw, anchor, anchor + b'\r\n\tvoid ProcessLinkerKeys455(DWORD now, BOOL focused);'), True
    if relative == 'gameprogress/cinputprocessmgr.cpp':
        anchor = b'KM_GAME_PLAY_REALTIME_MOVIE, KM_GAME_CHANGE_REALTIME_WIDE_MODE, KM_GAME_CHANGE_REALTIME_CAMERA_MODE,'
        raw = replace(raw, anchor, anchor + b'\n\tKM_LINKER_SLOT_FIRST,')
        anchor = b'"PLAY_MOVIE", "MOVIE_WIDE_MODE", "MOVIE_CAMERA_MODE"'
        raw = replace(raw, anchor, anchor +
                      b',\n\t"SLOT_1", "SLOT_2", "SLOT_3", "SLOT_4", "SLOT_5",\n'
                      b'\t"SLOT_6", "SLOT_7", "SLOT_8", "SLOT_9", "SLOT_10"')
        for before, after in (
            (b'10 + 26 + 8;', b'10 + 26 + 8 + 12;'),
            (b'"PRINT"\n', b'"PRINT",\n\t\t"F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"\n'),
            (b'VK_PRINT\n', b'VK_PRINT,\n\t\tVK_F1, VK_F2, VK_F3, VK_F4, VK_F5, VK_F6, VK_F7, VK_F8, VK_F9, VK_F10, VK_F11, VK_F12\n'),
            (b'MAX_SECTION_NUM\t\t\t\t= 5;', b'MAX_SECTION_NUM\t\t\t\t= 6;'),
            (b'{ 10, 5, 7, 2, 13 }', b'{ 10, 5, 7, 2, 13, 10 }'),
            (b'{ "WINDOW", "COMBAT", "BEHAVIOR", "CHAT", "GAME" }', b'{ "WINDOW", "COMBAT", "BEHAVIOR", "CHAT", "GAME", "BELT" }'),
        ):
            raw = replace(raw, before, after)

        def process_keyboard(body):
            start = body.index(b'\tm_bShiftKeyDown\t\t=')
            stop = body.index(b'\n\n', start)
            modifiers = body[start:stop]
            body = body[:start] + body[stop + 2:]
            at = body.index(b'\tif( IsPressedMoveKey() )')
            return body[:at] + modifiers + b'''
    auto* chat = _GetChatWindow();
    auto* chatInput = _GetChatInputWindow();
    const BOOL focused = _GetMainGame()->IsChatMode() || g_nOpenedDlgBoxCount > 0 ||
        (chat && (chat->GetInputField()->IsFocused() || chat->GetWhisperInputField()->IsFocused())) ||
        (chatInput && chatInput->GetInputField() && chatInput->GetInputField()->IsFocused());
    ProcessLinkerKeys455(timeGetTime(), focused);
\n''' + body[at:]

        raw = patch_method(raw, section, b'CInputProcessMgr', b'InputProcess_Keyboard', process_keyboard)
        anchor = b'case WM_SYSKEYDOWN :\n\t\t\tm_bIsPressedKey = TRUE;'
        raw = replace(raw, anchor, anchor +
                      b'\n            if (wParam == VK_F10 && !(lParam & (1L << 29))) gScan[VK_F10] |= 1;')
        return raw + b'\n' + (native / 'client455_linker_input.inc').read_bytes(), True
    if relative == 'gameprogress/cgp_maingame.cpp':
        def use_input_manager(body):
            body, n = re.subn(rb'if\( wParam >= VK_F1 .*?else if\( wParam == VK_PROCESSKEY \)',
                              b'if( wParam == VK_PROCESSKEY )', body, count=1, flags=re.S)
            if n != 1:
                raise ValueError('Legacy F-key dispatch anchor changed')
            body, n = re.subn(rb'\t\t\t// F10[^\n]*\n\t\t\tif\([^\n]+0x44[^\n]+\n'
                              rb'\t\t\t\t_GetSFBeltWindow\(\)->UseItem\( 5 \);',
                              b'            m_pInputProcessMgr->MsgProc(hWnd, uMsg, wParam, lParam);', body, count=1)
            if n != 1:
                raise ValueError('Legacy F10 dispatch anchor changed')
            return body

        raw = patch_method(raw, section, b'CGP_MainGame', b'MsgProc', use_input_manager)
        raw, n = re.subn(rb'\tg_pUiSFBeltWindow\t\t= static_cast< CGUIForceBeltWindow \* >[^\n]+\n', b'', raw)
        if n != 1:
            raise ValueError('Legacy Linker window cast anchor changed')
        return raw, True
    return raw, False
