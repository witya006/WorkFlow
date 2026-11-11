"""Replace legacy initial-download wire layouts on the normal client path."""
import re

from client455_trade_ore_port import patch_method, remove_methods, replace


OWNER = b'CNetworkMgr'
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
        raw = replace(raw, member, b'RF455DownloadStep m_initialDownload455 = RF455DownloadStep::Idle;\n\t' + member)
        for name, _, _ in RESULTS:
            method = b'InitMsg_' + name + b'DownloadResult_zocl'
            raw = replace(raw, b'void\t' + method + b'( char * pi_pMsg );',
                          b'bool\t' + method + b'(const char* packet, std::size_t bytes);')
        anchor = b'bool\tInitMsg_CumDownloadResult_zocl(const char* packet, std::size_t bytes);'
        raw = replace(raw, anchor, anchor + b'\n\tbool InitMsg_QuestDownloadResult455(const char* packet, std::size_t bytes);'
                      b'\n\tbool InitMsg_SpecialDownloadResult455(BYTE subtype, const char* packet, std::size_t bytes);'
                      b'\n\tbool InitMsg_MinerDownloadResult455(const char* packet, std::size_t bytes);')
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
                case 55:
                    return InitMsg_MinerDownloadResult455(pi_pMsg, pMsgHeader->m_wSize - 4);''')
        anchor = b'case init_msg :\n\t\t\tswitch( pMsgHeader->m_byType[1] )'
        raw = replace(raw, anchor, b'''case init_msg :
            // The legacy world dispatcher assigns these slots different meanings.
            if (m_initialDownload455 == RF455DownloadStep::Special &&
                (pMsgHeader->m_byType[1] == 14 || pMsgHeader->m_byType[1] == 15))
                return InitMsg_SpecialDownloadResult455(pMsgHeader->m_byType[1], pi_pMsg, pMsgHeader->m_wSize - 4);
\t\t\tswitch( pMsgHeader->m_byType[1] )''')
        return raw, True
    if relative == 'network/cnetworkmgr_systemmsg.cpp':
        raw = patch_method(raw, section, OWNER, b'InitMsg_BaseDownloadRequest_clzo', lambda body: replace(
            body, b'return l_nResult;', b'if (l_nResult) m_initialDownload455 = RF455DownloadStep::Base;\n\treturn l_nResult;'))
        raw = remove_methods(raw, section, OWNER, [(b'InitMsg_' + name + b'DownloadResult_zocl', b'void')
                                                   for name, _, _ in RESULTS])
        return raw + b'\n' + (native / 'client455_initial_download.inc').read_bytes(), True
    if relative == 'gameobject/board/skillforceboard/csfboard.cpp':
        raw = patch_method(raw, section, b'CSFBoard', b'SetSuccessCountOfMastery', lambda body: replace(
            body, b'\tif( !m_bIsUsableMastery[pi_byMasteryType+1]',
            b'\tif( pi_byMasteryType + 1 >= m_byTotalMasteryNum ) return;\n\n\tif( !m_bIsUsableMastery[pi_byMasteryType+1]'))
        return raw, True
    return raw, False
