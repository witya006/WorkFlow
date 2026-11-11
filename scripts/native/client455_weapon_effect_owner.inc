RF455EffectEquipment EFUtil_Equipment455(CCharacter* actor, BYTE part)
{
    if (!actor || (!actor->IsEqualCharType(CTI_PLAYER) && !actor->IsEqualCharType(CTI_AVATAR)))
        return {};
    auto* player = static_cast<CPlayer*>(actor);
    if (player->IsEqualUnitMountState(UMS_MOUNT)) return {nullptr, player->GetEquipItem(part)};
    return {player->GetEquipItem455(part), nullptr};
}

DWORD RF455EffectEquipment::meshID() const
{
    if (typed) return typed->GetPlan455().meshID;
    return legacy ? legacy->GetMeshID() : ID_INVALID;
}

DWORD RF455EffectEquipment::material() const
{
    if (typed) {
        const RF455ConditionItem item(typed->GetItem455());
        if (item.valid) return item.field<DWORD>(208);
    }
    if (legacy && legacy->GetData())
        return static_cast<EQUIPMENT_DATA*>(legacy->GetData())->dwEffectMaterial;
    return _M_METAL_;
}

BYTE RF455EffectEquipment::dummy(DWORD index) const
{
    if (typed) return typed->GetDummy455(index);
    return legacy ? legacy->GetDummyIndex(index) : 255;
}

BOOL EFUtil_GetCharTransformFromIndex(Vector3f* position, CCharacter* actor,
                                    const RF455EffectEquipment& item, DWORD id)
{
    return RF455_WeaponTransform(position, actor, item.dummy(id));
}

BOOL EFUtil_GetCharTransformFromIndex(Vector3f* position, CCharacter* actor, CEquipItem* item, DWORD id)
{
    return EFUtil_GetCharTransformFromIndex(position, actor, RF455EffectEquipment{nullptr, item}, id);
}
