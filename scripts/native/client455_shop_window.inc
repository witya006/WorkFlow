// Ordinary merchant window and pager, target RVA 2987F0..29A99E.
#include "client455_money.h"
#include "client455_unit_view_skin.h"
#include <algorithm>
#include <cstdio>
#include <iterator>
#include <memory>

namespace {
constexpr DWORD ShopLabelColor = 0xffc4c4c4;
constexpr DWORD ShopValueColor = 0xffc3c1be;

void CenterShopText(CGUIText& text, LONG x, LONG y, LONG width, LONG height)
{
    text.SetPos(x + (width - text.GetSizeX()) / 2, y + (height - text.GetSizeY()) / 2);
}

void SetShopValue(CGUIWindow& window, CGUIText& text, LONG y, __int64 value)
{
    char buffer[32] = {};
    RF455_FormatMoney(value, buffer);
    text.SetString(buffer);
    text.SetPos(window.GetPosX() + 136 - text.GetSizeX(),
                window.GetPosY() + y + (16 - text.GetSizeY()) / 2);
}
}

void CGUIShopWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(*this, 9, 0, 0);
    for (auto& tab : m_uiTradeTab) {
        auto normal = Image(9, 0, 2);
        auto selected = Image(9, 0, 1);
        tab.SetSpriteInfoEx(&normal);
        tab.SetSpriteInfoEx(DISABLED, &selected);
        tab.SetSize(normal.pSprite->GetSpriteOrgXL(0, 2), normal.pSprite->GetSpriteOrgYL(0, 2));
    }
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiOKButton, 1, 1, 0, true, true);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    m_uiPageBoard.SetSprite();
}

void CGUIShopWindow::Init()
{
    using namespace RF455UnitView;
    SetSprite();
    const LONG x = GetPosX(), y = GetPosY();
    m_uiTitle.SetString(Text(0x3c6));
    const unsigned race = BYTE(_GetAvatarRace()) / 2;
    m_uiDalant.SetString(race < 3 ? Text(10 + race) : nullptr);
    m_uiGold.SetString(Text(0x3c7));
    m_uiPvpLabel455.SetString("PVP");
    m_uiPointLabel455.SetString(Text(0x105d));
    m_uiTradeTab[Buy_Mode].SetLabel(Text(0x3c8));
    m_uiTradeTab[Sell_Mode].SetLabel(Text(0x3ca));
    m_uiTradeTab[Repair_Mode].SetLabel(Text(0x3c9));
    m_uiOKButton.SetLabel(Text(0x35d));
    m_uiOKButton.SetLabelStyle(R3_HAN_OUTLINE);
    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);

    m_uiPageBoard.Initialize(x + 20, y + 223, this);

    CGUIText* labels[] = {&m_uiDalant, &m_uiGold, &m_uiPvpLabel455, &m_uiPointLabel455};
    const LONG labelY[] = {295, 324, 353, 382};
    for (unsigned i = 0; i < 4; ++i) {
        CenterShopText(*labels[i], x + 148, y + labelY[i], 57, 17);
        labels[i]->GetFont()->dwColor = i < 3 ? ShopLabelColor : ShopValueColor;
    }
    m_uiTitle.GetFont()->dwColor = ShopValueColor;
    m_uiTradeMoneyTitle.GetFont()->dwColor = ShopLabelColor;
    m_uiTotalTradeDalantStr.GetFont()->dwColor = ShopValueColor;
    m_uiTotalTradeGoldStr.GetFont()->dwColor = ShopValueColor;
    m_uiPvpValue455.GetFont()->dwColor = ShopValueColor;
    m_uiPointValue455.GetFont()->dwColor = ShopValueColor;
    m_uiOKButton.SetPos(x + 80, y + 421);
    m_uiOKButton.SetLabelColor(0xffe8e8e8);

    Add(&m_uiAniTitleBar);
    Add(&m_uiTitle);
    Add(&m_uiPageBoard);
    Add(&m_uiTradeMoneyTitle);
    Add(&m_uiTotalTradeDalantStr);
    Add(&m_uiTotalTradeGoldStr);
    Add(&m_uiPvpValue455);
    Add(&m_uiPointValue455);
    Add(&m_uiPointLabel455);
    Add(&m_uiPvpLabel455);
    Add(&m_uiDalant);
    Add(&m_uiGold);
    Add(&m_uiCloseButton);
    Add(&m_uiHelpButton);
    m_uiCloseButton.AddMouseEventHandler(this);
    m_uiHelpButton.AddMouseEventHandler(this);
    for (auto& tab : m_uiTradeTab) {
        tab.AddMouseEventHandler(this);
        tab.SetLabelColor(0xffe8e8e8);
        tab.SetARGB(0xd8ffffff);
    }
    for (BYTE i = 0; i < TOTAL_SHOP_ITEM_SOCKET; ++i) {
        auto& slot = m_uiShopItemBoard[i];
        slot.SetSize(34, 34);
        slot.SetPos(x + 21 + 38 * (i % 5), y + 64 + 38 * (i / 5));
        slot.AddMouseEventHandler(this);
        Add(&slot);
    }
    m_uiOKButton.AddMouseEventHandler(this);
    Add(&m_uiOKButton);
    SetMoveObject(this);
    SetMovable(TRUE);
    SetName("Shop");
    SetDalant(0);
    SetGold(0);
    SetPvp455(0);
    SetPoints455(0);
    SetCurrentShopBoard(0);
    SetARGB(0xd8ffffff);
}

void CGUIShopWindow::SetShopType(ShopType type)
{
    m_eCurShopType = type;
    Remove(&m_uiTradeTab[Repair_Mode]);
    m_uiTradeTab[Buy_Mode].SetPos(GetPosX() + 17, GetPosY() + 31);
    m_uiTradeTab[Sell_Mode].SetPos(GetPosX() + 119, GetPosY() + 31);
    Add(&m_uiTradeTab[Buy_Mode]);
    Add(&m_uiTradeTab[Sell_Mode]);
}

void CGUIShopWindow::SetTradeMode(TradeMode mode)
{
    if (m_eCurTradeMode <= Repair_Mode) m_uiTradeTab[m_eCurTradeMode].Enable();
    m_eCurTradeMode = mode;
    if (mode > Repair_Mode) return;
    m_uiTradeTab[mode].Disable();
    m_uiTradeMoneyTitle.SetString(RF455UnitView::Text(0x3cb + mode));
    CenterShopText(m_uiTradeMoneyTitle, GetPosX() + 78, GetPosY() + 264, 73, 18);
    UpdateShopBoard();
}

BOOL CGUIShopWindow::TakeInBuyItem(UI_SHOP_ITEM* data, BOOL insertAtBegin)
{
    if (!data) return FALSE;
    auto item = std::make_unique<CGUIItem>();
    item->SetIconType455(0);
    item->SetItemID(data->dwMeshID);
    item->SetSpriteID(data->dwIconID);
    item->SetNum(WORD(data->dwQuantity));
    item->SetUsableLevel(data->byUsableLevel);
    item->SetSize(32, 32);
    item->SetSprite();
    item->Show(IsShow());
    item->DrawItemNum(FALSE);
    m_listBuyItem.insert(insertAtBegin ? m_listBuyItem.begin() : m_listBuyItem.end(), item.get());
    item.release();
    UpdateShopBoard();
    return TRUE;
}

BOOL CGUIShopWindow::TakeOutBuyItem(DWORD index)
{
    if (index >= m_listBuyItem.size()) return FALSE;
    auto at = m_listBuyItem.begin();
    std::advance(at, index);
    std::unique_ptr<CGUIItem> removed(*at);
    m_listBuyItem.erase(at);
    UpdateShopBoard();
    return TRUE;
}

void CGUIShopWindow::ClearBuyItemList()
{
    if (m_eCurTradeMode == Buy_Mode) ClearShopBoard();
    for (auto* item : m_listBuyItem) delete item;
    m_listBuyItem.clear();
    if (m_eCurTradeMode == Buy_Mode) {
        ClearTradeItemList();
        UpdateShopBoard();
    }
}

void CGUIShopWindow::TakeInTradeItem(DWORD index, DWORD itemId, DWORD icon, BYTE quantity)
{
    auto entry = std::make_unique<TRADE_ITEM_INFO>();
    auto item = std::make_unique<CGUIItem>();
    item->SetIconType455(0);
    item->SetItemID(itemId);
    item->SetSpriteID(icon);
    item->SetSprite();
    item->SetNum(quantity);
    item->DrawItemNum(TRUE);
    item->SetSize(32, 32);
    entry->pItem = item.get();
    entry->dwListIndex = index;
    m_listTradeItem.push_back(entry.get());
    item.release();
    entry.release();
    UpdateShopBoard();
}

void CGUIShopWindow::TakeOutTradeItem(DWORD index)
{
    const auto found = std::find_if(m_listTradeItem.begin(), m_listTradeItem.end(),
                                   [index](const TRADE_ITEM_INFO* entry) { return entry->dwListIndex == index; });
    if (found == m_listTradeItem.end()) return;
    std::unique_ptr<TRADE_ITEM_INFO> entry(*found);
    std::unique_ptr<CGUIItem> removed(entry->pItem);
    m_listTradeItem.erase(found);
    UpdateShopBoard();
}

void CGUIShopWindow::ClearTradeItemList()
{
    const bool active = m_eCurTradeMode == Sell_Mode || m_eCurTradeMode == Repair_Mode;
    if (active) ClearShopBoard();
    for (auto* entry : m_listTradeItem) {
        delete entry->pItem;
        delete entry;
    }
    m_listTradeItem.clear();
    if (active) UpdateShopBoard();
}

void CGUIShopWindow::UpdateShopBoard()
{
    if (m_eCurTradeMode == None_Mode) return;
    const auto count = m_eCurTradeMode == Buy_Mode ? m_listBuyItem.size() : m_listTradeItem.size();
    m_byTotalPageNo = BYTE((count + TOTAL_SHOP_ITEM_SOCKET - 1) / TOTAL_SHOP_ITEM_SOCKET);
    m_uiPageBoard.SetCount(m_byTotalPageNo);
    SetCurrentShopBoard(m_byCurPageNo);
}

void CGUIShopWindow::SetCurrentShopBoard(BYTE requested)
{
    m_uiPageBoard.SetPage(requested);
    m_byCurPageNo = BYTE(m_uiPageBoard.Current());

    ClearShopBoard();
    if (!m_byTotalPageNo) return;
    const unsigned first = unsigned(m_byCurPageNo) * TOTAL_SHOP_ITEM_SOCKET;
    if (m_eCurTradeMode == Buy_Mode) {
        auto at = m_listBuyItem.begin();
        std::advance(at, (std::min)(std::size_t(first), m_listBuyItem.size()));
        for (unsigned i = 0; i < TOTAL_SHOP_ITEM_SOCKET && at != m_listBuyItem.end(); ++i, ++at)
            m_uiShopItemBoard[i].SetItem(*at);
    } else {
        auto at = m_listTradeItem.begin();
        std::advance(at, (std::min)(std::size_t(first), m_listTradeItem.size()));
        for (unsigned i = 0; i < TOTAL_SHOP_ITEM_SOCKET && at != m_listTradeItem.end(); ++i, ++at)
            m_uiShopItemBoard[i].SetItem((*at)->pItem);
    }
}

void CGUIShopWindow::SetDalant(__int64 value) { SetShopValue(*this, m_uiTotalTradeDalantStr, 296, value); }
void CGUIShopWindow::SetGold(__int64 value) { SetShopValue(*this, m_uiTotalTradeGoldStr, 325, value); }
void CGUIShopWindow::SetPvp455(DWORD value) { SetShopValue(*this, m_uiPvpValue455, 353, value); }
void CGUIShopWindow::SetPoints455(DWORD value) { SetShopValue(*this, m_uiPointValue455, 382, value); }
