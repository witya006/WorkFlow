"""Connect confirmed 455 BattleDungeon gate requests and map results."""

from client455_trade_ore_port import patch_method, replace


PROCESSOR = 'network/netmsgprocessor/dungeon/cnetmsgprocessor_dungeon'
INVENTORY = 'gameobject/board/itemboard/cinventoryboard'


def port_battle_dungeon_map(raw, relative, native, section):
    if relative == PROCESSOR + '.h':
        anchor = b'bool\tAnalysisServerPacket( _MSG_HEADER * pMsgHeader, char* pi_pMsg );'
        raw = replace(raw, b'#include "../CNetMsgProcessor_Base.h"',
                      b'#include "client455_battle_dungeon_map.h"\n#include "../CNetMsgProcessor_Base.h"')
        raw = replace(raw, anchor, anchor + b'''
    bool ReceiveBattleDungeonMap455(BYTE message, const char* bytes, std::size_t size);
    bool HasBattleDungeonGate455(CGroundItem* item) const;
    BOOL RequestBattleDungeonOpen455(DWORD serial);
    BOOL RequestBattleDungeonEntry455(CGroundItem* item);
    void CancelBattleDungeonEntry455();
    void StopBattleDungeonGateEffect455(float seconds);
''')
        return replace(raw, b'\n};', b'''
private:
    void ClearBattleDungeonGate455();
    void StartBattleDungeonGateEffect455();
    RF455BattleDungeonGate m_battleDungeonGate455{};
    DWORD m_battleDungeonGateEffect455 = 0;
    bool m_battleDungeonOpenPending455 = false;
    bool m_battleDungeonEntryPending455 = false;
};'''), True

    if relative == PROCESSOR + '.cpp':
        return raw + b'\n' + (native / 'client455_battle_dungeon_map.inc').read_bytes(), True

    if relative == INVENTORY + '.h':
        anchor = b'#include "CItemBoard.h"'
        raw = replace(raw, anchor, anchor + b'\n#include "client455_battle_dungeon_panel.h"')
        anchor = b'class CInventoryBoard : public CItemBoard\n{'
        raw = replace(raw, anchor, anchor + b'''
    CGUIDungeonGatePanel455 m_dungeonGatePanel455;
    DWORD m_dungeonGateKey455 = 0xffffffffu;
    BYTE m_dungeonGatePack455 = 0xff;
    BYTE m_dungeonGateSlot455 = 0xff;
    bool m_dungeonGatePending455 = false;

public:
    CGUIDungeonGatePanel455& DungeonGatePanel455() { return m_dungeonGatePanel455; }
    BOOL StageBattleDungeonKey455(BYTE pack, BYTE slot);
    void ConfirmBattleDungeonKey455();
    void CompleteBattleDungeonKey455(bool accepted);
    void CancelBattleDungeonKey455();
''')
        return raw, True

    if relative == 'gameprogress/cgp_maingame.cpp':
        anchor = b'\t_GetInventoryBoard()->InitWindow( UII_INVENTORY, 400, 0 );'
        raw = replace(raw, anchor, anchor + b'''
    auto& gatePanel = _GetInventoryBoard()->DungeonGatePanel455();
    gatePanel.Init();
    _GetUIScreen()->Add(&gatePanel);''')
        anchor = b'\t// remove all window'
        raw = patch_method(raw, section, b'CGP_MainGame', b'Destroy_UI',
                           lambda body: replace(body, anchor, b'''    if (auto* inventory = _GetInventoryBoard()) inventory->CancelBattleDungeonKey455();
''' + anchor))
        return raw, True

    if relative == 'cland.cpp':
        anchor = b'#include "CLand.h"'
        raw = replace(raw, anchor, anchor + b'''
#include "GameObject/Board/Common/CBoardManager.h"
#include "GameObject/Board/ItemBoard/CInventoryBoard.h"
#include "Network/NetMsgProcessor/Dungeon/CNetMsgProcessor_Dungeon.h"''')

        def change_map(body):
            anchor = b'    if (m_byMapIndex != index) {'
            return replace(body, anchor, anchor + b'''
        if (auto* network = _GetNetworkMgr()) {
            if (auto* dungeon = static_cast<CNetMsgProcessor_Dungeon*>(network->GetNetMsgProcessor(NMP_DUNGEON))) {
                dungeon->StopBattleDungeonGateEffect455(0.0f);
                dungeon->CancelBattleDungeonEntry455();
            }
        }
        if (auto* inventory = _GetInventoryBoard()) inventory->CancelBattleDungeonKey455();''')

        return patch_method(raw, section, b'CLand', b'SetMapIndex', change_map), True

    if relative == INVENTORY + '.cpp':
        anchor = b'#include "../Common/CBoardManager.h"'
        raw = replace(raw, anchor, anchor + b'\n#include "../General/CPartyBoard.h"')
        anchor = b'BOOL\nCInventoryBoard::UI_UseRequest_ProcessObject( void )\n{'
        raw = replace(raw, anchor, (native / 'client455_battle_dungeon_inventory.inc').read_bytes() + b'\n' + anchor)

        def open_gate(body):
            anchor = b'    auto* boards = _GetGBM();'
            return replace(body, anchor, anchor + b'''
    if (auto* object = boards->GetOrgObject()) {
        if (auto* item = dynamic_cast<RF455BasicItem*>(object->GetItem455())) {
            const auto data = item->rawData();
            if (item->header().kind == 0 && data.data && data.size > 152 &&
                (data.data[88] == IEPT_DUNGEON || data.data[88] == 29)) {
                const BOOL staged = StageBattleDungeonKey455(boards->GetOrgPackNo(), boards->GetOrgSocketNo());
                boards->ClearOperation();
                return staged;
            }
        }
    }
''')

        return patch_method(raw, section, b'CInventoryBoard', b'UI_UseRequest_ProcessObject', open_gate), True

    if relative == 'character/avatar/cavatar.cpp':
        anchor = b'#include "../../CLand.h"'
        raw = replace(raw, anchor, anchor + b'\n#include "../../Network/NetMsgProcessor/Dungeon/CNetMsgProcessor_Dungeon.h"')

        def check_portal(body):
            anchor = b'\t\t\t\t\t\tl_pPortalInfo->bIsUsable\t= TRUE;'
            return replace(body, anchor, b'''                        // RVA 0x009000 uses the staged gate when walking into a race portal.
                        if (l_pPortalInfo->byPortalType == 1 &&
                            RF455_IsBattleDungeonPortal455(l_pPortalInfo->pName, m_byRace)) {
                            auto* network = _GetNetworkMgr();
                            auto* dungeon = network ? static_cast<CNetMsgProcessor_Dungeon*>(
                                network->GetNetMsgProcessor(NMP_DUNGEON)) : nullptr;
                            if (dungeon && dungeon->RequestBattleDungeonEntry455(nullptr)) {
                                _GetGBM()->CloseUnnecessaryWindow();
                                return;
                            }
                            continue;
                        }
''' + anchor)

        return patch_method(raw, section, b'CAvatar', b'FrameMove_Portal', check_portal), True

    if relative == 'character/avatar/cavatar_relationinfo.cpp':
        def move_request(body):
            anchor = b'\tpNetMsgProcessor->GotoDungeonRequest_clzo( pi_pDungeonItem );'
            return replace(body, anchor, b'''    if (pNetMsgProcessor->HasBattleDungeonGate455(pi_pDungeonItem)) {
        if (!pNetMsgProcessor->RequestBattleDungeonEntry455(pi_pDungeonItem))
            return FALSE;
        _GetGBM()->CloseUnnecessaryWindow();
        return TRUE;
    }
''' + anchor)
        return patch_method(raw, section, b'MOVEMENT_BETWEEN_MAP_INFO',
                            b'MoveToDungeon_Request', move_request), True

    if relative == 'network/netmsgprocessor/map/cnetmsgprocessor_map.cpp':
        raw = replace(raw, b'#include "../../../CLand.h"',
                      b'#include "../../../CLand.h"\n#include "../dungeon/cnetmsgprocessor_dungeon.h"')
        anchor = b'void CNetworkMgr::CancelPendingMapRequests455()\n{\n    CancelBasePortalRequest455();'
        return replace(raw, anchor, anchor + b'''
    if (auto* dungeon = static_cast<CNetMsgProcessor_Dungeon*>(GetNetMsgProcessor(NMP_DUNGEON)))
        dungeon->CancelBattleDungeonEntry455();'''), True

    if relative == 'network/cnetworkmgr.cpp':
        anchor = b'#include "../GameObject/Manager/CCharacterMgr.h"'
        raw = replace(raw, anchor, anchor + b'''
#include "../GameObject/Board/Common/CBoardManager.h"
#include "../GameObject/Board/ItemBoard/CInventoryBoard.h"''')
        def stop_gate(body, anchor):
            return replace(body, anchor, b'''    if (auto* dungeon = static_cast<CNetMsgProcessor_Dungeon*>(GetNetMsgProcessor(NMP_DUNGEON)))
        dungeon->StopBattleDungeonGateEffect455(0.0f);
''' + anchor)

        raw = patch_method(raw, section, b'CNetworkMgr', b'Destroy',
                           lambda body: stop_gate(body, b'\tfor( int i = 0; i < MAX_NET_MSG_PROCESSOR; ++i )'))
        def close_client(body):
            anchor = b'        CancelPendingMapRequests455();'
            return replace(body, anchor, b'''        if (auto* dungeon = static_cast<CNetMsgProcessor_Dungeon*>(GetNetMsgProcessor(NMP_DUNGEON)))
            dungeon->StopBattleDungeonGateEffect455(0.0f);
        CancelPendingMapRequests455();
        if (auto* inventory = _GetInventoryBoard()) inventory->CancelBattleDungeonKey455();''')

        raw = patch_method(raw, section, b'CNetworkMgr', b'CloseClientCheck', close_client)
        anchor = b'\t\tcase dungeon_msg :'
        handler = b'''        case 35: { // 455 BattleDungeon dispatch (RVA 0x1818E0).
            const BYTE message = pMsgHeader->m_byType[1];
            if (pMsgHeader->m_wSize < sizeof(_MSG_HEADER)) return false;
            auto* dungeon = static_cast<CNetMsgProcessor_Dungeon*>(GetNetMsgProcessor(NMP_DUNGEON));
            return dungeon && dungeon->ReceiveBattleDungeonMap455(
                message, pi_pMsg, pMsgHeader->m_wSize - sizeof(_MSG_HEADER));
        }

'''
        return replace(raw, anchor, handler + anchor), True

    return raw, False
