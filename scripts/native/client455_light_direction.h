#pragma once
#if !defined(_M_IX86)
#error RF455 light direction requires Win32 x86
#endif
extern "C" float* __cdecl RF455_NormalizeLightVector(float* vector);
extern "C" void __cdecl RF455_BuildLightDirection(float* output,float world[4][4],float* light);
