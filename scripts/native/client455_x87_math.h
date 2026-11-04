#pragma once
#if !defined(_M_IX86)
#error RF455 compatibility math requires Win32 x86
#endif
extern "C" int __cdecl RF455_MatrixInvert(float output[4][4],float input[4][4]);
extern "C" void __cdecl RF455_Vector3fTransform(float output[3],float position[3],float matrix[4][4]);
