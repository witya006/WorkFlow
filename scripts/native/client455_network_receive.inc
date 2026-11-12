namespace {
class ReceiveLock455 {
public:
    explicit ReceiveLock455(CNetCriticalSection& section) : section_(section) { section_.Lock(); }
    ~ReceiveLock455() { section_.Unlock(); }

    ReceiveLock455(const ReceiveLock455&) = delete;
    ReceiveLock455& operator=(const ReceiveLock455&) = delete;

private:
    CNetCriticalSection& section_;
};
}

int CNetProcess::ConnectSocket455(DWORD index, sockaddr_in& address)
{
    if (!m_csRecv || index >= m_Type.m_wSocketMaxNum) return WSAEINVAL;
    ReceiveLock455 lock(m_csRecv[index]);
    return m_NetSocket.Connect(index, &address);
}

bool CNetProcess::wt_AcceptClient(DWORD* index)
{
    if (!m_csRecv) return false;
    if (m_Type.m_bServer) {
        *index = m_NetSocket.FindEmptySocket();
        if (*index == 0xffffffff) return false;
    }
    ReceiveLock455 lock(m_csRecv[*index]);
    const bool accepted = m_Type.m_bServer ? m_NetSocket.Accept_Server(*index)
                                        : m_NetSocket.Accept_Client(*index);
    if (!accepted) return false;

    m_pRecvBuffer[*index].Init();
    m_pSendBuffer[*index].Init();
    // A peer can send data or finish while the main thread is accepting the socket.
    if (!m_Type.m_bServer) m_listRecvEvent.PushNode_Back(*index);
    return true;
}

bool CNetProcess::wt_CloseClient(DWORD index)
{
    if (!m_csRecv) return false;
    ReceiveLock455 lock(m_csRecv[index]);
    if (!m_NetSocket.GetSocket(index)->m_bAccept) return false;

    m_NetSocket.CloseSocket(index);
    m_pRecvBuffer[index].Init();
    m_pSendBuffer[index].Init();
    while (m_listRecvEvent.FindNode(index)) {}
    m_listGracefulClose455.FindNode(index);
    return true;
}

void CNetProcess::RecvThread(void* context)
{
    auto& worker = *static_cast<_thread_parameter*>(context);
    auto& process = *static_cast<CNetProcess*>(worker.m_pParam);
    unsigned idle = 0;
    while (worker.m_bStart) {
        DWORD index;
        while (worker.m_bStart && process.m_listRecvEvent.PopNode_Front(&index)) {
            ReceiveLock455 lock(process.m_csRecv[index]);
            const auto* socket = process.m_NetSocket.GetSocket(index);
            if (!socket->m_bAccept) continue;

            auto& buffer = process.m_pRecvBuffer[index];
            const DWORD contiguous = buffer.m_capacity - buffer.m_dwPushPnt;
            int received = 0;
            if (!process.m_NetSocket.Recv(index, buffer.GetPushPos(), contiguous + buffer.m_extra, &received)) {
                if (received != WSAEWOULDBLOCK) {
                    process.PushCloseNode(index);
                    if (process.m_Type.m_bSvrToS)
                        process.m_LogFile[system_log].Write("recv(%lu) failed: %d", index, received);
                }
                continue;
            }
            if (received == 0) {
                if (!process.m_listGracefulClose455.IsInList(index))
                    process.m_listGracefulClose455.PushNode_Back(index);
                continue;
            }
            const auto bytes = static_cast<DWORD>(received);
            if (buffer.GetTotalPush() - buffer.GetTotalPop() + bytes > buffer.m_capacity) {
                process.m_LogFile[system_log].Write("recv(%lu) buffer full", index);
                process.PushCloseNode(index);
                continue;
            }
            if (bytes > contiguous)
                memcpy(buffer.m_sMainBuffer, buffer.m_sMainBuffer + buffer.m_capacity, bytes - contiguous);
            buffer.AddPushPos(bytes);
            if (socket->m_peerFin455 && !process.m_listRecvEvent.IsInList(index))
                process.m_listRecvEvent.PushNode_Back(index);
        }
        if (++idle > process.m_Type.m_byRecvSleepTime) {
            Sleep(1);
            idle = 0;
        }
    }
}
