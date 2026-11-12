int CNetWorking::ConnectRaw455(DWORD process,DWORD socketIndex,DWORD address,WORD port)
{
    if(process>=m_dwUseProcessNum)return WSAEINVAL;
    sockaddr_in target={};target.sin_family=AF_INET;target.sin_port=htons(port);target.sin_addr.S_un.S_addr=address;
    return m_Process[process].ConnectSocket455(socketIndex,target);
}
bool CNetWorking::Connect(DWORD process,DWORD socketIndex,DWORD address,WORD port)
{
    return ConnectRaw455(process,socketIndex,address,port)==0;
}
