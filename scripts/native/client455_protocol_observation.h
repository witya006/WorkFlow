#pragma once
#include <windows.h>
#include <cstdio>

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
};

inline RF455WorldObservation& RF455_WorldObservation() {
    static RF455WorldObservation state;
    return state;
}

inline void RF455_RecordMonsterDraw(unsigned serial, unsigned mesh, unsigned animation, unsigned boneFrame,
                                    float screenX, float screenY) {
    auto& state = RF455_WorldObservation();
    if (!state.captureMonsters || !state.remaining || state.monsterDraw.present || state.monsterCaptures >= 3 ||
        (state.monsterCaptures && serial != state.sampledMonster)) return;
    state.monsterDraw = {true, serial, mesh, animation, boneFrame, screenX, screenY};
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
    }
}
