// UnitStorehouse 455, window Init 32A700 and SetSprite 32A9F0.
#include "client455_unit_view_skin.h"

using namespace RF455UnitView;

void CGUIUnitStoreWindow::SetSprite()
{
    m_uiTitleBoard.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    Button(m_uiTakeOutUnitButton, 1, 1, 0, true, true);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    m_uiUnitListBoard.CGUIContainer::SetSprite();
}

void CGUIUnitStoreWindow::Init()
{
    SetSprite();
    SetSize(228, 288);
    m_uiFrame455.SetSize(228, 288);
    m_uiFrame455.SetPos(GetPosX(), GetPosY());
    m_uiFrame455.SetOutline455(1, 6, 0xff6a6e72);
    m_uiFrame455.SetARGB(0xcc222628);
    m_uiUnitListBoard.SetSize(218, VIEW_UNIT_NUM * UNIT_SIZE_Y);
    m_uiTitle.SetString(Text(0x409));
    m_uiTakeOutUnitButton.SetLabel(Text(0x40a));
    HeaderPosition(*this, m_uiTitleBoard, m_uiTitle, m_uiCloseButton);
    m_uiUnitListBoard.SetPos(GetPosX() + 7, GetPosY() + 31);
    m_uiTakeOutUnitButton.SetPos(GetPosX() + (GetSizeX() - m_uiTakeOutUnitButton.GetSizeX()) / 2,
                                GetPosY() + 258);
    m_uiCloseButton.AddMouseEventHandler(this);
    m_uiTakeOutUnitButton.AddMouseEventHandler(this);
    Add(&m_uiFrame455);
    Add(&m_uiTitleBoard);
    Add(&m_uiTitle);
    Add(&m_uiCloseButton);
    Add(&m_uiUnitListBoard);
    Add(&m_uiTakeOutUnitButton);
    m_uiTitle.GetFont()->dwColor = 0xffc7bdb6;
    m_uiTakeOutUnitButton.SetLabelStyle(R3_HAN_OUTLINE);
    SetMoveObject(&m_uiTitle);
    SetMoveObject(&m_uiTitleBoard);
    SetMovable(TRUE);
    m_uiUnitListBoard.GetScrollbar()->SetArrowAdjustmentUnit(UNIT_SIZE_Y);
    SetWheelScrollObject(m_uiUnitListBoard.GetScrollbar());
    UnSelectUnit();
}
