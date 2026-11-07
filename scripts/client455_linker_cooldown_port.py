"""Wire selected455 cooldowns into ordinary client owners and FrameMove."""
def port_linker_cooldown(raw,relative,section):
    if relative=='gameobject/board/common/clinkboard.h':
        raw=b'#include "client455_linker_cooldown.h"\r\n'+raw
        anchor=b'\tbool m_linkerOwned455[50]={};'
        if raw.count(anchor)!=1:raise ValueError('Cooldown owner anchor')
        raw=raw.replace(anchor,anchor+b'\r\n\tRF455LinkerCooldownState m_linkerCooldown455;')
        anchor=b'\tCLinkBoard();'
        if raw.count(anchor)!=1:raise ValueError('Cooldown API anchor')
        return raw.replace(anchor,anchor+b'\r\n\tRF455LinkerCooldownState& CooldownState455(){return m_linkerCooldown455;}\r\n\tvoid BeginTypedDelay455(RF455ManagedItem&,DWORD,LONG elapsed=-1);\r\n\tvoid ProcessCooldowns455();\r\n\tvoid RemoveCooldownObject455(CBoardObject*);\r\n\tCBoardObject* FindOriginalTyped455(RF455ManagedItem&,BOOL equal);'),True
    if relative=='gameobject/board/common/cboard.h':
        anchor=b'\tinline\tBYTE\tGetMaxPackNum( void )'
        if raw.count(anchor)!=1:raise ValueError('Source-board socket-count API anchor')
        return raw.replace(anchor,b'\tBYTE GetMaxSocketNum455(BYTE bank){return bank<m_byMaxPackNum?m_listItemPack[bank].GetMaxSocketNum():0;}\r\n'+anchor),True
    if relative!='gameobject/board/common/clinkboard.cpp':return raw,False
    for signature,statement in [(b'CLinkBoard::BeginDelayAnimation(',b'if(pi_pOrgObject&&pi_pOrgObject->GetItem455()){BeginTypedDelay455(*pi_pOrgObject->GetItem455(),pi_dwTime);return;}'),(b'CLinkBoard::GetOrgBoardObject(',b'if(pi_pObject&&pi_pObject->GetItem455())return FindOriginalTyped455(*pi_pObject->GetItem455(),FALSE);')]:
        begin,end=section(raw,signature,signature);body=raw[begin:end];at=body.index(b'{')+1;raw=raw[:begin]+body[:at]+b'\r\n\t'+statement+body[at:]+raw[end:]
    anchor=b'CObjectBoard::FrameMove();'
    if raw.count(anchor)!=1:raise ValueError('Cooldown FrameMove anchor')
    return raw.replace(anchor,anchor+b'\r\n\tProcessCooldowns455();'),True
