// 455 skill/force row creation and presentation, RVA 2C6200..2C74D2.
#include "client455_unit_view_skin.h"
#include <cmath>
#include <cstdio>

CGUISkFcUnit::CGUISkFcUnit()
    : m_dwIndex(0xffffffff), m_byStep(0), m_eUnitState(Enabled), m_bHovered(FALSE)
{
    SetSize(207, 44);
    m_cIconBackground455.SetSize(40, 40);
    m_cIconBackground455.SetARGB(0xa0030303);
    m_cItem.SetSize(38, 38);
    m_cItemName.GetFont()->dwColor = 0xffe8e8e8;
    m_cUnderline.SetARGB(0xa0000000);
    m_cExpNumber.SetARGB(0xffffffc8);
    m_cCover.SetARGB(0xffffffff);
    Add(&m_cIconBackground455);
    Add(&m_cItem);
    Add(&m_cItemName);
    Add(&m_cUnderline);
    Arrange455();
}

void CGUISkFcUnit::SetSprite()
{
    RF455UnitView::Bind(m_cExpBase, 45, 0, 0);
    RF455UnitView::Bind(m_cExp, 45, 0, 1);
    m_cExpNumber.Configure455(1, 7, 3, 7, 9);
    SetExp(m_percent455);
    if (!m_cItem.IsEmpty()) m_cItem.SetSprite();
    Arrange455();
}

void CGUISkFcUnit::SetSize(LONG width, LONG height)
{
    CGUIObject::SetSize(width, height);
    m_cCover.SetSize(width, height);
    m_cUnderline.SetSize(width, 1);
    m_cUnderline.SetPos(GetPosX(), GetPosY() + height - 1);
}

void CGUISkFcUnit::Arrange455()
{
    const LONG x = GetPosX(), y = GetPosY();
    const bool classSkill = m_kind455 == 2;
    const bool mastery = m_level455 == 7;
    m_cIconBackground455.SetPos(x + (classSkill ? 6 : 4), y + 2);
    m_cItem.SetPos(m_cIconBackground455.GetPosX() + 1, y + 3);
    m_cExpBase.SetPos(x + 45, y + 27);
    m_cExp.SetPos(x + 47, y + 29);
    m_cExpNumber.SetPos(x + GetSizeX() - m_cExpNumber.GetSizeX(), y + 26);
    m_cItemName.SetPos(x + (classSkill || mastery ? 52 : 49),
                      classSkill || mastery ? y + (GetSizeY() - m_cItemName.GetSizeY()) / 2
                                             : y + 23 - m_cItemName.GetSizeY());
    m_cLevelStr.SetPos(x + 176, m_cItemName.GetPosY());
    m_cCover.SetPos(x, y);

    Remove(&m_cCover);
    if (classSkill || mastery) {
        Remove(&m_cExpBase);
        Remove(&m_cExp);
        Remove(&m_cExpNumber);
    } else {
        Add(&m_cExpBase);
        Add(&m_cExp);
        Add(&m_cExpNumber);
    }
    if (classSkill) Remove(&m_cLevelStr);
    else Add(&m_cLevelStr);
    Add(&m_cCover);
}

void CGUISkFcUnit::SetKind455(BYTE kind)
{
    m_kind455 = kind;
    Arrange455();
}

void CGUISkFcUnit::SetUnitState(UnitState state)
{
    m_eUnitState = state;
    switch (state) {
    case Enabled:
    case Linked: m_cCover.SetARGB(0xffffffff); break;
    case Disabled: m_cCover.SetARGB(0x80a05050); break;
    case NoneUnit: m_cCover.SetARGB(0xb0000000); break;
    }
}

void CGUISkFcUnit::SetItemName(char* name)
{
    m_cItemName.SetString(name);
    Arrange455();
}

void CGUISkFcUnit::SetLevel(BYTE level)
{
    if (m_kind455 == 2 || level > 7) return;
    m_level455 = level;
    char text[16] = {};
    if (level == 7) std::snprintf(text, sizeof(text), "G M");
    else std::snprintf(text, sizeof(text), "Lv %u", unsigned(level));
    m_cLevelStr.SetString(text);
    m_cLevelStr.GetFont()->dwColor = level == 7 ? 0xffbcc0fa : 0xffffb847;
    Arrange455();
}

void CGUISkFcUnit::SetItem(CGUIItem* item)
{
    m_cItem.SetData(item);
    m_cItem.SetSize(38, 38);
    m_cItem.Show(IsShow());
}

void CGUISkFcUnit::SetItem(DWORD id, DWORD sprite, BYTE type)
{
    m_cItem.SetItemID(id);
    m_cItem.SetSpriteID(sprite);
    m_cItem.SetIconType455(type);
    m_cItem.SetSize(38, 38);
    m_cItem.SetSprite();
    m_cItem.Show(IsShow());
}

void CGUISkFcUnit::SetExp(float percent)
{
    if (!std::isfinite(percent)) return;
    m_percent455 = percent;
    const float ratio = percent < 0 ? 0 : percent > 99.99f ? 1 : percent / 99.99f;
    const LONG width = m_cExp.GetSpriteInfo()->pSprite
        ? m_cExp.GetSpriteInfo()->pSprite->GetSpriteOrgXL(0, 1) : 0;
    const LONG filled = (std::min)(width, 7L * LONG(ratio * 17));
    m_cExp.SetSize(filled, m_cExp.GetSizeY());
    m_cExp.SetSpriteU(0, width > 0 ? float(filled) / width : 0);
    char text[48] = {};
    std::snprintf(text, sizeof(text), "%.2f%%", double(percent));
    m_cExpNumber.SetString455(text);
    m_cExpNumber.SetPos(GetPosX() + GetSizeX() - m_cExpNumber.GetSizeX(), GetPosY() + 26);
}
