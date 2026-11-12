// 455 shared Skill/Force window and list ownership, RVA 2C70A0..2C8BC0.
#include "client455_modal.h"
#include "client455_unit_view_skin.h"
#include <algorithm>
#include <memory>

namespace {
constexpr LONG SkillForceRowHeight = 44;
constexpr DWORD SectionTitleColor = 0xffdad8d4;

void PositionRows(CGUIContainer& content)
{
    const int count = content.GetAddedObjectNum();
    for (int i = 0; i < count; ++i)
        content.GetAddedObject(WORD(i))->SetPos(content.GetPosX(), content.GetPosY() + i * SkillForceRowHeight);
    content.SetSize(content.GetSizeX(), count * SkillForceRowHeight);
}
}

CGUISkillForceBoard::CGUISkillForceBoard() : m_pHoveredUnit(nullptr) {}

CGUISkillForceBoard::~CGUISkillForceBoard()
{
    Clear455();
    for (auto* row : m_listUnit) delete row;
}

void CGUISkillForceBoard::Init(POINT& size, BYTE count)
{
    Init455(count, 207, 18, size.x, size.y);
    SetSprite();
    Scrollbar455().SetArrowAdjustmentUnit(22);
    SetSize(size);
}

void CGUISkillForceBoard::SetSprite()
{
    RF455_ConfigureModalScrollbar(Scrollbar455());
    SetHeaderSprites455({1, 5, 0}, {1, 5, 1});
    for (auto* row : m_listUnit) row->SetSprite();
}

void CGUISkillForceBoard::SetTabName(BYTE index, char* name)
{
    SetTitle455(index, name, SectionTitleColor);
}

BOOL CGUISkillForceBoard::AddUnit(CGUISkFcUnit* row)
{
    auto* content = Content455(row->GetStep());
    if (!content) return FALSE;
    row->SetSize(content->GetSizeX(), SkillForceRowHeight);
    row->SetPos(content->GetPosX(), content->GetPosY() + content->GetAddedObjectNum() * SkillForceRowHeight);
    m_listUnit.push_back(row);
    try {
        content->Add(row);
    } catch (...) {
        m_listUnit.pop_back();
        throw;
    }
    content->SetSize(content->GetSizeX(), content->GetAddedObjectNum() * SkillForceRowHeight);
    Reflow455();
    return TRUE;
}

CGUISkFcUnit* CGUISkillForceBoard::RemoveUnit(DWORD index)
{
    auto found = std::find_if(m_listUnit.begin(), m_listUnit.end(),
                              [index](CGUISkFcUnit* row) { return row->GetIndex() == index; });
    if (found == m_listUnit.end()) return nullptr;
    auto* row = *found;
    if (row == m_pHoveredUnit) SetHoverUnit(nullptr);
    auto& content = *Content455(row->GetStep());
    content.Remove(row);
    m_listUnit.erase(found);
    PositionRows(content);
    Reflow455();
    return row;
}

CGUISFWindow::~CGUISFWindow()
{
    SetWheelScrollObject(nullptr);
    RemoveAll();
    delete[] m_pSFBoardList;
    delete[] m_uiSFBoardTab;
}

void CGUISFWindow::CreateSFBoard(BYTE count, BYTE* groups)
{
    SetWheelScrollObject(nullptr);
    RemoveAll();
    delete[] m_pSFBoardList;
    delete[] m_uiSFBoardTab;
    m_pSFBoardList = nullptr;
    m_uiSFBoardTab = nullptr;
    m_bySFBoardNum = 0;
    m_byCurBoardTab = 255;
    if (!count) return;

    std::unique_ptr<CGUISkillForceBoard[]> lists(new CGUISkillForceBoard[count]);
    std::unique_ptr<CGUIObject[]> tabs(new CGUIObject[count]);
    POINT size = {219, 298};
    for (BYTE i = 0; i < count; ++i) lists[i].Init(size, groups[i]);
    m_pSFBoardList = lists.release();
    m_uiSFBoardTab = tabs.release();
    m_bySFBoardNum = count;
}

void CGUISFWindow::Init()
{
    using namespace RF455UnitView;
    if (!m_bySFBoardNum) return;
    SetSize(228, 395);
    m_uiBoard.SetSize(GetSizeX(), GetSizeY());
    m_uiBoard.SetPos(GetPosX(), GetPosY());
    m_uiBoard.SetOutline455(3, 1, 0xff6a6e72);
    m_uiBoard.SetARGB(0xd8222628);
    HeaderPosition(*this, m_uiAniTitleBar, m_uiTitle, m_uiCloseButton);
    m_uiHelpButton.SetPos(m_uiAniTitleBar.GetPosX() + 4, m_uiAniTitleBar.GetPosY() + 4);
    m_uiTitle.GetFont()->dwColor = 0xffc7bdb6;
    const LONG tabWidth = (GetSizeX() - 8) / m_bySFBoardNum;
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) {
        auto& tab = m_uiSFBoardTab[i];
        tab.SetPos(GetPosX() + 4 + i * tabWidth + (tabWidth - tab.GetSizeX()) / 2,
                   m_uiAniTitleBar.GetPosY() + m_uiAniTitleBar.GetSizeY() + 8);
    }
    m_uiResizeUnderBar.SetPos(GetPosX(), GetPosY() + GetSizeY() - m_uiResizeUnderBar.GetSizeY());
    Add(&m_uiBoard);
    Add(&m_uiAniTitleBar);
    Add(&m_uiTitle);
    for (auto* control : {static_cast<CGUIObject*>(&m_uiCloseButton),
                          static_cast<CGUIObject*>(&m_uiHelpButton), &m_uiResizeUnderBar})
        control->AddMouseEventHandler(this);
    Add(&m_uiCloseButton);
    Add(&m_uiHelpButton);
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) {
        m_pSFBoardList[i].AddMouseEventHandler(this);
        m_uiSFBoardTab[i].AddMouseEventHandler(this);
        Add(&m_uiSFBoardTab[i]);
    }
    Add(&m_uiResizeUnderBar);
    SetReSizeObject(CGUIWindow::BOTTOM, &m_uiResizeUnderBar);
    SetReSizable(TRUE);
    SetMoveObject(&m_uiAniTitleBar);
    SetMovable(TRUE);
    SoundOn(TRUE);
    RECT bounds = {};
    GetBound(bounds);
    SetBound(bounds);
    SetCurBoardTab(0);
}

void CGUISFWindow::SetSprite()
{
    using namespace RF455UnitView;
    m_uiAniTitleBar.SetImage455(Image(1, 4, 0).pSprite, 4, 0);
    m_uiSelectedTab455.SetImage455(Image(1, 7, 6).pSprite, 7, 6);
    m_uiSelectedTab455.SetSheet455(1, 4);
    m_uiSelectedTab455.SetFPS455(5);
    m_uiSelectedTab455.SetMouseInput455(FALSE);
    Bind(m_uiResizeUnderBar, 1, 4, 2);
    Button(m_uiCloseButton, 1, 0, 0, true, false);
    Button(m_uiHelpButton, 1, 0, 3, true, false);
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) m_pSFBoardList[i].SetSprite();
}

void CGUISFWindow::SetBound(RECT& bounds)
{
    if (bounds.bottom - bounds.top < m_uiAniTitleBar.GetSizeY() + m_uiResizeUnderBar.GetSizeY() + 137)
        return;
    CGUIObject::SetBound(bounds);
    m_uiBoard.SetBound(bounds);
    m_uiResizeUnderBar.SetPos(GetPosX() + (GetSizeX() - m_uiResizeUnderBar.GetSizeX()) / 2,
                             GetPosY() + GetSizeY() - m_uiResizeUnderBar.GetSizeY() - 6);
    if (!m_bySFBoardNum) return;
    RECT list = {GetPosX() + 5, m_uiSFBoardTab[0].GetPosY() + m_uiSFBoardTab[0].GetSizeY() + 8,
                 GetPosX() + 5 + m_pSFBoardList[0].GetSizeX(), m_uiResizeUnderBar.GetPosY() - 1};
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) m_pSFBoardList[i].SetBound(list);
}

void CGUISFWindow::SetCurBoardTab(BYTE index)
{
    if (index >= m_bySFBoardNum || index == m_byCurBoardTab) return;
    if (m_byCurBoardTab < m_bySFBoardNum) Remove(&m_pSFBoardList[m_byCurBoardTab]);
    m_byCurBoardTab = index;
    auto& board = m_pSFBoardList[index];
    board.SetPos(GetPosX() + 5, m_uiSFBoardTab[0].GetPosY() + m_uiSFBoardTab[0].GetSizeY() + 8);
    Add(&board);
    SetWheelScrollObject(&board.Scrollbar455());
    m_uiSelectedTab455.SetPos(m_uiSFBoardTab[index].GetPosX(), m_uiSFBoardTab[index].GetPosY());
    Add(&m_uiSelectedTab455);
}

CGUIItem* CGUISFWindow::RevealSkill455(BYTE bank, DWORD index)
{
    auto* row = GetIconBoard(bank, index);
    if (!row) return nullptr;
    SetCurBoardTab(bank);
    auto& list = m_pSFBoardList[bank];
    list.SetOpened455(row->GetStep(), TRUE);
    auto& scroll = list.Scrollbar455();
    const LONG top = list.GetPosY();
    const LONG bottom = top + list.GetSizeY();
    if (row->GetPosY() < top) scroll.SetCurrentAmount(scroll.GetCurrentAmount() + row->GetPosY() - top);
    else if (row->GetPosY() + row->GetSizeY() > bottom)
        scroll.SetCurrentAmount(scroll.GetCurrentAmount() + row->GetPosY() + row->GetSizeY() - bottom);
    list.RepositionScroll455();
    return row->GetItem();
}

void CGUISkillWindow::Init()
{
    BYTE groups[] = {4, 4, 1, 3, 1};
    CreateSFBoard(5, groups);
    m_uiTitle.SetString(RF455UnitView::Text(0x357));
    SetSprite();
    CGUISFWindow::Init();
    const unsigned names[] = {0x3db, 0x3dc, 0xb8b, 0x3dd, 0xd17};
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) {
        m_uiSFBoardTab[i].SetName(RF455UnitView::Text(names[i]));
        m_pSFBoardList[i].SetOpened455(0, TRUE);
    }
    SetName("SkillWindow");
}

void CGUISkillWindow::SetSprite()
{
    CGUISFWindow::SetSprite();
    for (BYTE i = 0; i < m_bySFBoardNum; ++i) RF455UnitView::Bind(m_uiSFBoardTab[i], 45, 1, i);
}
