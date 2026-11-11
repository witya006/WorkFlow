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

    actor->SetAction(CAI_FORCE_INVOKE, FALSE);
    if (packet.hasTarget) {
        if (auto* target = manager->GetCharacter(packet.targetType, packet.targetSerial))
            actor->SetRotY(actor->GetPosition(), target->GetPosition(), TRUE);
    }
    RF455_ObserveProtocol("monster-force-result", packet.index, force.GetLevel(), unsigned(size));
    return true;
}
