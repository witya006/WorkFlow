namespace {
BOOL UseLinkedBoardObject455(CObjectBoard* board, DWORD serial)
{
    BYTE pack, slot;
    if (!board || !board->GetObjectPosition(pack, slot, serial)) return FALSE;
    board->UI_UseRequest(pack, slot);
    return TRUE;
}
}

BOOL CLinkBoard::UseShortcut455(BYTE bank, BYTE slot)
{
    if (slot >= GetMaxSocketNum455(bank)) return FALSE;
    auto* shortcut = GetObject(bank, slot);
    auto* item = shortcut ? shortcut->GetItem455() : nullptr;
    if (!item) return FALSE;

    const DWORD serial = item->header().serial;
    switch (item->header().kind) {
    case 0:
        // The stock Linker tries the inventory before equipped items.
        return UseLinkedBoardObject455(_GetInventoryBoard(), serial) ||
               UseLinkedBoardObject455(_GetEquipBoard(), serial);
    case 1: {
        auto* skill = dynamic_cast<RF455SkillForceItem*>(item);
        if (!skill || !_GetAvatar()) return FALSE;
        auto* board = skill->record().subtype == 1
            ? static_cast<CSFBoard*>(_GetSkillBoard())
            : static_cast<CSFBoard*>(_GetForceBoard());
        BYTE pack, sourceSlot;
        if (!board || !board->GetObjectPosition(pack, sourceSlot, serial)) return FALSE;
        auto* source = dynamic_cast<CSFItem*>(board->GetObject(pack, sourceSlot));
        if (!source) return FALSE;
        _GetAvatar()->ClearSFTargetPos();
        board->UseSkillForce_Request(source, nullptr, TRUE);
        return TRUE;
    }
    case 2:
        return UseLinkedBoardObject455(_GetAnimusBoard(), serial);
    default:
        return FALSE;
    }
}
