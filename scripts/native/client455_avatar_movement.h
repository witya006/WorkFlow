#pragma once

#include <cmath>
#include <cstddef>
#include <cstdint>

constexpr std::uint8_t RF455MoveOpcode = 1;
constexpr std::uint8_t RF455PositionSampleOpcode = 2;
constexpr std::uint8_t RF455StopOpcode = 19;
constexpr std::uint8_t RF455StopResultOpcode = 20;

struct RF455MovementState {
    std::uint32_t sequence = 1;
    std::uint32_t pendingAt = 0;
    bool pending = false;
    bool stopArmed = false;
    bool predictLocally = false;

    bool isWaiting(std::uint32_t now) const
    {
        return pending && now - pendingAt < 5000;
    }

    void clearPending()
    {
        pending = false;
        pendingAt = 0;
    }
};

#pragma pack(push, 1)
struct RF455MoveRequest {
    std::uint8_t moveMode;
    float current[3];
    std::uint32_t sequence;
    std::int16_t targetXZ[2];
    std::uint8_t flags;
    float speed;
};

struct RF455PositionReport {
    std::uint32_t sequence;
    float current[3];
};

struct RF455MoveBroadcast {
    std::uint32_t serial;
    std::int16_t current[3];
    std::int16_t targetXZ[2];
    std::int16_t speed;
    std::uint8_t flags;
};

struct RF455StopResult {
    std::uint32_t serial;
    std::int16_t position[3];
};
#pragma pack(pop)

static_assert(sizeof(RF455MoveRequest) == 26 && offsetof(RF455MoveRequest, sequence) == 13 &&
              offsetof(RF455MoveRequest, targetXZ) == 17 && offsetof(RF455MoveRequest, speed) == 22);
static_assert(sizeof(RF455PositionReport) == 16 && offsetof(RF455PositionReport, current) == 4);
static_assert(sizeof(RF455MoveBroadcast) == 17 && offsetof(RF455MoveBroadcast, speed) == 14);
static_assert(sizeof(RF455StopResult) == 10 && offsetof(RF455StopResult, position) == 4);

inline bool RF455_FinitePosition(const float* position)
{
    return position && std::isfinite(position[0]) && std::isfinite(position[1]) &&
           std::isfinite(position[2]);
}

inline bool RF455_EncodeMovementTarget(float x, float z, std::int16_t (&target)[2])
{
    const auto fits = [](float value) { return value > -32769.f && value < 32768.f; };
    if (!fits(x) || !fits(z)) return false;
    target[0] = static_cast<std::int16_t>(x);
    target[1] = static_cast<std::int16_t>(z);
    return true;
}

// This is the position message transform inside the existing framed transport.
inline void RF455_EncodePositionBody(void* body, std::size_t size, std::uint8_t opcode,
                                    std::uint8_t delta, std::uint16_t mask, bool tutorial)
{
    if (tutorial) return;
    auto* bytes = static_cast<std::uint8_t*>(body);
    const auto add = static_cast<std::uint8_t>(delta + 24);
    const auto xorMask = static_cast<std::uint8_t>(mask + opcode + 32);
    for (std::size_t index = 0; index < size; ++index)
        bytes[index] = static_cast<std::uint8_t>(bytes[index] + add) ^ xorMask;
}
