"""Bind the PC Room reward board to the ordinary MainGame stage."""


def port_reward_window(raw, relative, section, native):
    nl = b'\r\n' if b'\r\n' in raw else b'\n'

    def after(anchor, text):
        nonlocal raw
        if raw.count(anchor) != 1:
            raise ValueError('Reward window source boundary: ' + repr(anchor))
        raw = raw.replace(anchor, anchor + nl + text.replace(b'\n', nl))

    if relative == 'gameprogress/cgp_maingame.h':
        after(b'#include "CGameProgress.h"', b'#include "client455_reward_window.h"')
        after(b'CGUIRadarWindow\t\t\tm_uiRadarWindow;', b'\tCGUIRewardWindow455 m_rewardWindow455;')
        after(b'\tCGP_MainGame();', b'\tCGUIRewardWindow455& RewardWindow455() { return m_rewardWindow455; }')
        return raw, True
    if relative == 'gameprogress/cgp_maingame.cpp':
        after(b'm_uiRadarWindow.Init();', b'\tm_rewardWindow455.Init();')
        after(b'_GetUIScreen()->Add( &m_uiOptionWindow );', b'\t_GetUIScreen()->Add(&m_rewardWindow455);')
        anchor = b'CGP_MainGame::Destroy_UI('
        start, end = section(raw, anchor, anchor)
        body = raw[start:end]
        at = body.index(b'{') + 1
        raw = raw[:start] + body[:at] + nl + b'\tm_rewardWindow455.Close();' + body[at:] + raw[end:]
        return raw, True
    if relative == 'network/netmsgprocessor/event/cnetmsgprocessor_event.cpp':
        path = native / 'client455_reward_dispatch.inc'
        after(b'#include "CNetMsgProcessor_Event.h"',
              b'\n' + path.read_bytes().replace(b'\r\n', b'\n'))
        anchor = b'switch( pMsgHeader->m_byType[1] )'
        start = raw.index(anchor)
        at = raw.index(b'{', start) + 1
        entries = b'''
        case 32:
            return showRewardOffer455(pMsgHeader->m_wSize, pi_pMsg);
        case 34:
            return showRewardResult455(pMsgHeader->m_wSize, pi_pMsg);
'''
        raw = raw[:at] + entries.replace(b'\n', nl) + raw[at:]
        return raw, True
    return raw, False
