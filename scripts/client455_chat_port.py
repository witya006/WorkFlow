"""Own chat profile in MainGame and add selected target insertion to real panes."""
import re

from client455_trade_ore_port import patch_method, remove_methods


def port_chat(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Chat anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='gameprogress/cgp_maingame.h':
        raw=b'#include "client455_chat_profile.h"\r\n'+raw
        raw,count=re.subn(rb'(\tCGUIChatWindow\s+m_uiChatWindow;)',rb'\tRF455ChatProfile m_chatProfile455;\r\n\1',raw)
        if count!=1:raise ValueError('MainGame chat member boundary')
        once(b'\tCGP_MainGame();',b'\tCGP_MainGame();\r\n\tRF455ChatProfile& ChatProfile455(){return m_chatProfile455;}\r\n\tCGUIChatWindow& ChatWindow455(){return m_uiChatWindow;}')
        return raw,True
    if relative=='gameprogress/cgp_maingame.cpp':
        once(b'\tm_bIsCreated_UI = TRUE;',b'\tm_bIsCreated_UI = TRUE;\r\n\tm_uiChatWindow.InitializeChat455();')
        return raw,True
    if relative=='userinterface/gamewindow/guichatwindow.h':
        raw=b'#include "client455_chat_window.h"\r\n'+raw
        begin=raw.index(b'class CGUIChatWindow : public CGUIWindow')
        end=raw.index(b'class CGUIChatInputWindow : public CGUIWindow',begin)
        selected,count=re.subn(rb'(BOOL\s+m_bCreated;)',rb'\1\r\n\tRF455ChatWindowState m_chat455;',raw[begin:end])
        if count!=1:raise ValueError('ChatWindow state member')
        raw=raw[:begin]+selected+raw[end:]
        declarations=(b'\tCGUIChatWindow();\r\n'
                      b'\tvoid InitializeChat455(const char* settings="./DataTable/GameSetting.ini");\r\n'
                      b'\tvoid SetChatFilterKernel455(BYTE category,DWORD value,BYTE pane=0xff);\r\n'
                      b'\tDWORD GetChatFilter455(unsigned category,unsigned pane=4)const;\r\n'
                      b'\tCGUITextBoard* GetChatBoard455(unsigned pane);\r\n'
                      b'\tbool WrapChat455(const char* input,int firstWidth,int indentation,std::string& output);\r\n'
                      b'\tvoid InsertText455(const char* id,const char* text,int style,int category);\r\n'
                      b'\tvoid InsertChatRaw455(const char* text,int style,int category);')
        once(b'\tCGUIChatWindow();',declarations)
        begin=raw.index(b'class CGUIChatInputWindow : public CGUIWindow')
        end=raw.index(b'class CGUIBuddyWindow : public CGUIWindow',begin)
        compact=raw[begin:end]
        for line in (b'CGUIObject\t\tm_uiOpenChatWin;',b'CGUIChatWindow\t*\tm_pChatWindow;',
                     b'void\tSetSprite( void );',b'void\tSetChatWindow( CGUIChatWindow * pi_pWin ) { m_pChatWindow = pi_pWin; }',
                     b'void\tMouseEvent( _mouse_event &event );'):
            if compact.count(b'\t'+line)!=1:raise ValueError('Compact chat declaration '+repr(line))
            compact=compact.replace(b'\t'+line,b'')
        return raw[:begin]+compact+raw[end:],True
    if relative=='userinterface/gamewindow/guichatwindow.cpp':
        owner=b'CGUIChatInputWindow'
        raw=remove_methods(raw,section,owner,[(b'SetSprite',b'void'),(b'MouseEvent',b'void')])
        once(b'\tm_pChatInputWin->SetChatWindow( this );',b'')
        def compact_init(body):
            begin=body.index(b'{')+1
            return body[:begin]+b'''
    m_pInputField = pi_pInput;
    Add(m_pInputField);
    DisableFocus();
    SetFocusObject(m_pInputField);
}'''
        raw=patch_method(raw,section,owner,b'Init',compact_init)
        def compact_draw(body):
            for old,new in [(b'0x90604023',b'0x60030303'),(b'0xA0D5B383',b'0x90919181')]:
                body=body.replace(old,new)
            start=body.index(b'\n\telse',body.index(b'0x90919181'))
            end=body.index(b'\n\tCGUIContainer::Draw();',start)
            return body[:start]+b'\n'+body[end:]
        raw=patch_method(raw,section,owner,b'Draw',compact_draw)
        return raw,True
    if relative=='userinterface/guicontroller/guitextboard.h':
        once(b'    void InsertText(char* text,FONT_INFO* font);',b'    void InsertText(char* text,FONT_INFO* font);\r\n    void InsertStyled455(char* text,FONT_INFO* font,BOOL adjustView){InsertFragment(text,font,adjustView);}')
        return raw,True
    return raw,False
