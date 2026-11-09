#pragma once
#include <cstdio>
struct RF455ShaderLight {
    float scale=1.f,radius=10.f;
    float position[3]={0,0,0};
    float color[3]={255,255,255};
};
static_assert(sizeof(RF455ShaderLight)==32,"455 shader light record");
RF455ShaderLight* RF455_ReadShaderLight(FILE*);
int RF455_AppendShaderLight(RF455ShaderLight*);
RF455ShaderLight* RF455_GetShaderLight(int);
int RF455_GetShaderLightCount();
void RF455_ClearShaderLights();
void RF455_UpdateParticleShaderLight(int,const float* position);
