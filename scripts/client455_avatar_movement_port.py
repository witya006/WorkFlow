"""Replace legacy movement payloads and their mismatched response dispatch."""

from client455_trade_ore_port import patch_method, remove_methods, replace


NETWORK = b'CNetworkMgr'


def port_avatar_movement(raw, relative, native, section):
    if relative == 'network/cnetworkmgr.h':
        anchor = b'void\tPositionMsg_PlayerMove_zocl( char * pi_pMsg );'
        raw = replace(raw, anchor, b'''bool PositionMsg_PlayerMove455(const char* bytes, std::size_t size);
    bool PositionMsg_PlayerStop455(const char* bytes, std::size_t size);
    BOOL SendAvatarMove455(const float* target);
    BOOL SendAvatarPosition455(BYTE opcode);
    RF455MovementState m_movement455;''')
        return b'#include "client455_avatar_movement.h"\n' + raw, True
    if relative == 'network/cnetworkmgr.cpp':
        raw = replace(raw, b'case player_move_zocl :\n\t\t\t\t\tPositionMsg_PlayerMove_zocl( pi_pMsg );\n\t\t\t\t\tbreak;',
                      b'case 4:\n\t\t\t\t\treturn PositionMsg_PlayerMove455(pi_pMsg, pMsgHeader->m_wSize - 4);')
        raw = replace(raw, b'case goto_avator_result_zocl :\n\t\t\t\t\tPositionMsg_GotoAvatorResult_zocl( pi_pMsg );',
                      b'''case RF455StopResultOpcode:
                    return PositionMsg_PlayerStop455(pi_pMsg, pMsgHeader->m_wSize - 4);
                case 29:
                    if (!pi_pMsg || pMsgHeader->m_wSize != 19) return false;
                    PositionMsg_GotoAvatorResult_zocl(pi_pMsg);''')
        raw = replace(raw, b'if (dwProID == NST_GAME_SERVER) CancelBasePortalRequest455();',
                      b'''if (dwProID == NST_GAME_SERVER) {
        CancelBasePortalRequest455();
        // Login's world-to-zone handoff closes the previous connection.
        // Keep the prediction mode selected by the world-entry reply.
        m_movement455.clearPending();
        m_movement455.stopArmed = false;
    }''')
        return raw, True
    if relative != 'network/cnetworkmgr_positionmsg.cpp':
        return raw, False

    def move_request(body):
        body = replace(body, b'if( _GetAvatar()->IsDisable( ROSF_MOVABLE ) )',
                       b'if (!_GetAvatar() || !RF455_FinitePosition(pi_vecTargetPos) ||\n'
                       b'        _GetAvatar()->IsDisable(ROSF_MOVABLE) || m_movement455.isWaiting(timeGetTime()))')
        body = replace(body, b'\t_move_request_clzo l_sSend;', b'')
        for assignment in (
            b'l_sSend.byMoveType = _GetAvatar()->GetWalkMode();',
            b'l_sSend.byModeType = _GetAvatar()->GetCombatMode();',
            b'FloatPosToShortPos( l_sSend.zCur, _GetAvatar()->GetPosition() );',
            b'l_sSend.zTar[0] = l_vecRealTargetPos[0];',
            b'l_sSend.zTar[1] = l_vecRealTargetPos[2];',
        ):
            body = replace(body, b'\t' + assignment, b'')
        first = body.index(b'\tBYTE l_nType[]')
        last = body.index(b');', first) + 2
        body = body[:first] + b'    const BOOL l_nResult = SendAvatarMove455(l_vecRealTargetPos);' + body[last:]
        return replace(body, b'if( l_nResult )\n\t{',
                       b'if (l_nResult && m_movement455.predictLocally)\n\t{').replace(
                           b'\telse\n\t{\n\t\tNetLogWrite(', b'\telse if (!l_nResult)\n\t{\n\t\tNetLogWrite(')

    def goto_avatar_request(body):
        return replace(body, b'position_msg, goto_avator_request_clzo',
                       b'position_msg, 28')

    def goto_avatar_result(body):
        return replace(body, b'if( l_sRecv.byRet == 0 )\n\t{',
                       b'''if (l_sRecv.byRet == 0)
    {
        auto* land = _GetLand();
        if (!land || !land->MapData455().maps || l_sRecv.byMapCode >= land->MapData455().count ||
            !RF455_FinitePosition(l_sRecv.fStartPos)) return;''')

    raw = patch_method(raw, section, NETWORK, b'PositionMsg_MoveRequest_clzo', move_request)
    raw = patch_method(raw, section, NETWORK, b'PositionMsg_GotoAvatorRequest_clzo', goto_avatar_request)
    raw = patch_method(raw, section, NETWORK, b'PositionMsg_GotoAvatorResult_zocl', goto_avatar_result)
    raw = remove_methods(raw, section, NETWORK, (
        (b'PositionMsg_MoveRequest_Simple_clzo', b'BOOL'),
        (b'PositionMsg_RealMovposRequest_clzo', b'BOOL'),
        (b'PositionMsg_PlayerStop_clzo', b'BOOL'),
        (b'PositionMsg_PlayerMove_zocl', b'void'),
    ))
    return raw + b'\n' + (native / 'client455_avatar_movement.inc').read_bytes(), True
