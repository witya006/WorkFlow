// Currency exchange in the 455 window at RVA 290AF0.
#include "client455_money.h"
#include "client455_unit_view_skin.h"

#include <algorithm>
#include <cmath>
#include <cstdio>

namespace {
constexpr LONG MaxExchangeGold = 100000000;

void ExchangeDirection(CGUIText& label, const char* from, const char* to)
{
    char buffer[128] = {};
    const char* format = RF455UnitView::Text(0x13c4);
    if (format && from && to) std::snprintf(buffer, sizeof buffer, format, from, to);
    label.SetString(buffer);
}

void ExchangeAmount(CGUIText& label, LONG right, __int64 amount)
{
    char buffer[32];
    RF455_FormatMoney(amount, buffer);
    label.SetString(buffer);
    label.SetPos(right - label.GetSizeX(), label.GetPosY());
}
}

void CGUIExchangeWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(m_uiBase, 12, 0, 0);
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    Button(m_uiExchangeButton, 1, 1, 0, true, true);
    Button(m_uiRecoveryButton, 1, 1, 0, true, true);

    auto& slider = m_uiExchangeAdjScrollbar;
    Bind(slider, 1, 8, 6);
    const LONG trackWidth = slider.GetSizeX(), trackHeight = slider.GetSizeY();
    // The thumb uses one image in every state. The arrows have two frames each.
    Bind(slider.GetButton455(), 1, 8, 7);
    auto thumb = Image(1, 8, 7);
    slider.GetButton455().SetSpriteInfoEx(&thumb);
    Button(slider.GetTopArrow455(), 1, 8, 8, false, false);
    Button(slider.GetBottomArrow455(), 1, 8, 10, false, false);
    slider.SetAutoThumb455(FALSE);
    slider.SetStyle(CGUIScrollbar::Horizontal);
    slider.SetSize(trackWidth + slider.GetTopArrow455().GetSizeX() + slider.GetBottomArrow455().GetSizeX(), trackHeight);
}

void CGUIExchangeWindow::Init()
{
    using namespace RF455UnitView;
    SetSprite();
    SetSize(228, 419);
    const LONG x = GetPosX(), y = GetPosY();
    m_uiBase.SetPos(x, y);
    const unsigned race = BYTE(_GetAvatarRace()) / 2;
    char* currency = Text(10 + (race < 3 ? race : 0));
    char* gold = Text(9);
    m_uiTitle.SetString(Text(0x13c2));
    m_uiFeeTitle.SetString(Text(0x13c3));
    m_uiAssetsTitle.SetString(Text(0x3a4));
    m_uiGoldStr.SetString(gold);
    m_uiDalantStr.SetString(currency);
    m_uiAdjustTitle.SetString(Text(0x3a5));
    m_uiExchangeButton.SetLabel(Text(0x1cf));
    ExchangeDirection(m_uiBuyDirection, currency, gold);
    ExchangeDirection(m_uiSellDirection, gold, currency);
    for (unsigned i = 0; i < 4; ++i) m_uiFeeNotes[i].SetString(Text(0x13c5 + i));

    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    CGUIText* centered[] = {&m_uiFeeTitle, &m_uiBuyDirection, &m_uiFeeNotes[0], &m_uiFeeNotes[1],
                           &m_uiSellDirection, &m_uiFeeNotes[2], &m_uiFeeNotes[3], &m_uiAssetsTitle,
                           &m_uiAdjustTitle};
    const LONG rows[] = {50, 80, 100, 115, 145, 165, 180, 263, 337};
    for (unsigned i = 0; i < std::size(centered); ++i)
        centered[i]->SetPos(x + (228 - centered[i]->GetSizeX()) / 2, y + rows[i]);
    m_uiGoldStr.SetPos(x + 15 + (94 - m_uiGoldStr.GetSizeX()) / 2, y + 285 + (15 - m_uiGoldStr.GetSizeY()) / 2);
    m_uiDalantStr.SetPos(x + 120 + (94 - m_uiDalantStr.GetSizeX()) / 2, y + 285 + (15 - m_uiDalantStr.GetSizeY()) / 2);
    m_uiGold.SetPos(x, y + 302);
    m_uiDalant.SetPos(x, y + 302);
    m_uiExchangeAdjScrollbar.SetPos(x + 18, y + 353);
    m_uiExchangeButton.SetPos(x + 81, y + 385);
    m_uiTitle.GetFont()->dwColor = 0xffc3c1be;
    m_uiBuyDirection.GetFont()->dwColor = m_uiSellDirection.GetFont()->dwColor = 0xffe3e0d9;
    m_uiAdjustTitle.GetFont()->dwColor = 0xffe3e0d9;
    m_uiBuyDirection.GetFont()->dwStyle = m_uiSellDirection.GetFont()->dwStyle = R3_HAN_OUTLINE;
    m_uiExchangeButton.SetLabelStyle(R3_HAN_OUTLINE);

    for (auto* button : {static_cast<CGUIButton*>(&m_uiExchangeButton), &m_uiCloseButton, &m_uiHelpButton})
        button->AddMouseEventHandler(this);
    m_uiExchangeAdjScrollbar.AddScrollHandler(this);
    CGUIObject* children[] = {&m_uiBase, &m_uiAniTitleBar, &m_uiTitle, &m_uiCloseButton, &m_uiHelpButton,
                             &m_uiFeeTitle, &m_uiBuyDirection, &m_uiExchangeButton, &m_uiExchangeAdjScrollbar,
                             &m_uiAdjustTitle, &m_uiFeeNotes[0], &m_uiFeeNotes[1], &m_uiFeeNotes[2],
                             &m_uiFeeNotes[3], &m_uiSellDirection, &m_uiDalantStr, &m_uiDalant, &m_uiGoldStr,
                             &m_uiGold, &m_uiAssetsTitle};
    for (auto* object : children) Add(object);
    m_uiTitle.SetMouseInput455(FALSE);
    SetMoveObject(&m_uiAniTitleBar);
    SetMovable(TRUE);
    SetARGB(0xd8ffffff);
    EnableExchange(FALSE);
    EnableRecovery(FALSE);
    SetExchangeRate(1000);
}

// These economy graph operations are empty in 455. Existing callers still use their names.
void CGUIExchangeWindow::SetRaceType(BYTE) {}
void CGUIExchangeWindow::InitEconomyRatePoint(BYTE, BYTE, WORD*) {}
void CGUIExchangeWindow::InsertEconomyRatePoint(BYTE, int) {}

void CGUIExchangeWindow::SetExchangeRate(DWORD rate)
{
    m_dwDalantPerGold = rate;
    SetExchangeAdjustbar();
}

void CGUIExchangeWindow::SetExchangeCommission(float commission)
{
    m_fExchangeCommission = commission;
    SetExchangeAdjustbar();
}

void CGUIExchangeWindow::SetExchangeAdjustbar()
{
    if (!g_pUiInventWindow || !m_dwDalantPerGold) return;
    const auto gold = std::max<__int64>(0, std::min<__int64>(g_pUiInventWindow->GetOwnGold(), MaxExchangeGold));
    const double unit = double(m_dwDalantPerGold) * (1.0 + double(m_fExchangeCommission));
    if (!std::isfinite(unit) || unit <= 0) return;
    const auto buyingPower = double(g_pUiInventWindow->GetOwnDalant()) / unit;
    const LONG available = static_cast<LONG>(std::max<double>(0.0, std::min<double>(buyingPower, MaxExchangeGold - gold)));
    m_uiExchangeAdjScrollbar.SetAmount(static_cast<LONG>(gold) + available, available);
}

void CGUIExchangeWindow::SetTaxRate(float tax)
{
    char buffer[32];
    std::snprintf(buffer, sizeof buffer, "%.2f%%", double(tax));
    m_uiTaxRateStr.SetString(buffer);
}

void CGUIExchangeWindow::SetGold(__int64 amount)
{
    m_dwGold = amount;
    ExchangeAmount(m_uiGold, m_uiBase.GetPosX() + 102, amount);
}

void CGUIExchangeWindow::SetDalant(__int64 amount)
{
    m_dwDalant = amount;
    ExchangeAmount(m_uiDalant, m_uiBase.GetPosX() + 207, amount);
}

void CGUIExchangeWindow::ScrollEvent(_scroll_event&)
{
    if (!g_pUiInventWindow) return;
    const auto gold = g_pUiInventWindow->GetOwnGold();
    const auto dalant = g_pUiInventWindow->GetOwnDalant();
    SetGold(m_uiExchangeAdjScrollbar.GetTotalAmount() - m_uiExchangeAdjScrollbar.GetCurrentAmount());
    const auto delta = m_dwGold - gold;
    const auto exchange = delta * m_dwDalantPerGold;
    // Buying adds 5 percent. Selling uses the base rate.
    SetDalant(dalant - exchange - (delta > 0 ? exchange / 20 : 0));
    EnableExchange(delta != 0);
    EnableRecovery(delta != 0);
}
