"""Route selected live world packets to their 455 consumers."""
from client455_trade_ore_port import replace


def port_world_updates(raw, relative, native):
    if relative == 'network/cnetworkmgr.h':
        anchor = b'void\tInitMsg_MonsterCreate_zocl( char * pi_pMsg );'
        return replace(raw, anchor, anchor + b'''
    bool InitMsg_MonsterSpawn455(const char* bytes, std::size_t size);
    bool PositionMsg_MonsterMove455(const char* bytes, std::size_t size);
    bool PositionMsg_PlayerStatus455(const char* bytes, std::size_t size);'''), True
    if relative == 'network/cnetworkmgr.cpp':
        raw = replace(raw, b'case player_die_zocl :\n\t\t\t\t\tInitMsg_PlayerDie_zocl( pi_pMsg );\n\t\t\t\t\tbreak;',
                      b'case 16:\n\t\t\t\t\treturn InitMsg_MonsterSpawn455(pi_pMsg, pMsgHeader->m_wSize - 4);')
        raw = replace(raw, b'case monster_move_zocl :\n\t\t\t\t\tPositionMsg_MonsterMove_zocl( pi_pMsg );\n\t\t\t\t\tbreak;',
                      b'''case 5:
                    return PositionMsg_MonsterMove455(pi_pMsg, pMsgHeader->m_wSize - 4);
                case 12:
                    RF455_ObserveProtocol("position-noop", 4, 12, pMsgHeader->m_wSize - 4);
                    return true;
                case 25:
                    return PositionMsg_PlayerStatus455(pi_pMsg, pMsgHeader->m_wSize - 4);''')
        return raw, True
    includes = b'#include "client455_world_updates.h"\n#include "client455_protocol_observation.h"\n'
    if relative == 'network/cnetworkmgr_initmsg.cpp':
        return includes + raw + b'\n' + (native / 'client455_world_monster_spawn.inc').read_bytes(), True
    if relative == 'network/cnetworkmgr_positionmsg.cpp':
        return includes + raw + b'\n' + (native / 'client455_world_position.inc').read_bytes(), True
    return raw, False
