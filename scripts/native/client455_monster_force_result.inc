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

DWORD CSFItem::GetDTCode()
{
    if (m_pData) return m_pData->dwDTCode;
    if (!HasForceRow455()) return ID_INVALID;
    const auto row = RF455_GameItems().skillForce.get(CAT_FORCE, m_forceRow455);
    DWORD code = ID_INVALID;
    if (row.size >= 8) std::memcpy(&code, row.data + 4, sizeof code);
    return code;
}

BYTE CSFItem::GetRangeTypeForEffect()
{
    if (m_pData) return m_pData->byRangeType_For_Effect;
    if (!HasForceRow455()) return 0xff;
    const auto row = RF455_GameItems().skillForce.get(CAT_FORCE, m_forceRow455);
    constexpr std::size_t effectRangeOffset = 1036;
    return row.size > effectRangeOffset ? row.data[effectRangeOffset] : 0xff;
}
