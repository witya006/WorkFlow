"""Bind the confirmed center-message owner to ordinary MainGame lifetime/frames."""
import re


def port_center_messages(raw,relative):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Center messages anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='gameprogress/cgp_maingame.h':
        raw=b'#include "client455_center_messages.h"\r\n'+raw
        raw,count=re.subn(rb'(\tCGUIOptionWindow\s+m_uiOptionWindow;)',rb'\1\r\n\tRF455CenterMessages m_centerMessages455;',raw)
        if count!=1:raise ValueError('Center MainGame UI-member boundary')
        once(b'\tCGP_MainGame();',b'\tCGP_MainGame();\r\n\tRF455CenterMessages& CenterMessages455(){return m_centerMessages455;}')
        return raw,True
    if relative=='gameprogress/cgp_maingame.cpp':
        once(b'\t_GetGBM()->FrameMove();',b'\t_GetGBM()->FrameMove();\r\n\tm_centerMessages455.FrameMove();')
        once(b'\t\tRF455_NuclearAiming().FrameMove();',b'\t\tRF455_NuclearAiming().FrameMove();\r\n\t\tm_centerMessages455.Draw();')
        return raw,True
    return raw,False
