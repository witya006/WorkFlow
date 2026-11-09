#pragma once
#include <d3d9.h>
struct RF455SunValues {float theta,phi,orbit,scale,alpha,intensity;};
const RF455SunValues& RF455_GetSunValues();
void RF455_UpdateSunValues();
void RF455_CreateSkyResources();
void RF455_ReleaseSkyResources();
void RF455_DrawSkyAtmosphere();
// Read-only resource views for actual device/lifetime verification.
IDirect3DVertexBuffer9* RF455_GetSkyDomeVertices();
IDirect3DIndexBuffer9* RF455_GetSkyDomeIndices();
IDirect3DVertexShader9* RF455_GetSkyDomeShader();
IDirect3DTexture9* RF455_GetSunTexture();
void RF455_SetVPIPTex1KeepingShader(void*,void*,IDirect3DVertexDeclaration9*);
