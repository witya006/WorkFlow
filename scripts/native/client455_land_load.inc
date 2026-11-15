BOOL CLand::LoadLevel(char* name)
{
    DiscardPreparedMap455();
    const auto prepared = PrepareLevel455(name);
    return prepared && LoadBspLevel455(name, *prepared);
}

BOOL CLand::LoadLevel(BYTE index)
{
    if (index == 0xff) index = m_byMapIndex;
    const auto prepared = TakePreparedMap455(index);
    return prepared && LoadIndexedLevel455(index, *prepared);
}

BOOL CLand::LoadTransitionLevel455(BYTE index, void (*beforeUnload)())
{
    const auto prepared = TakePreparedMap455(index);
    if (!prepared) return FALSE;
    if (beforeUnload) beforeUnload();
    return UnloadLevel() && LoadIndexedLevel455(index, *prepared);
}

BOOL CLand::LoadBspLevel455(char* name, const RF455SceneInput455& prepared)
{
    // The renderer has one set of global level materials and lightmaps.
    // Release that set before loading the replacement.
    auto* next = new CLevel;
    delete m_pLevel;
    m_pLevel = next;
    g_pLevel = m_pLevel;
    m_pLevel->LoadLevel(name, &prepared);
    if (!m_pLevel->IsLoadedBsp() || !m_pLevel->mBsp->IsLoaded()) return FALSE;
    if (auto* camera = _GetCamera()) camera->Create();
    return TRUE;
}
