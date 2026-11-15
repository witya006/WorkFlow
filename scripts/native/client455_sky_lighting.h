#pragma once
#include <windows.h>
#include <stdio.h>
struct RF455_ExtMaterial;
class RF455ResourceText;
struct RF455SkyFogEndpoint {float start,end;DWORD color;};
const RF455SkyFogEndpoint& RF455_GetSkyDayFog();
const RF455SkyFogEndpoint& RF455_GetSkyNightFog();
void RF455_ResetSkyFogEndpoints();
void RF455_LoadSkyFogEndpoints(const RF455_ExtMaterial&);
void RF455_ReadSkyFogToken(FILE*,char* mutableToken);
bool RF455_ReadSkyFogToken(RF455ResourceText&,char (&mutableToken)[256]);
void RF455_UpdateSkyLighting();
DWORD RF455_GetSkyTintColor();
DWORD RF455_GetSkyDirectColor();
DWORD RF455_ApplySkyTint(DWORD);
void RF455_GetSkySunPosition(float* xyz);
void RF455_GetSkySunColor(float* rgba);
void RF455_GetSkyScatterParameters(float* values17);
void RF455_SetSkyFogExposure(float);
float RF455_GetSkyFogExposure();
void RF455_SetSkyFogExposureColor(DWORD);
DWORD RF455_SampleSkyColor(const float* xyz);
unsigned RF455_GetSkyFogSampleCount();
unsigned RF455_GetSkyFogSampleDivisor();
