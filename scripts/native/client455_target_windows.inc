// 455 selected character bar and target information panel.
#include "client455_unit_view_skin.h"
#include <cstdio>

namespace {
constexpr BYTE MainSprite = 4;
constexpr BYTE RenewalSprite = 41;
constexpr DWORD GaugeBackdropColor = 0xffc8c8c8;

void TargetGauge(CGUIObjectEx& gauge, LONG width, float rate)
{
    gauge.SetSize(static_cast<LONG>(width * rate), gauge.GetSizeY());
    gauge.SetSpriteU(0.0f, rate);
}
}

void CGUISelectedCharWin::Init()
{
    if (m_bCreated) return;
    m_bIsAttackState = FALSE;
    SetSprite();
    m_uiStateBoard.SetPos(m_ptPos);
    m_uiHPBackdrop455.SetPos(m_ptPos);
    m_uiHPGauge.SetPos(m_ptPos);
    m_uiCharName.SetPos(GetPosX(), GetPosY() + 15);
    Add(&m_uiStateBoard);
    Add(&m_uiHPBackdrop455);
    Add(&m_uiHPGauge);
    Add(&m_uiCharName);
    m_uiCharName.GetFont()->dwColor = 0xfffd3f82;
    m_uiCharName.GetFont()->dwStyle = R3_HAN_OUTLINE;
    m_bCreated = TRUE;
}

void CGUISelectedCharWin::SetSprite()
{
    using RF455UnitView::Bind;
    Bind(m_uiStateBoard, MainSprite, 7, 0);
    const WORD frame = m_bIsAttackState ? 2 : 1;
    Bind(m_uiHPBackdrop455, MainSprite, 7, frame);
    Bind(m_uiHPGauge, MainSprite, 7, frame);
    m_uiHPBackdrop455.SetARGB(GaugeBackdropColor);
    SetSize(m_uiStateBoard.GetSizeX(), m_uiStateBoard.GetSizeY());
    SetHPRate(m_hpRate455);
}

void CGUISelectedCharWin::SetAttackState()
{
    m_bIsAttackState = TRUE;
    if (m_bCreated) {
        m_uiHPGauge.GetSpriteInfo()->wFrameNo = 2;
        m_uiHPBackdrop455.GetSpriteInfo()->wFrameNo = 2;
    }
}

void CGUISelectedCharWin::SetSelectState()
{
    m_bIsAttackState = FALSE;
    if (m_bCreated) {
        m_uiHPGauge.GetSpriteInfo()->wFrameNo = 1;
        m_uiHPBackdrop455.GetSpriteInfo()->wFrameNo = 1;
    }
}

void CGUISelectedCharWin::SetHPRate(float rate)
{
    if (!(rate >= 0.0f && rate <= 1.0f)) return;
    m_hpRate455 = rate;
    if (m_uiHPGauge.GetSpriteInfo()->pSprite)
        TargetGauge(m_uiHPGauge, m_uiStateBoard.GetSizeX(), rate);
}

void CGUISelectedMobInfoWin::Init()
{
    if (m_bIsCreated) return;
    SetSprite();
    m_uiHPBackdrop455.SetPos(GetPosX() + 67, GetPosY() + 20);
    m_uiHPGauge.SetPos(m_uiHPBackdrop455.m_ptPos);
    m_uiMobName.SetPos(GetPosX() + 55, GetPosY() + 5);
    m_uiLevel455.SetPos(GetPosX() + 30, GetPosY() + 24);
    m_uiMobName.GetFont()->dwColor = 0xffc7bdb6;
    m_uiLevel455.GetFont()->dwColor = 0xffffffff;
    Add(&m_uiLevel455);
    Add(&m_uiHPBackdrop455);
    Add(&m_uiMobName);
    Add(&m_uiHPGauge);
    SetMoveObject(&m_uiMobName);
    SetMovable(TRUE);
    m_bIsCreated = TRUE;
}

void CGUISelectedMobInfoWin::SetSprite()
{
    using RF455UnitView::Bind;
    Bind(*this, RenewalSprite, 0, 1);
    Bind(m_uiHPBackdrop455, MainSprite, 9, 1);
    Bind(m_uiHPGauge, MainSprite, 9, 1);
    m_uiHPBackdrop455.SetARGB(GaugeBackdropColor);
    SetHP(m_hpRate455);
}

void CGUISelectedMobInfoWin::SetMobName(char* name)
{
    m_uiMobName.SetString(name);
    m_uiMobName.SetPos(GetPosX() + 55, GetPosY() + 5);
}

void CGUISelectedMobInfoWin::SetLevel455(unsigned level)
{
    char number[16] = {};
    if (level) std::snprintf(number, sizeof number, "%u", level);
    m_uiLevel455.SetString(number);
    m_uiLevel455.SetPos(GetPosX() + 30, GetPosY() + 24);
}

void CGUISelectedMobInfoWin::SetHP(float rate)
{
    if (!(rate >= 0.0f && rate <= 1.0f)) return;
    m_hpRate455 = rate;
    if (m_uiHPGauge.GetSpriteInfo()->pSprite)
        TargetGauge(m_uiHPGauge, m_uiHPBackdrop455.GetSizeX(), rate);
}
