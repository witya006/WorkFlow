#pragma once
#include <d3d9.h>
#include <cstdint>

struct RF455LobbySkyTelemetry {
    bool ready;
    std::uint64_t draws, errors;
    HRESULT error;
    char stage[64], compilerError[384];
    std::uint64_t volumeTextureBytes; // Legacy field name; now orbital textures + mip levels.
};
// Inside BeginScene, before BSP. Returns true only when the replacement drew.
// The caller owns the enhanced-lobby-only gate; authored assets are manifest-pinned.
bool RF455_RenderLobbySky(IDirect3DDevice9*);
void RF455_ReleaseLobbySky();
RF455LobbySkyTelemetry RF455_GetLobbySkyTelemetry();
IDirect3DTexture9* RF455_LobbyEnvironmentTexture(); // borrowed, managed celestial panorama
// Optional real camera override if the sky hook has already changed D3D
// transforms. Pass both null to resume reading the actual device transforms.
void RF455_SetLobbySkyCamera(const D3DMATRIX* view, const D3DMATRIX* projection);
