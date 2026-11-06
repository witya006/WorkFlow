_NET_TYPE_PARAM typeParam[2];
for(unsigned i=0;i<2;++i) {
    typeParam[i].m_bSendThread=TRUE; // 455 always starts its send worker
    typeParam[i].m_bRecvLogFile=FALSE;
    typeParam[i].m_bSendLogFile=FALSE;
    typeParam[i].m_bServer=FALSE;
    typeParam[i].m_bSystemLogFile=TRUE;
    typeParam[i].m_byProtocolID=protocol_tcp;
    typeParam[i].m_byRecvThreadNum=1;
    typeParam[i].m_wSocketMaxNum=1;
    typeParam[i].m_dwIPCheckTerm=120000;
    typeParam[i].m_dwSocketRecycleTerm=0;
    typeParam[i].m_dwRealSendCheckTerm=0;
    typeParam[i].m_dwKeyCheckTerm=120000;
    typeParam[i].m_byRecvSleepTime=1;
    typeParam[i].m_bySendSleepTime=1;
    typeParam[i].m_dwProcessMsgNumPerLoop=0xffffffff;
    sprintf(typeParam[i].m_szModuleName,"RF_CLIENT");
}
const BOOL transportCreated=SetNetSystem(2,typeParam,"RF_CLIENT");
m_Process[0].m_codec455.initializeDefault(true);
m_Process[1].m_codec455.configured=false;
m_Process[1].m_codec455.enabled=false;
