BOOL CNetworkMgr::AccountMsg_JoinAccountRequest_cllo( void )
{
    BYTE packet[84];RF455_PackCredentials(packet,m_pID,m_pPassword);
    BYTE type[2]={21,1};const BOOL sent=SendNetMessage(0,type,packet,sizeof(packet));
    if(sent){SendRequestMsg();memset(m_pPassword,0,sizeof(m_pPassword));}
    else NetLogWrite("455 account join request failed");return sent;
}
void CNetworkMgr::AccountMsg_JoinAccountResult_locl( char * pi_pMsg )
{m_byResultOfUserRegistration=static_cast<BYTE>(pi_pMsg[0]);ReceiveResponseMsg();}
BOOL CNetworkMgr::AccountMsg_LoginAccountRequest_cllo( const char* ticket )
{
    BYTE packet[RF455LoginBytes];
    const bool ticketProfile=RF455_GetNormalNationPaths()->nation==8;
    if(!RF455_PackLogin(packet,m_account455,m_pID,m_pPassword,ticketProfile,ticket,RF455_IsTutorialAvatarStage()))return FALSE;
    BYTE type[2]={21,3};const BOOL sent=SendNetMessage(0,type,packet,sizeof(packet));
    if(sent)SendRequestMsg();else NetLogWrite("455 account login request failed");return sent;
}
void CNetworkMgr::AccountMsg_LoginAccountResult_locl( char * pi_pMsg )
{
    m_byResultOfLogin=static_cast<BYTE>(pi_pMsg[0]);memcpy(&m_dwAccountIndex,pi_pMsg+1,4);
    if(m_byResultOfLogin!=5)memset(m_pPassword,0,sizeof(m_pPassword));ReceiveResponseMsg();
}
BOOL CNetworkMgr::AccountMsg_WorldListRequest_cllo( void )
{
    BYTE packet[4]={},type[2]={21,5};const BOOL sent=SendNetMessage(0,type,packet,sizeof(packet));
    if(sent)SendRequestMsg();else NetLogWrite("455 world list request failed");return sent;
}
void CNetworkMgr::AccountMsg_WorldListResult_locl( char * pi_pMsg )
{
    WORD bytes;memcpy(&bytes,pi_pMsg+1,2);
    if(RF455_ReadWorldList(pi_pMsg,std::size_t(bytes)+3,m_pWorldServerList,MAX_WORLD_SERVER,
                          m_byResultOfRequestForWorldServerList,m_byWorldServerNum))ReceiveResponseMsg();
}
BOOL CNetworkMgr::AccountMsg_SelectWorldRequest_cllo( DWORD pi_dwIndex )
{
    const WORD index=static_cast<WORD>(pi_dwIndex);m_account455.selectedWorld=index;
    BYTE type[2]={21,7};const BOOL sent=SendNetMessage(0,type,const_cast<WORD*>(&index),sizeof(index));
    if(sent)SendRequestMsg();else NetLogWrite("455 select world request failed");return sent;
}
void CNetworkMgr::AccountMsg_SelectWorldResult_locl( char * pi_pMsg )
{
    m_byResultOfSelectWorldServer=static_cast<BYTE>(pi_pMsg[0]);
    memcpy(&m_dwServerIP[1],pi_pMsg+1,4);WORD port;memcpy(&port,pi_pMsg+5,2);m_dwServerPort[1]=port;
    memcpy(m_dwWorldServerKey,pi_pMsg+7,16);ReceiveResponseMsg();
}
BOOL CNetworkMgr::AccountMsg_PushCloseRequest_cllo( void )
{
    BYTE packet[88]={},credentials[84];RF455_PackCredentials(credentials,m_pID,m_pPassword);memcpy(packet,credentials,84);
    BYTE type[2]={21,9};const BOOL sent=SendNetMessage(0,type,packet,sizeof(packet));
    if(sent){SendRequestMsg();memset(m_pPassword,0,sizeof(m_pPassword));}
    else NetLogWrite("455 push close request failed");return sent;
}
void CNetworkMgr::AccountMsg_PushCloseResult_locl( char * pi_pMsg )
{m_byResultOfRequestForDisconnectAccount=static_cast<BYTE>(pi_pMsg[0]);ReceiveResponseMsg();}
