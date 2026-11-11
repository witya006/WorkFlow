// 455 selected target menu at RVA 278920.
#include "client455_unit_view_skin.h"

void CGUISelectedCharMenu::SetSprite()
{
    for (auto& button : m_uiFuncMenu)
        RF455UnitView::Button(button, 4, 8, 0, true, true);
}

void CGUISelectedCharMenu::SetMenuType(BYTE type)
{
    if (type > GUARD_TOWER) return;
    m_byMenuType = type;
    for (auto& button : m_uiFuncMenu) Remove(&button);

    static const unsigned playerLabels[] = {0x484, 0x485, 0x486, 0x487, 0x16b1, 0x488, 0x489};
    static const unsigned unitLabels[] = {0x48a, 0x48b, 0x48c};
    static const unsigned towerLabels[] = {0x48d};
    static_assert(PLAYER_MENU_NUM == sizeof playerLabels / sizeof playerLabels[0]);
    static_assert(UNIT_MENU_NUM == sizeof unitLabels / sizeof unitLabels[0]);
    const auto* labels = type == PLAYER ? playerLabels : type == UNIT ? unitLabels : towerLabels;
    const int count = type == PLAYER ? PLAYER_MENU_NUM : type == UNIT ? UNIT_MENU_NUM : GUARD_TOWER_MENU_NUM;
    SetSize(106, 24 * count + 26);
    for (int i = 0; i < count; ++i) {
        auto& button = m_uiFuncMenu[i];
        button.SetLabel(RF455UnitView::Text(labels[i]));
        button.SetPos(GetPosX() + 6, GetPosY() + 22 + 24 * i);
        Add(&button);
        EnableButton(static_cast<BYTE>(i), type == PLAYER ? i == Whisper || i == Trade || i == Follow : i == 0);
    }
    if (type == PLAYER) SetPartyMenu(None);
}

void CGUISelectedCharMenu::SetPartyMenu(PartyMenu menu)
{
    if (m_byMenuType != PLAYER) return;
    m_ePartyMenu = menu;
    if (menu == Invite || menu == Join)
        m_uiFuncMenu[Party].SetLabel(RF455UnitView::Text(menu == Invite ? 0x486 : 0x48e));
    EnableButton(Party, menu == Invite || menu == Join);
}
