"""Route selected live world packets to their 455 consumers."""
from client455_trade_ore_port import replace


def port_world_updates(raw, relative, native, section):
    if relative == 'character/npc/cbasenpc.cpp':
        anchor = b'_GetCharIF()->DrawCharacter( m_pMesh, m_vecPos, m_vecRot[1], m_fScale,scroll );'
        raw = replace(raw, anchor, anchor + b'''
    if (RF455_WorldObservation().captureMonsters && IsEqualCharType(CTI_MONSTER) &&
        !m_Animation.IsEmpty() && m_Animation.GetAniData()->m_Load) {
        BBOX bounds;
        D3DXVECTOR3 center(m_vecPos[0], m_vecPos[1], m_vecPos[2]);
        if (GetBoundBox(bounds)) {
            center.x = (bounds.pMin[0] + bounds.pMax[0]) * 0.5f;
            center.y = (bounds.pMin[1] + bounds.pMax[1]) * 0.5f;
            center.z = (bounds.pMin[2] + bounds.pMax[2]) * 0.5f;
        }
        D3DXVECTOR4 clip;
        D3DXVec3Transform(&clip, &center, &GetR3State()->mMatViewProj);
        if (clip.w > 0 && clip.z >= 0 && clip.z <= clip.w &&
            clip.x > -0.8f * clip.w && clip.x < 0.8f * clip.w &&
            clip.y > -0.38f * clip.w && clip.y < 0.55f * clip.w) {
            RF455_RecordMonsterDraw(GetIndex(), GetMeshID(), m_Animation.GetAniData()->m_Ident,
                                    GetBoneFrame(), clip.x / clip.w, clip.y / clip.w, clip.w);
        }
    }''')
        return b'#include "client455_protocol_observation.h"\n' + raw, True
    if relative == 'character/avatar/cavatar.h':
        anchor = b'\tBYTE\t\t\tm_byAttackMode;'
        raw = replace(raw, anchor, b'\tBYTE m_townState455 = 0xff;\n' + anchor)
        anchor = b'\t\t\tRESULT\t\tNormalAttack( CCharacter * pi_pTarget );'
        raw = replace(raw, anchor, anchor + b'''
    void SetTownState455(BYTE state) { m_townState455 = state; }
    BYTE GetTownState455() const { return m_townState455; }''')
        anchor = b'\t\t\tRESULT\t\tCheckTargetConditionForAttack( CCharacter * pi_pTarget );'
        return replace(raw, anchor, b'\t\t\tbool CheckTownAttack455(CCharacter& target);\n' + anchor), True
    if relative == 'character/avatar/cavatar_combat.cpp':
        anchor = (b'l_nResult = CheckAvatarConditionForAttack();\n'
                  b'\tif( l_nResult != ARC_SUCCESS ) return l_nResult;')
        raw = replace(raw, anchor, anchor + b'\n\tif (!CheckTownAttack455(*pi_pTarget)) return ARC_FAIL_STOP;')
        return b'#include "client455_language.h"\n' + raw + b'''

bool CAvatar::CheckTownAttack455(CCharacter& target)
{
    if (m_townState455 == 0xff || target.IsEqualCharType(CTI_MONSTER)) return true;

    const char* message = RF455_GetNormalLanguagePack()->get(128);
    if (message && *message) _SetSystemMsg("%s", message);
    if (_GetTargetMgr()->IsEqualTarget(&target)) _GetTargetMgr()->SetTarget(nullptr);
    return false;
}
''', True
    if relative == 'network/cnetworkmgr.h':
        raw = replace(raw, b'void\tPositionMsg_ObjectRealFixpositon_zocl( char * pi_pMsg );',
                      b'bool PositionMsg_ObjectRefresh455(const char* bytes, std::size_t size);')
        anchor = b'void\tInitMsg_MonsterCreate_zocl( char * pi_pMsg );'
        return replace(raw, anchor, anchor + b'''
    bool InitMsg_MonsterSpawn455(const char* bytes, std::size_t size);
    bool PositionMsg_MonsterMove455(const char* bytes, std::size_t size);
    bool PositionMsg_PlayerStatus455(const char* bytes, std::size_t size);
    bool PositionMsg_TownState455(const char* bytes, std::size_t size);'''), True
    if relative == 'network/cnetworkmgr.cpp':
        raw = replace(raw, b'case correct_position_zocl :\n\t\t\t\t\tbreak;',
                      b'case 10:\n\t\t\t\t\treturn PositionMsg_ObjectRefresh455(pi_pMsg, pMsgHeader->m_wSize - 4);')
        raw = replace(raw, b'\t\t\t\tcase object_real_fixpositon_zocl :\n\t\t\t\t\tPositionMsg_ObjectRealFixpositon_zocl( pi_pMsg );\n\t\t\t\t\tbreak;\n\n', b'')
        raw = replace(raw, b'case player_die_zocl :\n\t\t\t\t\tInitMsg_PlayerDie_zocl( pi_pMsg );\n\t\t\t\t\tbreak;',
                      b'case 16:\n\t\t\t\t\treturn InitMsg_MonsterSpawn455(pi_pMsg, pMsgHeader->m_wSize - 4);')
        raw = replace(raw, b'case monster_move_zocl :\n\t\t\t\t\tPositionMsg_MonsterMove_zocl( pi_pMsg );\n\t\t\t\t\tbreak;',
                      b'''case 5:
                    return PositionMsg_MonsterMove455(pi_pMsg, pMsgHeader->m_wSize - 4);
                case 12:
                    RF455_ObserveProtocol("position-noop", 4, 12, pMsgHeader->m_wSize - 4);
                    return true;
                case 25:
                    return PositionMsg_PlayerStatus455(pi_pMsg, pMsgHeader->m_wSize - 4);
                case 34:
                    return PositionMsg_TownState455(pi_pMsg, pMsgHeader->m_wSize - 4);''')
        return raw, True
    includes = b'#include "client455_world_updates.h"\n#include "client455_protocol_observation.h"\n'
    if relative == 'network/cnetworkmgr_initmsg.cpp':
        return includes + raw + b'\n' + (native / 'client455_world_monster_spawn.inc').read_bytes(), True
    if relative == 'network/cnetworkmgr_positionmsg.cpp':
        old = b'void\nCNetworkMgr::PositionMsg_ObjectRealFixpositon_zocl( char * pi_pMsg )'
        start, end = section(raw, old, old)
        raw = raw[:start] + raw[end:]
        raw = replace(raw, b'Vector3f pi_vecTar, BYTE pi_byMoveFlag )',
                      b'Vector3f pi_vecTar, BYTE pi_byMoveFlag, bool resetSpeedOnSnap = true )')
        snap = b'pi_pChar->SetPosition( pi_vecCur );\n\t\tpi_pChar->SetMagnificationOfSpeed( 1.0f );'
        raw = replace(raw, snap, snap.replace(b'pi_pChar->SetMagnificationOfSpeed',
                                             b'if (resetSpeedOnSnap) pi_pChar->SetMagnificationOfSpeed'))
        return includes + raw + b'\n' + (native / 'client455_world_position.inc').read_bytes(), True
    return raw, False
