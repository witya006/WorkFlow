bool CNetMsgProcessor_Combat::MonsterForceResult455(const char* bytes, std::size_t size)
{
    RF455MonsterForceResult packet{};
    if (!RF455_ReadMonsterForceResult(bytes, size, packet) || packet.actorType != CTI_MONSTER)
        return false;

    _GetGGI()->SetRequestProcessState(FALSE);
    auto* manager = _GetCharMgr();
    if (!manager) return true;
    auto* actor = manager->GetCharacter(CTI_MONSTER, packet.serial);
    if (!actor) return true;
    actor->GetCombatState()->SetReceiveAttackResultMsg(TRUE);
    actor->SetReceiveNetMsg("Attack/SF");
    if (actor->GetCombatMode() != CSI_COMBAT) actor->SetCombatMode(CSI_COMBAT);

    CSFItem force;
    if (!force.CreateForce455(packet.index, packet.level)) return true;
    actor->SetSFItem(&force);
    actor->GetCombatState()->SetAttackError(FALSE);
    if (actor->IsDeath()) return true;

    std::array<CCharacter*, RF455MonsterForceResult::maxTargets> targets{};
    for (std::size_t i = 0; i < packet.targetCount; ++i) {
        auto& row = packet.targets[i];
        const bool player = row.type == CTI_PLAYER || row.type == CTI_AVATAR;
        if (row.damage == -1 || (!player && row.damage == 1)) row.damage = 0;
        if (player && !_GetAvatar()) continue;
        auto* target = manager->GetCharacter(row.type, row.serial);
        if (!target) continue;
        targets[i] = target;
        auto* victim = actor->AddVictimInfo(target, TRUE);
        victim->SetAttacked(TRUE);
        victim->SetAttackPoint(static_cast<DWORD>(row.damage));
    }

    actor->GetCombatState()->SetAttackType_Dist(ADT_NEAR);
    actor->SetAction(CAI_FORCE_INVOKE, FALSE);
    if (auto* target = targets[0])
        actor->SetRotY(actor->GetPosition(), target->GetPosition(), TRUE);

    for (std::size_t i = 0; i < packet.targetCount; ++i) {
        auto* target = targets[i];
        if (!target) continue;
        target->SetReceiveNetMsg("Damaged");
        auto* incoming = target->AddAttackerInfo(actor, TRUE);
        const auto damage = packet.targets[i].damage;
        incoming->SetForceDamage455(damage);
        incoming->SetDamageType_Dist(ADT_NEAR);
        incoming->SetDamageType_AT(CAT_FORCE);
        incoming->SetDamageType_CT(i == 0 ? packet.critical : packet.critical && packet.targets[0].type != CTI_PLAYER);
        incoming->SetEffectFrameNum(actor->GetMaxEffectFrameNum());
        incoming->SetSFItem(&force);
    }
    RF455_ObserveProtocol("monster-force-result", packet.index, force.GetLevel(), unsigned(size));
    return true;
}
