    if (auto* payload = pi_pOrgObject->GetItem455()) {
        const auto metadata = RF455_ReadBasicIconMetadata(*payload);
        if (!metadata.quantity) return FALSE;

        std::unique_ptr<CBoardObject> copy(pi_pOrgObject->Clone());
        auto& pack = m_listItemPack[pi_byTarPackNo];
        if (!copy || !pack.Add(pi_byTarSocketNo, copy.get())) return FALSE;

        auto* object = copy.release();
        auto* window = static_cast<CGUIItemWindow*>(m_uiWindow);
        if (!window->TakeInItem(pi_byTarPackNo, pi_byTarSocketNo, metadata.itemID, metadata.spriteID,
                                metadata.quantity, metadata.usableLevel)) {
            pack.Remove(pi_byTarSocketNo);
            return FALSE;
        }
        if (auto* icon = window->GetItem(pi_byTarPackNo, pi_byTarSocketNo)) {
            if (!icon->UsesTypedIcon455()) {
                icon->SetIconType455(0);
                icon->SetSprite();
            }
            icon->SetGrade455(metadata.grade);
            object->SetIcon(icon);
            object->RefreshLock455();
        }
        return TRUE;
    }
