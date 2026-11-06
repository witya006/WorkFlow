__declspec(noinline) BOOL CMainApp::ConnectNetwork455()
{
    // Slot284 returnsfalse in every pinned455country profile;there is no
    // connect bypass for any of the11 accepted profiles in this revision.
    auto& report=*RF455_GetConnectionReport();report=RF455ConnectionReport{};
    report.timeoutMs=RF455_ReadConnectTimeout();
    char debug[96];sprintf(debug,"RF455 Connect:start:%lu",static_cast<unsigned long>(report.timeoutMs));OutputDebugStringA(debug);
    report.rawResult=m_cNetworkMgr.ConnectToServer455(1,0);
    const auto* pack=RF455_GetNormalLanguagePack();char text[256]={};
    if(report.rawResult){
        report.outcome=RF455ConnectionOutcome::TransportError;report.detailError=report.rawResult;
        sprintf(debug,"RF455 Connect:failed:%d",report.rawResult);OutputDebugStringA(debug);
        _snprintf_s(text,sizeof(text),_TRUNCATE,pack->get(0x6be),report.rawResult);MessageBoxA(nullptr,text,nullptr,0);return FALSE;
    }
    RF455ConnectionWait wait={&m_cNetworkMgr,
        [](void*)->std::uint32_t{return timeGetTime();},
        [](void* p){static_cast<CNetworkMgr*>(p)->PumpEvents455();},
        [](void* p)->bool{return static_cast<CNetworkMgr*>(p)->IsConnectedToServer(1)!=FALSE;},
        [](void*,std::uint32_t ms){Sleep(ms);}};
    if(RF455_WaitForConnection(wait,report.timeoutMs,report.waitIterations)){
        report.outcome=RF455ConnectionOutcome::Connected;OutputDebugStringA("RF455 Connect:connected");return TRUE;
    }
    report.outcome=RF455ConnectionOutcome::Timeout;report.detailError=WSAGetLastError();
    _snprintf_s(text,sizeof(text),_TRUNCATE,pack->get(0xbfa),report.detailError);
    sprintf(debug,"RF455 Connect:timeout:%d",report.detailError);OutputDebugStringA(debug);
    ShowWindow(_GetHWND(),SW_HIDE);MessageBoxA(nullptr,text,nullptr,0);return FALSE;
}
