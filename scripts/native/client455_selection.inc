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
