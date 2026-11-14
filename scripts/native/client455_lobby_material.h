#pragma once
#include <d3d9.h>
#include <cstdint>

struct RF455LobbyMaterialTelemetry {
    std::uint64_t attempts, binds, skips, errors;
    std::uint64_t authoredBinds, authoredTextureBytes;
    std::uint64_t authoredSetBinds[2]; // Wall atlas, broad-panel atlas; successful material binds.
    HRESULT error;
    char errorStage[96];
    char compilerError[384]; // Last compile diagnostic only; bounded, no frame log spam.
    bool ready, authoredReady;
};
// Release before Reset/Invalidate; the implementation lives in r3render.cpp.
void RF455_ReleaseLobbyMaterial();
RF455LobbyMaterialTelemetry RF455_GetLobbyMaterialTelemetry();
void RF455_ResetLobbyMaterialTelemetry();
