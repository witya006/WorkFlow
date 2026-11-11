// Character promotion view in 455, RVA 28D960.
#include "client455_text_metrics.h"
#include "client455_unit_view_skin.h"

#include <algorithm>

void CGUIClassChangeWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(*this, 20, 0, 0);
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    Button(m_uiOKButton, 1, 1, 0, true, true);
    Button(m_uiCancelButton, 1, 1, 0, true, true);
    Button(m_uiScrollbar.GetTopArrow455(), 1, 2, 0, false, false);
    Button(m_uiScrollbar.GetBottomArrow455(), 1, 2, 2, false, false);
    POINT thumb = {5, 18};
    m_uiScrollbar.SetBarSize(thumb);
    m_uiScrollbar.SetMinimumThumb455(18);
    m_uiScrollbar.SetBarColor455(0xff70635d);
    m_uiScrollbar.SetSize(m_uiScrollbar.GetTopArrow455().GetSizeX(), m_uiClassDescription.GetSizeY());

    auto atlas = Image(20, 0, 2);
    for (auto& button : m_uiClassSelectButton) button.GetSpriteInfo()->pSprite = atlas.pSprite;
    auto mark = Image(20, 0, 1);
    if (!m_uiSelectedButtonMark.GetSpriteInfo()->pSprite) mark.pSprite = nullptr;
    m_uiSelectedButtonMark.SetSpriteInfo(&mark);
    for (auto& icon : m_uiClassSkillIcon)
        if (!icon.IsEmpty()) icon.SetSprite();
}

void CGUIClassChangeWindow::Init()
{
    using namespace RF455UnitView;
    m_uiClassDescription.SetSize(182, 100);
    SetSprite();
    const LONG x = GetPosX(), y = GetPosY();
    m_uiTitle.SetString(Text(0x39e));
    m_uiOKButton.SetLabel(Text(0x35d));
    m_uiCancelButton.SetLabel(Text(0x35e));
    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    m_uiClassDescription.SetPos(x + 26, y + 70);
    m_uiOKButton.SetPos(x + 18, y + 361);
    m_uiCancelButton.SetPos(x + 143, y + 361);
    m_uiTitle.GetFont()->dwColor = 0xffc7bdb6;
    m_uiClassNameStr.GetFont()->dwColor = 0xffc3c1be;
    m_uiOKButton.SetLabelColor(0xffe8e8e8);
    m_uiCancelButton.SetLabelColor(0xffe8e8e8);
    m_uiOKButton.SetLabelStyle(R3_HAN_OUTLINE);
    m_uiCancelButton.SetLabelStyle(R3_HAN_OUTLINE);
    m_uiClassDescription.SetMargin(3, 3);
    m_uiClassDescription.SetColumnGap(3);
    m_uiClassDescription.AddScrollbar(&m_uiScrollbar);
    SetWheelScrollObject(&m_uiScrollbar);

    for (auto& button : m_uiClassSelectButton) {
        auto atlas = Image(20, 0, 2);
        button.SetSpriteInfo(&atlas);
        button.SetSize(45, 45);
        button.AddMouseEventHandler(this);
    }
    for (auto& icon : m_uiClassSkillIcon) {
        icon.SetSize(32, 32);
        icon.AddMouseEventHandler(this);
    }
    m_uiSelectedButtonMark.SetSize(47, 47);
    CGUIObject* children[] = {&m_uiAniTitleBar, &m_uiTitle, &m_uiCloseButton, &m_uiHelpButton,
                             &m_uiClassNameStr, &m_uiClassDescription, &m_uiSelectedButtonMark,
                             &m_uiOKButton, &m_uiCancelButton};
    for (auto* object : children) Add(object);
    for (auto* button : {&m_uiCloseButton, &m_uiHelpButton,
                        static_cast<CGUIButton*>(&m_uiOKButton), static_cast<CGUIButton*>(&m_uiCancelButton)})
        button->AddMouseEventHandler(this);
    m_uiTitle.SetMouseInput455(FALSE);
    SetMoveObject(&m_uiAniTitleBar);
    SetMoveObject(&m_uiTitle);
    SetMovable(TRUE);
    SoundOn(TRUE);
    SetARGB(0xd8ffffff);
    SetName(const_cast<char*>("classchange"));
}

void CGUIClassChangeWindow::SetTotalClassNum(BYTE count, BYTE* iconIds)
{
    m_byTotalClassButtonNum = iconIds ? std::min<BYTE>(count, MAX_CLASS_BUTTON_NUM) : 0;
    m_uiSelectedButtonMark.GetSpriteInfo()->pSprite = nullptr;
    auto atlas = RF455UnitView::Image(20, 0, 2);
    for (unsigned i = 0; i < MAX_CLASS_BUTTON_NUM; ++i) {
        auto& button = m_uiClassSelectButton[i];
        if (i >= m_byTotalClassButtonNum) {
            Remove(&button);
            continue;
        }
        const unsigned row = i / 4, column = i % 4;
        const LONG columns = std::min<unsigned>(4, m_byTotalClassButtonNum - row * 4);
        button.SetSpriteInfo(&atlas);
        button.SetSpriteTileByIndex(iconIds[i]);
        button.SetPos(GetPosX() + (GetSizeX() - columns * 48) / 2 + LONG(column) * 48,
                      GetPosY() + 257 + LONG(row) * 48);
        Add(&button);
    }
}

void CGUIClassChangeWindow::SelectClass(BYTE index)
{
    if (index >= m_byTotalClassButtonNum) return;
    const auto& button = m_uiClassSelectButton[index];
    auto mark = RF455UnitView::Image(20, 0, 1);
    m_uiSelectedButtonMark.SetSpriteInfo(&mark);
    m_uiSelectedButtonMark.SetPos(button.m_ptPos.x - 1, button.m_ptPos.y - 1);
}

void CGUIClassChangeWindow::SetSkillIcon(BYTE count, DWORD* iconIds)
{
    const unsigned size = iconIds ? std::min<BYTE>(count, MAX_CLASS_SKILL_ICON_NUM) : 0;
    const LONG firstRow = GetPosY() + m_uiClassDescription.GetMarginY() +
                         (std::min)(m_uiClassDescription.GetTotalLineNum() + 5, 11) *
                         (RF455_DefaultTextHeight() + m_uiClassDescription.GetColumnGap());
    for (unsigned i = 0; i < MAX_CLASS_SKILL_ICON_NUM; ++i) {
        auto& icon = m_uiClassSkillIcon[i];
        if (i >= size) {
            Remove(&icon);
            continue;
        }
        const unsigned row = i / 5, column = i % 5;
        const LONG columns = (std::min)(5u, size - row * 5);
        icon.SetIconType455(2);
        icon.SetSpriteID(iconIds[i]);
        icon.SetItemID(iconIds[i]);
        icon.SetSprite();
        icon.SetPos(GetPosX() + (GetSizeX() - columns * 37) / 2 + LONG(column) * 37,
                    firstRow + LONG(row) * 34);
        Add(&icon);
    }
}

void CGUIClassChangeWindow::SetClassName(char* name)
{
    m_uiClassNameStr.SetString(name);
    m_uiClassNameStr.SetPos(GetPosX() + 67 + (94 - m_uiClassNameStr.GetSizeX()) / 2,
                           GetPosY() + 42 + (16 - m_uiClassNameStr.GetSizeY()) / 2);
}

void CGUIClassChangeWindow::SetDescription(char* description)
{
    FONT_INFO font;
    m_uiClassDescription.ReplaceFormatted455(description, &font);
    const LONG y = m_uiClassDescription.GetPosY();
    if (m_uiScrollbar.GetTotalAmount() > 0) {
        m_uiClassDescription.SetPos(GetPosX() + 19, y);
        m_uiScrollbar.SetPos(m_uiClassDescription.GetPosX() + m_uiClassDescription.GetSizeX(), y);
        Add(&m_uiScrollbar);
    } else {
        m_uiClassDescription.SetPos(GetPosX() + (GetSizeX() - m_uiClassDescription.GetSizeX()) / 2, y);
        Remove(&m_uiScrollbar);
    }
}
