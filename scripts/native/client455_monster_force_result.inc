BOOL CSFItem::CreateForce455(DWORD index, BYTE level)
{
    const auto row = RF455_GameItems().skillForce.get(CAT_FORCE, index);
    if (!row.data) return FALSE;
    Clear();
    m_forceRow455 = index;
    SetSFType(CAT_FORCE);
    SetIndex(index);
    SetLevel(level);
    char name[33] = {};
    std::memcpy(name, row.data + 112, 32);
    SetName(name);
    return TRUE;
}
