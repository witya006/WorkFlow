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
                if (lobbyMenu455.Started()) PlayCamera(CAM_TOP_TO_LOGINA, m_Course, true);
                g_LoginState = LGS_CHARACTERLOBBY;
                RF455_ObserveProtocol("lobby-avatars-ready", 0, 0, 0);
            }''')


def reveal_lobby_loading(raw):
    start = raw.index(b'\tm_uiLoadingWindow.Open();')
    stop = raw.index(b'\tGetD3dDevice()->Present( NULL, NULL, NULL, NULL );', start)
    end = raw.index(b'\n', stop)
    if raw[start:end].count(b'_GetUIScreen()->Draw();') != 1:
        raise ValueError('Legacy loading screen draw boundary changed')
    raw = raw[:start] + b'''    const bool koreanLoading = RF455_GetNormalNationPaths()->nation == RF455_MapNation("Korea");
    // The standalone Korean rating uses the background alone.
    if (koreanLoading && m_uiLoadingWindow.SelectLoadingFrame455(1)) {
        m_uiLoadingWindow.Open();
        constexpr DWORD ratingMs = 3000;
        const DWORD ratingStart = timeGetTime();
        for (DWORD elapsed = 0; elapsed < ratingMs; elapsed = timeGetTime() - ratingStart) {
            if (R3BeginScene()) {
                R3ClearFrameBuffer();
                _GetUIScreen()->Draw();
                R3EndScene();
                RF455_CaptureGameRatingIfRequested(elapsed);
                GetD3dDevice()->Present(nullptr, nullptr, nullptr, nullptr);
            }
            Sleep(1);
        }
        RF455_ObserveProtocol("lobby-rating-end", timeGetTime() - ratingStart, 0, 0);
        m_uiLoadingWindow.Close();
    }
    const auto* loadingNetwork = _GetNetworkMgr();
    m_uiLoadingWindow.PrepareLoading455(koreanLoading, loadingNetwork->PremiumState455() != 0,
                                        loadingNetwork->m_worldEntry455.kind);
    m_uiLoadingWindow.Open();
    // 455 reveals the loading sprite before the synchronous lobby load.
    constexpr DWORD revealMs = 800;
    const DWORD revealStart = timeGetTime();
    DWORD elapsed;
    do {
        elapsed = timeGetTime() - revealStart;
        const bool complete = elapsed >= revealMs;
        if (R3BeginScene()) {
            R3ClearFrameBuffer();
            _GetUIScreen()->Draw();
            if (!complete) SetFadeFactor(0, 1.0f - float(elapsed) / revealMs, nullptr);
            R3EndScene();
            RF455_CaptureLoadingRevealIfRequested(elapsed, complete);
            const HRESULT result = GetD3dDevice()->Present(nullptr, nullptr, nullptr, nullptr);
            if (complete) RF455_ObserveProtocol("lobby-loading-reveal", elapsed, unsigned(result), 0);
        }
        if (!complete) Sleep(1);
    } while (elapsed < revealMs);''' + raw[end:]
    raw = replace(raw, b'\tR3ClearFrameBuffer();\n\tGetD3dDevice()->Present( NULL, NULL, NULL, NULL );\n\t//\n\tm_uiLoadingWindow.Disable();',
                  b'\tm_uiLoadingWindow.Close();')
    return replace(raw, b'\tSetFadeOut(0x00,0,1.0f);\n\tSetFadeIn(0x00,3.0,1.0f);',
                   b'\tSetFadeIn(0, 0, 1.0f);')


def port_lobby_menu(raw, relative, native):
    if relative == 'userinterface/loginwindow/guiloadingwindow.h':
        raw = replace(raw, b'\tCGUIObject\t\tm_cLoading;',
                      b'\tCGUIObject\t\tm_cLoading;\n'
                      b'\tCGUIObject m_loadingBadges455[5];\n\tWORD m_loadingFrame455 = 0;')
        return replace(raw, b'\tvoid\tSetSprite( void );',
                       b'\tvoid SetSprite() override;\n'
                       b'\tbool SelectLoadingFrame455(WORD frame);\n'
                       b'\tvoid PrepareLoading455(bool korean, bool premium, BYTE ageKind);'), True
    if relative == 'userinterface/loginwindow/guiloadingwindow.cpp':
        start = raw.index(b'void\nCGUILoadingWindow::Init( void )')
        return raw[:start] + (native / 'client455_loading_window.inc').read_bytes(), True
    if relative == 'mainapp.cpp':
        # Land unload releases effect resources. Do it before the engine and
        # function-local effect owners are destroyed, while they are still alive.
        raw = replace(raw, b'\tm_cCamera.Destroy();', b'\tm_cLand.Destroy();\n\tm_cCamera.Destroy();')
        return raw, True
    if relative != 'gameprogress/cgp_login.cpp':
        return raw, False

    raw = replace(raw, b'#include "../MainApp.h"', b'#include "../MainApp.h"\n' +
                  (native / 'client455_lobby_menu.inc').read_bytes())
    raw = replace(raw, b'{ CAM_TOP_TO_LOGINC, 4, 0, 40 },', b'{ CAM_TOP_TO_LOGINC, 4, 0, 66 },')
    raw = replace(raw, b'{ CAM_TOP_TO_LOGINC, 22, 0, 55 },', b'{ CAM_TOP_TO_LOGINC, 22, 0, 70 },')
    raw = replace(raw, b'int\t\tm_CurAniKey = 0;', b'''constexpr DWORD CameraStartWave455 = 32001;
constexpr DWORD CameraMiddleWave455 = 32002;
constexpr DWORD CameraEndWave455 = 32003;
static bool cameraEndSoundPending455;
static DWORD cameraSoundStartFrame455;
static DWORD cameraSoundEndFrame455;''')
    raw = replace(raw, b'void PlayCamera(CameraAni\tani,DWORD\tcourse = 0)', b'''void PlayLobbyIdleCamera455(bool returningFromCredits = false)
{
    cameraEndSoundPending455 = false;
    StopWave(CameraMiddleWave455);
    const DWORD camera = m_AniCamera.GetCameraIndex(!RF455_LobbyReferenceMode() && m_RandomStart ? "c_ex01" : "c_ex02");
    if (camera != ID_INVALID) {
        m_AniCamera.SetPrePlayCamera(camera, 0, returningFromCredits ? 0 : ID_INVALID,
                                     returningFromCredits ? _CAM_FLAG_FINAL_STOP : 0);
        RF455_ObserveProtocol("lobby-idle-camera", m_RandomStart, returningFromCredits, 0);
    }
}

void PlayCamera(CameraAni ani, DWORD course = 0, bool fromLobby = false)''')
    start = raw.index(b'#define\t\tCAM_START_WAV')
    end = raw.index(b'\n}', start)
    raw = raw[:start] + b'''    DWORD clip = ani + course;
    if (m_RandomStart && (fromLobby || g_LoginState == LGS_ENTER_WORLDSERVER)) clip += 23;
    const auto& clipFrames = m_AniCamKeyFrame[clip];
    const DWORD camera = m_AniCamera.GetCameraIndex(CamName[clipFrames[1]]);
    PlayWave(CameraStartWave455, 0, 1.0f, 0.0f);
    cameraSoundStartFrame455 = clipFrames[2];
    cameraSoundEndFrame455 = clipFrames[3];
    cameraEndSoundPending455 = camera != ID_INVALID;
    RF455_ObserveProtocol("lobby-camera-sound-start", CameraStartWave455, clipFrames[1], clipFrames[3]);
    if (fromLobby) {
        RF455_ObserveProtocol("lobby-selection-camera", course, clipFrames[1], clipFrames[3]);
    }
    m_AniCamera.SetPrePlayCamera(camera, clipFrames[2], clipFrames[3], _CAM_FLAG_FINAL_STOP);''' + raw[end:]
    raw = replace(raw, b'''DWORD\tcam = 0;
\tif ( m_RandomStart )
\t{
\t\tcam =m_AniCamera.GetCameraIndex("C_05");
\t}
\telse
\t{
\t\tcam =m_AniCamera.GetCameraIndex("C_01");
\t}
\tm_AniCamera.SetPrePlayCamera(cam,0,0,_CAM_FLAG_FINAL_STOP);''', b'PlayLobbyIdleCamera455();')
    raw = open_lobby_after_avatar_loading(raw)
    raw = reveal_lobby_loading(raw)
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
    raw = replace(raw, b'\t\t_GetUIScreen()->Draw();\n\n\t\t// User Interface',
                  b'        if (lobbyMenu455.ShowingCredits()) FullScreenEffect();\n'
                  b'\t\t_GetUIScreen()->Draw();\n\n\t\t// User Interface')
    raw = replace(raw, b'\t\tDrawFadeScreen();', b'        lobbyMenu455.DrawCredits();\n\t\tDrawFadeScreen();')
    raw = replace(raw, b'\tRF455_CaptureLoginFrameIfRequested();',
                  b'\tRF455_CaptureLoginFrameIfRequested();\n'
                  b'    if (lobbyMenu455.ShowingCredits() && lobbyMenu455.CreditsScrolled())\n'
                  b'        RF455_CaptureLobbyCameraIfRequested(3);')
    raw = replace(raw, b'sprintf( l_pBuf, "Closed Beta v %.3f", _GetMainApp()->GetVersion() );',
                  b'strcpy( l_pBuf, "RF Online 4.55" );')

    raw = replace(raw, b'\tNetworkInput();', b'''    NetworkInput();
    switch (lobbyMenu455.TakeAction()) {
    case LobbyMenu455::Action::Start:
        lobbyMenu455.Start();
        m_CameraAni = true;
        PlayCamera(CAM_TOP_TO_LOGINA, m_Course, true);
        RF455_ObserveProtocol("lobby-start", 0, 0, 0);
        return TRUE;
    case LobbyMenu455::Action::Credits:
        if (lobbyMenu455.OpenCredits()) {
            PlayLobbyIdleCamera455();
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
    start = raw.index(b'\tstatic float endframe = 0;')
    end = raw.index(b'\tif (g_LoginState == LGS_CHARACTERLOBBY)', start)
    if raw[start:end].count(b'PlayWave( CAM_END_WAV') != 2:
        raise ValueError('Legacy camera sound boundary changed')
    raw = raw[:start] + b'''    if (!lobbyMenu455.ShowingCredits()) {
        if (!m_CameraAni || !lobbyMenu455.Started()) {
            cameraEndSoundPending455 = false;
            StopWave(CameraMiddleWave455);
        } else if (cameraEndSoundPending455) {
            const float position = m_AniCamera.GetNowFrame();
            // 455 uses 32 ms per authored frame for the audio cue.
            const float cue = static_cast<float>(cameraSoundEndFrame455 * 0.032);
            const bool reachedCue = cameraSoundStartFrame455 > cameraSoundEndFrame455
                ? position < cue + 0.1f
                : position > cue - 0.1f && position <= cue;
            if (reachedCue && position > 0.0f) {
                cameraEndSoundPending455 = false;
                PlayWave(CameraEndWave455, 0, 1.0f, 0.0f);
                RF455_ObserveProtocol("lobby-camera-sound-end", CameraEndWave455, cameraSoundEndFrame455,
                                      static_cast<unsigned>(position * 1000.0f));
            }
        }
    }
''' + raw[end:]
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
    raw = replace(raw, b'\t\t\tUI_SetMoveWindow( SELECT_CHAR_WIN, TRUE );',
                  b'\t\t\tUI_SetMoveWindow( SELECT_CHAR_WIN, TRUE );\n'
                  b'\t\t\tRF455_ObserveProtocol("lobby-selection-open", 0, 0, 0);\n'
                  b'\t\t\tRF455_ObserveProtocol("lobby-selection-slot", m_Course, m_HaveCharacter[m_Course] != FALSE, 0);')
    raw = replace(raw, b'''if( g_bClosingWindow )
\t\t\t{
\t\t\t\tm_uiSelectCharacter.Close();
\t\t\t\tg_bClosingWindow = FALSE;
\t\t\t}''', b'''if (g_bClosingWindow) {
                m_uiSelectCharacter.Close();
                g_bClosingWindow = FALSE;
            } else {
                RF455_ObserveProtocol("lobby-selection-input-ready", RF455_SelectedCharacterSlot(), 0, 0);
            }''')
    raw = replace(raw, b'CGP_LogIn::MsgProc( HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam )\n{',
                  b'''CGP_LogIn::MsgProc( HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam )
{
    if (uMsg == WM_SYSKEYDOWN && wParam == VK_F10) {
        if (!(lParam & (1L << 30))) RF455_OpenLobbySettings();
        return 0xffffffff;
    }
    if (uMsg == WM_SIZE && lobbyMenu455.IsShow()) lobbyMenu455.Layout();
    if (uMsg == WM_KEYDOWN && !(lParam & (1L << 30))) {
        const bool credits = lobbyMenu455.ShowingCredits();
        if (lobbyMenu455.KeyDown(wParam)) {
            if (credits) PlayLobbyIdleCamera455(true);
            return 0xffffffff;
        }
    }''')
    # Scope the modern passes to the ordinary Login renderer, preserving loading/credits.
    start=raw.index(b'CGP_LogIn::Render(')
    stop=raw.index(b'\nBOOL',start) if b'\nBOOL' in raw[start:] else len(raw)
    body=raw[start:stop]
    body=replace(body,b'\tif( R3BeginScene() )',b'    lobbyFrameSample455.begin();\n\tif( R3BeginScene() )')
    body=replace(body,b'\t\tR3ClearFrameBuffer();',b'        const bool modernLobby = !lobbyMenu455.ShowingCredits() && !GetStateFullScreenEffect() && RF455_BeginLobbyPost(GetD3dDevice());\n\t\tR3ClearFrameBuffer();')
    body=replace(body,b'        if (lobbyMenu455.ShowingCredits()) FullScreenEffect();',b'''        if(modernLobby){
            RF455_EndLobbyPost(GetD3dDevice());
            if(!RF455_GetLobbyPostTelemetry().uiSceneReady)return S_OK;
        }
        if (lobbyMenu455.ShowingCredits()) FullScreenEffect();''')
    body=replace(body,b'\t\t_GetUIScreen()->Draw();',b'        if(!RF455_LobbyReferenceMode())_GetUIScreen()->Draw();\n        else if(RF455_LobbyOptions() && RF455_LobbyOptions()->IsShow()){RF455_LobbyOptions()->Draw();_GetUIScreen()->GetMouse()->Draw();}')
    body=replace(body,b'if (lobbyMenu455.IsShow() || g_LoginState == LGS_IDANDPASSWORD)',b'if (!RF455_LobbyReferenceMode() && (lobbyMenu455.IsShow() || g_LoginState == LGS_IDANDPASSWORD))')
    body=replace(body,b'\tR3EndScene();',b'\tR3EndScene();\n    lobbyFrameSample455.end();\n    RF455_SaveLobbyVisualMetadata();\n    RF455_ObserveLobbySettings();')
    raw=raw[:start]+body+raw[stop:]
    raw=replace(raw,b'\tm_CameraAni = m_AniCamera.PlayAniCamera(get_mat,1.0f);',b'    if(RF455_LobbyReferenceMode())m_AniCamera.SetNowFrame(RF455_LobbyReferenceSeconds());\n\tm_CameraAni = m_AniCamera.PlayAniCamera(get_mat,1.0f);')
    return raw, True
