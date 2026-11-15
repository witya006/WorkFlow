#ifndef RF455_REWARD_WIRE_H
#define RF455_REWARD_WIRE_H

#include "client455_reward_state.h"
#include <array>
#include <cstddef>
#include <cstdint>

inline bool RF455_ReadRewardOfferOrdinal(const char* payload, std::size_t size,
                                       std::uint32_t& ordinal)
{
    // Event 11/32 uses the first DWORD of the body.
    if (!payload || size < 4) return false;
    ordinal = 0;
    for (unsigned byte = 0; byte < 4; ++byte)
        ordinal |= std::uint32_t(static_cast<unsigned char>(payload[byte])) << (8 * byte);
    return true;
}

inline bool RF455_MakeRewardSelection(const RF455RewardState& state,
                                      std::array<unsigned char, 9>& payload)
{
    // 0x1A7B80 sends Event 11/33: zero-extended row index and five slot bytes.
    if (state.Phase() != RF455RewardPhase::ReadyToSubmit) return false;
    const auto ordinal = state.Ordinal();
    payload = {static_cast<unsigned char>(ordinal), static_cast<unsigned char>(ordinal >> 8), 0, 0};
    const auto& choices = state.Selections();
    for (std::size_t i = 0; i < choices.size(); ++i) payload[4 + i] = choices[i];
    return true;
}

#endif
