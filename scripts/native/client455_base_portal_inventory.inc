namespace {
RF455BasicItem* ReturnItem455(CBoardObject* object)
{
    auto* item = object ? dynamic_cast<RF455BasicItem*>(object->GetItem455()) : nullptr;
    if (!item || item->header().kind != 0) return nullptr;
    const auto metadata = item->rawMetadata();
    return metadata.size > 88 && metadata.data[88] == IEPT_RETURN ? item : nullptr;
}
}

BOOL CInventoryBoard::UI_CheckBeforeUse_CheckOriginalObject()
{
    auto* object = _GetGBM()->GetOrgObject();
    if (!ReturnItem455(object)) return CItemBoard::UI_CheckBeforeUse_CheckOriginalObject();
    auto* avatar = _GetAvatar();
    if (!avatar || object->IsUsing()) return FALSE;
    if (avatar->IsEqualUnitMountState(UMS_MOUNT)) {
        RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(0x56d));
        return FALSE;
    }
    if (!avatar->IsEnableMove() || avatar->IsEqualAction(CAI_ITEM_USE_MINING)) {
        RF455_ShowSystemMessage("%s", RF455_GetNormalLanguagePack()->get(0x56e));
        return FALSE;
    }
    return TRUE;
}

void CInventoryBoard::CompleteBasePortalUse455(DWORD serial, bool succeeded)
{
    auto* boards = _GetGBM();
    if (boards->GetOperationType() != IOT_USE || boards->GetOrgBoardType() != IBT_INVENTORY)
        return;

    const auto pack = boards->GetOrgPackNo();
    const auto slot = boards->GetOrgSocketNo();
    auto* object = GetObject(pack, slot);
    if (auto* item = ReturnItem455(object)) {
        if (item->header().serial == serial && succeeded) {
            Remove(pack, slot, 1);
            if (auto* avatar = _GetAvatar()) avatar->ClearUsingItem455();
        }
    } else if (auto* avatar = _GetAvatar()) {
        if (auto* legacy = dynamic_cast<CBoardItem*>(object)) {
            if (legacy == avatar->GetUsingItem() && legacy->GetIndex() == serial) {
                if (succeeded) {
                    UI_UseResult(TRUE);
                    return;
                }
                avatar->RemoveUsingItem();
            }
        }
    }
    if (!boards->HaveHoverObject()) boards->ClearOperation();
}
