#pragma once
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

// Source-owned load model, not a binary overlay of the 20600-byte RTM actor.
// Resource handles and camera/dummy bindings belong to the runtime owner.
struct RF455RvpActor {
    std::uint32_t flags=0, color=0, meshId=0, magicIndex=0;
    std::uint32_t linkedActor=0xffffffffu, traceAction=0, traceOn=0, traceOff=0;
    float scale=1, waveDistance=0, xAngle=0, yAngle=0;
    std::string name, mesh, bone, texturePath, wave, swordTrace, magicId, mapDummy;
    std::vector<std::string> animations;
};

enum class RF455RvpKind : std::uint8_t {
    Camera=1, FadeIn=2, FadeOut=3, Quake=5, Blur=10, TimerRate=11,
    Animation=0x84, CharacterFadeIn=0x86, CharacterFadeOut=0x87,
    Magic=0x88, Wave=0x89, Throw=0x8c
};

struct RF455RvpTrack {
    RF455RvpKind kind=RF455RvpKind::Camera;
    float frame=0, first=0, second=0;
    std::uint32_t actor=0xffffffffu, value=0;
    // Camera/dummy names keep the argument bytes; resolving removes its first
    // byte exactly as the455 loader does, rather than guessing a prefix.
    std::string reference, resource, attachment;
};

struct RF455RvpDocument {
    std::uint32_t flags=0, totalFrame=0;
    std::vector<RF455RvpActor> actors;
    std::vector<RF455RvpTrack> tracks;
    std::size_t ignoredTokens=0;
};
struct RF455CameraDocument;

// Transactional on rejected/truncated input. Unsafe legacy fixed-buffer overflow
// domains are rejected, not claimed equivalent to the original's corruption.
bool RF455_ParseRvp(const void*, std::size_t, RF455RvpDocument&, std::string* error=nullptr,
                    const RF455CameraDocument* camera=nullptr);
bool RF455_LoadRvp(const char*, RF455RvpDocument&, std::string* error=nullptr,
                   const RF455CameraDocument* camera=nullptr);

//4558D4D80 searches relative to the already-consumed cursor, preserving source
// order and equal-frame records. It requires a key on BOTH sides of the cursor.
bool RF455_RvpInterpolate(const RF455RvpDocument&, std::size_t cursor,
                         RF455RvpKind, float frame, float& value);
