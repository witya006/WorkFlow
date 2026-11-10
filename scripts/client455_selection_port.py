"""Restore selected-character wire consumer;full UI/state handoff is separate."""


def port_selection(raw,relative,native,section):
    if relative=='network/cnetworkmgr.h':
        old=b'void\tSystemMsg_SelCharResult_zone( char * pi_pMsg );'
        if raw.count(old)!=1:raise ValueError('Selection receiver API anchor')
        return b'#include "client455_selection.h"\n'+raw.replace(old,old+b'\n\tbool DispatchSelectedCharacter455(char*,std::size_t);'),True
    if relative=='network/cnetworkmgr_masterservermsg.cpp':
        bridge=(native/'client455_selection.inc').read_bytes()
        for name in [b'SystemMsg_SelCharRequest_zone',b'SystemMsg_SelCharResult_zone']:
            signature=b'CNetworkMgr::'+name+b'(';first,last=section(raw,signature,signature);a,b=section(bridge,signature,signature)
            raw=raw[:first]+bridge[a:b]+raw[last:]
        raw+=b'\n'+bridge[bridge.index(b'bool CNetworkMgr::DispatchSelectedCharacter455'):]
        return b'#include <stdexcept>\n'+raw,True
    if relative=='network/cnetworkmgr.cpp':
        signature=b'CNetworkMgr::AnalysisServerPacket(';first,last=section(raw,signature,signature);body=raw[first:last];at=body.index(b'{')+1
        body=body[:at]+b'\n\tif(pMsgHeader&&pMsgHeader->m_wSize>=4&&pMsgHeader->m_byType[0]==1&&pMsgHeader->m_byType[1]==15)return DispatchSelectedCharacter455(pi_pMsg,pMsgHeader->m_wSize-4);\n'+body[at:]
        return raw[:first]+body+raw[last:],True
    if relative=='network/protocol/pt_zone_client.h':
        for old,new in [(b'#define sel_char_request_zone 13',b'#define sel_char_request_zone 14'),(b'#define sel_char_result_zone 14',b'#define sel_char_result_zone 15')]:
            if raw.count(old)!=1:raise ValueError('Selection opcode declaration anchor')
            raw=raw.replace(old,new)
        first=raw.index(b'struct _sel_char_result_zone {');last=raw.index(b'\n};',first)+3
        raw=raw[:first]+b'''struct _sel_char_result_zone {
    WORD wRetCode;DWORD dwWorldSerial;
    __int64 nDalant,nGold;
    int size(){return sizeof(*this);}
};'''+raw[last:]
        return raw,True
    if relative=='gameprogress/cgp_login.cpp':
        signature=b'NetworkInput(';first,last=section(raw,signature,signature);body=raw[first:last]
        begin=body.index(b'case MOVEOUT_FROM_SERVER_SUCCESS:');end=body.index(b'\n\t\t\tbreak;',begin)
        fragment=body[begin:end]
        old=b'_GetAvatar()->SetDTIndex( _GetAvatarDummy(m_Course)->GetDTIndex() );'
        if fragment.count(old)!=1:raise ValueError('Selection Avatar skip flag anchor')
        fragment=fragment.replace(old,old+b'\n\t\t\t\t_GetAvatar()->SetSkipTutorial455(_GetAvatarDummy(m_Course)->GetSkipTutorial455());')
        old=b'for( i = 0; i < MAX_DEFAULT_PART; ++i )'
        if fragment.count(old)!=1:raise ValueError('Selection six defaults anchor')
        fragment=fragment.replace(old,b'for( i = 0; i < 6; ++i )')
        old=b'_GetAvatar()->SetDefaultItem( i, _GetAvatarDummy(m_Course)->GetDefaultItem( i ) );'
        if fragment.count(old)!=1:raise ValueError('Selection typed default copy anchor')
        fragment=fragment.replace(old,b'_GetAvatar()->SetDefaultItem455(BYTE(i),_GetAvatarDummy(m_Course)->GetDefaultItem455(BYTE(i)));')
        old=b'for( i = 0; i < MAX_EQUIP_PART + 1; ++i )'
        if fragment.count(old)!=1:raise ValueError('Selection eleven equipment anchor')
        fragment=fragment.replace(old,b'for( i = 0; i < 11; ++i )')
        old=b'_GetAvatar()->PutOnEquipment( _GetAvatarDummy(m_Course)->GetEquipItem( i ) );'
        if fragment.count(old)!=1:raise ValueError('Selection typed worn copy anchor')
        fragment=fragment.replace(old,b'_GetAvatar()->PutOnEquipment455(_GetAvatarDummy(m_Course)->GetEquipItem455(BYTE(i)),true);')
        body=body[:begin]+fragment+body[end:];raw=raw[:first]+body+raw[last:]
        raw+=b'\nunsigned RF455_SelectedCharacterSlot(){return static_cast<unsigned>(m_Course);}\n'
        return raw,True
    if relative=='character/avatar/cavatar.h':
        old=b'BOOL\t\tSetDefaultItem( BYTE pi_byPartType, DWORD pi_dwIndex );'
        if raw.count(old)!=1:raise ValueError('Selection default transfer API anchor')
        return raw.replace(old,old+b'\n\tBOOL SetDefaultItem455(BYTE part,RF455EquipmentObject* source);'),True
    if relative=='character/avatar/cavatar_etc.cpp':
        raw+=b'''\nBOOL CAvatar::SetDefaultItem455(BYTE part,RF455EquipmentObject* source){
    if(part>=6||!source)return FALSE;
    m_defaultItems455[part].CopyRetainedState455(*source);return TRUE;
}\n'''
        return raw,True
    return raw,False
