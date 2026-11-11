// Item upgrade view from the 455 Taiwan skin and virtual dispatch.
#include "client455_unit_view_skin.h"

void CGUIItemUpgradeWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(*this, 15, 0, 0);
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    Button(m_uiUpgradeButton, 1, 1, 4, true, true);
    Button(m_uiReturnButton455, 1, 1, 4, true, true);
    for (auto& item : m_uiUpgradeItem)
        if (!item.IsEmpty()) item.SetSprite();
}

void CGUIItemUpgradeWindow::Init()
{
    using namespace RF455UnitView;
    SetSprite();
    const LONG x = GetPosX(), y = GetPosY();
    m_uiTitle.SetString(Text(0x37c));
    m_uiTitle.GetFont()->dwColor = 0xffc7bdb6;
    m_uiUpgradeButton.SetLabel(Text(0x37c));
    m_uiReturnButton455.SetLabel(Text(0x6b));
    m_uiUpgradeButton.SetLabelStyle(R3_HAN_OUTLINE);
    m_uiReturnButton455.SetLabelStyle(R3_HAN_OUTLINE);
    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    m_uiUpgradeButton.SetPos(x + 32, y + 363);
    m_uiReturnButton455.SetPos(x + 118, y + 363);
    Add(&m_uiReturnButton455);
    Add(&m_uiAniTitleBar);
    Add(&m_uiTitle);
    constexpr POINT positions[] = {{82, 134}, {98, 53}, {11, 125}, {185, 125}, {159, 222}, {37, 222}};
    static_assert(sizeof(positions) / sizeof(positions[0]) == TOTAL_UPGRADE_SOCKET_NO, "455 upgrade slots");
    for (unsigned i = 0; i < TOTAL_UPGRADE_SOCKET_NO; ++i) {
        auto& item = m_uiUpgradeItem[i];
        const LONG side = i ? 32 : 64;
        item.SetSize(side, side);
        item.SetPos(x + positions[i].x, y + positions[i].y);
        item.AddMouseEventHandler(this);
        Add(&item);
    }
    for (auto* control : {static_cast<CGUIButton*>(&m_uiUpgradeButton), &m_uiCloseButton, &m_uiHelpButton}) {
        control->AddMouseEventHandler(this);
        Add(control);
    }
    m_uiReturnButton455.AddMouseEventHandler(this);
    SetMoveObject(this);
    SetMoveObject(&m_uiAniTitleBar);
    SetMoveObject(&m_uiTitle);
    SetMovable(TRUE);
    EnableUpgrade(FALSE);
    UpdateReturnButton455();
    SoundOn(TRUE);
    SetARGB(0xd0ffffff);
}

BOOL CGUIItemUpgradeWindow::TakeInItem(BYTE, BYTE slot, DWORD itemId, DWORD spriteId, BYTE quantity, BYTE)
{
    if (slot >= TOTAL_UPGRADE_SOCKET_NO) return FALSE;
    auto& item = m_uiUpgradeItem[slot];
    item.SetIconType455(0);
    item.SetItemID(itemId);
    item.SetSpriteID(spriteId);
    item.SetNum(quantity);
    item.SetSprite();
    UpdateReturnButton455();
    return TRUE;
}

BOOL CGUIItemUpgradeWindow::TakeOutItem(BYTE, BYTE slot, BYTE, CGUIItem*)
{
    if (slot >= TOTAL_UPGRADE_SOCKET_NO || m_uiUpgradeItem[slot].IsEmpty()) return FALSE;
    m_uiUpgradeItem[slot].SetEmpty();
    UpdateReturnButton455();
    return TRUE;
}

CGUIItem* CGUIItemUpgradeWindow::GetItem(BYTE, BYTE slot)
{
    if (slot >= TOTAL_UPGRADE_SOCKET_NO || m_uiUpgradeItem[slot].IsEmpty()) return nullptr;
    return &m_uiUpgradeItem[slot];
}

void CGUIItemUpgradeWindow::UpdateReturnButton455()
{
    const bool hasMainItem = !m_uiUpgradeItem[UpgradeItem].IsEmpty();
    const bool hasCrystal = !m_uiUpgradeItem[Crystal].IsEmpty();
    if (hasMainItem || hasCrystal) {
        m_uiReturnButton455.Enable();
        m_uiReturnButton455.SetLabelColor(0xffff0000);
    } else {
        m_uiReturnButton455.Disable();
        m_uiReturnButton455.SetLabelColor(0xff8d8d8d);
    }
    if (!hasMainItem || !hasCrystal) EnableUpgrade(FALSE);
}

void CGUIItemUpgradeWindow::MouseEvent(_mouse_event& event)
{
    CGUIWindow::MouseEvent(event);
    if (event.id == MOUSE_CLICKED) {
        if (event.source == &m_uiUpgradeButton) PostUIMessage(WM_ITEM_UPGRADE_BOARD_PROCESS, 0);
        else if (event.source == &m_uiReturnButton455) PostUIMessage(WM_ITEM_UPGRADE_BOARD_CANCEL, 0);
        else if (event.source == &m_uiHelpButton) PostUIMessage(WM_OPEN_WINDOW_HELP, 0);
        else if (event.source == &m_uiCloseButton) Close();
        return;
    }
    for (BYTE i = 0; i < TOTAL_UPGRADE_SOCKET_NO; ++i) {
        if (event.source != &m_uiUpgradeItem[i]) continue;
        if (event.id == MOUSE_HOVERED && !m_uiUpgradeItem[i].IsEmpty()) {
            PostUIMessage(WM_BOARD_HOVER_OBJECT, UI_MOUSE_MSG(0, i, 0, 0));
        } else if (event.id == MOUSE_STROKED) {
            if (gScreen.ExistObject()) {
                PostUIMessage(WM_BOARD_ADD_OBJECT, UI_MOUSE_MSG(0, i, 0, 0));
                return;
            }
            SetQuickEvent();
            if (g_bIsQuickEvent_Trade) PostUIMessage(WM_BOARD_TRADE_HOT_KEY, UI_MOUSE_MSG(0, i, 0, 0));
            else if (i) PostUIMessage(WM_BOARD_CHECK_REMOVE_OBJECT, UI_MOUSE_MSG(0, i, 0, 0));
            else {
                for (BYTE slot = 0; slot < TOTAL_UPGRADE_SOCKET_NO; ++slot)
                    if (!m_uiUpgradeItem[slot].IsEmpty())
                        PostUIMessage(WM_BOARD_CHECK_REMOVE_OBJECT, UI_MOUSE_MSG(0, slot, 0, 0));
            }
        }
        return;
    }
}
