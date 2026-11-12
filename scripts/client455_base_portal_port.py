"""Connect the 455 Return item and its position messages to the ordinary client."""

from client455_trade_ore_port import patch_method, remove_methods, replace


BOARD = 'gameobject/board/itemboard/cinventoryboard'
MANAGER = 'gameobject/board/common/cboardmanager.cpp'


def port_base_portal(raw, relative, native, section):
    if relative == BOARD + '.h':
        anchor = b'virtual\tBOOL\t\tUI_UseRequest_ProcessObject( void );'
        raw = replace(raw, anchor,
                      b'BOOL UI_CheckBeforeUse_CheckOriginalObject() override;\n\t' + anchor)
        anchor = b'BOOL\t\tUI_AutoPickUpItemRequest( void );'
        return replace(raw, anchor,
                       b'void CompleteBasePortalUse455(DWORD serial, bool succeeded);\n\t\t\t' + anchor), True
    if relative == BOARD + '.cpp':
        anchor = b'BOOL\nCInventoryBoard::UI_UseRequest_ProcessObject( void )\n{'
        raw = replace(raw, anchor, (native / 'client455_base_portal_inventory.inc').read_bytes() +
                      b'\n' + anchor + b'''
    auto* boards = _GetGBM();
    if (auto* item = ReturnItem455(boards->GetOrgObject())) {
        if (_GetNetworkMgr()->PositionMsg_GotoBaseportalRequest_clzo(item->header().serial))
            return TRUE;
        boards->ClearOperation();
        return FALSE;
    }
''')
        anchor = b'_GetNetworkMgr()->PositionMsg_GotoBaseportalRequest_clzo( pOrgItem->GetIndex() );'
        raw = replace(raw, anchor,
                           b'if (!_GetNetworkMgr()->PositionMsg_GotoBaseportalRequest_clzo(pOrgItem->GetIndex()))\n'
                      b'                    return FALSE;')
        return (b'#include "client455_item_payloads.h"\n'
                b'#include "client455_language.h"\n'
                b'#include "client455_message_dispatch.h"\n' + raw), True
    if relative == MANAGER:
        def close_windows(body):
            return b'''CBoardManager::CloseUnnecessaryWindow( void )
{
    const auto close = [](auto* window) {
        if (window && window->IsShow()) window->Close();
    };
    close(_GetShopWindow());
    close(_GetMiningWindow());
    close(_GetOreProcWindow());
    close(_GetExchangeWindow());
    close(_GetSummonsSelectWindow());
    close(_GetSummonsControlWindow());
    close(_GetNpcIntroWindow());
    close(_GetItemWorkWindow());
    close(_GetItemUpgradeWindow());
    if (auto* targets = _GetTargetMgr()) targets->CloseAllWindow();
    close(_GetMoveMapWindow());
    close(_GetMinimapWindow());
    close(_GetSelectAttackPartWindow());
    auto* classChange = m_listBoard[IBT_CLASS_CHANGE];
    if (classChange && classChange->IsOpen()) classChange->CloseWindow();
}'''
        raw = patch_method(raw, section, b'CBoardManager', b'CloseUnnecessaryWindow', close_windows)
        def expire_request(body):
            return replace(body, b'm_bIsRequestProcess = FALSE;',
                           b'if (auto* network = _GetNetworkMgr()) network->CancelBasePortalRequest455();\n'
                           b'\t\t\tm_bIsRequestProcess = FALSE;')
        return patch_method(raw, section, b'CBoardManager', b'FrameMove', expire_request), True
    if relative == 'network/cnetworkmgr.h':
        raw = replace(raw, b'void\tPositionMsg_GotoBaseportalResult_zocl( char * pi_pMsg );',
                      b'bool PositionMsg_BasePortalResult455(const char* bytes, std::size_t size);\n'
                      b'\tbool m_basePortalPending455 = false;\n\tDWORD m_basePortalSerial455 = 0;')
        anchor = b'BOOL\tPositionMsg_GotoBaseportalRequest_clzo( DWORD pi_dwIndex );'
        return replace(raw, anchor, anchor + b'\n\t\t\tvoid CancelBasePortalRequest455();'), True
    if relative == 'network/cnetworkmgr.cpp':
        raw = replace(raw,
                      b'case goto_baseportal_result_zocl :\n\t\t\t\t\tPositionMsg_GotoBaseportalResult_zocl( pi_pMsg );\n\t\t\t\t\tbreak;',
                      b'case 27:\n\t\t\t\t\treturn PositionMsg_BasePortalResult455(pi_pMsg, pMsgHeader->m_wSize - 4);')
        def close_connection(body):
            at = body.index(b'{') + 1
            return body[:at] + b'\n    if (dwProID == NST_GAME_SERVER) CancelBasePortalRequest455();' + body[at:]
        return patch_method(raw, section, b'CNetworkMgr', b'CloseClientCheck', close_connection), True
    if relative == 'network/cnetworkmgr_positionmsg.cpp':
        raw = remove_methods(raw, section, b'CNetworkMgr', (
            (b'PositionMsg_GotoBaseportalRequest_clzo', b'BOOL'),
            (b'PositionMsg_GotoBaseportalResult_zocl', b'void'),
        ))
        return raw + b'\n' + (native / 'client455_base_portal_position.inc').read_bytes(), True
    if relative == 'gameprogress/cgp_maingame.cpp':
        return replace(raw, b'\t_GetUISpriteMgr()->LoadSprite( SP_ID_MAPLOADING );\n', b''), True
    if relative == 'character/avatar/cavatar_relationinfo.cpp':
        def begin_transition(body):
            anchor = b'\t_GetAvatar()->Disable( ROSF_MOVABLE );'
            return replace(body, anchor, b'\t_GetNetworkMgr()->ResetAvatarMovement455();\n' + anchor)
        raw = patch_method(raw, section, b'MOVEMENT_BETWEEN_MAP_INFO', b'MoveToPortal_Result', begin_transition)
        def before_loading(body):
            body = replace(body, b'if( timeGetTime() - m_dwMoveStepStartTime >= m_dwMoveDelay )', b'''const bool sameMapPortal = m_byEnterMapIndex == m_byExitMapIndex &&
        (m_byMoveType == GST_PORTAL || m_byMoveType == GST_BASE_PORTAL);
    const bool ordinaryWorldPortal = m_byMoveType == GST_PORTAL && !_GetDungeonInfo()->IsInDungeon();
    const DWORD delay = sameMapPortal ? 700 : ordinaryWorldPortal ? 1300 : m_dwMoveDelay;
    if (timeGetTime() - m_dwMoveStepStartTime >= delay)''')
            return replace(body, b'_GetMapLoadingWindow()->Open();',
                           b'if (!sameMapPortal) _GetMapLoadingWindow()->Open();')
        raw = patch_method(raw, section, b'MOVEMENT_BETWEEN_MAP_INFO', b'MoveToPortal_Result_PrevLoadData', before_loading)
        def after_loading(body):
            anchor = b'if( m_byEnterMapIndex != m_byExitMapIndex )\n\t{'
            body = replace(body, anchor, anchor + b'''
        auto* land = _GetLand();
        const auto fail = [&] {
            if (_GetMapLoadingWindow()->IsShow()) _GetMapLoadingWindow()->Close();
            m_byMoveStep = MMS_NONE;
            m_pEnterPortalInfo = m_pExitPortalInfo = nullptr;
            RF455_ObserveProtocol("map-load-failed", m_byEnterMapIndex, m_byExitMapIndex, m_byMoveType);
            // An accepted transition cannot continue on the previous server position.
            EP_DisconnectedFromServer();
        };
        if (!land->CanLoadMap455(m_byExitMapIndex)) {
            fail();
            return;
        }
''')
            body = replace(body, b'_GetLand()->UnloadLevel();\n\t\t_GetLand()->LoadLevel( m_byExitMapIndex );',
                           b'''land->UnloadLevel();
        if (!land->LoadLevel(m_byExitMapIndex)) {
            fail();
            return;
        }''')
            return replace(body, b'm_dwMoveDelay\t\t\t= DEFAULT_MOVEMAP_DELAY;',
                           b'm_dwMoveDelay = m_byMoveType == GST_PORTAL ||\n'
                           b'        (m_byMoveType == GST_BASE_PORTAL && m_byEnterMapIndex == m_byExitMapIndex)\n'
                           b'        ? 1300 : DEFAULT_MOVEMAP_DELAY;')
        raw = patch_method(raw, section, b'MOVEMENT_BETWEEN_MAP_INFO', b'MoveToPortal_Result_LoadData', after_loading)
        def finish_transition(body):
            return replace(body, b'\t_GetAvatar()->Enable( ROSF_MOVABLE );\n'
                           b'\t_GetNetworkMgr()->InitMsg_NewPosStartRequest_clzo( m_byMoveType );',
                           b'''    if (!_GetNetworkMgr()->InitMsg_NewPosStartRequest_clzo(m_byMoveType)) {
        m_byMoveStep = MMS_NONE;
        m_pEnterPortalInfo = m_pExitPortalInfo = nullptr;
        RF455_ObserveProtocol("map-arrival-send-failed", m_byExitMapIndex, m_byMoveType, 0);
        EP_DisconnectedFromServer();
        return;
    }
    _GetAvatar()->Enable(ROSF_MOVABLE);''')
        raw = patch_method(raw, section, b'MOVEMENT_BETWEEN_MAP_INFO', b'MoveToPortal_Result_BeginNewMap', finish_transition)
        return b'#include "client455_protocol_observation.h"\nvoid EP_DisconnectedFromServer();\n' + raw, True
    if relative == 'userinterface/gamewindow/etcwin/guimaploadingwindow.cpp':
        def bind_loading_sprite(body):
            return b'''CGUIMapLoadingWindow::SetSprite( void )
{
    SetSize(gScreen.m_ptSize.x, gScreen.m_ptSize.y);
    auto* sprite = gSpriteMgr.GetTargetSprite455(7);
    if (sprite && !sprite->GetMaxFrames(0)) sprite = nullptr;
    SPRITE_INFO info{sprite, 0, 0};
    SetSpriteInfo(&info);
}'''
        return patch_method(raw, section, b'CGUIMapLoadingWindow', b'SetSprite', bind_loading_sprite), True
    return raw, False
