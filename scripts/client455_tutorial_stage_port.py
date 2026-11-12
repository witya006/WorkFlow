"""Bind the ordinary client stages and route the initial Tutorial dialog."""

from client455_trade_ore_port import replace


def port_tutorial_stage(raw, relative):
    if relative == 'mainapp.h':
        raw = replace(raw, b'#define MAX_GAME_PROGRESS\t3', b'#define MAX_GAME_PROGRESS\t4')
        raw = replace(raw, b'#define GPI_MAIN_GAME\t\t0x2',
                      b'#define GPI_TUTORIAL\t\t0x2\n#define GPI_MAIN_GAME\t\t0x3')
        anchor = b'\tBOOL\tGameMainLoop( void );'
        raw = replace(raw, anchor, anchor + b'\n\tvoid TutorialDialog455(WORD id, DWORD result);')
    elif relative == 'mainapp.cpp':
        raw = b'#include "client455_tutorial_stage.h"\n' + raw
        raw = replace(raw, b'RF455_FromLegacyStage(m_byGameProgressID)', b'm_byGameProgressID')
        raw = replace(raw, b'if( m_pGameProgress->MainLoop( m_bIsActive ) )\n'
                      b'\t\t\tCreate_GameProgress( ( m_byGameProgressID + 1 ) % MAX_GAME_PROGRESS );',
                      b'''if (m_pGameProgress->MainLoop(m_bIsActive)) {
            DWORD next = m_pGameProgress->GetNextStage455();
            if (next == ID_INVALID) next = m_byGameProgressID == GPI_LOGIN ? GPI_MAIN_GAME : GPI_TITLE;
            if (next < MAX_GAME_PROGRESS) Create_GameProgress(static_cast<BYTE>(next));
        }''')
        anchor = b'else if( m_byGameProgressID == GPI_MAIN_GAME )\n\t\tm_pGameProgress = new CGP_MainGame;'
        raw = replace(raw, anchor, b'else if (m_byGameProgressID == GPI_TUTORIAL)\n'
                      b'\t\tm_pGameProgress = RF455_CreateTutorialStage();\n\t' + anchor)
        raw += b'''\nvoid CMainApp::TutorialDialog455(WORD id, DWORD result)
{
    if (m_byGameProgressID == GPI_TUTORIAL && m_pGameProgress)
        RF455_DeliverTutorialDialog(*m_pGameProgress, id, result);
}

void RF455_ReceiveTutorialDialog(WORD id, DWORD result)
{
    g_MainApp.TutorialDialog455(id, result);
}
'''
    elif relative == 'gameprogress/cgp_login.cpp':
        begin = raw.index(b'\t\t\t\t_GetAvatar()->SetName( _GetAvatarDummy(m_Course)->GetName() );')
        end = raw.index(b'\n\t\t\t\t_GetNetworkMgr()->Close( GST_WORLD );', begin)
        transfer = raw[begin:end]
        transfer = b'\n'.join(line[3:] if line.startswith(b'\t' * 4) else line
                              for line in transfer.split(b'\n'))
        transfer = transfer.replace(b'for( i =', b'for( int i =')
        raw = raw[:begin] + b'\t\t\t\tApplySelectedAvatar455();\n' + raw[end:]
        entry = b'void EventJoinGameFunc()\n'
        raw = replace(raw, entry, b'namespace {\nvoid ApplySelectedAvatar455()\n{\n' + transfer + b'\n}\n}\n\n' + entry)
        anchor = b'\t\t_GetNetworkMgr()->SystemMsg_SelCharRequest_zone( m_Course );'
        raw = replace(raw, anchor, b'''        if (!_GetAvatarDummy(m_Course)->GetSkipTutorial455()) {
            ApplySelectedAvatar455();
            _GetNetworkMgr()->Close(GST_WORLD);
            PlayCamera(CAM_A_TO_JOIN, m_Course);
            m_MP3ElapseTime = timeGetTime();
            FadeOutSound();
            UI_SetMoveWindow(SELECT_CHAR_WIN, FALSE);
            SetFadeOut(0, 1.0f, 1.0f);
            g_LoginState = LGS_TUTORIAL455;
            RF455_ObserveProtocol("tutorial-selected", m_Course, _GetAvatar()->GetRace(), 0);
            return;
        }
''' + anchor)
        raw = replace(raw, b'LGS_EXIT\n', b'LGS_EXIT, LGS_TUTORIAL455\n')
        anchor = b'\tif( IsFadeOut() && ( g_LoginState == LGS_EXIT ) && ( !m_bRequestConnect ) )'
        raw = replace(raw, anchor, b'''    if (g_LoginState == LGS_TUTORIAL455 && IsFadeOut()) {
        st_PlayMP3.StopR3MP3();
        st_PlayMP3.ReleaesR3MP3();
        CloseLoginSound();
        SetNextStage455(GPI_TUTORIAL);
        RequestStageExit455();
        return TRUE;
    }

''' + anchor)
        raw += b'\nvoid RF455_CaptureTutorialFrame455() { RF455_CaptureLoginFrameIfRequested(); }\n'
    elif relative == 'userinterface/guicontroller/guiscreen.cpp':
        anchor = b'\tCGUIWindow::ClosingDialogBox( pi_pDlg );'
        raw = b'#include "client455_tutorial_stage.h"\n' + raw
        raw = replace(raw, anchor, b'''    if (pi_pDlg->GetUserDefinedID() >= 0x6000 && pi_pDlg->GetUserDefinedID() <= 0x6003)
        RF455_ReceiveTutorialDialog(pi_pDlg->GetUserDefinedID(), pi_pDlg->GetResultMsg());

''' + anchor)
    elif relative == 'gameobject/board/common/cboardmanager.h':
        raw = replace(raw, b'\tvirtual ~CBoardManager();', b'\tvirtual ~CBoardManager();\n\tvoid ClearBoards455();')
    elif relative == 'gameobject/board/common/cboardmanager.cpp':
        raw = replace(raw, b'CBoardManager::~CBoardManager()\n{\n\tfor( int i = 0; i < MAX_BOARD_TYPE; ++i )\n'
                      b'\t\t_DELETE( m_listBoard[i] );', b'''void CBoardManager::ClearBoards455()
{
    for (auto& board : m_listBoard) {
        delete board;
        board = nullptr;
    }
}

CBoardManager::~CBoardManager()
{
    ClearBoards455();''')
    elif relative == 'gameprogress/cgp_maingame.cpp':
        raw = replace(raw, b'CGP_MainGame::Destroy_Board( void )\n{\n}', b'''CGP_MainGame::Destroy_Board( void )
{
    // Board windows may still unregister animations from the live GUI manager.
    _GetGBM()->ClearBoards455();
    m_bIsCreated_Board = FALSE;
}''')
    else:
        return raw, False
    return raw, True
