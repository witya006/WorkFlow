BOOL CNetworkMgr::SystemMsg_EnterWorldRequest_zone( void )
{
    BYTE packet[RF455WorldEntryRequestBytes],type[2]={1,1};
    const std::uint32_t keys[4]={m_dwWorldServerKey[0],m_dwWorldServerKey[1],m_dwWorldServerKey[2],m_dwWorldServerKey[3]};
    RF455_PackWorldEntry(packet,m_dwAccountIndex,keys,!_IsWindowed());
    m_bIsRequestClose=TRUE; // Target435992 is also written by Close562880.
    const BOOL sent=SendNetMessage(0,type,packet,sizeof(packet));
    if(sent)SendRequestMsg();else NetLogWrite("455 world entry request failed");return sent;
}

void CNetworkMgr::SystemMsg_EnterWorldResult_zone( char* packet )
{
    RF455WorldEntry decoded;
    if(!RF455_ReadWorldEntry(packet,RF455WorldEntryResponseBytes,decoded))return;
    RF455_ObserveProtocol("world-result",decoded.result,0,0);
    const BYTE kind=decoded.kind;decoded.kind=m_worldEntry455.kind;
    m_worldEntry455=decoded;
    m_byResultOfEnterTheWorldServer=decoded.result;m_byAvatarGrade=decoded.grade;
    m_movement455.predictLocally = true;
    ReceiveResponseMsg();
    m_worldEntry455.kind=kind; // Target stores kind after the response/dialog callback.
}

bool CNetworkMgr::DispatchWorldEntry455(char* packet,std::size_t bytes)
{
    if(!packet||bytes<RF455WorldEntryResponseBytes)return false;
    SystemMsg_EnterWorldResult_zone(packet);return true;
}
