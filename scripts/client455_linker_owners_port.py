"""Migrate actual Linker typed clone/registration ownership before full UI events."""

def port_linker_owners(raw,relative,section):
    changed=False
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Linker owner anchor:'+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='gameobject/board/common/clinkboard.h':
        once(b'\tDWORD m_hotbarUploadTime455=0;',b'\tDWORD m_hotbarUploadTime455=0;\r\n\tbool m_linkerOwned455[50]={};')
        once(b'\tCLinkBoard();',b'\tCLinkBoard();\r\n\tBOOL AddTypedObject455(BYTE,BYTE,CBoardObject*);\r\n\tBOOL RemoveTypedObject455(BYTE,BYTE);\r\n\tvoid ClearTypedLinker455();\r\n\tCGUIItem* LinkerIcon455(BYTE,BYTE);')
        changed=True
    elif relative=='gameobject/board/common/clinkboard.cpp':
        for signature,hook in [
            (b'CLinkBoard::Add_ProcessExistObject(',b'if(pi_pOrgObject&&pi_pOrgObject->GetItem455())return FALSE;'),
            (b'CLinkBoard::Add_ProcessNewObject(',b'if(pi_pOrgObject&&pi_pOrgObject->GetItem455())return AddTypedObject455(pi_byTarPackNo,pi_byTarSocketNo,pi_pOrgObject);'),
            (b'CLinkBoard::Remove_ProcessRemoveObject(',b'if(pi_byPackNo<5&&pi_bySocketNo<10&&m_linkerOwned455[10*pi_byPackNo+pi_bySocketNo])return RemoveTypedObject455(pi_byPackNo,pi_bySocketNo);'),
            (b'CLinkBoard::~CLinkBoard(',b'ClearTypedLinker455();')]:
            begin,end=section(raw,signature,signature);body=raw[begin:end];at=body.index(b'{')+1
            raw=raw[:begin]+body[:at]+b'\r\n\t'+hook+body[at:]+raw[end:]
        changed=True
    elif relative=='userinterface/gamewindow/guiforcebeltwindow.h':
        raw=b'#include "client455_linker_owners.h"\r\n'+raw
        once(b'\tRF455HotbarWindowState m_hotbarState455;',b'\tRF455HotbarWindowState m_hotbarState455;\r\n\tRF455LinkerIconSlots m_linkerIcons455;')
        once(b'\tCGUIForceBeltWindow();',b'\tCGUIForceBeltWindow();\r\n\tRF455LinkerIconSlots& LinkerIcons455(){return m_linkerIcons455;}')
        changed=True
    return raw,changed
