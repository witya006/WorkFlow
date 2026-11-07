"""Wire source-owned typed hover/dual backups into ordinary manager andscreen."""
import re


def port_board_hover(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Hover anchor:'+relative+':'+repr(old))
        raw=raw.replace(old,new)
    def prepend(signature,statement):
        nonlocal raw
        start,end=section(raw,signature,signature);body=raw[start:end];at=body.index(b'{')+1
        raw=raw[:start]+body[:at]+b'\r\n\t'+statement+body[at:]+raw[end:]
    if relative=='gameobject/board/common/cboardmanager.h':
        raw=b'#include "client455_board_hover.h"\r\n'+raw
        raw,count=re.subn(rb'(CBoardObject\s*\*\s*m_pHoverObject\s*;)',rb'\1\r\n\tRF455BoardHoverState* m_hoverState455;',raw)
        if count!=1:raise ValueError('Hover owner member')
        api=b'''\r\n\tvoid InitHover455();\r\n\tvoid DestroyHover455();\r\n\tBOOL UsesTypedHover455()const;\r\n\tCBoardObject* SetTypedHover455(CBoardObject*);\r\n\tCBoardObject* HoverObject455();\r\n\tCBoardObject* PreviousHover455();\r\n\tCBoardObject* OperationObject455();\r\n\tvoid SetOperationObject455(CBoardObject*);\r\n\tvoid ClearHoverBackups455();\r\n\tCBoardItem* LegacyHoverItem455();\r\n\tCBoardItem* LegacyDeletedHover455();\r\n\tBOOL AddTypedBoardObject455(BYTE,BYTE,BYTE,CBoardObject*);'''
        once(b'\tCBoardManager();',b'\tCBoardManager();'+api)
        for name,old,new in [('GetHoverObject',b'return m_pHoverObject;',b'return HoverObject455();'),
                             ('GetHoverItem',b'return static_cast< CBoardItem * >( m_pHoverObject );',b'return LegacyHoverItem455();'),
                             ('GetDeletedHoverItem',b'return ( m_pDeletedHoverItem->IsEmpty() ? NULL : m_pDeletedHoverItem );',b'return LegacyDeletedHover455();')]:
            pattern=rb'('+name.encode()+rb'\( void \)\s*\{ )'+re.escape(old)+rb'( \})'
            raw,count=re.subn(pattern,lambda match:match[1]+new+match[2],raw)
            if count!=1:raise ValueError('Hover getter anchor '+name)
        return raw,True
    if relative=='gameobject/board/common/cboardmanager.cpp':
        for signature,statement in [(b'CBoardManager::CBoardManager(',b'InitHover455();'),(b'CBoardManager::~CBoardManager(',b'DestroyHover455();')]:
            start,end=section(raw,signature,signature);raw=raw[:end-1]+b'\r\n\t'+statement+b'\r\n'+raw[end-1:]
        prepend(b'CBoardManager::SetHoverObject(',b'if(RF455_IsOwnBoardObject455(pi_pObject)||UsesTypedHover455())return SetTypedHover455(pi_pObject);')
        prepend(b'CBoardManager::ReturnHoverObject(',b'if(UsesTypedHover455()){AddTypedBoardObject455(m_byOrgBoardType,m_byOrgPackNo,m_byOrgSocketNo,HoverObject455());return;}')
        prepend(b'CBoardManager::AddObject(',b'if(RF455_IsOwnBoardObject455(pi_pTarObject))return AddTypedBoardObject455(pi_byBoardType,pi_byPackNo,pi_bySocketNo,pi_pTarObject);')
        prepend(b'CBoardManager::FrameMove(',b'if(RF455_IsOwnBoardObject455(m_pHoverObject)&&m_pHoverObject->GetIcon())m_pHoverObject->GetIcon()->Update();')
        return raw,True
    if relative=='userinterface/guicontroller/guiscreen.h':
        once(b'\tCGUIScreen();',b'\tCGUIScreen();\r\n\tvoid AddTypedHoverIcon455(CGUIItem*);\r\n\tvoid RemoveTypedHoverIcon455();')
        return raw,True
    if relative=='userinterface/guicontroller/guiscreen.cpp':
        prepend(b'CGUIScreen::AddObject(',b'if(!pi_pItem)return;if(pi_pItem->UsesTypedIcon455()){AddTypedHoverIcon455(pi_pItem);return;}')
        prepend(b'CGUIScreen::RemoveObject(',b'if(m_cCatchedItem.UsesTypedIcon455()){RemoveTypedHoverIcon455();return;}')
        return raw,True
    return raw,False
