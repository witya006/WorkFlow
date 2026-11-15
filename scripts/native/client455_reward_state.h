#ifndef RF455_REWARD_STATE_H
#define RF455_REWARD_STATE_H

#include "client455_client_items.h"
#include <array>
#include <cstddef>
#include <cstdint>

enum class RF455RewardPhase {
    Idle,
    Choice,
    Summary,
    ReadyToSubmit,
};

struct RF455RewardVisibleEntry {
    std::uint8_t slot = 0xff;
    RF455PremiumOfferSlot item;
};

class RF455RewardState {
public:
    bool Begin(std::uint32_t ordinal, const RF455PremiumOffer& offer)
    {
        if (ordinal > 0xfffeu) return false;
        Clear();
        ordinal_ = static_cast<std::uint16_t>(ordinal);
        offer_ = offer;
        ShowPage(0);
        return true;
    }

    void Clear()
    {
        phase_ = RF455RewardPhase::Idle;
        ordinal_ = 0xffffu;
        page_ = 6;
        visibleCount_ = 0;
        selections_.fill(0xff);
    }

    unsigned Page() const { return page_; } // 6 while idle.
    RF455RewardPhase Phase() const { return phase_; }
    std::uint16_t Ordinal() const { return ordinal_; }
    const std::array<std::uint8_t, 5>& Selections() const { return selections_; }
    std::size_t VisibleCount() const { return visibleCount_; }
    const RF455RewardVisibleEntry* VisibleAt(std::size_t index) const
    {
        return index < visibleCount_ ? &visible_[index] : nullptr;
    }

    bool Choose(unsigned visibleIndex)
    {
        if (phase_ != RF455RewardPhase::Choice || visibleIndex >= visibleCount_) return false;
        selections_[page_] = visible_[visibleIndex].slot;
        ShowPage(page_ + 1);
        return true;
    }

    bool Confirm()
    {
        if (phase_ != RF455RewardPhase::Summary) return false;
        phase_ = RF455RewardPhase::ReadyToSubmit;
        return true;
    }

private:
    RF455PremiumOffer offer_{};
    std::array<std::uint8_t, 5> selections_{{0xff, 0xff, 0xff, 0xff, 0xff}};
    std::array<RF455RewardVisibleEntry, 10> visible_{};
    std::size_t visibleCount_ = 0;
    RF455RewardPhase phase_ = RF455RewardPhase::Idle;
    std::uint16_t ordinal_ = 0xffffu;
    unsigned page_ = 6;

    void ShowPage(unsigned next)
    {
        // RVA 0x092860 skips a choice page when its first reward is missing.
        while (next < selections_.size() && !offer_.pages[next][0].resolved) ++next;
        page_ = next;
        visibleCount_ = 0;
        const bool summary = page_ == selections_.size();
        const auto& items = offer_.pages[page_];
        for (std::size_t slot = 0; slot < items.size(); ++slot) {
            if (!items[slot].resolved) {
                // RVA 0x092860 keeps scanning the summary after a gap.
                if (summary) continue;
                break;
            }
            visible_[visibleCount_++] = {static_cast<std::uint8_t>(slot), items[slot]};
        }
        if (summary)
            phase_ = visibleCount_ ? RF455RewardPhase::Summary : RF455RewardPhase::ReadyToSubmit;
        else
            phase_ = RF455RewardPhase::Choice;
    }
};

#endif
