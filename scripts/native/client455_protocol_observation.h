#pragma once
#include <windows.h>
#include <cstdio>
#include <cstdlib>

// Opt-in own-client diagnostics. Never pass account data, keys or payloads.
inline void RF455_ObserveProtocol(const char* event,unsigned category,unsigned kind,unsigned bytes){
    char enabled[2]={};
    if(GetEnvironmentVariableA("RF455_OBSERVE_PROTOCOL",enabled,sizeof(enabled))!=1||enabled[0]!='1')return;
    char text[128];
    std::sprintf(text,"RF455 Protocol:%s:%u:%u:%u",event,category,kind,bytes);
    OutputDebugStringA(text);
}

struct RF455MonsterDraw {
    bool present = false;
    unsigned serial = 0;
    unsigned mesh = 0;
    unsigned animation = 0;
    unsigned boneFrame = 0;
    float screenX = 0;
    float screenY = 0;
    float depth = 0;
};

struct RF455WorldObservation {
    unsigned remaining = 0;
    ULONGLONG acceptedAt = 0;
    bool walk = false;
    bool walkKeyObserved = false;
    bool walkKeyReleased = false;
    bool camera = false;
    unsigned cameraPhase = 0;
    bool captureMonsters = false;
    RF455MonsterDraw monsterDraw;
    unsigned monsterCaptures = 0;
    unsigned sampledMonster = 0;
    ULONGLONG nextMonsterCaptureAt = 0;
    bool combat = false;
    unsigned combatRecord = ~0u;
    unsigned combatApproachMs = 0;
    RF455MonsterDraw combatDraw;
    unsigned combatTarget = 0;
    unsigned combatPreviousTarget = 0;
    unsigned combatClicks = 0;
    unsigned combatAttackKeys = 0;
    unsigned combatAmmunitionUpdates = 0;
    unsigned combatImpactFrames = 0;
    unsigned combatImpactDamage = 0;
    bool combatImpactPending = false;
    float combatScanBaseYaw = 0;
    ULONGLONG nextCombatClickAt = 1280;
    bool combatButtonDown = false;
};

inline RF455WorldObservation& RF455_WorldObservation() {
    static RF455WorldObservation state;
    return state;
}

inline unsigned RF455_ReadCombatObservationOption(const char* name, unsigned maximum, unsigned fallback) {
    char value[6]{};
    const auto length = GetEnvironmentVariableA(name, value, sizeof(value));
    if (!length || length >= sizeof(value)) return fallback;
    char* end = nullptr;
    const auto number = std::strtoul(value, &end, 10);
    return *end == '\0' && number <= maximum ? number : fallback;
}

inline void RF455_RecordCombatImpact(unsigned serial, unsigned damage, float health) {
    auto& state = RF455_WorldObservation();
    if (!state.combat || serial != state.combatTarget) return;
    const unsigned basis = health >= 1.0f ? 10000 : health > 0.0f ? unsigned(health * 10000.0f + 0.5f) : 0;
    RF455_ObserveProtocol("combat-impact", serial, damage, basis);
    if (state.combatImpactFrames < 2) {
        state.combatImpactDamage = damage;
        state.combatImpactPending = true;
    }
}

inline void RF455_RecordMonsterDraw(unsigned serial, unsigned record, unsigned mesh, unsigned animation, unsigned boneFrame,
                                    float screenX, float screenY, float depth) {
    auto& state = RF455_WorldObservation();
    if (!state.captureMonsters || !state.remaining) return;
    const RF455MonsterDraw draw{true, serial, mesh, animation, boneFrame, screenX, screenY, depth};
    if (!state.monsterDraw.present && state.monsterCaptures < 3 &&
        (!state.monsterCaptures || serial == state.sampledMonster)) state.monsterDraw = draw;
    const bool clearOfMinimap = screenX < 0.5f || screenY < 0.35f;
    const bool clearOfStatus = screenX > -0.35f || screenY < 0.65f;
    if (state.combat && clearOfMinimap && clearOfStatus && !state.combatTarget &&
        (state.combatRecord == ~0u || state.combatRecord == record) &&
        serial != state.combatPreviousTarget &&
        (!state.combatDraw.present || depth < state.combatDraw.depth)) state.combatDraw = draw;
}

inline void RF455_ArmWorldObservation(BYTE mode) {
    char enabled[2] = {};
    if (mode == 0xff ||
        GetEnvironmentVariableA("RF455_CAPTURE_WORLD", enabled, sizeof(enabled)) != 1 ||
        enabled[0] != '1') return;
    auto& state = RF455_WorldObservation();
    if (!state.acceptedAt) {
        const bool walk = GetEnvironmentVariableA("RF455_OBSERVE_WALK", enabled, sizeof(enabled)) == 1 &&
                          enabled[0] == '1';
        state = {walk ? 6u : 3u, GetTickCount64(), walk};
        state.camera = !walk && GetEnvironmentVariableA("RF455_OBSERVE_CAMERA", enabled, sizeof(enabled)) == 1 &&
                       enabled[0] == '1';
        state.captureMonsters = walk && GetEnvironmentVariableA("RF455_CAPTURE_MONSTERS", enabled, sizeof(enabled)) == 1 &&
                                enabled[0] == '1';
        state.combat = state.captureMonsters &&
                       GetEnvironmentVariableA("RF455_OBSERVE_COMBAT", enabled, sizeof(enabled)) == 1 &&
                       enabled[0] == '1';
        if (state.combat) {
            state.combatRecord = RF455_ReadCombatObservationOption("RF455_COMBAT_RECORD", 65535, ~0u);
            state.combatApproachMs = RF455_ReadCombatObservationOption("RF455_COMBAT_APPROACH_MS", 30000, 0);
            if (state.combatApproachMs) state.nextCombatClickAt = state.combatApproachMs + 900;
        }
    }
}
