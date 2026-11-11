// Ore selection and mining controls in 455, RVA 27FE80.
#include "client455_unit_view_skin.h"

void CGUIMiningWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(*this, 11, 0, 0);
    Bind(m_uiOreSelectBase, 11, 0, 1);
    auto* sprite = Image(11, 0, 2).pSprite;
    for (unsigned i = 0; i < 5; ++i) {
        auto& mark = m_uiOreSelectObject[i];
        mark.SetImage455(sprite, 0, 2);
        mark.SetSheet455(1, 5);
        mark.SetFPS455(10.0f);
        mark.SetPauseInterval455(200);
        if (i != m_bySelectedOreIndex) mark.GetSpriteInfo()->pSprite = nullptr;
    }
    Button(m_uiMiningButton, 4, 8, 0, true, true);
}

void CGUIMiningWindow::Init()
{
    SetSprite();
    const LONG x = GetPosX(), y = GetPosY();
    m_uiOreSelectBase.SetPos(x + 6, y + 17);
    m_uiMiningButton.SetPos(x + 27, y + 43);
    m_uiTitle.SetString(RF455UnitView::Text(0x39b));
    m_uiTitle.SetPos(x + (GetSizeX() - m_uiTitle.GetSizeX()) / 2,
                    y + 4 + (14 - m_uiTitle.GetSizeY()) / 2);
    Add(&m_uiOreSelectBase);
    for (unsigned i = 0; i < 5; ++i) {
        auto& mark = m_uiOreSelectObject[i];
        mark.SetPos(x + 9 + 27 * i, y + 21);
        mark.AddMouseEventHandler(this);
        Add(&mark);
    }
    Add(&m_uiTitle);
    m_uiMiningButton.AddMouseEventHandler(this);
    Add(&m_uiMiningButton);
    m_uiTitle.SetMouseInput455(FALSE);
    SetMoveObject(this);
    SetMovable(TRUE);
    Mining_Off();
    EnableMiningButton(TRUE);
    SelectOre(0);
    SetName(const_cast<char*>("Mining"));
    SetARGB(0xd8ffffff);
}

void CGUIMiningWindow::SelectOre(BYTE ore)
{
    if (ore >= 5 || ore == m_bySelectedOreIndex) return;
    if (m_bySelectedOreIndex < 5) m_uiOreSelectObject[m_bySelectedOreIndex].GetSpriteInfo()->pSprite = nullptr;
    m_bySelectedOreIndex = ore;
    m_uiOreSelectObject[ore].GetSpriteInfo()->pSprite = GetSpriteInfo()->pSprite;
}

void CGUIMiningWindow::Mining_On()
{
    m_uiMiningButton.SetLabel(RF455UnitView::Text(0x39c));
}

void CGUIMiningWindow::Mining_Off()
{
    m_uiMiningButton.SetLabel(RF455UnitView::Text(0x39d));
}
