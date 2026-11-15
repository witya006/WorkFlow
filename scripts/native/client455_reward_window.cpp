#include "client455_reward_window.h"
#include "client455_item_text.h"
#include "client455_language.h"
#include "client455_modal.h"
#include "2dsprite.h"
#include "userinterface/guicontroller/guiscreen.h"
#include "userinterface/spritemgr.h"
#include <cstring>

namespace {
constexpr LONG rewardWidth = 462;
constexpr LONG rewardHeight = 274;
constexpr LONG rewardPitch = 70;
constexpr LONG rewardIconSize = 64;
constexpr unsigned noSelection = 0xff;

char* rewardText455(unsigned index)
{
    return const_cast<char*>(RF455_GetNormalLanguagePack()->get(index));
}

bool rewardStackable455(unsigned kind)
{
    switch (kind) {
    case 13: case 16: case 17: case 20: case 22: case 23: case 26: case 30:
    case 31: case 32: case 34: case 35:
        return true;
    default:
        return false;
    }
}

void centerRewardText455(CGUIText& text, LONG x, LONG y)
{
    text.SetPos(x + (rewardWidth - text.GetSizeX()) / 2, y);
}

void choicePrompt455(char (&text)[512])
{
    // The shipped prompt expects one decimal argument. Expand only that
    // placeholder so a custom language file cannot supply varargs directives.
    const char* source = rewardText455(0xe79);
    std::size_t count = 0;
    while (*source && count < sizeof(text) - 1) {
        if (source[0] == '%' && source[1] == 'd') {
            text[count++] = '1';
            source += 2;
        } else {
            text[count++] = *source++;
        }
    }
    text[count] = 0;
}
}

void CGUIRewardWindow455::RewardIcon::DrawSelection()
{
    if (!selected_ || !IsShow()) return;
    const LONG left = GetPosX(), top = GetPosY();
    const LONG right = left + GetSizeX(), bottom = top + GetSizeY();
    constexpr DWORD color = 0xffd9c096;
    Draw2DRectangle(left, top, right, top + 2, color);
    Draw2DRectangle(left, bottom - 2, right, bottom, color);
    Draw2DRectangle(left, top + 2, left + 2, bottom - 2, color);
    Draw2DRectangle(right - 2, top + 2, right, bottom - 2, color);
}

BOOL CGUIRewardWindow455::RewardIcon::Draw()
{
    const auto drawn = CGUIItem::Draw();
    DrawSelection();
    return drawn;
}

BOOL CGUIRewardWindow455::RewardIcon::Draw(RECT& clipping)
{
    const auto drawn = CGUIItem::Draw(clipping);
    DrawSelection();
    return drawn;
}

void CGUIRewardWindow455::RewardButton::DrawFallback()
{
    if (!IsShow() || GetSpriteInfo()->pSprite) return;
    const LONG left = GetPosX(), top = GetPosY();
    const LONG right = left + GetSizeX(), bottom = top + GetSizeY();
    Draw2DRectangle(left, top, right, bottom, 0xff645b50);
    Draw2DRectangle(left + 1, top + 1, right - 1, bottom - 1, 0xff272c2e);
}

BOOL CGUIRewardWindow455::RewardButton::Draw()
{
    DrawFallback();
    return CGUIButtonEx::Draw();
}

BOOL CGUIRewardWindow455::RewardButton::Draw(RECT& clipping)
{
    DrawFallback();
    return CGUIButtonEx::Draw(clipping);
}

CGUIRewardWindow455::~CGUIRewardWindow455()
{
    board_.RemoveAll();
    RemoveAll();
}

void CGUIRewardWindow455::Init()
{
    if (!initialized_) {
        SetID(51);
        SetSize(rewardWidth, rewardHeight);
        board_.SetColors455(0xff222628, 0xff5a5857);
        board_.SetBorder455(1, 3);
        title_.DisableFocus();
        prompt_.DisableFocus();
        title_.SetMouseInput455(FALSE);
        prompt_.SetMouseInput455(FALSE);
        title_.GetFont()->dwColor = 0xffe2d7c3;
        prompt_.GetFont()->dwColor = 0xffe2d7c3;
        action_.SetLabelColor(0xffe2d7c3);
        action_.SetLabelHoveredColor(0xffffdeb1);
        board_.Add(&title_);
        board_.Add(&prompt_);
        for (auto& icon : icons_) {
            icon.SetIconType455(0);
            icon.SetSize(rewardIconSize, rewardIconSize);
            icon.ShowGradeFrame455(FALSE);
            icon.AddMouseEventHandler(this);
            board_.Add(&icon);
        }
        action_.AddMouseEventHandler(this);
        board_.Add(&action_);
        Add(&board_);
        Show(FALSE);
        initialized_ = true;
    }
    SetSprite();
}

void CGUIRewardWindow455::SetSprite()
{
    auto* common = gSpriteMgr.GetTargetSprite455(1);
    if (!common || common->GetMaxActions() <= 4 || common->GetMaxFrames(4) <= 4)
        common = nullptr;
    board_.SetCaps455(common, TRUE);
    if (!common) {
        board_.GetUpper455().SetSize(0, 0);
        board_.GetLower455().SetSize(0, 0);
    }
    RF455_ConfigureModalButton(action_);
    if (!action_.GetSpriteInfo()->pSprite) action_.SetSize(88, 24);
    RF455_ConfigureModalCaption(action_, 0x6a);
    title_.SetString(rewardText455(0xe78));
    if (initialized_) {
        RefreshPage455();
        Layout455();
    }
}

void CGUIRewardWindow455::Layout455()
{
    const LONG x = (gScreen.GetSizeX() - rewardWidth) / 2;
    const LONG y = (gScreen.GetSizeY() - rewardHeight) / 2;
    SetPos(x, y);
    board_.SetPos(x, y);
    board_.SetSize(rewardWidth, rewardHeight);
    centerRewardText455(title_, x, y + 12);
    centerRewardText455(prompt_, x, y + 50);
    for (unsigned i = 0; i < icons_.size(); ++i) {
        icons_[i].SetPos(x + 24 + rewardPitch * (i % 6), y + 78 + rewardPitch * (i / 6));
    }
    action_.SetPos(x + (rewardWidth - action_.GetSizeX()) / 2, y + 225);
}

void CGUIRewardWindow455::RefreshPage455()
{
    ClearRewardTooltip455();
    if (state_.Phase() == RF455RewardPhase::Choice) {
        char text[512] = {};
        choicePrompt455(text);
        prompt_.SetString(text);
    } else {
        prompt_.SetString(rewardText455(0xe7b));
    }
    for (unsigned i = 0; i < icons_.size(); ++i) {
        auto& icon = icons_[i];
        const auto* entry = state_.VisibleAt(i);
        const auto row = entry ? RF455_GameItems().data.getItem(entry->item.kind, entry->item.itemOrdinal)
                               : RF455ItemDataSpan{};
        icon.SetSelected(i == selected_);
        if (!row.data || row.size < 89) {
            icon.SetEmpty();
            icon.Show(FALSE);
            continue;
        }
        DWORD itemId, spriteId;
        std::memcpy(&itemId, row.data + 72, sizeof(itemId));
        std::memcpy(&spriteId, row.data + 76, sizeof(spriteId));
        icon.SetItemID(itemId);
        icon.SetSpriteID(spriteId);
        icon.SetObjectIndex455(entry->item.itemOrdinal);
        const auto kind = row.data[88];
        const bool hasGrade = kind <= 10 && row.size > 152;
        icon.SetGrade455(hasGrade ? row.data[152] : 0);
        icon.SetNum(rewardStackable455(kind) ? entry->item.quantity : 1);
        icon.DrawItemNum(TRUE);
        icon.SetSprite();
        icon.Show(IsShow());
    }
    if (state_.Phase() == RF455RewardPhase::Choice && selected_ == noSelection)
        action_.Disable();
    else
        action_.Enable();
    centerRewardText455(prompt_, GetPosX(), GetPosY() + 50);
}

void CGUIRewardWindow455::ShowRewardTooltip455(unsigned index)
{
    const auto* entry = state_.VisibleAt(index);
    if (!entry || !icons_[index].IsShow() || hovered_ == index) return;
    ClearRewardTooltip455();

    // Resolve the compact summary through the displayed entry even after a gap.
    RF455RewardTooltip tooltip;
    if (!RF455_GameItems().data.makeRewardTooltip(entry->item.kind, entry->item.itemOrdinal, tooltip))
        return;
    char lines[TOOLTIP_MAX_LINE][TOOLTIP_MAX_STR]{};
    const auto length = RF455_AppendTooltipLines455(tooltip, RF455_GetNormalLanguagePack()->codepage,
                                                    lines, TOOLTIP_MAX_LINE);
    if (!length) return;
    gScreen.SetTooltip_Item(&icons_[index], static_cast<BYTE>(length), lines);
    hovered_ = index;
}

void CGUIRewardWindow455::ClearRewardTooltip455()
{
    if (hovered_ < icons_.size() && GetMouseDetectedObject() == &icons_[hovered_])
        gScreen.RemoveTooltip();
    hovered_ = noSelection;
}

void CGUIRewardWindow455::Select455(unsigned index)
{
    if (state_.Phase() != RF455RewardPhase::Choice || !state_.VisibleAt(index) || !icons_[index].IsShow())
        return;
    if (selected_ != noSelection) icons_[selected_].SetSelected(false);
    selected_ = index;
    icons_[selected_].SetSelected(true);
    action_.Enable();
}

bool CGUIRewardWindow455::TrySubmit455()
{
    if (state_.Phase() != RF455RewardPhase::ReadyToSubmit || !submit_ || !submit_(state_))
        return false;
    Close();
    return true;
}

bool CGUIRewardWindow455::Present455(std::uint32_t ordinal, const RF455PremiumOffer& offer)
{
    if (!state_.Begin(ordinal, offer)) return false;
    if (!initialized_) Init();
    selected_ = noSelection;
    if (TrySubmit455()) return true;
    Layout455();
    CGUIWindow::Open();
    RefreshPage455();
    return true;
}

void CGUIRewardWindow455::Close()
{
    ClearRewardTooltip455();
    if (IsShow()) CGUIWindow::Close();
    state_.Clear();
    selected_ = noSelection;
}

void CGUIRewardWindow455::MouseEvent(_mouse_event& event)
{
    CGUIWindow::MouseEvent(event);
    if (!IsShow()) return;
    for (unsigned i = 0; i < icons_.size(); ++i) {
        if (event.source != &icons_[i]) continue;
        if (event.id == MOUSE_HOVERED) ShowRewardTooltip455(i);
        if ((event.id == MOUSE_LEAVED || event.id == MOUSE_STROKED || event.id == LMOUSE_STROKED) &&
            hovered_ == i) {
            // The shared GUI input code clears the tooltip before dispatch.
            hovered_ = noSelection;
        }
        if (event.id == MOUSE_STROKED) Select455(i);
        return;
    }
    if (event.id != MOUSE_CLICKED || event.source != &action_) return;
    if (state_.Phase() == RF455RewardPhase::Choice) {
        if (!state_.Choose(selected_)) return;
        selected_ = noSelection;
        RefreshPage455();
    } else if (state_.Phase() == RF455RewardPhase::Summary) {
        state_.Confirm();
    }
    TrySubmit455();
}
