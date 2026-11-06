int CNetworkMgr::ConnectToServer455(BYTE endpoint,BYTE process)
{
    RF455NetworkState state;
    for(unsigned i=0;i<6;++i)state.active[i]=m_activeServer455[i];
    for(unsigned i=0;i<4;++i)state.connected[i]=m_bIsConnectedToServer[i];
    struct Context{CNetworkMgr*self;RF455NetworkState*state;} context={this,&state};
    const auto transport=[](void*pointer,unsigned index,std::uint32_t address,std::uint16_t port)->int{
        auto&c=*static_cast<Context*>(pointer);return c.self->ConnectRaw455(index,0,address,port);
    };
    const auto accepted=[](void*pointer){
        auto&c=*static_cast<Context*>(pointer);
        // 455's direct branch calls the virtual callback with process0 even
        // when a different requested process was written;do not silently fix it.
        if(c.state->active[0]>=MAX_GAME_SERVER)return; // target's unsafe callback domain is not accepted
        for(unsigned i=0;i<6;++i)c.self->m_activeServer455[i]=c.state->active[i];
        c.self->m_nActiveServerID=static_cast<char>(c.state->active[0]);
        c.self->AcceptClientCheck(0,0,0);
        for(unsigned i=0;i<4;++i)c.state->connected[i]=c.self->m_bIsConnectedToServer[i];
    };
    const int result=RF455_AttemptConnect(state,endpoint,process,_GetMainApp()->IsRequestLogout()!=FALSE,
        endpoint<MAX_GAME_SERVER?GetServerIP(endpoint):0,endpoint<MAX_GAME_SERVER?static_cast<WORD>(GetServerPort(endpoint)):0,transport,accepted,&context);
    for(unsigned i=0;i<6;++i)m_activeServer455[i]=state.active[i];
    for(unsigned i=0;i<4;++i)m_bIsConnectedToServer[i]=state.connected[i];
    m_nActiveServerID=static_cast<char>(state.active[0]);return result;
}
