"""Bind confirmed messages to actual source objects and ordinary formatted callers."""
import re


def port_message_dispatch(raw,relative):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Message dispatch anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='mainapp.h':
        anchor=b'inline\tBYTE\tGetGameProgressID( void )'
        once(anchor,b'CGameProgress* GetGameProgress455()const{return m_pGameProgress;}\r\n\t'+anchor)
        return raw,True
    if relative=='gameprogress/cgp_login.h':
        raw=b'#include "client455_message_dispatch.h"\r\n'+raw
        once(b'\tCGP_LogIn();',b'\tCGP_LogIn();\r\n\tRF455LoginMessages& SystemMessages455(){return m_messages455;}')
        once(b'\tCIMEEdit\tm_cIME;',b'\tRF455LoginMessages m_messages455;\r\n\tCIMEEdit\tm_cIME;')
        return raw,True
    if relative=='gameprogress/cgp_login.cpp':
        raw,count=re.subn(rb'(CGP_LogIn::Init\( void \)\s*\{)',rb'\1\r\n\tm_messages455.Clear();',raw)
        if count!=1:raise ValueError('Login message Init boundary')
        begin=raw.index(b'CGP_LogIn::Render( void )');end=raw.index(b'EP_SelectWorldServer(',begin)
        body=raw[begin:end]
        if body.count(b'R3EndScene();')!=1:raise ValueError('Actual Login Render end')
        raw=raw[:begin]+body.replace(b'R3EndScene();',b'm_messages455.Draw();\r\n\tR3EndScene();')+raw[end:]
        return raw,True
    if relative=='userinterface/gamewindow/guichatwindow.h':
        once(b'void InitializeChat455(',b'bool ChatReady455()const{return m_chat455.initialized;}\r\n\tvoid InitializeChat455(')
        return raw,True
    if relative=='global.cpp':
        raw=b'#include "client455_message_dispatch.h"\r\n'+raw
        pattern=rb'void\s+_SetSystemMsg\( const char \* l_pFormatString, \.\.\. \)\s*\{.*?\n\}'
        replacement=b'void\n_SetSystemMsg( const char * l_pFormatString, ... )\n{\n    va_list args;va_start(args,l_pFormatString);\n    RF455_ShowSystemMessageV(l_pFormatString,args);va_end(args);\n}'
        raw,count=re.subn(pattern,replacement,raw,flags=re.S)
        if count!=1:raise ValueError('Ordinary formatted message boundary')
        return raw,True
    return raw,False
