CNetProcess::_Receipt(bool dispatchFinalFrames)
{
    DWORD index;
    for(unsigned count=0;count<102 && m_listAcceptEvent.PopNode_Front(&index);++count){
        if(wt_AcceptClient(&index)){
            auto* socket=m_NetSocket.GetSocket(index);
            if(m_Type.m_bServer)m_pNetwork->AcceptClientCheck(m_nIndex,index,socket->m_dwSerial);
            else m_listAcceptReady.PushNode_Back(index);
        }
    }
    const auto close = [&](DWORD socketIndex) {
        const auto* socket = m_NetSocket.GetSocket(socketIndex);
        if (!socket->m_bAccept) return;
        const DWORD serial = socket->m_dwSerial;
        if (wt_CloseClient(socketIndex)) {
            m_listAcceptReady.FindNode(socketIndex);
            m_pNetwork->CloseClientCheck(m_nIndex, socketIndex, serial);
        }
    };
    for (unsigned count = 0; count < 102 && m_listCloseEvent.PopNode_Front(&index); ++count)
        close(index);
    for (unsigned count = 0; count < 102 && m_listGracefulClose455.PopNode_Front(&index); ++count) {
        const auto* socket = m_NetSocket.GetSocket(index);
        if (!socket->m_bAccept) continue;
        const DWORD serial = socket->m_dwSerial;
        if (dispatchFinalFrames && !m_listAcceptReady.IsInList(index))
            _PopRecvMsg(static_cast<WORD>(index));
        if (socket->m_dwSerial == serial) close(index);
    }
    const DWORD now=timeGetTime();
    for(unsigned count=0;count<102 && m_listAcceptReady.CopyFront(&index);++count){
        auto* socket=m_NetSocket.GetSocket(index);
        if(!RF455_AcceptDelayElapsed(now,socket->m_dwConnectTime))break;
        if(socket->m_bAccept)m_pNetwork->AcceptClientCheck(m_nIndex,index,socket->m_dwSerial);
        m_listAcceptReady.PopNode_Front(&index);
    }
}
