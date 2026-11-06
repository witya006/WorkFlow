CNetProcess::LoadSendMsg(DWORD dwClientIndex,BYTE* pbyType,char* szMsg,WORD nLen)
{
    if(dwClientIndex>=m_Type.m_wSocketMaxNum||!pbyType)return FALSE;
    auto* socket=m_NetSocket.GetSocket(dwClientIndex);if(!socket->m_bAccept)return FALSE;
    auto& buffer=m_pSendBuffer[dwClientIndex];std::size_t size=0;WORD type;memcpy(&type,pbyType,2);
    if(!m_codec455.encode(type,szMsg,nLen,m_encoded455,sizeof(m_encoded455),size))return FALSE;
    if(buffer.GetTotalPush()-buffer.GetTotalPop()+size>buffer.m_capacity){if(!m_Type.m_bSvrToS)PushCloseNode(dwClientIndex);return FALSE;}
    const DWORD at=buffer.m_dwPushPnt;memcpy(buffer.m_sMainBuffer+at,m_encoded455,size);
    const DWORD left=buffer.m_capacity-at;if(left<size)memcpy(buffer.m_sMainBuffer,buffer.m_sMainBuffer+buffer.m_capacity,size-left);
    buffer.AddPushPos(static_cast<DWORD>(size));return TRUE;
}
