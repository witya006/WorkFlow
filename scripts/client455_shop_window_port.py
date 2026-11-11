"""Install the 455 merchant window in the ordinary client build."""
import re


SHOP = 'userinterface/gamewindow/npc/guishopwindow'


def replace(raw, before, after):
    if raw.count(before) != 1:
        raise ValueError(f'Shop source anchor changed: {before!r}')
    return raw.replace(before, after)


def shop_header(raw):
    for before, after in (
        (b'CGUIObjectAni\t\t\tm_uiAniTitleBar;', b'RF455GuiAnimatedImage m_uiAniTitleBar;'),
        (b'CGUIObject\t\t\t\tm_uiPageBoard;', b'RF455GuiPageBoard m_uiPageBoard;'),
        (b'CGUIButton\t\t\t\tm_uiPageUp;', b''),
        (b'CGUIButton\t\t\t\tm_uiPageDown;', b''),
        (b'CGUIText\t\t\t\tm_uiCurPageStr;', b''),
        (b'm_uiGold;', b'm_uiGold;\n\tCGUIText m_uiPvpLabel455, m_uiPointLabel455, m_uiPvpValue455, m_uiPointValue455;'),
        (b'BOOL\t\t\t\t\tm_bIsCreated;', b''),
        (b'SetDalant( DWORD pi_dwDalant );', b'SetDalant(__int64 value);'),
        (b'SetGold( DWORD pi_dwGold );', b'SetGold(__int64 value);\n\tvoid SetPvp455(DWORD value);\n\tvoid SetPoints455(DWORD value);'),
        (b'private:\n\t\n\t\t\tvoid\t\tTabLabelPosSetting( TradeMode pi_eTradeMode, BOOL pi_bIsActive );', b''),
    ):
        raw = replace(raw, before, after)
    return replace(raw, b'#include "../../UIGlobal.h"',
                   b'#include "../../UIGlobal.h"\n#include "client455_briefing_controls.h"\n'
                   b'#include "client455_gui_page_board.h"')


def shop_source(raw, section, native):
    methods = {
        b'Init': b'void', b'SetSprite': b'void', b'SetShopType': b'void',
        b'SetTradeMode': b'void', b'TakeInBuyItem': b'BOOL', b'TakeOutBuyItem': b'BOOL',
        b'ClearBuyItemList': b'void', b'TakeInTradeItem': b'void', b'TakeOutTradeItem': b'void',
        b'ClearTradeItemList': b'void', b'UpdateShopBoard': b'void', b'SetCurrentShopBoard': b'void',
        b'SetDalant': b'void', b'SetGold': b'void', b'TabLabelPosSetting': b'void',
    }
    for name, return_type in methods.items():
        anchor = b'CGUIShopWindow::' + name + b'('
        start, end = section(raw, anchor, anchor)
        declaration = re.search(rb'\b' + return_type + rb'[ \t\r\n]*$', raw[:start])
        if declaration is None:
            raise ValueError(f'Shop declaration changed: {name!r}')
        raw = raw[:declaration.start()] + raw[end:]
    raw = replace(raw, b'm_bIsCreated\t\t= FALSE;',
                  b'm_byTotalPageNo = 0;\n\tm_eSelectedTradeMode = None_Mode;\n\tm_bySelectedSocketNo = 0;')
    raw = replace(raw, b'&m_uiPageUp', b'&m_uiPageBoard.Previous()')
    raw = replace(raw, b'&m_uiPageDown', b'&m_uiPageBoard.Next()')
    return raw + b'\n' + (native / 'client455_shop_window.inc').read_bytes()


def port_shop_window(raw, relative, section, native):
    if relative == SHOP + '.h':
        return shop_header(raw), True
    if relative == SHOP + '.cpp':
        return shop_source(raw, section, native), True
    if relative == 'define.h':
        return replace(raw, b'UII_SHOP_WINDOW\t\t\t\t\t8', b'UII_SHOP_WINDOW\t\t\t\t\t7'), True
    if relative == 'gameprogress/cgp_maingame.cpp':
        return replace(raw, b'Create( IBT_SHOP, 1, MAX_MERCHANT_ITEM_NUM )',
                       b'Create(IBT_SHOP, 1, 200)'), True
    if relative == 'gameobject/board/shopboard/cshoptradeboard.cpp':
        return replace(raw, b'uiItem.byUsableLevel\t= pOrgItem->GetUsableLevel();',
                       b'uiItem.byUsableLevel\t= pOrgItem->GetUsableLevel();\n'
                       b'\tuiItem.dwQuantity\t\t= pOrgItem->GetQuantity();'), True
    return raw, False
