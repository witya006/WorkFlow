CNetProcess::_Receipt()
{
    DWORD index;
    for(unsigned count=0;count<102 && m_listAcceptEvent.PopNode_Front(&index);++count){
        if(wt_AcceptClient(&index)){
            auto* socket=m_NetSocket.GetSocket(index);
            if(m_Type.m_bServer)m_pNetwork->AcceptClientCheck(m_nIndex,index,socket->m_dwSerial);
            else m_listAcceptReady.PushNode_Back(index);
        }
    }
    for(unsigned count=0;count<102 && m_listCloseEvent.PopNode_Front(&index);++count){
        if(wt_CloseClient(index)){
            auto* socket=m_NetSocket.GetSocket(index);m_pNetwork->CloseClientCheck(m_nIndex,index,socket->m_dwSerial);
        }
    }
    const DWORD now=timeGetTime();
    for(unsigned count=0;count<102 && m_listAcceptReady.CopyFront(&index);++count){
        auto* socket=m_NetSocket.GetSocket(index);
        if(!RF455_AcceptDelayElapsed(now,socket->m_dwConnectTime))break;
        if(socket->m_bAccept)m_pNetwork->AcceptClientCheck(m_nIndex,index,socket->m_dwSerial);
        m_listAcceptReady.PopNode_Front(&index);
    }
}
