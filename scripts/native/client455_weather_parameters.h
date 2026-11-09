#pragma once
#include <windows.h>
#include <stdio.h>

// Source-owned counterpart of4551157D3C. BSS initial0;InitCore does not reset it.
extern DWORD RF455_MaterialWeather;
DWORD RF455_GetMaterialWeather();
void RF455_ReadWeatherParameters(FILE*,char* mutableToken);
