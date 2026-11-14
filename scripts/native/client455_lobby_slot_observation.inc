// Opt-in read-only camera sweep in the full, server-connected client. No roster
// mutation, reference camera, synthetic models or hidden UI in this check.
void RF455_ObserveLobbySlots(){
    static const bool enabled=[] {char value[8]{};return GetEnvironmentVariableA("RF455_LOBBY_INSPECT_SLOTS",value,sizeof(value))&&value[0]=='1';}();
    static unsigned completed=0;static DWORD settled=0;
    if(!enabled||completed>=3)return;
    if(g_LoginState!=LGS_CHARACTERLOBBY||m_CameraAni||!m_uiSelectCharacter.IsShow()||lobbyMenu455.IsShow()){settled=0;return;}
    const DWORD now=GetTickCount();if(!settled){settled=now;return;}if(now-settled<1400)return;
    const unsigned slot=static_cast<unsigned>(m_Course);if(slot>=3)return;
    char filename[64];std::snprintf(filename,sizeof(filename),"lobby-slot-%u.png",slot);
    D3DSURFACE_DESC description{};if(FAILED(RF455_SaveLoginBackbuffer(filename,description)))return;
    std::snprintf(filename,sizeof(filename),"lobby-slot-%u.json",slot);
    const auto shadow=RF455_GetLobbyShadowTelemetry();
    if(FILE* file=std::fopen(filename,"wb")){
        std::fprintf(file,"{\"slot\":%u,\"occupied\":%s,\"width\":%u,\"height\":%u,\"shadow_bsp_draws\":%u,\"shadow_actor_draws\":%u,\"shadow_errors\":%llu,\"full_client\":true}\n",
            slot,m_HaveCharacter[slot]?"true":"false",description.Width,description.Height,shadow.bspDraws,shadow.actorDraws,shadow.errors);
        std::fclose(file);
    }
    ++completed;settled=0;if(completed<3)EventNextButton();
}
