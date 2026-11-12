BOOL CSFItem::CreateForce455(DWORD index, BYTE level)
{
    return CreateTyped455(CAT_FORCE, index, level);
}

BOOL CSFItem::CreateSkill455(DWORD index, BYTE level)
{
    return CreateTyped455(CAT_SKILL, index, level);
}

BOOL CSFItem::CreateTyped455(BYTE type, DWORD index, BYTE level)
{
    const auto row = RF455_GameItems().skillForce.get(type, index);
    if (row.size < 144) return FALSE;
    Clear();
    m_typedSFRow455 = index;
    SetSFType(type);
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
    if (m_typedSFRow455 == ID_INVALID) return ID_INVALID;
    const auto row = RF455_GameItems().skillForce.get(m_bySFType, m_typedSFRow455);
    DWORD code = ID_INVALID;
    if (row.size >= 8) std::memcpy(&code, row.data + 4, sizeof code);
    return code;
}

BYTE CSFItem::GetRangeTypeForEffect()
{
    if (m_pData) return m_pData->byRangeType_For_Effect;
    if (m_typedSFRow455 == ID_INVALID) return 0xff;
    const auto row = RF455_GameItems().skillForce.get(m_bySFType, m_typedSFRow455);
    constexpr std::size_t effectRangeOffset = 1036;
    return row.size > effectRangeOffset ? row.data[effectRangeOffset] : 0xff;
}
