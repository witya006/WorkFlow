#pragma once
#include "client455_draw.h"
#include <vector>
struct RF455NormalTransformApi {
    void* (__stdcall *rotationZ)(void*,float);
    RF455MeshMatrixOps matrix;
};
extern "C" {
//92FE80: optional second matrix has unit scale and the same translation.
void RF455_BuildNormalCharacterWorld(float* world,float* unscaled,const float* position,
    float yaw,float scale,const RF455NormalTransformApi*);
//934F00 differs from scene8C2C90 by the m32 dot spill before adding plane.w.
int RF455_IsNormalModelBoxVisible(const float*,const float*,const float (*)[4]);
//91CBB0; literal writes, not a state block or restoration of arbitrary state.
void RF455_UnsetNormalCharacterState(const RF455CharacterDrawState*);
// Own explicit shutdown adapter. Call only after destroying all CRender owners.
void RF455_ReleaseNormalCharacterSharedResources();
}

// D3DX sprite notifications for Reset on the same device. Managed Character
// resources stay resident, and each sprite retries only failed callbacks.
HRESULT RF455_InvalidateCharacterSprite455(IDirect3DDevice9*);
HRESULT RF455_RestoreCharacterSprite455(IDirect3DDevice9*);

struct RF455CharacterManager;
struct RF455EffectStore;
// Unload the scene before preparing remaining Character owners. Keep supplied
// model/effect storage and texture entries stable through restore or retry.
HRESULT RF455_PrepareCharacterDeviceReplacement455(IDirect3DDevice9*,
    const std::vector<RF455CharacterManager*>& extraModels, RF455EffectStore* rvpEffects);
HRESULT RF455_RestoreCharacterDeviceReplacement455(IDirect3DDevice9*);
