bool CNetMsgProcessor_Combat::NormalAttackResult455(const char* bytes, std::size_t size)
{
    RF455NormalAttackResult packet{};
    if (!RF455_ReadNormalAttackResult(bytes, size, packet)) return false;
    _GetGGI()->SetRequestProcessState(FALSE);

    auto* manager = _GetCharMgr();
    if (!manager || !_GetAvatar()) return true;
    auto* actor = manager->GetCharacter(packet.attackerType, packet.attackerSerial);
    if (!actor) return true;
    actor->GetCombatState()->SetReceiveAttackResultMsg(TRUE);
    actor->SetReceiveNetMsg("Attack/SF");
    actor->GetCombatState()->SetAttackError(FALSE);
    if (actor->IsDeath()) return true;

    const bool local = actor->IsEqualCharType(CTI_AVATAR);
    if (!local) {
        if (actor->GetCombatMode() != CSI_COMBAT) actor->SetCombatMode(CSI_COMBAT);
        if (auto* player = dynamic_cast<CPlayer*>(actor)) player->SetBulletDTIndex(
            packet.projectile == 0xffff ? ID_INVALID : static_cast<DWORD>(packet.projectile));
    }

    std::array<CCharacter*, 32> targets{};
    unsigned resolved = 0;
    for (unsigned i = 0; i < packet.targetCount; ++i) {
        auto& row = packet.targets[i];
        if (row.damage == -1 || (row.damage == 1 && row.type != CTI_PLAYER && row.type != CTI_AVATAR))
            row.damage = 0;
        auto* target = manager->GetCharacter(row.type, row.serial);
        if (!target) continue;
        targets[i] = target;
        ++resolved;
        auto* victim = local ? actor->GetVictimInfo(target) : nullptr;
        if (!victim) victim = actor->AddVictimInfo(target, !local || !i);
        if (victim) {
            victim->SetAttacked(TRUE);
            if (row.damage > 0)
                victim->SetAttackPoint(victim->GetAttackPoint() + static_cast<DWORD>(row.damage));
        }
    }

    if (!local) {
        actor->SetAction(CAI_COMBAT_ATTACK, FALSE);
        if (auto* target = targets[0])
            actor->SetRotY(actor->GetPosition(), target->GetPosition(), TRUE);
    }

    for (unsigned i = 0; i < packet.targetCount; ++i) {
        auto* target = targets[i];
        if (!target) continue;
        target->SetReceiveNetMsg("Damaged");
        auto* incoming = target->AddAttackerInfo(actor, TRUE);
        if (!incoming) continue;
        const auto damage = packet.targets[i].damage;
        incoming->SetSpecialHit455(damage == -2);
        if (damage > 0) incoming->SetTotalDamagePoint(incoming->GetTotalDamagePoint() + static_cast<DWORD>(damage));
        incoming->SetDamageType_Dist(actor->GetAttackDistanceType(CAT_NORMAL));
        incoming->SetDamageType_AT(CAT_NORMAL);
        incoming->SetDamageType_CT(packet.critical && (i == 0 || packet.targets[0].type != CTI_PLAYER));
        incoming->SetEffectFrameNum(actor->GetMaxEffectFrameNum());
        incoming->SetSFItem(nullptr);
    }
    RF455_ObserveProtocol("normal-attack-result", packet.targetCount, resolved,
                         packet.targetCount ? static_cast<unsigned>(packet.targets[0].damage) : 0);
    return true;
}
