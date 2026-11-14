#pragma once
#include <d3d9.h>
#include <cstdint>

struct RF455LobbyMaterialTelemetry {
    std::uint64_t attempts, binds, skips, errors;
    HRESULT error;
    char errorStage[96];
    char compilerError[384]; // Last compile diagnostic only; bounded, no frame log spam.
    bool ready;
};
// Release before Reset/Invalidate; the implementation lives in r3render.cpp.
void RF455_ReleaseLobbyMaterial();
RF455LobbyMaterialTelemetry RF455_GetLobbyMaterialTelemetry();
void RF455_ResetLobbyMaterialTelemetry();
