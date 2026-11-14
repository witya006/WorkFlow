BOOL CNetworkMgr::SystemMsg_SelCharRequest_zone(BYTE slot){
    BYTE type[2]={1,14};const BOOL sent=SendNetMessage(0,type,&slot,1);
    if(sent)SendRequestMsg();else NetLogWrite("455 select character request failed");
    return sent;
}

void CNetworkMgr::SystemMsg_SelCharResult_zone(char* packet){
    RF455CharacterSelection decoded;
    if(!RF455_ReadCharacterSelection(packet,RF455CharacterSelectionBytes,decoded))return;
    m_byResultOfCharacterSelect=static_cast<BYTE>(decoded.result);
    m_dwAvatarIndex=decoded.serial;
    auto* actor=_GetAvatar();
    if(actor->GetSkipTutorial455()!=1){
        const unsigned slot=RF455_SelectedCharacterSlot();
        if(slot>2)throw std::logic_error("455 selected character slot outside observed domain");
        actor=_GetAvatarDummy(slot);
    }
    actor->SetDalant(decoded.dalant);actor->SetGold(decoded.gold);
    ReceiveResponseMsg();
    RF455_ObserveProtocol("select-result",decoded.result,0,0);
}

bool CNetworkMgr::DispatchSelectedCharacter455(char* packet,std::size_t bytes){
    if(!packet||bytes<RF455CharacterSelectionBytes)return false;
    SystemMsg_SelCharResult_zone(packet);return true;
}

BOOL CNetworkMgr::SystemMsg_DelCharRequest_zone(BYTE slot){
    if(slot>=3||m_pendingDeleteSlot455!=255||IsSendRequestMsg())return FALSE;
    BYTE type[2]={1,12};const BOOL sent=SendNetMessage(0,type,&slot,1);
    if(sent){
        m_pendingDeleteSlot455=slot;m_deletedSlot455=255;
        m_byResultOfCharacterDelete=CHAR_DELETE_NOT_RECIVED;
        SendRequestMsg();
    }else NetLogWrite("455 delete character request failed");
    return sent;
}

void CNetworkMgr::SystemMsg_DelCharResult_zone(char* packet){
    RF455CharacterDeletion reply;
    if(!RF455_ReadCharacterDeletion(packet,2,reply)||reply.slot!=m_pendingDeleteSlot455)return;
    m_byResultOfCharacterDelete=reply.result;
    m_deletedSlot455=reply.result==CHAR_DELETE_SUCCESS?reply.slot:255;
    m_pendingDeleteSlot455=255;
    ReceiveResponseMsg();
    RF455_ObserveProtocol("delete-result",reply.result,reply.slot,0);
}

bool CNetworkMgr::DispatchDeletedCharacter455(char* packet,std::size_t bytes){
    RF455CharacterDeletion reply;
    if(!RF455_ReadCharacterDeletion(packet,bytes,reply))return false;
    // A delayed/duplicate reply must not clear another outstanding request.
    if(reply.slot==m_pendingDeleteSlot455)SystemMsg_DelCharResult_zone(packet);
    return true;
}
