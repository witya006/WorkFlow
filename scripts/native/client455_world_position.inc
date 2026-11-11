bool CNetworkMgr::PositionMsg_MonsterMove455(const char* bytes, std::size_t size) {
    RF455MonsterMove packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;

    auto* monster = _GetCharMgr()->GetMonster(packet.serial);
    const bool applied = monster && !monster->IsDeath();
    if (applied) {
        Vector3f current = {float(packet.current[0]), float(packet.current[1]), float(packet.current[2])};
        Vector3f target = {float(packet.targetXZ[0]), current[1], float(packet.targetXZ[1])};
        if (current[0] == target[0] && current[2] == target[2]) monster->SetAction(CAI_MOVE_STOP);
        SetClientCurrentPosition(monster, current, target, CPF_MOVE);
        monster->SetFirstMoving(TRUE);
        monster->SetAction(CAI_MOVE_MOVING);
        monster->SetReceiveNetMsg("Move");
    }
    RF455_ObserveProtocol("monster-move", applied, 0, sizeof(packet));
    return true;
}

bool CNetworkMgr::PositionMsg_PlayerStatus455(const char* bytes, std::size_t size) {
    RF455PlayerStatusUpdate packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;

    auto* player = _GetCharMgr()->GetPlayer(packet.serial);
    if (player) {
        player->SetServerStatusFlag(packet.flags);
        player->SetReceiveNetMsg("server status flag");
    }
    RF455_ObserveProtocol("player-status-update", player != nullptr, player && player == _GetAvatar(), sizeof(packet));
    return true;
}
