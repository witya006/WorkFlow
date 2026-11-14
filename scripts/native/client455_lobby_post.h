#pragma once
#include <d3d9.h>
#include <cstdint>

enum class RF455LobbyPostStatus : unsigned {
    Disabled, Pending, Ready, Rendering, Complete, Unsupported, Failed
};
struct RF455LobbyPostTelemetry {
    RF455LobbyPostStatus status;
    bool enabled, available, active, inputLinear, uiSceneReady, fallbackDrawn;
    unsigned width, height, passCount, multisampleCount;
    D3DMULTISAMPLE_TYPE multisampleType;
    D3DFORMAT colorFormat, depthFormat;
    std::uint64_t estimatedVideoBytes, completedFrames;
    HRESULT error;
    char errorStage[96];
};

// Call after successful R3BeginScene, before its Clear and any 3D submissions.
// The caller must bypass this module while the legacy fullscreen-effect target
// is active (including credits). False leaves the original render state intact.
bool RF455_BeginLobbyPost(IDirect3DDevice9*);
// Called before UI. Ends the 3D scene, resolves MSAA outside Begin/EndScene,
// then starts a new scene, composites and restores state for the ordinary UI.
// The caller closes that scene with its normal R3EndScene. On device failure,
// uiSceneReady=false requires skipping UI and that EndScene for this frame.
void RF455_EndLobbyPost(IDirect3DDevice9*);
// Call before device Reset/Invalidate. No nested BeginScene, no Present here.
void RF455_ReleaseLobbyPost();
// Default disabled. Enabling requests lazy capability/resource initialization;
// capability failure leaves classic rendering usable and is reported below.
bool RF455_SetLobbyPostEnabled(bool);
bool RF455_LobbyPostEnabled();
RF455LobbyPostTelemetry RF455_GetLobbyPostTelemetry();

// Internal producer contract, not a user quality setting. Default false:
// legacy material outputs are display-referred; first post pass decodes RGB.
// Only set true when ALL scene producers supply linear RGB. Alpha, data maps
// and legacy texture sampler sRGB states are never globally reinterpreted.
bool RF455_SetLobbyPostInputLinear(bool);
