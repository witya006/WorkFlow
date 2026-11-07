"""Replace the actual Linker window member with its banked455 implementation."""
import re

def port_linker_window(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Linker window anchor:'+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='gameobject/board/common/clinkboard.h':
        raw=b'#include "client455_linker_window.h"\r\n'+raw
        once(b'CGUIForceBeltWindow\t\tm_uiLinkWindow;',b'CGUILinkWindow455\t\tm_uiLinkWindow;')
        once(b'\tCLinkBoard();',b'\tCLinkBoard();\r\n\tCGUILinkWindow455& LinkerWindow455(){return m_uiLinkWindow;}')
        return raw,True
    if relative=='gameobject/board/common/clinkboard.cpp':
        once(b'CLinkBoard::CLinkBoard(){ResetHotbarUpload455();}',b'CLinkBoard::CLinkBoard(){m_uiLinkWindow.BindBoard455(this);ResetHotbarUpload455();}')
        raw,count=re.subn(rb'CGUISFItem(\s*\*\s*pIcon\s*=\s*m_uiLinkWindow.GetItem)',rb'CGUIItem\1',raw)
        if count!=3:raise ValueError('Legacy Linker icon caller types changed')
        if raw.count(b'pIcon->IsDelayAnimation()')!=2:raise ValueError('Legacy Linker timer callers changed')
        raw=raw.replace(b'pIcon->IsDelayAnimation()',b'RF455_LinkerIconDelaying455(pIcon)')
        begin,end=section(raw,b'CLinkBoard::InitWindow(',b'CLinkBoard::InitWindow(');body=raw[begin:end]
        body=body[:-1]+b'\r\n\tm_uiLinkWindow.SetPos(gScreen.GetSizeX()-m_uiLinkWindow.GetSizeX(),gScreen.GetSizeY()-m_uiLinkWindow.GetSizeY());\r\n}'
        raw=raw[:begin]+body+raw[end:]
        begin,end=section(raw,b'CLinkBoard::MsgProc(',b'CLinkBoard::MsgProc(');body=raw[begin:end];at=body.index(b'{')+1
        raw=raw[:begin]+body[:at]+b'\r\n\tif(uMsg==0x50c&&static_cast<LONG>(lParam)<m_byMaxPackNum)m_byActivePackNo=static_cast<BYTE>(lParam);'+body[at:]+raw[end:]
        return raw,True
    return raw,False
