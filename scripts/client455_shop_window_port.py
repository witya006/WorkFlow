"""Install the 455 merchant window in the ordinary client build."""
import re


SHOP = 'userinterface/gamewindow/npc/guishopwindow'


def replace(raw, before, after):
    if raw.count(before) != 1:
        raise ValueError(f'Shop source anchor changed: {before!r}')
    return raw.replace(before, after)


def shop_header(raw):
    raw = replace(raw, b'BYTE\tbyUsableLevel;', b'BYTE\tbyUsableLevel;\n\tBYTE grade455 = 0;')
    for before, after in (
        (b'CGUIObjectAni\t\t\tm_uiAniTitleBar;', b'RF455GuiAnimatedImage m_uiAniTitleBar;'),
        (b'CGUIObject\t\t\t\tm_uiPageBoard;', b'RF455GuiPageBoard m_uiPageBoard;'),
        (b'CGUIButton\t\t\t\tm_uiPageUp;', b''),
        (b'CGUIButton\t\t\t\tm_uiPageDown;', b''),
        (b'CGUIText\t\t\t\tm_uiCurPageStr;', b''),
        (b'm_uiGold;', b'm_uiGold;\n\tCGUIText m_uiPvpLabel455, m_uiPointLabel455, m_uiPvpValue455, m_uiPointValue455;'),
        (b'BOOL\t\t\t\t\tm_bIsCreated;', b'bool m_previewCatalog455 = false;\n'
         b'\tstd::unordered_map<const CGUIItem*, RF455StorePreview> m_buyPreview455;\n'
         b'\tvoid ShowBuyPreview455(WORD index);'),
        (b'TakeInBuyItem( UI_SHOP_ITEM * pi_pItemInfo, BOOL pi_bInsertAtBegin = FALSE );',
         b'TakeInBuyItem(UI_SHOP_ITEM* data, BOOL insertAtBegin = FALSE,\n'
         b'\t\t\t\t\t\t  const RF455StorePreview* preview = nullptr);'),
        (b'SetDalant( DWORD pi_dwDalant );', b'SetDalant(__int64 value);'),
        (b'SetGold( DWORD pi_dwGold );', b'SetGold(__int64 value);\n\tvoid SetPvp455(DWORD value);\n\tvoid SetPoints455(DWORD value);'),
        (b'private:\n\t\n\t\t\tvoid\t\tTabLabelPosSetting( TradeMode pi_eTradeMode, BOOL pi_bIsActive );', b''),
    ):
        raw = replace(raw, before, after)
    raw = replace(raw, b'\tCGUIShopWindow();', b'\tCGUIShopWindow();\n\tvoid SetPreviewCatalog455(bool value) { m_previewCatalog455 = value; }\n'
                  b'\tvoid SetSelection455(const char* name, BOOL enabled);')
    return replace(raw, b'#include "../../UIGlobal.h"',
                   b'#include "../../UIGlobal.h"\n#include "client455_briefing_controls.h"\n'
                   b'#include "client455_gui_page_board.h"\n#include "client455_client_items.h"\n'
                   b'#include <unordered_map>')


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
    raw = replace(raw, b'\t\t\tSetQuickEvent();', b'''        if (m_previewCatalog455) {
                PostUIMessage(WM_BOARD_TRADE_HOT_KEY, UI_MOUSE_MSG(0, bySocketNo, 1, 0));
                return;
            }
\t\t\tSetQuickEvent();''')
    hover = b'BYTE bySocketNo = m_byCurPageNo * TOTAL_SHOP_ITEM_SOCKET + i;'
    raw = replace(raw, hover, hover + b'''
                if (m_eCurTradeMode == Buy_Mode && m_previewCatalog455) {
                    ShowBuyPreview455(bySocketNo);
                    return;
                }''')
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
    if relative == 'gameobject/board/shopboard/cshoptradeboard.h':
        raw = b'#include "client455_shop_transactions.h"\n#include <vector>\n' + raw
        raw = replace(raw, b'\tCShopTradeBoard();', b'''    bool m_catalogActive455 = false;
    RF455ShopPending455 m_pending455;
    std::vector<RF455ShopPending455> m_buyChoices455, m_sellChoices455;
    const RF455ShopPending455& PendingTransaction455() const { return m_pending455; }
    void FinishTransaction455();
    void RebuildSellChoices455();
    BOOL SelectTransaction455(unsigned index);
    BOOL RequestSelected455();
    virtual void CloseWindow() override;
\tCShopTradeBoard();''')
        return raw, True
    if relative == 'gameobject/board/shopboard/cshoptradeboard.cpp':
        raw = b'#include "client455_item_icon_metadata.h"\n#include "client455_client_items.h"\n#include <stdexcept>\n' + raw
        anchor = b'\tSetTradeMode( STM_BUY );'
        first, last = section(raw, b'CShopTradeBoard::OpenShopWindow(', b'CShopTradeBoard::OpenShopWindow(')
        body = replace(raw[first:last], anchor, anchor + b'''

    FinishTransaction455();
    m_catalogActive455 = false;
    m_buyChoices455.clear();
    m_sellChoices455.clear();
    m_uiShopWindow.SetPreviewCatalog455(false);
    RF455StoreNpcView store;
    if (_GetCharDataMgr()->Tables455().storeNpcByIndex(pi_dwNpcIndex, store)) {
        // UI rows map to catalog slots, never to compacted display indices.
        const auto& catalog = RF455_GameItems();
        const auto& items = catalog.data;
        const auto products = RF455_ResolveStoreProducts(store, items);
        ClearShopItemList();
        m_catalogActive455 = true;
        m_uiShopWindow.SetPreviewCatalog455(true);
        m_pMerchant = pMerchant;
        m_dwNpcIndex = pi_dwNpcIndex;
        for (const auto& product : products) {
            const auto row = items.getItemExtent(product.kind, product.itemIndex);
            try {
                const auto icon = RF455_ReadBasicIconMetadata(row, 1);
                UI_SHOP_ITEM entry{};
                entry.dwIndex = product.storeSlot;
                entry.dwMeshID = icon.itemID;
                entry.dwIconID = icon.spriteID;
                entry.dwQuantity = icon.quantity;
                entry.byUsableLevel = icon.usableLevel;
                entry.grade455 = icon.grade;
                RF455StorePreview preview;
                const bool hasPreview = catalog.makeStorePreview(
                    product.kind, product.itemIndex, preview, store.upgradeCode, store.priceMultiplier);
                if (m_uiShopWindow.TakeInBuyItem(&entry, FALSE, hasPreview ? &preview : nullptr)) {
                    RF455ShopPending455 choice;
                    choice.kind = RF455ShopPending455::Buy;
                    choice.merchant = pi_dwNpcIndex;
                    choice.catalogSlot = product.storeSlot;
                    choice.itemKind = product.kind;
                    choice.itemIndex = product.itemIndex;
                    m_buyChoices455.push_back(choice);
                }
            } catch (const std::out_of_range&) {
                // The table resolver can find a product lacking icon metadata.
                // Leave it out of the display without affecting other products.
            }
        }
        OpenWindow();
        return;
    }
''')
        at = body.index(b'{') + 1
        body = body[:at] + b'\n    if (m_pending455.sent) return;\n' + body[at:]
        raw = raw[:first] + body + raw[last:]
        # Intercept the existing grid/OK/tab events before any old derived item
        # cast or obsolete transaction opcode can be reached.
        first, last = section(raw, b'CShopTradeBoard::MsgProc(', b'CShopTradeBoard::MsgProc(')
        body = raw[first:last]
        anchor = b'\tUI_MOUSE_MSG\tstRecvMsg( lParam );'
        body = replace(body, anchor, anchor + b'''
    if (m_catalogActive455) {
        switch (uMsg) {
        case WM_BOARD_TRADE_HOT_KEY:
        case WM_BOARD_CHECK_REMOVE_OBJECT:
            SelectTransaction455(stRecvMsg.m_bySocketNo); return 0;
        case WM_BOARD_TRADE:
            RequestSelected455(); return 0;
        case WM_BOARD_CHANGE_TRADE_MODE:
            if (m_pending455.sent) return 0;
            FinishTransaction455();
            if (stRecvMsg.m_byPackNo == STM_BUY || stRecvMsg.m_byPackNo == STM_SELL) {
                SetTradeMode(stRecvMsg.m_byPackNo);
                if (m_byTradeMode == STM_SELL) RebuildSellChoices455();
            }
            return 0;
        case WM_BOARD_CANCEL_TRADE:
            if (!m_pending455.sent) FinishTransaction455();
            return 0;
        case WM_BOARD_ADD_OBJECT: // Ordinary sale uses the bag list in Sell tab.
        case WM_BOARD_REMOVE_OBJECT:
        case WM_BOARD_HOVER_OBJECT:
            return 0;
        case WM_CLOSING_WINDOW:
        case WM_CLOSE_WINDOW:
            if (m_pending455.sent) return 1;
            FinishTransaction455();
            break;
        }
    }
''')
        raw = raw[:first] + body + raw[last:]
        # These public legacy entry points can also be reached outside MsgProc.
        for name, guard in (
            (b'BuyItem_Request', b'if (m_catalogActive455) return RequestSelected455();'),
            (b'SellItem_Request', b'if (m_catalogActive455) return RequestSelected455();'),
            (b'RepairItem_Request', b'if (m_catalogActive455) return FALSE;'),
            (b'BuyItem_Result', b'if (m_catalogActive455) return;'),
            (b'SellItem_Result', b'if (m_catalogActive455) return;'),
            (b'RepairItem_Result', b'if (m_catalogActive455) return FALSE;'),
            (b'CancelTrade', b'if (m_catalogActive455) { if (!m_pending455.sent) FinishTransaction455(); return; }'),
            (b'SelectBuyItem', b'if (m_catalogActive455) return FALSE;'),
            (b'SelectSellItem', b'if (m_catalogActive455) return FALSE;'),
            (b'SelectRepairItem', b'if (m_catalogActive455) return FALSE;'),
            (b'UI_AddRequest_ProcessObject', b'if (m_catalogActive455) return FALSE;'),
            (b'UI_RemoveRequest_ProcessObject', b'if (m_catalogActive455) return FALSE;'),
            (b'UI_SelectItem_By_HotKey', b'if (m_catalogActive455) { SelectTransaction455(pi_bySocketNo); return; }'),
        ):
            first, last = section(raw, b'CShopTradeBoard::' + name + b'(', b'CShopTradeBoard::' + name + b'(')
            body = raw[first:last]
            at = body.index(b'{') + 1
            raw = raw[:first] + body[:at] + b'\n    ' + guard + b'\n' + body[at:] + raw[last:]
        raw += b'\n' + (native / 'client455_shop_transactions.inc').read_bytes()
        return replace(raw, b'uiItem.byUsableLevel\t= pOrgItem->GetUsableLevel();',
                       b'uiItem.byUsableLevel\t= pOrgItem->GetUsableLevel();\n'
                       b'\tuiItem.dwQuantity\t\t= pOrgItem->GetQuantity();'), True
    return raw, False
