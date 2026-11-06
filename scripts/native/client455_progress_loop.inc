CGameProgress::MainLoop( BOOL pi_bIsActive )
{
    // RVA138FF0 has no active-window branch at the stage-base level.
    // Keep the owned source API while migrating its derived consumers together.
    InputProcess();
    if(m_bExit)return TRUE;
    FrameMove();
    Render();
    g_Particle.ResetParticleCount();
    return FALSE;
}
