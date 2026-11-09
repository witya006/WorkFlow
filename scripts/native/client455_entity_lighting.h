#pragma once
#include <d3d9.h>
void RF455_SetLightingCaps(const D3DCAPS9*);
BOOL RF455_HasBumpEnvironment();
void RF455_SetLitGrass(float,float*,float,DWORD,const float*);
