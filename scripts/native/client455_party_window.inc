// 455 party member and window views at RVA 2EB000 and 2ED090.
#include "client455_unit_view_skin.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>

namespace {
constexpr unsigned PartyStatusSlots = 8;
constexpr LONG PartyFullWidth = 238;
constexpr LONG PartyCompactWidth = 168;
constexpr LONG PartyFullHeight = 53;
constexpr LONG PartyCompactHeight = 33;

void PartyStatus(CGUIItem (&slots)[PartyStatusSlots], BYTE type, DWORD item, DWORD sprite)
{
    if (item == NONE_ITEM_ID) return;
    for (auto& slot : slots) {
        if (slot.GetItemID() != NONE_ITEM_ID) continue;
        slot.SetIconType455(type == 0 ? 1 : 3);
        slot.SetItemID(item);
        slot.SetSpriteID(sprite);
        slot.SetSprite();
        return;
    }
}

void RemovePartyStatus(CGUIItem (&slots)[PartyStatusSlots], DWORD item)
{
    if (item == NONE_ITEM_ID) return;
    for (unsigned i = 0; i < PartyStatusSlots; ++i) {
        if (slots[i].GetItemID() != item) continue;
        for (; i + 1 < PartyStatusSlots && slots[i + 1].GetItemID() != NONE_ITEM_ID; ++i) {
            slots[i].SetData(&slots[i + 1]);
            slots[i].SetSize(16, 16);
            slots[i].SetSprite();
        }
        slots[i].SetEmpty();
        return;
    }
}
}

void CGUIPartyMemberInfo::SetSprite()
{
    using namespace RF455UnitView;
    Bind(m_uiRowSkin455, 4, 6, 1);
    m_uiRowSkin455.SetARGB(0x90ffffff);
    for (unsigned i = 0; i < 3; ++i) {
        Bind(m_uiGauge455[i], 4, 0, WORD(i + 1));
        m_uiGauge455[i].SetSpriteV(0, 1);
    }
    Button(m_uiRemoveButton, 4, 6, 5, false, true);
    Button(m_uiChangeReaderButton, 4, 6, 2, false, true);
    SetClassIcon455(m_classIcon455);
    for (auto* slots : {m_uiDamageSF, m_uiHelpSF})
        for (unsigned i = 0; i < PartyStatusSlots; ++i)
            if (slots[i].GetItemID() != NONE_ITEM_ID) slots[i].SetSprite();
    Layout455(m_compact455, m_localLeader455, m_first455);
}

void CGUIPartyMemberInfo::Init(int, int)
{
    SetSprite();
    CGUIObject* surfaces[] = {&m_uiRowSkin455, &m_uiEventCover, &m_uiClassIcon455, &m_uiCharName, &m_uiLevel};
    for (auto* object : surfaces) {
        object->AddMouseEventHandler(this);
        Add(object);
    }
    for (auto& gauge : m_uiGauge455) {
        gauge.AddMouseEventHandler(this);
        Add(&gauge);
    }
    for (unsigned i = 0; i < PartyStatusSlots; ++i) {
        for (auto* slot : {&m_uiHelpSF[i], &m_uiDamageSF[i]}) {
            slot->SetSize(16, 16);
            slot->AddMouseEventHandler(this);
            Add(slot);
        }
    }
    m_uiChangeReaderButton.AddMouseEventHandler(this);
    m_uiRemoveButton.AddMouseEventHandler(this);
    Add(&m_uiChangeReaderButton);
    Add(&m_uiRemoveButton);
    m_uiCharName.GetFont()->dwColor = UI_PARTY_MEMBER_COLOR;
    ClearMemberInfo();
}

void CGUIPartyMemberInfo::SetClassIcon455(BYTE index)
{
    using namespace RF455UnitView;
    m_classIcon455 = index;
    const bool known = index < 160;
    auto image = known ? Image(20, 0, 2) : Image(49, 0, 2);
    m_uiClassIcon455.SetSpriteInfo(&image);
    m_uiClassIcon455.SetSize(45, 45);
    if (known) m_uiClassIcon455.SetSpriteTileByIndex(index);
    else {
        m_uiClassIcon455.SetSpriteU(0, 1);
        m_uiClassIcon455.SetSpriteV(0, 1);
    }
    if (m_compact455) m_uiClassIcon455.SetSize(33, 33);
}

void CGUIPartyMemberInfo::Layout455(bool compact, bool localLeader, bool first)
{
    m_compact455 = compact;
    m_localLeader455 = localLeader;
    m_first455 = first;
    const LONG x = GetPosX(), y = GetPosY();
    const LONG width = compact ? PartyCompactWidth : PartyFullWidth;
    const LONG height = compact ? PartyCompactHeight : PartyFullHeight;
    SetSize(width, height);
    m_uiEventCover.SetSize(width, height);
    m_uiEventCover.SetPos(x, y);
    m_uiRowSkin455.SetPos(x + 47, y);
    m_uiRowSkin455.Show(IsShow() && !compact);
    m_uiClassIcon455.SetPos(x - 2, y + (compact ? 0 : 7));
    m_uiClassIcon455.SetSize(compact ? 33 : 45, compact ? 33 : 45);
    m_uiCharName.SetPos(x + (compact ? (first && !localLeader ? 76 : 62) : (first && !localLeader ? 90 : 76)), y + 3);
    m_uiLevel.SetPos(x + (compact ? 35 : 49), y + 3);
    for (unsigned i = 0; i < 3; ++i) {
        m_uiGauge455[i].SetPos(x + (compact ? 33 : 47), y + 19 + LONG(i) * (compact ? 5 : 12));
        SetGauge455(i, m_rates455[i]);
    }
    for (unsigned i = 0; i < PartyStatusSlots; ++i) {
        m_uiHelpSF[i].SetPos(x + 96 + 18 * i, y + 19);
        m_uiDamageSF[i].SetPos(x + 96 + 18 * i, y + 37);
        m_uiHelpSF[i].Show(IsShow() && !compact);
        m_uiDamageSF[i].Show(IsShow() && !compact);
    }
    const LONG buttonY = y + (compact ? 20 : 2);
    m_uiRemoveButton.SetPos(x + width - 19 - (compact ? 3 : 0), buttonY);
    m_uiChangeReaderButton.SetPos(m_uiRemoveButton.GetPosX() - 20, buttonY);
    m_uiRemoveButton.Show(IsShow() && (localLeader || !compact));
    m_uiChangeReaderButton.Show(IsShow() && (localLeader || !compact));
}

void CGUIPartyMemberInfo::ClearMemberInfo()
{
    SetMemberID(NONE_MEMBER_ID);
    m_uiCharName.SetString(nullptr);
    m_uiCharName.GetFont()->dwColor = UI_PARTY_MEMBER_COLOR;
    SetLevel(0);
    for (unsigned i = 0; i < 3; ++i) SetGauge455(i, 0);
    RemoveAllSF();
    if (m_uiClassIcon455.GetSpriteInfo()->pSprite) SetClassIcon455(0xff);
}

void CGUIPartyMemberInfo::SetLevel(int level)
{
    char label[16];
    std::snprintf(label, sizeof label, "lv%d", level);
    m_uiLevel.SetString(label);
}

void CGUIPartyMemberInfo::SetGauge455(unsigned index, float rate)
{
    rate = std::isfinite(rate) ? (std::max)(0.f, (std::min)(1.f, rate)) : 0.f;
    m_rates455[index] = rate;
    auto& gauge = m_uiGauge455[index];
    if (!gauge.GetSpriteInfo()->pSprite) return;
    const float extent = m_compact455 ? (m_localLeader455 ? 120 * 0.77f : 120.f) : 47.f;
    gauge.SetSpriteU(0, rate);
    gauge.SetSize(static_cast<LONG>(extent * rate), m_compact455 ? 5 : 10);
}

void CGUIPartyMemberInfo::SetHPGauge(float rate) { SetGauge455(0, rate); }
void CGUIPartyMemberInfo::SetFPGauge(float rate) { SetGauge455(1, rate); }
void CGUIPartyMemberInfo::SetSPGauge(float rate) { SetGauge455(2, rate); }

void CGUIPartyMemberInfo::AddDamageSF(BYTE type, DWORD item, DWORD sprite) { PartyStatus(m_uiDamageSF, type, item, sprite); }
void CGUIPartyMemberInfo::AddHelpSF(BYTE type, DWORD item, DWORD sprite) { PartyStatus(m_uiHelpSF, type, item, sprite); }
void CGUIPartyMemberInfo::RemoveDamageSF(BYTE, DWORD item) { RemovePartyStatus(m_uiDamageSF, item); }
void CGUIPartyMemberInfo::RemoveHelpSF(BYTE, DWORD item) { RemovePartyStatus(m_uiHelpSF, item); }
void CGUIPartyMemberInfo::RemoveAllSF()
{
    for (auto& icon : m_uiDamageSF) icon.SetEmpty();
    for (auto& icon : m_uiHelpSF) icon.SetEmpty();
}

void CGUIPartyWindow::SetSprite()
{
    using namespace RF455UnitView;
    Bind(m_uiTitleBoard, 4, 6, 0);
    Bind(m_uiDistribution455, 4, 6, WORD(9 + 2 * m_distribution455));
    Bind(m_uiViewToggle455, 4, 6, m_compact455 ? 18 : 17);
    Bind(m_uiLeaderMark455, 49, 0, 0);
    m_uiLeaderMark455.SetSize(10, 10);
    Button(m_uiLockNLeaveButton, 1, 1, 0, true, true);
    if (m_bCreated) {
        for (auto& member : m_uiMember) member.SetSprite();
        Layout455();
    }
}

void CGUIPartyWindow::Init()
{
    SetSprite();
    SetSize(248, 60);
    m_uiTitleBoard.SetSize(240, 18);
    for (auto& member : m_uiMember) member.Init(PartyFullWidth, PartyFullHeight);
    Add(&m_uiTitleBoard);
    Add(&m_uiTitle);
    Add(&m_uiViewToggle455);
    m_uiViewToggle455.AddMouseEventHandler(this);
    m_uiDistribution455.AddMouseEventHandler(this);
    m_uiLockNLeaveButton.AddMouseEventHandler(this);
    m_uiLockNLeaveButton.SetLabelStyle(R3_HAN_OUTLINE);
    m_uiTitle.GetFont()->dwColor = 0xffc3c1be;
    m_uiTitle.SetMouseInput455(FALSE);
    SetMoveObject(&m_uiTitleBoard);
    SetMoveObject(&m_uiTitle);
    SetMovable(TRUE);
    SoundOn(TRUE);
    SetARGB(0xd0252525);
    m_uiTitleBoard.SetARGB(0xd0ffffff);
    Layout455(true);
    m_bCreated = TRUE;
}

void CGUIPartyWindow::Layout455(bool initial)
{
    const LONG x = GetPosX(), y = GetPosY();
    const LONG width = m_compact455 ? 176 : 248;
    const LONG rowStep = m_compact455 ? 35 : 56;
    const LONG height = initial ? 60 : 22 + m_byTotalMember * (m_compact455 ? 33 : 56) + m_uiLockNLeaveButton.GetSizeY() + 30;
    SetSize(width, height);
    m_uiTitleBoard.SetPos(x + 4, y + 4);
    m_uiTitleBoard.SetSize(width - 8, 18);
    SetTotalMemberNum(m_byTotalMember);
    m_uiDistribution455.SetPos(x + width - 4 - m_uiDistribution455.GetSizeX() - 2, y + 6);
    m_uiViewToggle455.SetPos(m_uiDistribution455.GetPosX() - m_uiViewToggle455.GetSizeX() - 1, y + 5);
    m_uiLockNLeaveButton.SetPos(x + (width - m_uiLockNLeaveButton.GetSizeX()) / 2,
                              y + height - m_uiLockNLeaveButton.GetSizeY() - 10);
    for (unsigned i = 0; i < m_byTotalMember; ++i) {
        auto& row = m_uiMember[m_byMemberOrder[i]];
        row.SetPos(x + 7, y + 22 + LONG(i) * rowStep);
        row.Layout455(m_compact455, m_byMemberType == UI_PMT_LEADER, i == 0);
    }
    const bool mark = m_byMemberType == UI_PMT_MEMBER && m_byTotalMember && m_leader455 == m_uiMember[m_byMemberOrder[0]].GetMemberID();
    if (mark) {
        m_uiLeaderMark455.SetPos(x + 7 + (m_compact455 ? 64 : 78), y + 25);
        Add(&m_uiLeaderMark455);
    } else Remove(&m_uiLeaderMark455);
}

void CGUIPartyWindow::Show(BOOL show)
{
    CGUIWindow::Show(show);
    if (show && m_bCreated) Layout455(!m_byTotalMember && GetSizeY() == 60);
}

void CGUIPartyWindow::SetWindowType(BYTE role)
{
    if (role > UI_PMT_LEADER) return;
    m_byMemberType = role;
    if (role == UI_PMT_NONE) {
        RemoveAllMember();
        Remove(&m_uiLockNLeaveButton);
        Remove(&m_uiDistribution455);
        return;
    }
    Lock(role == UI_PMT_LEADER && m_bIsLocked);
    Add(&m_uiLockNLeaveButton);
    Add(&m_uiDistribution455);
    for (auto& member : m_uiMember) {
        member.EnableRemveButton(role == UI_PMT_LEADER);
        member.EnableChLeaderButton(role == UI_PMT_LEADER);
    }
    EnableLockNLeaveButton(m_byTotalMember && (role != UI_PMT_LEADER || m_byTotalMember < MAX_PARTY_MEMBER_NUM));
    Layout455(m_byTotalMember == 0);
}

BOOL CGUIPartyWindow::AddMember(GROUP_MEMBER_INFO* info)
{
    if (!info || info->dwMemberID == NONE_MEMBER_ID || m_byMemberType == UI_PMT_NONE ||
        m_byTotalMember == MAX_PARTY_MEMBER_NUM) return FALSE;
    unsigned slot = MAX_PARTY_MEMBER_NUM;
    for (unsigned i = 0; i < MAX_PARTY_MEMBER_NUM; ++i) {
        const auto id = m_uiMember[i].GetMemberID();
        if (id == info->dwMemberID) return FALSE;
        if (slot == MAX_PARTY_MEMBER_NUM && id == NONE_MEMBER_ID) slot = i;
    }
    if (slot == MAX_PARTY_MEMBER_NUM) return FALSE;
    auto& row = m_uiMember[slot];
    row.SetMemberID(info->dwMemberID);
    char name[sizeof info->pCharName + 1] = {};
    std::memcpy(name, info->pCharName, sizeof info->pCharName);
    row.SetCharName(name);
    row.SetLevel(info->wLevel);
    row.SetHPGauge(info->fHPRate);
    row.SetFPGauge(info->fFPRate);
    row.SetSPGauge(info->fSPRate);
    row.SetClassIcon455(info->byClassIcon455);
    for (unsigned i = 0; i < PartyStatusSlots; ++i) {
        const auto& damage = info->sfDamage[i];
        const auto& help = info->sfHelp[i];
        row.AddDamageSF(damage.bySFType, damage.dwItemID, damage.dwSpriteID);
        row.AddHelpSF(help.bySFType, help.dwItemID, help.dwSpriteID);
    }
    const bool leader = m_byMemberType == UI_PMT_LEADER;
    row.EnableRemveButton(leader);
    row.EnableChLeaderButton(leader);
    m_byMemberOrder[m_byTotalMember++] = static_cast<BYTE>(slot);
    Add(&row);
    EnableLockNLeaveButton(!leader || m_byTotalMember < MAX_PARTY_MEMBER_NUM);
    Layout455();
    return TRUE;
}

void CGUIPartyWindow::RemoveMember(DWORD id)
{
    for (unsigned i = 0; i < m_byTotalMember; ++i) {
        auto& row = m_uiMember[m_byMemberOrder[i]];
        if (row.GetMemberID() != id) continue;
        row.ClearMemberInfo();
        Remove(&row);
        if (id == m_leader455) m_leader455 = NONE_MEMBER_ID;
        std::move(m_byMemberOrder + i + 1, m_byMemberOrder + m_byTotalMember, m_byMemberOrder + i);
        m_byMemberOrder[--m_byTotalMember] = NONE_ORDER;
        EnableLockNLeaveButton(m_byTotalMember != 0);
        Layout455();
        return;
    }
}

void CGUIPartyWindow::RemoveAllMember()
{
    for (unsigned i = 0; i < m_byTotalMember; ++i) {
        auto& row = m_uiMember[m_byMemberOrder[i]];
        row.ClearMemberInfo();
        Remove(&row);
        m_byMemberOrder[i] = NONE_ORDER;
    }
    m_byTotalMember = 0;
    m_leader455 = NONE_MEMBER_ID;
    EnableLockNLeaveButton(FALSE);
    Layout455();
}

void CGUIPartyWindow::SetLeader(DWORD id)
{
    for (unsigned i = 0; i < m_byTotalMember; ++i) {
        auto& row = m_uiMember[m_byMemberOrder[i]];
        if (row.GetMemberID() != id) continue;
        m_uiMember[m_byMemberOrder[0]].GetCharNameInfo()->GetFont()->dwColor = UI_PARTY_MEMBER_COLOR;
        std::rotate(m_byMemberOrder, m_byMemberOrder + i, m_byMemberOrder + i + 1);
        row.GetCharNameInfo()->GetFont()->dwColor = UI_PARTY_LEADER_COLOR;
        m_leader455 = id;
        Layout455();
        return;
    }
}

void CGUIPartyWindow::SetTotalMemberNum(int count)
{
    m_byTotalMember = static_cast<BYTE>(count);
    char label[96] = {};
    const char* format = RF455UnitView::Text(count ? 0x3e7 : 0x3e6);
    if (format) {
        if (count) std::snprintf(label, sizeof label, format, count + 1, 12);
        else std::snprintf(label, sizeof label, format, 12);
    }
    m_uiTitle.SetString(label);
    m_uiTitle.SetPos(m_uiTitleBoard.GetPosX() + 7,
                     m_uiTitleBoard.GetPosY() + (m_uiTitleBoard.GetSizeY() - m_uiTitle.GetSizeY()) / 2);
}

void CGUIPartyWindow::Lock(BOOL locked)
{
    m_bIsLocked = locked;
    const unsigned label = m_byMemberType != UI_PMT_LEADER ? 0x3e0 : (locked ? 0x3e2 : 0x3e1);
    m_uiLockNLeaveButton.SetLabel(RF455UnitView::Text(label));
}

void CGUIPartyWindow::EnableLockNLeaveButton(BOOL enable)
{
    if (enable) m_uiLockNLeaveButton.Enable();
    else m_uiLockNLeaveButton.Disable();
}

void CGUIPartyWindow::SetDistribution455(BYTE mode)
{
    if (mode >= 3) return;
    m_distribution455 = mode;
    m_uiDistribution455.GetSpriteInfo()->wFrameNo = WORD(9 + 2 * mode);
}

void CGUIPartyWindow::MouseEvent(_mouse_event& event)
{
    CGUIWindow::MouseEvent(event);
    if (event.id == MOUSE_STROKED && event.source == &m_uiDistribution455 && m_byMemberType == UI_PMT_LEADER) {
        PostMessageA(gScreen.GetHWND(), 0x41e, (m_distribution455 + 1) % 3, 0);
    } else if (event.id == MOUSE_CLICKED) {
        if (event.source == &m_uiViewToggle455) {
            m_compact455 = !m_compact455;
            m_uiViewToggle455.GetSpriteInfo()->wFrameNo = m_compact455 ? 18 : 17;
            Layout455();
        } else if (event.source == &m_uiLockNLeaveButton) {
            if (m_byMemberType == UI_PMT_LEADER)
                PostMessageA(gScreen.GetHWND(), WM_PARTY_LOCKON_ADDMEMBER, !m_bIsLocked, 0);
            else if (m_byMemberType == UI_PMT_MEMBER)
                PostMessageA(gScreen.GetHWND(), WM_PARTY_LEAVE_PARTY, 0, 0);
        }
    }
}
