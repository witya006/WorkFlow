BOOL CLand::LoadLevel(char* name)
{
    return CanReadLevel455(name) && LoadBspLevel455(name);
}

BOOL CLand::LoadBspLevel455(char* name)
{
    // The renderer has one set of global level materials and lightmaps.
    // Release that set before loading the replacement.
    auto* next = new CLevel;
    delete m_pLevel;
    m_pLevel = next;
    g_pLevel = m_pLevel;
    m_pLevel->LoadLevel(name);
    if (!m_pLevel->IsLoadedBsp() || !m_pLevel->mBsp->IsLoaded()) return FALSE;
    if (auto* camera = _GetCamera()) camera->Create();
    return TRUE;
}
