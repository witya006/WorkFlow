void CNetProcess::NetEventThread(void* context)
{
    auto& worker = *static_cast<_thread_parameter*>(context);
    auto& process = *static_cast<CNetProcess*>(worker.m_pParam);
    const DWORD first = worker.m_nIndex * event_per_therad;
    const DWORD remaining = process.m_Type.m_wSocketMaxNum - first;
    const DWORD count = remaining < event_per_therad ? remaining : event_per_therad;
    auto* events = process.m_NetSocket.m_Event + first;

    while (worker.m_bStart) {
        const DWORD wait = WSAWaitForMultipleEvents(count, events, FALSE, 100, FALSE);
        if (!worker.m_bStart) break;
        if (wait == WSA_WAIT_TIMEOUT) continue;
        if (wait - WSA_WAIT_EVENT_0 >= count) {
            Sleep(1);
            continue;
        }

        const DWORD eventIndex = wait - WSA_WAIT_EVENT_0;
        const DWORD socketIndex = first + eventIndex;
        const SOCKET socket = process.m_NetSocket.GetSocket(socketIndex)->m_Socket;
        WSANETWORKEVENTS pending{};
        // Winsock clears the event and its recorded notifications together.
        if (WSAEnumNetworkEvents(socket, events[eventIndex], &pending) == SOCKET_ERROR) {
            Sleep(1);
            continue;
        }
        if ((pending.lNetworkEvents & FD_CONNECT) && !pending.iErrorCode[FD_CONNECT_BIT])
            process.m_listAcceptEvent.PushNode_Back(socketIndex);
        if ((pending.lNetworkEvents & FD_READ) && !pending.iErrorCode[FD_READ_BIT])
            process.m_listRecvEvent.PushNode_Back(socketIndex);
        if (pending.lNetworkEvents & FD_CLOSE)
            process.m_listCloseEvent.PushNode_Back(socketIndex);
    }
}
