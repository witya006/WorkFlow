BOOL CMainApp::CreateNetworkMgr455( void )
{
    // Existing handlers/transport remain explicitly partial until their455
    // replacements are recovered;this performs real network initialization.
    const BOOL result=m_cNetworkMgr.Create();char message[64];
    sprintf(message,"RF455 Network:Create:%d",result);OutputDebugStringA(message);return result;
}
