bool CNetworkMgr::InitMsg_MonsterSpawn455(const char* bytes, std::size_t size) {
    RF455MonsterSpawn packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;

    cnm_create_monster info{};
    info.dwClientIndex = packet.serial;
    info.dwServerIndex = packet.zoneIndex;
    info.dwRecIndex = packet.record;
    auto* monster = CreateMonster(&info);
    if (monster) {
        monster->SetCreationType(CCT_NORMAL);
        monster->SetEffectInfo(CAI_CREATE_CREATE);
        monster->SetCombatMode((packet.flags & 0x40) ? CSI_COMBAT : CSI_PEACE);
        monster->SetWalkMode((packet.flags & 3) == 1 ? CMM_MOVE_RUN : CMM_MOVE_WALK);
        monster->SetPosition(packet.position[0], packet.position[1], packet.position[2], TRUE, TRUE);
        monster->CheckYPos();
        monster->CreatePath(monster->GetPosition());
        monster->SetRotY(packet.direction * 1.4117647409439087f + 180.0f, FALSE);
        RF455_ObserveProtocol("monster-mesh", packet.record, monster->GetMeshID(), monster->GetWidth());
    }
    RF455_ObserveProtocol("monster-spawn", packet.record, monster != nullptr, sizeof(packet));
    return true;
}

bool CNetworkMgr::InitMsg_MonsterDeath455(const char* bytes, std::size_t size)
{
    RF455MonsterDeath packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;

    auto* monster = _GetCharMgr()->GetMonster(packet.serial);
    if (monster) {
        monster->SetServerIndex(packet.zoneIndex);
        monster->SetDeath(packet.reason);
        monster->SetReceiveNetMsg("Death");
    }
    RF455_ObserveProtocol("monster-death", packet.serial, packet.reason, monster != nullptr);
    return true;
}
