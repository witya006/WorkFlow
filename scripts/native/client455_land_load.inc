BOOL CLand::LoadLevel(char* name){
    // Target7C8600 destroys the old dynamic level before selecting the new one.
    if(!name||std::strlen(name)<4)return FALSE; // Target's invalid string domain is not accepted.
    delete m_pLevel;m_pLevel=nullptr;g_pLevel=nullptr;
    if(!_stricmp(name+std::strlen(name)-4,".ins"))return FALSE; // CLevelIns is a tracked missing source provider.
    m_pLevel=new CLevel;g_pLevel=m_pLevel;m_pLevel->LoadLevel(name);
    _GetCamera()->Create(); // Rebind the actual camera to the new BSP.
    return TRUE;
}
