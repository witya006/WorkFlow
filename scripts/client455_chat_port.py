"""Own chat profile in MainGame and add selected target insertion to real panes."""
import re


def port_chat(raw,relative):
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
        return raw,True
    if relative=='userinterface/guicontroller/guitextboard.h':
        once(b'    void InsertText(char* text,FONT_INFO* font);',b'    void InsertText(char* text,FONT_INFO* font);\r\n    void InsertStyled455(char* text,FONT_INFO* font,BOOL adjustView){InsertFragment(text,font,adjustView);}')
        return raw,True
    return raw,False
