"""Replace legacy initial-download wire layouts on the normal client path."""
import re

from client455_trade_ore_port import patch_method, remove_methods, replace


OWNER = b'CNetworkMgr'
TRADE_OWNER = b'CNetMsgProcessor_ItemTrade'
OBSERVATION = b'#include "client455_protocol_observation.h"\n'
RESULTS = (
    (b'Base', b'base', 4),
    (b'Inven', b'inven', 6),
    (b'Cum', b'cum', 8),
    (b'Force', b'force', 10),
)


def port_initial_download(raw, relative, section, native):
    if relative == 'network/protocol/pt_zone_client.h':
        for _, name, opcode in RESULTS:
            key = name + b'_download_result_zocl'
            pattern = rb'^#define ' + key + rb' \d+\r?\nstruct _' + key + rb' \{[^\n]*\n.*?^\};'
            raw, count = re.subn(pattern, b'#define ' + key + b' ' + str(opcode).encode(), raw, flags=re.M | re.S)
            if count != 1:
                raise ValueError('Legacy download record changed: ' + key.decode())
        for key, old, new in ((b'inven_download_request_clzo', 7, 5), (b'force_download_request_clzo', 11, 9),
                              (b'cum_download_request_clzo', 9, 7), (b'special_download_request_clzo', 122, 13)):
            prefix = b'#define ' + key + b' '
            raw = replace(raw, prefix + str(old).encode(), prefix + str(new).encode())
        return raw, True
    if relative == 'network/cnetworkmgr.h':
        member = b'DWORD\t\tm_dwItemIndexForFirstItemSetting;'
        raw = replace(raw, member, b'RF455DownloadStep m_initialDownload455 = RF455DownloadStep::Idle;\n\t'
                      b'RF455MacroDownload m_macros455{};\n\tRF455PatriarchShoutDownload m_patriarchShout455{};\n\t' + member)
        for name, _, _ in RESULTS:
            method = b'InitMsg_' + name + b'DownloadResult_zocl'
            raw = replace(raw, b'void\t' + method + b'( char * pi_pMsg );',
                          b'bool\t' + method + b'(const char* packet, std::size_t bytes);')
        anchor = b'bool\tInitMsg_CumDownloadResult_zocl(const char* packet, std::size_t bytes);'
        raw = replace(raw, anchor, anchor + b'\n\tbool InitMsg_QuestDownloadResult455(const char* packet, std::size_t bytes);'
                      b'\n\tbool InitMsg_SpecialDownloadResult455(BYTE subtype, const char* packet, std::size_t bytes);'
                      b'\n\tbool InitMsg_MinerDownloadResult455(const char* packet, std::size_t bytes);'
                      b'\n\tbool InitMsg_LinkerDownloadResult455(const char* packet, std::size_t bytes);'
                      b'\n\tbool InitMsg_MacroDownloadResult455(const char* packet, std::size_t bytes);'
                      b'\n\tbool InitMsg_PatriarchShoutResult455(const char* packet, std::size_t bytes);')
        return b'#include "client455_initial_download.h"\n' + raw, True
    if relative == 'network/cnetworkmgr.cpp':
        for name, key, _ in RESULTS:
            case = b'case ' + key + b'_download_result_zocl :'
            method = b'InitMsg_' + name + b'DownloadResult_zocl'
            raw = replace(raw, case + b'\n\t\t\t\t\t' + method + b'( pi_pMsg );\n\t\t\t\t\tbreak;',
                          case + b'\n\t\t\t\t\treturn ' + method + b'(pi_pMsg, pMsgHeader->m_wSize - 4);')
        anchor = b'case inven_download_result_zocl :\n\t\t\t\t\treturn InitMsg_InvenDownloadResult_zocl(pi_pMsg, pMsgHeader->m_wSize - 4);'
        raw = replace(raw, anchor, anchor + b'''\n
                case 12:
                    return InitMsg_QuestDownloadResult455(pi_pMsg, pMsgHeader->m_wSize - 4);
                case 45:
                    return InitMsg_LinkerDownloadResult455(pi_pMsg, pMsgHeader->m_wSize - 4);
                case 50:
                    return InitMsg_MacroDownloadResult455(pi_pMsg, pMsgHeader->m_wSize - 4);
                case 55:
                    return InitMsg_MinerDownloadResult455(pi_pMsg, pMsgHeader->m_wSize - 4);''')
        anchor = b'case init_msg :\n\t\t\tswitch( pMsgHeader->m_byType[1] )'
        raw = replace(raw, anchor, b'''case init_msg :
            // The legacy world dispatcher assigns these slots different meanings.
            if (m_initialDownload455 == RF455DownloadStep::Special &&
                (pMsgHeader->m_byType[1] == 14 || pMsgHeader->m_byType[1] == 15))
                return InitMsg_SpecialDownloadResult455(pMsgHeader->m_byType[1], pi_pMsg, pMsgHeader->m_wSize - 4);
\t\t\tswitch( pMsgHeader->m_byType[1] )''')
        anchor = b'CNetworkMgr::AnalysisServerPacket( _MSG_HEADER * pMsgHeader, char* pi_pMsg )\n{'
        raw = replace(raw, anchor, anchor + b'''
    if (pMsgHeader && pMsgHeader->m_wSize >= 4 && pMsgHeader->m_byType[0] == 13 && pMsgHeader->m_byType[1] == 105) {
        RF455_ObserveProtocol("rx", 13, 105, pMsgHeader->m_wSize - 4);
        return InitMsg_PatriarchShoutResult455(pi_pMsg, pMsgHeader->m_wSize - 4);
    }
''')
        raw = replace(raw, b'case new_pos_start_result_zocl :\n\t\t\t\t\tInitMsg_NewPosStartResult_zocl( pi_pMsg );',
                      b'case new_pos_start_result_zocl :\n\t\t\t\t\tif (!pi_pMsg || pMsgHeader->m_wSize != 5) return false;'
                      b'\n\t\t\t\t\tInitMsg_NewPosStartResult_zocl( pi_pMsg );'
                      b'\n\t\t\t\t\tRF455_ObserveProtocol("position-mode", static_cast<BYTE>(pi_pMsg[0]), 0, 0);'
                      b'\n\t\t\t\t\tRF455_ArmWorldObservation(static_cast<BYTE>(pi_pMsg[0]));')
        raw = patch_method(raw, section, OWNER, b'SendNetMessage', lambda body: replace(
            body, b'\treturn l_bResult;', b'''    if (l_bResult && pi_pType[0] == 4 && RF455_WorldObservation().walk)
        RF455_ObserveProtocol("move-queued", pi_pType[0], pi_pType[1], pi_nSize);
    return l_bResult;'''))
        return raw, True
    if relative == 'network/cnetworkmgr_systemmsg.cpp':
        raw = patch_method(raw, section, OWNER, b'InitMsg_BaseDownloadRequest_clzo', lambda body: replace(
            body, b'return l_nResult;', b'if (l_nResult) {\n\t\tm_macros455 = {};\n\t\tm_patriarchShout455 = {};'
            b'\n\t\tm_initialDownload455 = RF455DownloadStep::Base;\n\t}\n\treturn l_nResult;'))
        raw = remove_methods(raw, section, OWNER, [(b'InitMsg_' + name + b'DownloadResult_zocl', b'void')
                                                   for name, _, _ in RESULTS])
        return raw + b'\n' + (native / 'client455_initial_download.inc').read_bytes(), True
    if relative == 'network/netmsgprocessor/itemtrade/cnetmsgprocessor_itemtrade.h':
        return b'#include <cstddef>\n' + replace(raw, b'NMP_VIRTUAL\tvoid\tStoreListResult_clzo( char * pi_pMsg );',
                       b'NMP_VIRTUAL\tbool\tStoreListResult_clzo(const char* bytes, std::size_t size);'), True
    if relative == 'network/netmsgprocessor/itemtrade/cnetmsgprocessor_itemtrade.cpp':
        raw = replace(raw, b'case store_list_result_zocl\t\t:\n\t\t\tStoreListResult_clzo( pi_pMsg );\n\t\t\tbreak;', b'')
        raw = replace(raw, b'case repair_result_zocl\t\t\t:\n\t\t\tRepairResult_zocl( pi_pMsg );\n\t\t\tbreak;',
                      b'case 9:\n\t\t\treturn pMsgHeader->m_wSize >= 4 && StoreListResult_clzo(pi_pMsg, pMsgHeader->m_wSize - 4);')
        raw = patch_method(raw, section, TRADE_OWNER, b'StoreListRequest_clzo', lambda body: replace(
            body, b'SendNetMessage( store_list_request_clzo,', b'SendNetMessage( 8,'))
        raw = patch_method(raw, section, TRADE_OWNER, b'RepairRequest_clzo', lambda body: body[:body.index(b'{') + 1] +
                           b'\n\t// The legacy repair opcode is the 455 store-list request.\n\treturn FALSE;\n}')
        raw = replace(raw, b'void\nCNetMsgProcessor_ItemTrade::StoreListResult_clzo( char * pi_pMsg )',
                      b'bool\nCNetMsgProcessor_ItemTrade::StoreListResult_clzo(const char* bytes, std::size_t size)')
        raw = patch_method(raw, section, TRADE_OWNER, b'StoreListResult_clzo', port_store_list)
        return b'#include "client455_initial_download.h"\n' + OBSERVATION + raw, True
    if relative == 'gameprogress/cinputprocessmgr.cpp':
        def use_localized_keys(body):
            body = replace(body, b'static\tconst\tchar\tFILE_NAME[128] = { "./DataTable/KeyMap.dat" };',
                           b'const std::string keyMap = std::string(RF455_GetClientDataRoot()) + "\\\\KeyMap.dat";')
            body = replace(body, b'32, FILE_NAME );', b'32, keyMap.c_str() );')
            return replace(body, b'\treturn TRUE;', b'''    RF455_ObserveProtocol("keymap", m_dwTotalKeyNum, m_listKey[KM_MOVE_UP][1], 0);
    return TRUE;''')

        raw = patch_method(raw, section, b'CInputProcessMgr', b'LoadData', use_localized_keys)
        raw = patch_method(raw, section, b'CInputProcessMgr', b'InputProcess_Keyboard', lambda body: replace(
            body, b'\tif( IsPressedMoveKey() )', b'''    const RF455WalkKeyObservation walkKey(m_listKey[KM_MOVE_UP][1]);
\tif( IsPressedMoveKey() )'''))
        return (OBSERVATION + b'#include "client455_nation_paths.h"\n#include <cstring>\n#include <string>\n'
                + (native / 'client455_walk_observation.inc').read_bytes() + b'\n' + raw), True
    if relative == 'gameprogress/cgp_maingame.h':
        return replace(raw, b'BOOL\tm_bIsCompleteDataDownload;',
                       b'bool m_reportedWorldFrame455 = false;\n\tBOOL\tm_bIsCompleteDataDownload;'), True
    if relative == 'gameprogress/cgp_maingame.cpp':
        raw = patch_method(raw, section, b'CGP_MainGame', b'Init', lambda body: replace(
            body, b'm_bIsCompleteDataDownload\t=', b'RF455_WorldObservation() = {};\n\tm_reportedWorldFrame455 = false;\n\tm_bIsCompleteDataDownload\t='))
        raw = patch_method(raw, section, b'CGP_MainGame', b'Create', lambda body: replace(
            body, b'\tLoadData();', b'\tif (!LoadData()) return FALSE;'))
        raw = patch_method(raw, section, b'CGP_MainGame', b'Create_Avatar', lambda body: replace(
            body, b'm_bIsCreated_Avatar = TRUE;', b'm_bIsCreated_Avatar = TRUE;\n\tRF455_ObserveProtocol("avatar-ready", 0, 0, 0);'))
        def observe_render(body):
            body = replace(body, b'if( R3BeginScene() )', b'const bool drewFrame = R3BeginScene() != FALSE;\n\tif (drewFrame)')
            return replace(body, b'R3EndScene();', b'''R3EndScene();
    if (drewFrame && !m_reportedWorldFrame455) {
        m_reportedWorldFrame455 = true;
        RF455_ObserveProtocol("world-frame", _GetLand()->GetMapIndex(), 0, 0);
    }
    if (drewFrame && m_bIsCreated_Avatar && RF455_WorldObservation().remaining) {
        const auto* avatarPosition = _GetAvatar()->GetPosition();
        float cameraPosition[3];
        auto* camera = _GetCamera();
        camera->GetPosition(cameraPosition);
        RF455_ObserveWorldFrame(avatarPosition, cameraPosition, camera->GetYaw(),
                                camera->GetPitch(), camera->GetDistance(),
                                _GetAvatar()->GetAction(), IsEnableInput());
    }''')
        raw = patch_method(raw, section, b'CGP_MainGame', b'Render', observe_render)
        raw = patch_method(raw, section, b'CGP_MainGame', b'LoadData', lambda body: replace(
            body, b'\t_GetLand()->LoadLevel();', b'''\tauto* land = _GetLand();
    const bool mapLoaded = land->LoadLevel() && land->GetLevel() && land->GetLevel()->IsLoadedBsp();
    RF455_ObserveProtocol("map-bsp", land->GetMapIndex(), mapLoaded, 0);
    if (!mapLoaded) return FALSE;'''))
        return (OBSERVATION + (native / 'client455_live_world_observation.inc').read_bytes()
                + b'\n' + raw), True
    if relative == 'gameobject/board/skillforceboard/csfboard.cpp':
        raw = patch_method(raw, section, b'CSFBoard', b'SetSuccessCountOfMastery', lambda body: replace(
            body, b'\tif( !m_bIsUsableMastery[pi_byMasteryType+1]',
            b'\tif( pi_byMasteryType + 1 >= m_byTotalMasteryNum ) return;\n\n\tif( !m_bIsUsableMastery[pi_byMasteryType+1]'))
        return raw, True
    return raw, False


def port_store_list(body):
    start = body.index(b'\n', body.index(b'{'))
    end = body.index(b'\n\tfor( int i = 0;')
    body = body[:start] + b'''
    RF455StoreDownload packet{};
    if (!_GetMainGame() || !RF455_ReadStoreDownload(bytes, size, packet)) return false;
    unsigned applied = 0;
''' + body[end:]
    body = replace(body, b'for( int i = 0; i < pRecvMsg->byStoreNum; ++i )',
                   b'for (unsigned i = 0; i < packet.count; ++i)')
    body = body.replace(b'pRecvMsg->StorePos[i].wStoreIndex', b'packet.entries[i].index')
    body = replace(body, b'pRecvMsg->StorePos[i].fPos', b'packet.entries[i].position')
    body = replace(body, b'l_pNpc = _GetCharMgr()->AddNpc( packet.entries[i].index );', b'''const auto index = packet.entries[i].index;
        auto* l_pNpcInfo = static_cast<DT_CNMInfo*>(_GetCharDataMgr()->GetCharacter(CTI_NPC, index));
        if (!l_pNpcInfo) continue;
        auto* l_pNpc = _GetCharMgr()->AddNpc(index);''')
    start = body.index(b'\t\t\tl_pNpcInfo =')
    end = body.index(b'\t\t\tl_pNpc->SetData', start)
    body = body[:start] + body[end:]
    body = replace(body, b'\t\t\tl_pItemList = l_pNpc->GetShopItemList();',
                   b'\t\t\t++applied;\n\t\t\tauto* l_pItemList = l_pNpc->GetShopItemList();')
    body = replace(body, b'l_pItem = l_pItemList->AddItem( j );', b'auto* l_pItem = l_pItemList->AddItem( j );')
    start = body.index(b'\t_GetMainGame()->SetCompleteDataDownload')
    return body[:start] + b'''    _GetMainGame()->SetCompleteDataDownload(TRUE);
    RF455_ObserveProtocol("store-applied", packet.count, applied, 1);
    return true;
}'''
