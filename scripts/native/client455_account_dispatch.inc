void CNetworkMgr::SendRequestMsg( void )
{
    m_bIsSendMsg=TRUE;m_dwSendMsgTime=timeGetTime();
    if((m_activeServer455[0]!=2||m_account455.zoneRequestMode==4)&&!_IsOpenedDialogBox(nullptr,0xf100))
        _GUIMessageBox(nullptr,const_cast<char*>(RF455_GetNormalLanguagePack()->get(0x305)),0xb0ffffff,0xf100,5);
}
void CNetworkMgr::ReceiveResponseMsg( void )
{
    m_bIsSendMsg=FALSE;m_dwSendMsgTime=0;
    if((m_activeServer455[0]!=2||m_account455.zoneRequestMode!=-1)&&_IsOpenedDialogBox(nullptr,0xf100))
        _CloseDialogBox(nullptr,0xf100);
}
BOOL CNetworkMgr::AccountMsg_CryptoSeedRequest455()
{
    BYTE type[2]={21,12};const BOOL sent=SendNetMessage(0,type,nullptr,0);
    if(sent)SendRequestMsg();else NetLogWrite("455 account seed request failed");return sent;
}
bool CNetworkMgr::DispatchAccount455(BYTE opcode,char* packet,std::size_t size)
{
    // All reads are bounded by the decoded frame length at the normal dispatcher.
    if(!packet&&size)return false;
    switch(opcode){
    case 2:if(size<1)return false;AccountMsg_JoinAccountResult_locl(packet);return true;
    case 4:if(size<50)return false;AccountMsg_LoginAccountResult_locl(packet);return true;
    case 6:
        if(!RF455_ReadWorldList(packet,size,m_pWorldServerList,MAX_WORLD_SERVER,
                               m_byResultOfRequestForWorldServerList,m_byWorldServerNum))return false;
        ReceiveResponseMsg();return true;
    case 8:if(size<24)return false;AccountMsg_SelectWorldResult_locl(packet);return true;
    case 10:if(size<1)return false;AccountMsg_PushCloseResult_locl(packet);return true;
    case 11:
        // Existing shutdown/UI remains legacy;track separately from wire recovery.
        if(size<2)return false;AccountMsg_ServerNotifyInform_locl(packet);return true;
    case 13:
        if(!RF455_ReadAccountSeed(m_account455,packet,size))return false;
        ReceiveResponseMsg();return true;
    default:return false;
    }
}
