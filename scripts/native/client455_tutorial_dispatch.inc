BOOL CNetworkMgr::DispatchTutorial455(DWORD client,BYTE* type,void* packet,int size){
    switch(RF455_TutorialPacketRoute(type[0],type[1])){
    case RF455TutorialPacketRoute::Ignored:return TRUE;
    case RF455TutorialPacketRoute::Transport:
        // Target564520 calls transport directly:it retains the current codec mode.
        return m_pProcess[0]->LoadSendMsg(client,type,static_cast<char*>(packet),size);
    case RF455TutorialPacketRoute::ClientHandler:
        NetLogWrite("455 Tutorial client handler not restored:group=%u opcode=%u",unsigned(type[0]),unsigned(type[1]));
        return FALSE; // Explicit missing local world/Avatar/feedback provider,not a successful no-op.
    }
    return FALSE;
}
