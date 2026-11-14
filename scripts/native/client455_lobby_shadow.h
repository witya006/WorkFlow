#pragma once
#include <d3d9.h>
#include <cstdint>
class CBsp;
struct RF455LobbyShadowTelemetry {
    bool ready, active;
    unsigned resolution, bspDraws, actorDraws;
    std::uint64_t frames, errors, bytes;
    HRESULT error;
    char stage[96];
    std::uint64_t lightMatrixChanges, fitExpansions, sceneGeneration;
    float worldUnitsPerTexelX, worldUnitsPerTexelY, lightMatrixMaxDelta;
    unsigned actorPoseAgeMsMax, actorPoseAgeFramesMax, pendingActors;
    std::uint64_t actorCaptureFrames, actorCaptureFailures, actorCaptureStateChecks;
    bool actorCaptureComplete;
};
// Entire BSP, not the camera's visible-leaf cache. Called inside the scene.
void RF455_RenderLobbyShadows(CBsp*);
bool RF455_BeginLobbyShadows(IDirect3DDevice9*,const float* minimum,const float* maximum);
void RF455_EndLobbyShadows(IDirect3DDevice9*);
void RF455_InvalidateLobbyShadows(bool discardActors);
// A fresh CPU-only geometry capture is mandatory before the shadow pass.
bool RF455_BeginLobbyActorCapture(IDirect3DDevice9*);
bool RF455_EndLobbyActorCapture(bool success);
bool RF455_QueueLobbyActorShadow(IDirect3DVertexBuffer9*,IDirect3DIndexBuffer9*,IDirect3DVertexDeclaration9*,
    unsigned start,unsigned vertices,unsigned firstIndex,unsigned triangles,bool indexed,const float* palette480);
// Geometry identity resets the stable envelope only on a new loaded scene.
void RF455_SetLobbyShadowScene(const void* owner,const void* vertices,unsigned vertexCount);
bool RF455_LobbyShadowPass();
void RF455_DrawLobbyShadowGroup(IDirect3DDevice9*,unsigned minimum,unsigned vertices,unsigned start,unsigned triangles);
void RF455_RecordLobbyActorShadow(IDirect3DDevice9*,unsigned mode,unsigned start,unsigned vertices,unsigned firstIndex,unsigned triangles,bool indexed);
// Borrowed texture; identity/disabled parameters on failure. Receiver sampler
// uses POINT depth comparisons, never hardware interpolation of depth values.
IDirect3DTexture9* RF455_LobbyShadowTexture(float* matrix16,float* parameters4);
RF455LobbyShadowTelemetry RF455_GetLobbyShadowTelemetry();
void RF455_ReleaseLobbyShadows();
