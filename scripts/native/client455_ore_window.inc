// Ore processing panel, target RVA 2956D0..296890.
#include "client455_money.h"
#include "client455_unit_view_skin.h"

namespace {
void CenterOreLabel(CGUIText& label, LONG x, LONG y, LONG width, LONG height)
{
    label.SetPos(x + (width - label.GetSizeX()) / 2, y + (height - label.GetSizeY()) / 2);
}
}

void CGUIOreProcWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(*this, 10, 0, 0);
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    Button(m_uiProcButton, 1, 1, 0, true, true);
    Button(m_uiDisposalButton, 1, 1, 0, true, true);
    Button(m_uiOutputScrollBar.GetTopArrow455(), 1, 2, 12, false, false);
    Button(m_uiOutputScrollBar.GetBottomArrow455(), 1, 2, 14, false, false);
    POINT thumb = {5, 18};
    m_uiOutputScrollBar.SetBarSize(thumb);
    m_uiOutputScrollBar.SetMinimumThumb455(18);
    m_uiOutputScrollBar.SetBarColor455(0xffdea990);
    m_uiOutputScrollBar.SetSize(m_uiOutputScrollBar.GetTopArrow455().GetSizeX(), 150);
    if (!m_uiInputOreItem.IsEmpty()) m_uiInputOreItem.SetSprite();
    for (auto& item : m_uiOutputOreItem)
        if (!item.IsEmpty()) item.SetSprite();
}

void CGUIOreProcWindow::Init()
{
    using namespace RF455UnitView;
    SetSprite();
    const LONG x = GetPosX();
    const LONG y = GetPosY();
    m_uiTitle.SetString(Text(0x3b1));
    m_uiTitle.GetFont()->dwColor = 0xffc3c1be;
    m_uiDalant.SetString(Text(0x3bb));
    const unsigned race = BYTE(_GetAvatarRace()) / 2;
    m_uiOreCurrency455.SetString(race < 3 ? Text(10 + race) : nullptr);
    m_uiDalant.GetFont()->dwColor = m_uiOreCurrency455.GetFont()->dwColor = 0xffd4ba94;
    m_uiProcPrice.GetFont()->dwColor = 0xffc3c1be;
    m_uiResultTitle455.GetFont()->dwColor = m_uiResultHelp455.GetFont()->dwColor = 0xffe8e8e8;
    m_uiProcButton.SetLabel(Text(0x3bc));
    m_uiDisposalButton.SetLabel(Text(0x3bd));
    m_uiProcButton.SetLabelStyle(R3_HAN_OUTLINE);
    m_uiDisposalButton.SetLabelStyle(R3_HAN_OUTLINE);

    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    CenterOreLabel(m_uiDalant, x + 15, y + 109, 63, 16);
    CenterOreLabel(m_uiOreCurrency455, x + 151, y + 109, 63, 16);
    m_uiProcPrice.SetPos(x + 168, y + 111);
    m_uiInputOreItem.SetSize(64, 64);
    m_uiInputOreItem.SetPos(x + 82, y + 35);
    m_uiResultTitle455.SetPos(x + 52, y + 167);
    m_uiResultHelp455.SetPos(x + 52, y + 182);
    m_uiOutputScrollBar.SetPos(x + 211, y + 202);
    m_uiProcButton.SetPos(x + 80, y + 132);
    m_uiDisposalButton.SetPos(x + 80, y + 363);
    CGUIObject* header[] = {&m_uiAniTitleBar, &m_uiTitle, &m_uiDalant, &m_uiOreCurrency455, &m_uiProcPrice};
    for (auto* object : header) Add(object);
    for (unsigned i = 0; i < MAX_RESULT_ORE_SOCKET; ++i) {
        auto& socket = m_uiOutputOreSocket[i];
        socket.SetSize(34, 34);
        socket.SetPos(x + 20 + 38 * (i % 5), y + 204 + 38 * (i / 5));
        socket.AddMouseEventHandler(this);
        Add(&socket);
    }
    for (auto& item : m_uiOutputOreItem) {
        item.SetSize(32, 32);
        item.AddMouseEventHandler(this);
    }
    m_uiInputOreItem.AddMouseEventHandler(this);
    Add(&m_uiInputOreItem);
    AddMouseEventHandler(this);
    m_uiOutputScrollBar.AddScrollHandler(this);
    m_uiOutputScrollBar.SetAdjustmentUnit(35);
    CGUIObject* buttons[] = {&m_uiProcButton, &m_uiDisposalButton, &m_uiCloseButton, &m_uiHelpButton};
    for (auto* button : buttons) {
        button->AddMouseEventHandler(this);
        Add(button);
    }
    Add(&m_uiResultTitle455);
    Add(&m_uiResultHelp455);
    m_uiAniTitleBar.SetMouseInput455(FALSE);
    m_uiTitle.SetMouseInput455(FALSE);
    SetMoveObject(this);
    SetMovable(TRUE);
    SetName("OreProcWin");
    EnableDisposal(FALSE);
    EnableProc(FALSE);
    SetARGB(0xd8ffffff);
}

void CGUIOreProcWindow::EnableDisposal(BOOL enabled)
{
    if (enabled) {
        m_uiDisposalButton.Enable();
        m_uiResultTitle455.SetString(RF455UnitView::Text(0x3be));
        m_uiResultHelp455.SetString(RF455UnitView::Text(0x3bf));
        CenterOreLabel(m_uiResultTitle455, GetPosX(), m_uiResultTitle455.GetPosY(), GetSizeX(), m_uiResultTitle455.GetSizeY());
        CenterOreLabel(m_uiResultHelp455, GetPosX(), m_uiResultHelp455.GetPosY(), GetSizeX(), m_uiResultHelp455.GetSizeY());
    } else {
        m_uiDisposalButton.Disable();
        m_uiResultTitle455.SetString(nullptr);
        m_uiResultHelp455.SetString(nullptr);
    }
}

void CGUIOreProcWindow::SetProcPrice(__int64 value)
{
    char buffer[32] = {};
    RF455_FormatMoney(value, buffer);
    m_uiProcPrice.SetString(buffer);
    m_uiProcPrice.SetPos(GetPosX() + 142 - m_uiProcPrice.GetSizeX(), m_uiDalant.GetPosY());
}
