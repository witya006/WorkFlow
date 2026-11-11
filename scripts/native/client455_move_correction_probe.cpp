#include "gameobject/manager/ccharactermgr.h"
#include "network/cnetworkmgr.h"

#include <array>
#include <cstdio>
#include <cstring>
#include <limits>
#include <memory>
#include <stdexcept>

namespace {
struct NetworkAccess : CNetworkMgr {
    using CNetworkMgr::AnalysisServerPacket;
};

struct AvatarAccess : CAvatar {
    using CPlayer::m_profile17796_455;
};

void require(bool result, const char* message)
{
    if (!result) throw std::runtime_error(message);
}

using Point = std::array<float, 3>;

int run()
{
    ChInterface renderer;
    g_ifCharIF = &renderer;
    struct ResetAnimation {
        ~ResetAnimation() {
            _DestroyAnimationMgr();
            g_ifCharIF = nullptr;
        }
    } animation;
    require(_CreateAnimationMgr(), "normal animation owner");
    auto network = std::make_unique<NetworkAccess>();
    auto player = std::make_unique<AvatarAccess>();
    auto& avatar = *player;
    avatar.SetCharTypeID(CTI_AVATAR);
    struct ResetAvatar {
        ~ResetAvatar() { g_pAvatar = nullptr; }
    } resetAvatar;

    const auto dispatch = [&](BYTE reason, Point position, WORD size = 13) {
        std::array<char, 14> bytes{};
        bytes[0] = static_cast<char>(reason);
        std::memcpy(bytes.data() + 1, position.data(), sizeof(float) * position.size());
        _MSG_HEADER header{WORD(size + 4), {4, 3}};
        return network->AnalysisServerPacket(&header, bytes.data());
    };
    const auto isAt = [&](Point position) {
        return avatar.GetPosX() == position[0] && avatar.GetPosY() == position[1] &&
               avatar.GetPosZ() == position[2];
    };

    constexpr Point first{-4743.4375f, 428.875f, 4802.0625f};
    require(dispatch(6, first), "valid correction before avatar binding");
    g_pAvatar = &avatar;
    avatar.CCharacter::SetAction(CAI_MOVE_STOP);
    require(dispatch(6, first) && isAt(first) && avatar.GetAction() == CAI_MOVE_STOP,
            "standing avatar accepts unaligned fractional coordinates");
    Vector3f previous{};
    avatar.GetPrevPosition(previous);
    require(previous[0] == first[0] + 0.5f && previous[1] == first[1] && previous[2] == first[2],
            "the usual position setter updates the previous point");

    avatar.CCharacter::SetAction(CAI_MOVE_MOVING);
    constexpr Point second{-4700.75f, 420.125f, 4797.25f};
    require(dispatch(6, second) && isAt(second) && avatar.GetAction() == CAI_MOVE_MOVING,
            "default profile continues moving after correction");
    constexpr float inf = std::numeric_limits<float>::infinity();
    constexpr float nan = std::numeric_limits<float>::quiet_NaN();
    _MSG_HEADER nullBody{17, {4, 3}};
    require(!dispatch(6, first, 12) && !dispatch(6, first, 14) &&
            !network->AnalysisServerPacket(&nullBody, nullptr) &&
            !dispatch(6, {nan, 1.0f, 2.0f}) && !dispatch(6, {1.0f, inf, 2.0f}) &&
            !dispatch(6, {1.0f, 2.0f, -inf}) && isAt(second) && avatar.GetAction() == CAI_MOVE_MOVING,
            "bad inputs preserve current position and action");

    avatar.m_profile17796_455 = 1;
    require(dispatch(7, first) && isAt(first) && avatar.GetAction() == CAI_MOVE_MOVING,
            "profile 1 continues moving for a different reason");
    for (BYTE reason : {BYTE(6), BYTE(12)}) {
        avatar.CCharacter::SetAction(CAI_MOVE_MOVING);
        require(dispatch(reason, second) && isAt(second) && avatar.GetAction() == CAI_MOVE_STOP,
                "profile 1 stops on the two original reason codes");
    }
    avatar.m_profile17796_455 = 2;
    avatar.CCharacter::SetAction(CAI_MOVE_MOVING);
    require(dispatch(12, first) && isAt(first) && avatar.GetAction() == CAI_MOVE_MOVING,
            "other nonzero profiles preserve movement");

    std::puts("{\"status\":\"PASS\",\"position_bytes\":13,\"invalid_cases\":6,"
              "\"standing_updates\":true,\"moving_updates\":true,\"previous_position_updated\":true,"
              "\"stop_profile\":1,\"stop_reasons\":[6,12]}");
    return 0;
}
}

int main()
{
    try {
        return run();
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n", error.what());
        return 1;
    }
}
