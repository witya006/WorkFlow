"""Install the 455 lobby menu in the ordinary login stage."""

import re

from client455_trade_ore_port import replace


def open_lobby_after_avatar_loading(raw):
    start = raw.rindex(b'#ifndef _DEVELOPER_', 0, raw.index(b'LOGODELAY = 3000;'))
    end = raw.index(b'#endif', start) + len(b'#endif')
    old_splash = raw[start:end]
    if old_splash.count(b'Draw2DTexture(') != 1 or b'PlayCamera(CAM_TOP_TO_LOGINA,m_Course);' not in old_splash:
        raise ValueError('Legacy login splash boundary changed')
    raw = raw[:start] + raw[end:].lstrip(b'\r\n')
    raw = replace(raw, b'BOOL\t\tm_LoadEquip\t= false;\n', b'')
    raw = replace(raw, b'\t\t\tm_LoadEquip\t\t\t= true;\n', b'')
    return replace(raw, b'''#ifdef _DEVELOPER_
\t\t\tPlayCamera(CAM_TOP_TO_LOGINA,m_Course);
\t\t\tg_LoginState\t=\tLGS_CHARACTERLOBBY;
#endif ''', b'''            if (g_LoginState == LGS_ENTER_WORLDSERVER ||
                g_LoginState == LGS_MOVEIN_WORLDSERVER ||
                g_LoginState == LGS_IDANDPASSWORD) {
                PlayCamera(CAM_TOP_TO_LOGINA, m_Course);
                g_LoginState = LGS_CHARACTERLOBBY;
                RF455_ObserveProtocol("lobby-avatars-ready", 0, 0, 0);
            }''')


def port_lobby_menu(raw, relative, native):
    if relative == 'mainapp.cpp':
        # Land unload releases effect resources. Do it before the engine and
        # function-local effect owners are destroyed, while they are still alive.
        raw = replace(raw, b'\tm_cCamera.Destroy();', b'\tm_cLand.Destroy();\n\tm_cCamera.Destroy();')
        return raw, True
    if relative != 'gameprogress/cgp_login.cpp':
        return raw, False

    raw = replace(raw, b'#include "../MainApp.h"', b'#include "../MainApp.h"\n' +
                  (native / 'client455_lobby_menu.inc').read_bytes())
    raw = open_lobby_after_avatar_loading(raw)
    raw = replace(raw, b'\tm_bIsLoadedData = TRUE;',
                  b'\tlobbyMenu455.Install(*_GetUIScreen(), _GetMainApp()->IsRequestLogout() != FALSE);\n'
                  b'\tm_bIsLoadedData = TRUE;')
    raw = replace(raw, b'\tm_AniCamera.ReleaseAniCamera();',
                  b'\tlobbyMenu455.Uninstall(*_GetUIScreen());\n\tm_AniCamera.ReleaseAniCamera();')
    legacy_logo_load = rb'if \( FAILED\(D3DXCreateTextureFromFile\( GetD3dDevice\(\),"\.\\\\system\\\\titlelogo\.tga", &g_LogoTexture \)\)\)\s*\{\s*int a= 0;\s*\}'
    raw, count = re.subn(legacy_logo_load, b'LoadLobbyLogo455(GetD3dDevice(), g_LogoTexture);', raw)
    if count != 1:
        raise ValueError('Lobby title texture load boundary changed')
    legacy_logo_draw = rb'if \(g_LoginState==LGS_IDANDPASSWORD\)\s*\{[^{}]*Draw2DTexture\(x,y,x \+ width ,height \+ y,0xfeffffff,g_LogoTexture\);\s*\}'
    raw, count = re.subn(legacy_logo_draw, b'if (lobbyMenu455.IsShow() || g_LoginState == LGS_IDANDPASSWORD)\n\t\t\tDrawLobbyLogo455(g_LogoTexture);', raw)
    if count != 1:
        raise ValueError('Lobby title texture draw boundary changed')
    raw = replace(raw, b'\tm_messages455.Draw();',
                  b'\tlobbyMenu455.DrawCredits();\n\tm_messages455.Draw();')
    raw = replace(raw, b'sprintf( l_pBuf, "Closed Beta v %.3f", _GetMainApp()->GetVersion() );',
                  b'strcpy( l_pBuf, "RF Online 4.55" );')

    raw = replace(raw, b'\tNetworkInput();', b'''    NetworkInput();
    switch (lobbyMenu455.TakeAction()) {
    case LobbyMenu455::Action::Start:
        lobbyMenu455.Start();
        if (!m_HaveCharacter[0] && !m_HaveCharacter[1] && !m_HaveCharacter[2]) {
            m_Course = A_COURSE;
            EventCreateCharacter();
        }
        RF455_ObserveProtocol("lobby-start", 0, 0, 0);
        return TRUE;
    case LobbyMenu455::Action::Credits:
        if (lobbyMenu455.OpenCredits()) {
            const DWORD camera = m_AniCamera.GetCameraIndex(m_RandomStart ? "c_ex01" : "c_ex02");
            if (camera != ID_INVALID) m_AniCamera.SetPrePlayCamera(camera, 0, ID_INVALID, 0);
            RF455_ObserveProtocol("lobby-credits-open", 0, 0, 0);
        } else {
            _GUIMessageBox(nullptr, "System/staff.txt", MSGBOXALPHA);
        }
        return TRUE;
    case LobbyMenu455::Action::Exit:
        RF455_ObserveProtocol("lobby-exit", 0, 0, 0);
        EventGameClose();
        return TRUE;
    case LobbyMenu455::Action::None:
        break;
    }''')

    raw = replace(raw, b'if (!m_CameraAni&&g_LoginState == LGS_CHARACTERLOBBY\t)',
                  b'if (g_LoginState == LGS_CHARACTERLOBBY)')
    raw = replace(raw, b'if( !m_uiSelectCharacter.IsShow() )\n\t\t{\n\t\t\tm_uiSelectCharacter.Open();',
                  b'''if (!lobbyMenu455.Started()) {
            if (!lobbyMenu455.IsShow() && !lobbyMenu455.ShowingCredits()) {
                lobbyMenu455.Layout();
                lobbyMenu455.Open();
                RF455_ObserveProtocol("lobby-menu-open", 0, 0, 0);
            }
        } else if( !m_CameraAni && !m_LoadDefaultStart && !m_uiSelectCharacter.IsShow() )
        {
            m_uiSelectCharacter.Open();''')
    raw = replace(raw, b'CGP_LogIn::MsgProc( HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam )\n{',
                  b'''CGP_LogIn::MsgProc( HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam )
{
    if (uMsg == WM_SIZE && lobbyMenu455.IsShow()) lobbyMenu455.Layout();
    if (uMsg == WM_KEYDOWN && !(lParam & (1L << 30))) {
        const bool credits = lobbyMenu455.ShowingCredits();
        if (lobbyMenu455.KeyDown(wParam)) {
            if (credits) PlayCamera(CAM_TOP_TO_LOGINA, m_Course);
            return 0xffffffff;
        }
    }''')
    return raw, True
