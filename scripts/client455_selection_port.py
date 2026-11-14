"""Restore selected-character wire handling and the ordinary zone handoff."""

import re

from client455_trade_ore_port import patch_method, replace


def port_selection(raw,relative,native,section):
    if relative == 'userinterface/loginwindow/guiselectcharacter.h':
        raw = replace(raw, b'SetCharInfo_Money( DWORD pi_dwDalant, DWORD pi_dwGold, BYTE pi_byRaceType )',
                      b'SetCharInfo_Money(__int64 dalant, __int64 gold, BYTE race)')
        raw = replace(raw, b'\tCGUIText\t\tm_cDalantStr;\n\tCGUIText\t\tm_cGoldStr;', b'''    class CurrencyLabel : public CGUIText {
    public:
        void SetMaximumWidth(LONG width) { maximumWidth_ = width; }
        BOOL Draw() override;

    private:
        LONG maximumWidth_ = 0;
    };
    CurrencyLabel m_cDalantStr;
    CurrencyLabel m_cGoldStr;''')
        return raw, True
    if relative == 'userinterface/loginwindow/guiselectcharacter.cpp':
        raw = b'#include "client455_language.h"\n#include "client455_selection.h"\n' + raw
        raw = patch_method(raw, section, b'CGUISelectCharacter', b'ClosingDialogBox', lambda body: b'''CGUISelectCharacter::ClosingDialogBox(CGUIDialogBox* dialog){
    if(!dialog)return;
    const bool accepted=dialog->GetResultMsg()==MSG_OK;
    const bool deletion=dialog->GetUserDefinedID()==DELETE_CHAR_BOX_ID;
    // Complete the old modal's ownership before a request can open another.
    CGUIWindow::ClosingDialogBox(dialog);
    if(accepted){if(deletion)EventDeleteCharacter();else EventGameClose();}
}''')
        raw = replace(raw, b'else if( event.source == &m_cDeleteButton )',
                      b'else if (event.source == &m_cDeleteButton && RF455_SelectedCharacterSlotOccupied())')
        raw = replace(raw, b'\tm_cRCharInfoBoard.SetSize( 161, 93 );',
                      b'\tm_cRCharInfoBoard.SetSize( 161, 93 );\n'
                      b'\tm_cDalantStr.SetMaximumWidth(m_cRCharInfoBoard.m_ptSize.x - 2 * 13);\n'
                      b'\tm_cGoldStr.SetMaximumWidth(m_cRCharInfoBoard.m_ptSize.x - 2 * 13);')
        raw = re.sub(rb'(m_c(?:Prev|Next|Create|Delete|Exit)Button)\.SetLabel\( "[^"\n]*" \);',
                     lambda match: match[1] + b'.SetLabel(const_cast<char*>(RF455_GetNormalLanguagePack()->get(' + {
                         b'm_cPrevButton': b'0x4b1', b'm_cNextButton': b'0x4b2', b'm_cCreateButton': b'0x48f',
                         b'm_cDeleteButton': b'0x4b3', b'm_cExitButton': b'0x4b4',
                     }[match[1]] + b')));', raw)
        if raw.count(b'.SetLabel(const_cast<char*>(RF455_GetNormalLanguagePack()->get(') != 5:
            raise ValueError('Selection button labels changed')
        for marker, index, count in [(b'0, DLG_STYLE_OK_CANCEL', b'0x4b6', 2),
                                     (b'DELETE_CHAR_BOX_ID, DLG_STYLE_OK_CANCEL', b'0x4b5', 2)]:
            pattern = rb'(_GUIMessageBox\( this, )"[^"\n]*",\s*0xb0ffffff,\s*' + marker
            raw, actual = re.subn(pattern, rb'\g<1>const_cast<char*>(RF455_GetNormalLanguagePack()->get(' +
                                  index + b')), 0xb0ffffff, ' + marker, raw)
            if actual != count:
                raise ValueError('Selection confirmation text changed')
        first, _ = section(raw, b'CGUISelectCharacter::SetCharInfo_Name(', b'CGUISelectCharacter::SetCharInfo_Name(')
        _, last = section(raw, b'CGUISelectCharacter::SetCharInfo_Money(', b'CGUISelectCharacter::SetCharInfo_Money(')
        begin = raw.rfind(b'\nvoid', 0, first) + 1
        return raw[:begin] + (native / 'client455_selection_text.inc').read_bytes() + raw[last:], True
    if relative=='network/cnetworkmgr.h':
        old=b'void\tSystemMsg_SelCharResult_zone( char * pi_pMsg );'
        if raw.count(old)!=1:raise ValueError('Selection receiver API anchor')
        return b'#include "client455_selection.h"\n'+raw.replace(old,old+b'''
public:
    bool DispatchSelectedCharacter455(char*,std::size_t);
    bool DispatchDeletedCharacter455(char*,std::size_t);
    BYTE TakeDeletedCharacterSlot455(){const BYTE slot=m_deletedSlot455;m_deletedSlot455=255;return slot;}
protected:
    BYTE m_pendingDeleteSlot455=255,m_deletedSlot455=255;
'''),True
    if relative=='network/cnetworkmgr_masterservermsg.cpp':
        bridge=(native/'client455_selection.inc').read_bytes()
        for name in [b'SystemMsg_SelCharRequest_zone',b'SystemMsg_SelCharResult_zone',
                     b'SystemMsg_DelCharRequest_zone',b'SystemMsg_DelCharResult_zone']:
            signature=b'CNetworkMgr::'+name+b'(';first,last=section(raw,signature,signature);a,b=section(bridge,signature,signature)
            raw=raw[:first]+bridge[a:b]+raw[last:]
        # Append only the two dispatchers; request/result bodies replaced above.
        for name in [b'DispatchSelectedCharacter455',b'DispatchDeletedCharacter455']:
            signature=b'CNetworkMgr::'+name+b'(';a,b=section(bridge,signature,signature)
            raw+=b'\nbool '+bridge[a:b]+b'\n'
        return b'#include <stdexcept>\n'+raw,True
    if relative=='network/cnetworkmgr.cpp':
        signature=b'CNetworkMgr::AnalysisServerPacket(';first,last=section(raw,signature,signature);body=raw[first:last];at=body.index(b'{')+1
        body=body[:at]+b'''
    if(pMsgHeader&&pMsgHeader->m_wSize>=4&&pMsgHeader->m_byType[0]==1){
        if(pMsgHeader->m_byType[1]==15)return DispatchSelectedCharacter455(pi_pMsg,pMsgHeader->m_wSize-4);
        if(pMsgHeader->m_byType[1]==13)return DispatchDeletedCharacter455(pi_pMsg,pMsgHeader->m_wSize-4);
    }
'''+body[at:]
        return raw[:first]+body+raw[last:],True
    if relative=='network/protocol/pt_zone_client.h':
        for old,new in [(b'#define sel_char_request_zone 13',b'#define sel_char_request_zone 14'),(b'#define sel_char_result_zone 14',b'#define sel_char_result_zone 15'),
                        (b'#define del_char_request_zone 11',b'#define del_char_request_zone 12'),(b'#define del_char_result_zone 12',b'#define del_char_result_zone 13')]:
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
        first,last=section(raw,b'void EventDeleteCharacter()',b'void EventDeleteCharacter()')
        raw=raw[:first]+b'''void EventDeleteCharacter(){
    if(g_LoginState==LGS_CHARACTERLOBBY&&RF455_SelectedCharacterSlotOccupied())
        _GetNetworkMgr()->SystemMsg_DelCharRequest_zone(BYTE(m_Course));
}'''+raw[last:]
        for callback, index in [(b'EventCreateCharacter()', b'0x556'), (b'EventJoinGameFunc()', b'0x558')]:
            first, last = section(raw, b'void '+callback, b'void '+callback)
            body, count = re.subn(rb'_GUIMessageBox\( NULL, "[^"\n]*",MSGBOXALPHA\);',
                                  b'_GUIMessageBox(nullptr, const_cast<char*>(RF455_GetNormalLanguagePack()->get(' +
                                  index + b')), MSGBOXALPHA);', raw[first:last], count=1)
            if count != 1:
                raise ValueError('Selection slot message changed')
            if callback == b'EventCreateCharacter()':
                body, count = re.subn(rb'(m_LoadDefaultStart = true;\s*)_GUIMessageBox\( NULL, "[^"\n]*",MSGBOXALPHA\);',
                                      rb'\g<1>_GUIMessageBox(nullptr, const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x557)), MSGBOXALPHA);', body)
                if count != 1:
                    raise ValueError('Character creation wait message changed')
            raw = raw[:first] + body + raw[last:]
        signature=b'NetworkInput(';first,last=section(raw,signature,signature);body=raw[first:last]
        select_start = body.index(b'\tswitch (res = _GetNetworkMgr()->GetResultOfCharacterSelect())')
        select_end = body.index(b'\tswitch (res = _GetNetworkMgr()->GetResultOfCharacterDelete())', select_start)
        selection = body[select_start:select_end]
        selection, count = re.subn(
            rb'\t\tdefault:\s*_GUIMessageBox\( NULL, "[^"\n]*",MSGBOXALPHA\);\s*break;',
            b'''        default: {
            // 455 rejection returns to the occupied-slot screen for another attempt.
            unsigned message = 521;
            switch (res) {
            case 72: message = 2779; break;
            case 74: message = 3732; break;
            case 76: message = 3816; break;
            }
            _GUIMessageBox(nullptr, const_cast<char*>(RF455_GetNormalLanguagePack()->get(message)),
                           MSGBOXALPHA, 0, DLG_STYLE_OK);
            g_LoginState = LGS_CHARACTERLOBBY;
            break;
        }''', selection)
        if count != 1:
            raise ValueError('Selected-character rejection branch changed')
        body = body[:select_start] + selection + body[select_end:]
        delete_start=body.index(b'\tswitch (res = _GetNetworkMgr()->GetResultOfCharacterDelete())')
        delete_end=body.index(b'\tswitch ( res = _GetNetworkMgr()->GetResultOfUserInfo())',delete_start)
        deletion=body[delete_start:delete_end]
        messages=re.findall(rb'_GUIMessageBox\([^;]+;',deletion)
        if len(messages)!=2:raise ValueError('Character deletion messages changed')
        deletion=b'''
    switch(res=_GetNetworkMgr()->GetResultOfCharacterDelete()){
    case CHAR_DELETE_NOT_RECIVED:break;
    case CHAR_DELETE_SUCCESS:{
        const unsigned slot=_GetNetworkMgr()->TakeDeletedCharacterSlot455();
        if(slot>=3)break;
        // Retire this roster slot before releasing shared item references. This
        // is preview teardown, not in-world unequip with skill/HUD callbacks.
        m_HaveCharacter[slot]=FALSE;
        RF455_InvalidateLobbyShadows(true);
        if(g_pAvatarDummy){
            auto* actor=_GetAvatarDummy(slot);actor->SetIndex(ID_INVALID);
            for(unsigned i=0;i<12;++i)if(auto* item=actor->GetEquipItem455(BYTE(i)))item->Clear();
            for(unsigned i=0;i<6;++i)if(auto* item=actor->GetDefaultItem455(BYTE(i)))item->Clear();
            actor->RefreshEquipmentConditions455();
        }
        if(static_cast<unsigned>(m_Course)>=3)m_Course=static_cast<COURSE>(slot);
        g_LoginState=LGS_CHARACTERLOBBY;
        if(static_cast<unsigned>(m_Course)==slot)SetCharacterBottom();
        _GUIMessageBox(nullptr,const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x20a)));
        break;
    }
    default:
        if(static_cast<unsigned>(m_Course)>=3)m_Course=static_cast<COURSE>(0);
        g_LoginState=LGS_CHARACTERLOBBY;
        _GUIMessageBox(nullptr,const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x20b)),MSGBOXALPHA);
        break;
    }
'''
        body=body[:delete_start]+deletion+body[delete_end:]
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
        fragment=replace(fragment, b'UI_SetMoveWindow( SELECT_CHAR_WIN, FALSE );',
                         b'UI_SetMoveWindow( SELECT_CHAR_WIN, FALSE );\n'
                         b'\t\t\t\tRF455_ObserveProtocol("selection-fade-start", 0, 0, 0);')
        body=body[:begin]+fragment+body[end:];raw=raw[:first]+body+raw[last:]
        def finish_after_fade(body):
            body = replace(body, b'\t\t\t_GetNetworkMgr()->Connect( GST_ZONE );',
                           b'\t\t\tRF455_ObserveProtocol("selection-zone-connect", timeGetTime() - m_MP3ElapseTime, 0, 0);\n'
                           b'\t\t\t_GetNetworkMgr()->Connect( GST_ZONE );')
            body = replace(body, b'if( ( _GetNetworkMgr()->IsConnectedToServer( GST_ZONE ) ) )',
                           b'if (g_LoginState == LGS_EXIT && m_bRequestConnect &&\n'
                           b'        _GetNetworkMgr()->IsConnectedToServer(GST_ZONE))')
            return replace(body, b'\t\tm_dwInputFocus = GPL_INPUT_END;\n\t\tm_bExit = TRUE;',
                           b'\t\tm_dwInputFocus = GPL_INPUT_END;\n\t\tSetNextStage455(GPI_MAIN_GAME);\n'
                           b'\t\tRequestStageExit455();\n'
                           b'\t\tRF455_ObserveProtocol("selection-world-handoff", timeGetTime() - m_MP3ElapseTime, 0, 0);')

        raw = patch_method(raw, section, b'CGP_LogIn', b'InputProcess', finish_after_fade)
        raw += b'''
unsigned RF455_SelectedCharacterSlot(){return static_cast<unsigned>(m_Course);}
bool RF455_SelectedCharacterSlotOccupied(){const unsigned slot=RF455_SelectedCharacterSlot();return slot<3&&g_pAvatarDummy&&m_HaveCharacter[slot]!=FALSE;}
'''
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
