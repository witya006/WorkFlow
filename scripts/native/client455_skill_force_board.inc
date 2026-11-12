// Typed Skill/Force rows use the regular view and the board's existing item ownership.
BOOL CSFBoard::AddTypedSF455(BYTE bank, BYTE slot, CBoardObject& source)
{
    auto* skill = dynamic_cast<RF455SkillForceItem*>(source.GetItem455());
    auto* window = static_cast<CGUISFWindow*>(m_uiWindow);
    if (!skill || !window || slot >= GetMaxSocketNum455(bank) || GetObject(bank, slot)) return FALSE;
    const auto row = skill->rawData();
    if (row.size < 144 || skill->record().iconBoard) return FALSE;
    _skill_force_info info{};
    info.bySFType = skill->record().subtype;
    info.dwIndex = source.GetIndex();
    info.byStep = row.data[15];
    std::memcpy(&info.dwItemID, row.data + 4, sizeof(info.dwItemID));
    std::memcpy(&info.dwSpriteID, row.data + 8, sizeof(info.dwSpriteID));
    info.byLevel = skill->EffectiveLevel455();
    info.fExpByPercent = skill->record().percent;
    info.pName = const_cast<char*>(skill->name());

    std::unique_ptr<CBoardObject> copy(source.Clone());
    if (!copy || !window->TakeInItem(bank, &info)) return FALSE;
    auto* view = window->GetIconBoard(bank, info.dwIndex);
    if (!view || !m_listItemPack[bank].Add(slot, copy.get())) {
        window->TakeOutItem(bank, info.dwIndex);
        return FALSE;
    }
    copy->SetIcon(view->GetItem());
    skill->SetIconBoard455(view);
    view->SetUnitState(CGUISkFcUnit::Disabled);
    copy.release();
    return TRUE;
}
