#include "client455_avatar_stage.h"

BOOL CNetworkMgr::SendAvatarMove455(const float* target)
{
    auto* avatar = _GetAvatar();
    if (!avatar || !RF455_FinitePosition(target) || !RF455_FinitePosition(avatar->GetPosition()))
        return FALSE;

    const auto now = timeGetTime();
    if (m_movement455.isWaiting(now)) return FALSE;

    RF455MoveRequest packet{};
    if (!RF455_EncodeMovementTarget(target[0], target[2], packet.targetXZ)) return FALSE;
    packet.moveMode = avatar->GetWalkMode();
    std::memcpy(packet.current, avatar->GetPosition(), sizeof(packet.current));
    packet.sequence = m_movement455.sequence++;
    packet.speed = avatar->GetSpeed();
    if (!std::isfinite(packet.speed)) return FALSE;
    BYTE type[] = {position_msg, RF455MoveOpcode};
    RF455_EncodePositionBody(&packet, sizeof(packet), type[1], m_account455.delta, m_account455.mask,
                             RF455_IsTutorialAvatarStage());
    if (!m_movement455.predictLocally) {
        m_movement455.pending = true;
        m_movement455.pendingAt = now;
    }
    const BOOL sent = SendNetMessage(NST_GAME_SERVER, type, &packet, sizeof(packet));
    if (sent)
        m_movement455.stopArmed = true;
    else
        m_movement455.clearPending();
    return sent;
}

BOOL CNetworkMgr::PositionMsg_MoveRequest_Simple_clzo(float* target)
{
    auto* avatar = _GetAvatar();
    if (!avatar || !RF455_FinitePosition(target)) return FALSE;
    static DWORD lastSend = 0;
    avatar->SetPosition(target, TRUE, FALSE);
    const auto now = timeGetTime();
    if (now - lastSend < 500) return FALSE;
    lastSend = now;
    return SendAvatarMove455(target);
}

BOOL CNetworkMgr::SendAvatarPosition455(BYTE opcode)
{
    auto* avatar = _GetAvatar();
    if (!avatar || !RF455_FinitePosition(avatar->GetPosition())) return FALSE;

    RF455PositionReport packet{};
    packet.sequence = m_movement455.sequence++;
    std::memcpy(packet.current, avatar->GetPosition(), sizeof(packet.current));
    BYTE type[] = {position_msg, opcode};
    RF455_EncodePositionBody(&packet, sizeof(packet), opcode, m_account455.delta, m_account455.mask,
                             RF455_IsTutorialAvatarStage());
    return SendNetMessage(NST_GAME_SERVER, type, &packet, sizeof(packet));
}

BOOL CNetworkMgr::PositionMsg_RealMovposRequest_clzo()
{
    return SendAvatarPosition455(RF455PositionSampleOpcode);
}

BOOL CNetworkMgr::PositionMsg_PlayerStop_clzo(BOOL setAction)
{
    auto* avatar = _GetAvatar();
    if (!avatar) return FALSE;
    const bool armed = m_movement455.stopArmed;
    if (armed) m_movement455.stopArmed = false;
    const BOOL sent = armed && SendAvatarPosition455(RF455StopOpcode);
    if (setAction && (!armed || sent)) avatar->SetAction(CAI_MOVE_STOP);
    return sent;
}

bool CNetworkMgr::PositionMsg_PlayerMove455(const char* bytes, std::size_t size)
{
    RF455MoveBroadcast packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;
    auto* avatar = _GetAvatar();
    if (!avatar) return true;
    const bool local = avatar->GetIndex() == packet.serial;
    auto* player = local ? avatar : (_GetCharMgr() ? _GetCharMgr()->GetPlayer(packet.serial) : nullptr);
    if (!player) return true;
    if (local) m_movement455.clearPending();
    if (!local || !m_movement455.predictLocally) {
        Vector3f current = {float(packet.current[0]), float(packet.current[1]), float(packet.current[2])};
        if (local) player->GetPosition(current);
        Vector3f target = {float(packet.targetXZ[0]), current[1], float(packet.targetXZ[1])};
        if (current[0] == target[0] && current[2] == target[2]) {
            player->SetAction(CAI_MOVE_STOP);
        } else {
            SetClientCurrentPosition(player, current, target, CPF_MOVE);
            player->SetFirstMoving(TRUE);
            player->SetAction(CAI_MOVE_MOVING);
        }
    }
    RF455_ObserveProtocol("move-broadcast", position_msg, local, size);
    return true;
}

bool CNetworkMgr::PositionMsg_PlayerStop455(const char* bytes, std::size_t size)
{
    RF455StopResult packet{};
    if (!RF455_ReadWorldRecord(bytes, size, packet)) return false;
    auto* avatar = _GetAvatar();
    if (!avatar) return true;
    Vector3f target = {float(packet.position[0]), float(packet.position[1]), float(packet.position[2])};
    const bool local = avatar->GetIndex() == packet.serial;
    if (local) {
        auto* next = _GetNextActionMgr();
        if (next && GetDist(avatar->GetPosition(), target) > 10.f) {
            next->SetNextAction(CAI_MOVE_MOVING);
            next->SetNextTargetPosition(target);
        }
    } else if (auto* manager = _GetCharMgr()) {
        if (auto* player = manager->GetPlayer(packet.serial)) {
            Vector3f current{};
            player->GetPosition(current);
            SetClientCurrentPosition(player, current, target, CPF_STOP);
        }
    }
    RF455_ObserveProtocol("move-stop-result", position_msg, local, size);
    return true;
}
