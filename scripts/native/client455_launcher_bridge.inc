CMainApp::GetDataFromLauncher( void )
{
    if(!RF455_InitializeLauncher())return FALSE;
    const auto&connection=*RF455_GetLauncherConnection();
    m_cNetworkMgr.SetServerIP(static_cast<BYTE>(connection.endpoint),connection.address);
    m_cNetworkMgr.SetServerPort(static_cast<BYTE>(connection.endpoint),connection.port);
    m_cNetworkMgr.SetID(const_cast<char*>(connection.identifier));
    if(connection.hasPassword)m_cNetworkMgr.SetPassword(const_cast<char*>(connection.password));
    if(connection.hasAccountFields){
        m_cNetworkMgr.SetAccountIndex(connection.account);
        DWORD keys[4];for(unsigned i=0;i<4;++i)keys[i]=connection.keys[i];
        m_cNetworkMgr.SetWorldServerKey(keys);
        m_cNetworkMgr.SetPremiumState455(connection.premium);
    }
    // worldIndex/personal/mode are preserved in the source-owned455
    // state until the corresponding target network/UI consumers are ported.
    return TRUE;
}
