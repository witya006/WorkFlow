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

struct RF455WorldObservation {
    unsigned remaining = 0;
    ULONGLONG acceptedAt = 0;
};

inline RF455WorldObservation& RF455_WorldObservation() {
    static RF455WorldObservation state;
    return state;
}

inline void RF455_ArmWorldObservation(BYTE mode) {
    char enabled[2] = {};
    if (mode == 0xff ||
        GetEnvironmentVariableA("RF455_CAPTURE_WORLD", enabled, sizeof(enabled)) != 1 ||
        enabled[0] != '1') return;
    auto& state = RF455_WorldObservation();
    if (!state.acceptedAt) state = {3, GetTickCount64()};
}
