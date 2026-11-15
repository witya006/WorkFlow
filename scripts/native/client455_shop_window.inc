// Ordinary merchant window and pager, target RVA 2987F0..29A99E.
#include "client455_money.h"
#include "client455_unit_view_skin.h"
#include "client455_language.h"
#include <algorithm>
#include <cstdio>
#include <cstring>
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

BOOL CGUIShopWindow::TakeInBuyItem(UI_SHOP_ITEM* data, BOOL insertAtBegin,
                                   const RF455StorePreview* preview)
{
    if (!data) return FALSE;
    auto item = std::make_unique<CGUIItem>();
    item->SetIconType455(0);
    item->SetItemID(data->dwMeshID);
    item->SetSpriteID(data->dwIconID);
    item->SetNum(WORD(data->dwQuantity));
    item->SetUsableLevel(data->byUsableLevel);
    item->SetGrade455(data->grade455);
    item->SetSize(32, 32);
    item->SetSprite();
    item->Show(IsShow());
    item->DrawItemNum(FALSE);
    const auto inserted = m_listBuyItem.insert(
        insertAtBegin ? m_listBuyItem.begin() : m_listBuyItem.end(), item.get());
    if (preview) {
        try {
            m_buyPreview455.emplace(item.get(), *preview);
        } catch (...) {
            m_listBuyItem.erase(inserted);
            throw;
        }
    }
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
    m_buyPreview455.erase(removed.get());
    m_listBuyItem.erase(at);
    UpdateShopBoard();
    return TRUE;
}

void CGUIShopWindow::ClearBuyItemList()
{
    if (m_eCurTradeMode == Buy_Mode) ClearShopBoard();
    m_buyPreview455.clear();
    for (auto* item : m_listBuyItem) delete item;
    m_listBuyItem.clear();
    if (m_eCurTradeMode == Buy_Mode) {
        ClearTradeItemList();
        UpdateShopBoard();
    }
}

void CGUIShopWindow::ShowBuyPreview455(WORD index)
{
    const auto found = m_buyPreview455.find(GetBuyableItem(index));
    if (found == m_buyPreview455.end() || found->second.name.empty()) {
        gScreen.RemoveTooltip();
        return;
    }

    const auto& preview = found->second;
    const auto& language = *RF455_GetNormalLanguagePack();
    const bool taiwan = language.codepage == 950;
    const bool localized = taiwan || language.codepage == 1251;
    char lines[4][TOOLTIP_MAX_STR] = {};
    const auto capacity = sizeof(lines[0]) - 1;
    std::size_t length = 0;
    while (length < preview.name.size() && length < capacity) {
        const auto byte = static_cast<unsigned char>(preview.name[length]);
        const std::size_t width = taiwan && IsDBCSLeadByteEx(language.codepage, byte) ? 2 : 1;
        if (length + width > capacity || length + width > preview.name.size()) break;
        length += width;
    }
    std::memcpy(lines[0], preview.name.data(), length);

    BYTE count = 1;
    if (localized && preview.currency <= 6) {
        // NDLanguage indices are selected by 455 RVA 0x24BB00.
        const unsigned race = BYTE(_GetAvatarRace()) / 2;
        const unsigned currencyLabel[] = {race < 3 ? 10 + race : 9, 9, 0xcf2, 0xcf2, 0xf75, 0xf76, 0x105e};
        const auto* unit = language.get(currencyLabel[preview.currency]);
        std::uint64_t price = preview.basePrice;
        const bool adjusted = RF455_CurrentShopUnitPrice(preview, price);
        const auto* label = adjusted
            ? (taiwan ? "\xbb\xf9\xae\xe6" : "\xd6\xe5\xed\xe0")
            : (taiwan ? "\xb0\xf2\xc2\xa6\xbb\xf9\xae\xe6" :
                        "\xc1\xe0\xe7\xee\xe2\xe0\xff \xf6\xe5\xed\xe0");
        char amount[32] = {};
        if (price <= 0x7fffffffffffffffULL)
            RF455_FormatMoney(static_cast<__int64>(price), amount);
        else
            std::snprintf(amount, sizeof(amount), "%llu", static_cast<unsigned long long>(price));
        if (unit && *unit && std::strlen(label) + std::strlen(amount) + std::strlen(unit) + 3 < sizeof(lines[0]))
            std::snprintf(lines[count], sizeof(lines[count]), "%s: %s %s", label, amount, unit);
        else
            std::snprintf(lines[count], sizeof(lines[count]), "%s: %s", label, amount);
        ++count;
    }
    if (localized && preview.sockets) {
        const auto* sockets = taiwan ? "\xb4\xa1\xbc\xd1" : "\xc3\xed\xb8\xe7\xe4\xe0";
        const auto* talics = taiwan ? "\xa6\xd0\xa5\xdb" : "\xd2\xe0\xeb\xe8\xea\xe8";
        std::snprintf(lines[count], sizeof(lines[count]), "%s: %u, %s: %u", sockets,
                      unsigned(preview.sockets), talics, unsigned(preview.installedTalics));
        ++count;
    }
    if (localized && preview.timed && preview.timer.durationSeconds) {
        // Big5 and Windows-1251 are the encodings expected by the legacy UI.
        const auto* format = taiwan
            ? "\xa6\xb3\xae\xc4\xb4\xc1\xad\xad: %u\xa4\xd1 %02u:%02u:%02u"
            : "\xd1\xf0\xee\xea \xe4\xe5\xe9\xf1\xf2\xe2\xe8\xff: %u \xe4. %02u:%02u:%02u";
        const unsigned seconds = preview.timer.durationSeconds;
        std::snprintf(lines[count], sizeof(lines[count]), format, seconds / 86400,
                      seconds / 3600 % 24, seconds / 60 % 60, seconds % 60);
        ++count;
    }
    gScreen.SetTooltip(count, lines);
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

void CGUIShopWindow::SetSelection455(const char* name, BOOL enabled)
{
    char label[256] = {};
    if (name) std::snprintf(label, sizeof(label), "%s x1", name);
    m_uiTitle.SetString(name ? label : RF455UnitView::Text(0x3c6));
    SetEnableTrade(enabled);
}
