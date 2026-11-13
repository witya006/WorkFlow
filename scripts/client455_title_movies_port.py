"""Restore the Title stage's locale-selected logo and opening movie."""

from client455_trade_ore_port import replace


def port_title_movies(raw, relative, native):
    if relative == 'gameprogress/cgp_title.h':
        raw = b'#include <memory>\nclass RF455TitleMovies;\n' + raw
        raw = replace(raw, b'class CGP_Title : public CGameProgress\n{',
                      b'class CGP_Title : public CGameProgress\n{\n    std::unique_ptr<RF455TitleMovies> m_openingMovies455;\n'
                      b'    bool m_videoFrameDrawn455 = false;')
        raw = replace(raw, b'\tCGP_Title();',
                      b'    bool HasVideoFrame455() const { return m_videoFrameDrawn455; }\n\tCGP_Title();')
        return raw, True
    if relative != 'gameprogress/cgp_title.cpp':
        return raw, False

    raw = replace(raw, b'#include "CGP_Title.h"', b'#include "CGP_Title.h"\n' +
                  (native / 'client455_title_movies.inc').read_bytes())
    raw = replace(raw, b'if( !CGameProgress::Create() ) return FALSE;',
                  b'''if( !CGameProgress::Create() ) return FALSE;
    m_openingMovies455 = std::make_unique<RF455TitleMovies>(_GetHWND());
    if (!m_openingMovies455->Start()) RequestStageExit455();''')
    raw = replace(raw, b'if( !CGameProgress::Destroy() ) return FALSE;',
                  b'm_openingMovies455.reset();\n\tif( !CGameProgress::Destroy() ) return FALSE;')
    raw = replace(raw, b'CGP_Title::FrameMove( void )\n{\n\treturn S_OK;',
                  b'''CGP_Title::FrameMove( void )
{
    if (m_openingMovies455 && !m_openingMovies455->Tick()) RequestStageExit455();
    return S_OK;''')
    raw = replace(raw, b'CGP_Title::InputProcess( void )\n{\n\tm_bExit = TRUE;\n\n\treturn TRUE;',
                  b'CGP_Title::InputProcess( void )\n{\n\treturn TRUE;')
    raw = replace(raw, b'CGP_Title::Render( void )\n{\n\treturn S_OK;',
                  b'CGP_Title::Render( void )\n{\n    m_videoFrameDrawn455 = m_openingMovies455 && m_openingMovies455->Render();\n    return S_OK;')
    raw = replace(raw, b'CGP_Title::MsgProc( HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam )\n{\n\treturn 0;',
                  b'''CGP_Title::MsgProc( HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam )
{
    if (!m_openingMovies455) return 0;
    if ((uMsg == WM_KEYDOWN || uMsg == WM_SYSKEYDOWN) && wParam == VK_ESCAPE) {
        m_openingMovies455->Skip();
        RequestStageExit455();
        return 0xffffffff;
    }
    return 0;''')
    return raw, True
