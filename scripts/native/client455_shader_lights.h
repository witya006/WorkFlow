#pragma once
#include <cstdio>
class RF455ResourceText;

struct RF455ShaderLight {
    float scale=1.f,radius=10.f;
    float position[3]={0,0,0};
    float color[3]={255,255,255};
};
static_assert(sizeof(RF455ShaderLight)==32,"455 shader light record");

template<class Device>
void RF455_SetShaderLightConstants(Device* device, const RF455ShaderLight& light)
{
    // The fourth pixel lane is outside the original 32-byte light record.
    const float color[4] = {light.color[0], light.color[1], light.color[2], 0.f};
    const float position[4] = {light.position[0], light.position[1], light.position[2], light.color[0]};
    device->SetPixelShaderConstantF(6, color, 1);
    device->SetVertexShaderConstantF(18, position, 1);
}

RF455ShaderLight* RF455_ReadShaderLight(FILE*);
RF455ShaderLight* RF455_ReadShaderLight(RF455ResourceText&);
// On success the registry takes ownership; on failure the caller retains it.
int RF455_AppendShaderLight(RF455ShaderLight*);
RF455ShaderLight* RF455_GetShaderLight(int);
int RF455_GetShaderLightCount();
void RF455_ClearShaderLights();
void RF455_UpdateParticleShaderLight(int,const float* position);
