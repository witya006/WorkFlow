#ifndef RF455_REWARD_WINDOW_H
#define RF455_REWARD_WINDOW_H

#include "client455_briefing_controls.h"
#include "client455_reward_state.h"
#include "userinterface/guicontroller/guibutton.h"
#include "userinterface/guicontroller/guiwindow.h"

class CGUIRewardWindow455 final : public CGUIWindow {
public:
    using Submit = bool (*)(const RF455RewardState&);

    ~CGUIRewardWindow455() override;
    void Init() override;
    void SetSprite() override;
    void SetSubmit455(Submit submit) { submit_ = submit; }
    bool Present455(std::uint32_t ordinal, const RF455PremiumOffer&);
    void Close() override;
    void MouseEvent(_mouse_event&) override;

private:
    class RewardIcon : public CGUIItem {
    public:
        void SetSelected(bool selected) { selected_ = selected; }
        BOOL Draw() override;
        BOOL Draw(RECT& clipping) override;
    private:
        bool selected_ = false;
        void DrawSelection();
    };
    class RewardButton : public CGUIButtonEx {
    public:
        BOOL Draw() override;
        BOOL Draw(RECT& clipping) override;
    private:
        void DrawFallback();
    };

    CGUIBriefingBoard board_;
    CGUIText title_, prompt_;
    RewardButton action_;
    std::array<RewardIcon, 10> icons_;
    RF455RewardState state_;
    Submit submit_ = nullptr;
    bool initialized_ = false;
    unsigned selected_ = 0xff;
    unsigned hovered_ = 0xff;

    void Layout455();
    void RefreshPage455();
    void Select455(unsigned index);
    void ShowRewardTooltip455(unsigned index);
    void ClearRewardTooltip455();
    bool TrySubmit455();
};

#endif
