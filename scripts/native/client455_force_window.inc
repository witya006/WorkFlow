// 455 Force tab layout and race-dependent first tab, RVA 2BFF70..2C01D9.
#include "client455_unit_view_skin.h"

void CGUIForceWindow::Init()
{
    BYTE groups[] = {4, 4, 4, 4, 4};
    CreateSFBoard(5, groups);
    m_uiTitle.SetString(RF455UnitView::Text(0x358));
    SetSprite();
    CGUISFWindow::Init();
    for (BYTE i = 1; i < m_bySFBoardNum; ++i)
        m_uiSFBoardTab[i].SetName(RF455UnitView::Text(0x40 + i));
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) m_pSFBoardList[i].SetOpened455(0, TRUE);
    SetName("ForceWindow");
}

void CGUIForceWindow::SetSprite()
{
    CGUISFWindow::SetSprite();
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) RF455UnitView::Bind(m_uiSFBoardTab[i], 46, 0, i);
}

void CGUIForceWindow::SetRaceType(BYTE race)
{
    if (!m_bySFBoardNum || race / 2 > 1) return;
    const bool cora = race / 2 == 1;
    RF455UnitView::Bind(m_uiSFBoardTab[0], 46, 0, cora ? 5 : 0);
    m_uiSFBoardTab[0].SetName(RF455UnitView::Text(cora ? 0x3f : 0x40));
}
