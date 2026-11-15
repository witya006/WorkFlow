"""Integrate the 455 currency exchange, mining and promotion views."""
import re

from client455_trade_ore_port import patch_method, remove_methods, replace


EXCHANGE = 'userinterface/gamewindow/npc/guiexchangewindow'
MINING = 'userinterface/gamewindow/mining/guiminingwindow'
PROMOTION = 'userinterface/gamewindow/npc/guiclasschangewindow'
BOARD = 'gameobject/board/general/cboard_etc'
TRADE_NET = 'network/netmsgprocessor/itemtrade/cnetmsgprocessor_itemtrade'


def exchange_header(raw):
    start = raw.index(b'class CGUIEconomyRateGraph')
    end = raw.index(b'class CGUIExchangeWindow', start)
    raw = raw[:start] + raw[end:]
    start = raw.index(b'private:', start)
    end = raw.index(b'public:', start)
    raw = raw[:start] + b'''private:
    CGUIObject m_uiBase;
    CGUIText m_uiTitle, m_uiFeeTitle, m_uiBuyDirection, m_uiSellDirection, m_uiFeeNotes[4];
    CGUIText m_uiAssetsTitle, m_uiGoldStr, m_uiDalantStr, m_uiGold, m_uiDalant, m_uiAdjustTitle, m_uiTaxRateStr;
    RF455GuiAnimatedImage m_uiAniTitleBar;
    CGUIButton m_uiCloseButton, m_uiHelpButton;
    CGUIButtonEx m_uiExchangeButton, m_uiRecoveryButton;
    CGUIScrollbarEX m_uiExchangeAdjScrollbar;
    __int64 m_dwGold = 0, m_dwDalant = 0;
    DWORD m_dwDalantPerGold;
    float m_fExchangeCommission;

''' + raw[end:]
    raw = replace(raw, b'#include "../../GUIController/GUIScrollbar.h"',
                  b'#include "../../GUIController/GUIScrollbar.h"\n#include "client455_briefing_controls.h"')
    for currency in (b'Gold', b'Dalant'):
        raw = replace(raw, b'Set' + currency + b'( DWORD ', b'Set' + currency + b'( __int64 ')
        raw = replace(raw, b'DWORD\tGet' + currency, b'__int64\tGet' + currency)
    return raw


def exchange_source(raw, section, native):
    start = raw.index(b'CGUIEconomyRateGraph::CGUIEconomyRateGraph(')
    end = raw.index(b'CGUIExchangeWindow::CGUIExchangeWindow(', start)
    raw = raw[:start] + raw[end:]
    raw = replace(raw, b'm_bIsCreated\t\t\t= FALSE;', b'')
    names = (b'Init', b'SetSprite', b'SetRaceType', b'InitEconomyRatePoint', b'InsertEconomyRatePoint',
             b'SetExchangeRate', b'SetExchangeCommission', b'SetExchangeAdjustbar', b'SetTaxRate',
             b'SetGold', b'SetDalant', b'ScrollEvent')
    raw = remove_methods(raw, section, b'CGUIExchangeWindow', [(name, b'void') for name in names])
    return raw + b'\n' + (native / 'client455_exchange_window.inc').read_bytes()


def mining_source(raw, section, native):
    raw = replace(raw, b'm_bIsCreated\t\t\t= FALSE;', b'')
    names = (b'Init', b'SetSprite', b'SelectOre', b'Mining_On', b'Mining_Off')
    raw = remove_methods(raw, section, b'CGUIMiningWindow', [(name, b'void') for name in names])
    return raw + b'\n' + (native / 'client455_mining_window.inc').read_bytes()


def promotion_source(raw, section, native):
    raw = replace(raw, b'm_bIsCreated\t\t= FALSE;', b'')
    names = (b'Init', b'SetSprite', b'SetTotalClassNum', b'SelectClass', b'SetSkillIcon', b'SetClassName', b'SetDescription')
    raw = remove_methods(raw, section, b'CGUIClassChangeWindow', [(name, b'void') for name in names])
    raw = replace(raw, b'WM_BOARD_OK, 0', b'WM_CLASS_CHANGE_OK_455, 0')
    raw = raw.replace(b'WM_BOARD_CANCEL, 0', b'WM_CLASS_CHANGE_CANCEL_455, 0')
    raw = replace(raw, b'//\t\t\tPostUIMessage( WM_OPEN_WINDOW_HELP, 0 );', b'PostUIMessage( WM_OPEN_WINDOW_HELP, 0 );')
    return raw + b'\n' + (native / 'client455_class_change_window.inc').read_bytes()


def packet_contract(raw):
    for name, old, new in ((b'exchange_dalant_for_gold_request_clzo', 12, 10),
                           (b'exchange_gold_for_dalant_request_clzo', 13, 11),
                           (b'exchange_money_result_zocl', 14, 13),
                           (b'economy_history_inform_zocl', 15, 14), (b'economy_rate_inform_zocl', 16, 15)):
        prefix = b'#define ' + name + b' '
        raw = replace(raw, prefix + str(old).encode(), prefix + str(new).encode())
    for structure, fields in ((b'_exchange_dalant_for_gold_request_clzo', (b'dwDalant',)),
                              (b'_exchange_gold_for_dalant_request_clzo', (b'dwGold',)),
                              (b'_exchange_money_result_zocl', (b'dwLeftGold', b'dwLeftDalant'))):
        start = raw.index(b'struct ' + structure)
        end = raw.index(b'};', start)
        body = raw[start:end]
        for field in fields:
            body, count = re.subn(rb'\bDWORD([ \t]+)' + field + rb'\b', rb'__int64\1' + field, body)
            if count != 1:
                raise ValueError(f'Currency exchange packet field changed: {field!r}')
        raw = raw[:start] + body + raw[end:]
    return raw


def exchange_packet_source(raw, section):
    owner = b'CNetMsgProcessor_ItemTrade'
    for name in (b'ExchangeDalantForGoldRequest_clzo', b'ExchangeGoldForDalantRequest_clzo'):
        raw = replace(raw, name + b'( DWORD ', name + b'( __int64 ')
        raw = patch_method(raw, section, owner, name, lambda body: replace(
            body, b'\treturn SendNetMessage', b'\tconst BOOL queued = SendNetMessage').rstrip()[:-1] +
            b'\n\tif (!queued) _GetGBM()->SetRequestProcessState(FALSE);\n\treturn queued;\n}')

    def replace_body(body, replacement):
        return body[:body.index(b'{')] + replacement

    raw = patch_method(raw, section, owner, b'ExchangeMoneyResult_zocl', lambda body: replace_body(body, b'''{
    const auto* result = reinterpret_cast<const _exchange_money_result_zocl*>(pi_pMsg);
    _GetGBM()->SetRequestProcessState(FALSE);
    if (result->byErrCode == 0)
        _GetExchangeBoard()->ExchangeMoney_Result(result->dwLeftDalant, result->dwLeftGold, TRUE);
    else if (result->byErrCode == 1 || result->byErrCode == 2)
        _GetExchangeBoard()->ExchangeMoney_Result(0, 0, FALSE);
}'''))
    raw = replace(raw, b'\t\t\tExchangeMoneyResult_zocl( pi_pMsg );', b'''            if (!pi_pMsg || pMsgHeader->m_wSize < sizeof(_MSG_HEADER) + 1 ||
                (!pi_pMsg[0] && pMsgHeader->m_wSize < sizeof(_MSG_HEADER) + sizeof(_exchange_money_result_zocl)))
                return false;
            ExchangeMoneyResult_zocl(pi_pMsg);''')
    raw = replace(raw, b'\t\t\tEconomyHistoryInform_zocl( pi_pMsg );', b'''            if (!pi_pMsg || pMsgHeader->m_wSize < sizeof(_MSG_HEADER) + sizeof(_economy_history_inform_zocl))
                return false;
            EconomyHistoryInform_zocl(pi_pMsg);''')
    raw = replace(raw, b'\t\t\tEconomyRateInform_zocl( pi_pMsg );', b'''            if (!pi_pMsg || pMsgHeader->m_wSize < sizeof(_MSG_HEADER) + 21) return false;
            EconomyRateInform_zocl(pi_pMsg);''')
    raw = replace(raw, b'SetExchangeRate( pRecvMsg->fPayExgRate );', b'SetExchangeRate(2000);')
    raw = replace(raw, b'_GetExchangeWindow()->InitEconomyRatePoint(',
                  b'if (_GetExchangeWindow()) _GetExchangeWindow()->InitEconomyRatePoint(')
    return replace(raw, b'_GetExchangeWindow()->InsertEconomyRatePoint(',
                   b'if (_GetExchangeWindow()) _GetExchangeWindow()->InsertEconomyRatePoint(')


def port_service_windows(raw, relative, section, native):
    if relative == EXCHANGE + '.h':
        return exchange_header(raw), True
    if relative == EXCHANGE + '.cpp':
        return exchange_source(raw, section, native), True
    if relative in (MINING + '.h', PROMOTION + '.h'):
        raw = replace(raw, b'#include "../../GUIController/GUIWindow.h"',
                      b'#include "../../GUIController/GUIWindow.h"\n#include "client455_briefing_controls.h"')
        raw = replace(raw, b'BOOL\t\t\t\tm_bIsCreated;', b'')
        if relative == PROMOTION + '.h':
            raw = replace(raw, b'MAX_CLASS_SKILL_ICON_NUM\t3', b'MAX_CLASS_SKILL_ICON_NUM\t10')
        return replace(raw, b'CGUIObjectAni\t', b'RF455GuiAnimatedImage\t'), True
    if relative == MINING + '.cpp':
        return mining_source(raw, section, native), True
    if relative == PROMOTION + '.cpp':
        return promotion_source(raw, section, native), True
    if relative == 'define.h':
        return replace(raw, b'UII_CLASS_CHANGE_WINDOW\t\t\t37', b'UII_CLASS_CHANGE_WINDOW\t\t\t36'), True
    if relative == 'definemessage.h':
        for name, old, new in ((b'MINING_BOARD_SELECT_ORE', b'0180', b'0186'), (b'MINING_BOARD_MINING', b'0181', b'0187')):
            pattern = rb'(#define[ \t]+WM_' + name + rb'[ \t]+\( WM_USER \+ 0x)' + old + rb'\b'
            raw, count = re.subn(pattern, lambda match: match[1] + new, raw)
            if count != 1:
                raise ValueError(f'Mining message changed: {name!r}')
        start, guard, end = raw.rpartition(b'#endif')
        if not guard:
            raise ValueError('Message header guard changed')
        return start + b'#define WM_CLASS_CHANGE_OK_455 (WM_USER + 0x0106)\n' \
            b'#define WM_CLASS_CHANGE_CANCEL_455 (WM_USER + 0x0107)\n' + guard + end, True
    if relative == 'gameobject/board/etcboard/cclasschangeboard.cpp':
        return replace(replace(raw, b'case WM_BOARD_OK :', b'case WM_CLASS_CHANGE_OK_455 :'),
                       b'case WM_BOARD_CANCEL :', b'case WM_CLASS_CHANGE_CANCEL_455 :'), True
    if relative == BOARD + '.h':
        raw = replace(raw, b'ExchangeMoney_Request( BYTE pi_byMoneyType, DWORD pi_dwMoney )',
                      b'ExchangeMoney_Request(BYTE type, __int64 amount)')
        return replace(raw, b'ExchangeMoney_Result( DWORD pi_dwDalant, DWORD pi_dwGold )',
                       b'ExchangeMoney_Result(__int64 dalant, __int64 gold, BOOL accepted)'), True
    if relative == BOARD + '.cpp':
        raw = remove_methods(raw, section, b'CExchangeBoard', [(b'ExchangeMoney_Request', b'BOOL'),
                             (b'ExchangeMoney_Result', b'void'), (b'MsgProc', b'LRESULT')])
        raw = replace(raw, b'm_uiExchangeWindow.SetRaceType( _GetAvatar()->GetRace() );', b'')
        raw = replace(raw, b'm_byOreIndex = pi_byOreIndex;', b'if (pi_byOreIndex >= 5) return;\n\tm_byOreIndex = pi_byOreIndex;')
        return raw + b'\n' + (native / 'client455_exchange_board.inc').read_bytes(), True
    if relative == 'network/protocol/pt_zone_client.h':
        return packet_contract(raw), True
    if relative == TRADE_NET + '.h':
        for name in (b'ExchangeDalantForGoldRequest_clzo', b'ExchangeGoldForDalantRequest_clzo'):
            raw = replace(raw, name + b'( DWORD ', name + b'( __int64 ')
        return raw, True
    if relative == TRADE_NET + '.cpp':
        return exchange_packet_source(raw, section), True
    if relative == 'character/avatar/cavatar_etc.cpp':
        raw = replace(raw, b'_GetExchangeWindow()->SetExchangeRate( m_dwExchangeRate );',
                      b'if (_GetExchangeWindow()) _GetExchangeWindow()->SetExchangeRate(m_dwExchangeRate);')
        return replace(raw, b'_GetExchangeWindow()->SetTaxRate( m_fTexRate * 100.0f );',
                       b'if (_GetExchangeWindow()) _GetExchangeWindow()->SetTaxRate(m_fTexRate * 100.0f);'), True
    return raw, False
