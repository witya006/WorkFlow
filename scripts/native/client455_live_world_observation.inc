// Own-client samples after the accepted starting-position response.
#include <d3dx9.h>
#include "client455_multisampling.h"

LPDIRECT3DDEVICE9 GetD3dDevice();

struct RF455WorldCaptureResult {
    HRESULT result;
    UINT width;
    UINT height;
};

static RF455WorldCaptureResult RF455_SaveWorldFrame(const char* filename) {
    IDirect3DSurface9* target = nullptr;
    IDirect3DSurface9* memory = nullptr;
    D3DSURFACE_DESC desc = {};
    auto* device = GetD3dDevice();
    HRESULT result = device ? device->GetRenderTarget(0, &target) : E_FAIL;
    if (SUCCEEDED(result)) result = target->GetDesc(&desc);
    if (SUCCEEDED(result)) {
        result = device->CreateOffscreenPlainSurface(desc.Width, desc.Height, desc.Format,
                                                     D3DPOOL_SYSTEMMEM, &memory, nullptr);
    }
    if (SUCCEEDED(result)) result = RF455_ReadRenderTarget(*device, *target, *memory);
    if (SUCCEEDED(result)) {
        result = D3DXSaveSurfaceToFileA(filename, D3DXIFF_PNG, memory, nullptr, nullptr);
    }
    if (memory) memory->Release();
    if (target) target->Release();
    return {result, desc.Width, desc.Height};
}

static void RF455_SampleMonsterFrame(RF455WorldObservation& state, ULONGLONG elapsed) {
    const auto draw = state.monsterDraw;
    state.monsterDraw = {};
    if (!draw.present || elapsed < 1200 || elapsed < state.nextMonsterCaptureAt) return;

    const unsigned index = state.monsterCaptures++;
    state.sampledMonster = draw.serial;
    state.nextMonsterCaptureAt = elapsed + 150;
    char filename[40];
    std::snprintf(filename, sizeof(filename), "world-monster-%u.png", index);
    const auto capture = RF455_SaveWorldFrame(filename);
    char message[180];
    std::snprintf(message, sizeof(message), "RF455 MonsterFrame:%u:%llu:%u:%u:%u:%u:%ld:%ux%u:%.6g:%.6g",
                  index, elapsed, draw.serial, draw.mesh, draw.animation, draw.boneFrame,
                  capture.result, capture.width, capture.height, draw.screenX, draw.screenY);
    OutputDebugStringA(message);
}

static void RF455_ObserveWorldFrame(const float* avatar, const float* camera,
                                    float yaw, float pitch, float distance,
                                    unsigned action, BOOL inputEnabled) {
    auto& state = RF455_WorldObservation();
    const unsigned sample = (state.walk ? 6 : 3) - state.remaining;
    constexpr ULONGLONG delays[] = {0, 1000, 3000, 4500, 6500, 8500};
    constexpr ULONGLONG cameraDelays[] = {0, 1800, 3400};
    constexpr ULONGLONG longWalkDelays[] = {0, 1000, 3000, 6500, 14000, 17000};
    const auto elapsed = GetTickCount64() - state.acceptedAt;
    const bool longWalk = state.walkDurationMs > 1000;
    if (longWalk && !state.zeroPositionReported && avatar[0] == 0.f && avatar[2] == 0.f) {
        state.zeroPositionReported = true;
        RF455_ObserveProtocol("movement-zero-position", static_cast<unsigned>(elapsed), action, inputEnabled);
    }
    if (state.captureMonsters) RF455_SampleMonsterFrame(state, elapsed);
    if (state.combatImpactPending) {
        state.combatImpactPending = false;
        const unsigned index = state.combatImpactFrames++;
        char filename[40];
        std::snprintf(filename, sizeof(filename), "world-impact-%u.png", index);
        const auto capture = RF455_SaveWorldFrame(filename);
        RF455_ObserveProtocol("combat-impact-frame", index, state.combatImpactDamage,
                             static_cast<unsigned>(capture.result));
    }
    const auto delay = state.combat && sample == 5 ? 36000 + state.combatApproachMs
                     : state.camera ? cameraDelays[sample]
                     : longWalk ? longWalkDelays[sample] : delays[sample];
    if (elapsed < delay) return;
    --state.remaining;

    char message[384];
    std::snprintf(message, sizeof(message),
                  "RF455 WorldSample:%u:%llu:%u:%d:%.6g,%.6g,%.6g:%.6g,%.6g,%.6g:%.6g,%.6g,%.6g",
                  sample, elapsed, action, inputEnabled != FALSE,
                  avatar[0], avatar[1], avatar[2], camera[0], camera[1], camera[2],
                  yaw, pitch, distance);
    OutputDebugStringA(message);

    if (sample != 0 && sample != 2) return;
    const char* filename = sample == 0 ? "world-post-position.png" : "world-post-position-settled.png";
    const auto capture = RF455_SaveWorldFrame(filename);
    std::snprintf(message, sizeof(message), "RF455 WorldCapture:%u:%ld:%ux%u",
                  sample, capture.result, capture.width, capture.height);
    OutputDebugStringA(message);
}
