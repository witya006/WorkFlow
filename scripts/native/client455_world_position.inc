bool CNetworkMgr::PositionMsg_MoveCorrection455(const char* bytes, std::size_t size)
{
    RF455MoveCorrection packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;
    const auto x = packet.position[0], y = packet.position[1], z = packet.position[2];
    if (!std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z)) return false;
    auto* avatar = _GetAvatar();
    if (avatar) avatar->ApplyMoveCorrection455(packet.reason, x, y, z);
    RF455_ObserveProtocol("move-correction", packet.reason, avatar != nullptr, sizeof(packet));
    return true;
}

bool CNetworkMgr::PositionMsg_MonsterMove455(const char* bytes, std::size_t size) {
    RF455MonsterMove packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;

    auto* monster = _GetCharMgr()->GetMonster(packet.serial);
    const bool applied = monster && !monster->IsDeath();
    if (applied) {
        Vector3f current = {float(packet.current[0]), float(packet.current[1]), float(packet.current[2])};
        Vector3f target = {float(packet.targetXZ[0]), current[1], float(packet.targetXZ[1])};
        if (current[0] == target[0] && current[2] == target[2]) monster->SetAction(CAI_MOVE_STOP);
        SetClientCurrentPosition(monster, current, target, CPF_MOVE, false);
        monster->SetFirstMoving(TRUE);
        monster->SetAction(CAI_MOVE_MOVING);
        monster->SetReceiveNetMsg("Move");
    }
    RF455_ObserveProtocol("monster-move", applied, 0, sizeof(packet));
    return true;
}

bool CNetworkMgr::PositionMsg_ObjectRefresh455(const char* bytes, std::size_t size) {
    RF455ObjectRefresh packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;

    bool applied = false;
    if (packet.objectKind == obj_kind_char) {
        CCharacter* actor = nullptr;
        if (packet.objectType == 8) {
            // Type 8 is the target's parked unit actor, stored as CTI_UNIT here.
            actor = _GetCharMgr()->GetUnit(packet.serial);
        } else if (packet.objectType <= CTI_GUARD_TOWER || packet.objectType == CTI_AVATAR) {
            actor = _GetCharMgr()->GetCharacter(packet.objectType, packet.serial);
        }
        if (actor) {
            actor->SetReceiveNetMsg("Real Fix");
            applied = actor->IsReceiveFixPositionMsg() != FALSE;
        }
    } else if (packet.objectKind == obj_kind_item) {
        CResObject* object = nullptr;
        if (packet.objectType == obj_id_parkingunit) {
            object = _GetCharMgr()->GetUnit(packet.serial);
        } else {
            object = _GetGroundItemMgr()->GetItem(packet.groundIndex);
        }
        if (object) {
            object->SetReceiveFixPositionMsg(TRUE);
            applied = object->IsReceiveFixPositionMsg() != FALSE;
        }
    }
    RF455_ObserveProtocol("position-refresh", packet.objectKind, packet.objectType, applied);
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

bool CNetworkMgr::PositionMsg_TownState455(const char* bytes, std::size_t size) {
    std::uint8_t townState = 0;
    if (!RF455_ReadWorldRecord(bytes, size, townState)) return false;

    auto* avatar = _GetAvatar();
    if (!avatar) return false;
    avatar->SetTownState455(townState);
    RF455_ObserveProtocol("town-state", avatar->GetTownState455(), townState == 0xff, sizeof townState);
    return true;
}
