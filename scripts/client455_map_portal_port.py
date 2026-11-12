"""Connect ordinary zone-local portals to the 455 map protocol."""
from client455_trade_ore_port import patch_method, remove_methods, replace


PROCESSOR = 'network/netmsgprocessor/map/cnetmsgprocessor_map'


def port_map_portal(raw, relative, native, section):
    if relative == PROCESSOR + '.h':
        anchor = b'\tNMP_VIRTUAL\tvoid\tMovePotalResult_zocl( char * pi_pMsg );'
        raw = replace(raw, anchor, b'''    void CancelPortalRequest455();

private:
    bool ReceivePortalResult455(const char* bytes, std::size_t size);
    bool m_portalPending455 = false;''')
        return b'#include <cstddef>\n' + raw, True
    if relative == PROCESSOR + '.cpp':
        raw = replace(raw, b'\t\t\tMovePotalResult_zocl( pi_pMsg );\n\t\t\tbreak;',
                      b'            return ReceivePortalResult455(pi_pMsg, pMsgHeader->m_wSize - sizeof(_MSG_HEADER));')
        raw = remove_methods(raw, section, b'CNetMsgProcessor_Map', (
            (b'MovePotalRequest_clzo', b'BOOL'), (b'MovePotalResult_zocl', b'void'),
        ))
        return raw + b'\n' + (native / 'client455_map_portal.inc').read_bytes(), True
    if relative == 'character/avatar/cavatar_relationinfo.cpp':
        def request(body):
            at = body.index(b'\n\t// clear')
            return body[:at] + b'''
    auto* processor = static_cast<CNetMsgProcessor_Map*>(_GetNetworkMgr()->GetNetMsgProcessor(NMP_MAP));
    if (!processor || !processor->MovePotalRequest_clzo(pi_byPortalIndex)) return FALSE;

    _GetNextActionMgr()->SetEmpty(TRUE);
    _GetGBM()->CloseUnnecessaryWindow();
    return TRUE;
}'''
        raw = patch_method(raw, section, b'MOVEMENT_BETWEEN_MAP_INFO', b'MoveToPortal_Request', request)
        return raw, True
    if relative == 'network/cnetworkmgr.h':
        anchor = b'void CancelBasePortalRequest455();'
        return replace(raw, anchor, anchor + b'\n\t\t\tvoid CancelPendingMapRequests455();'), True
    if relative == 'network/cnetworkmgr.cpp':
        return replace(raw, b'        CancelBasePortalRequest455();',
                       b'        CancelPendingMapRequests455();'), True
    if relative == 'gameobject/board/common/cboardmanager.cpp':
        return replace(raw, b'network->CancelBasePortalRequest455();',
                       b'network->CancelPendingMapRequests455();'), True
    return raw, False
