#include "client455_light_direction.h"
#include "client455_x87_math.h"

// 41DB90 -> CRT sqrt: for finite nonnegative inputs the CRT keeps the caller's
// precision, masks exceptions and uses nearest rounding during FSQRT. The
// wrapper stores binary32 AFTER restoring the caller's rounding mode.
// CRT matherr/errno/unmasked exception callbacks remain a separate open contract.
extern "C" __declspec(naked) float __cdecl RF455_LightSqrt(float){
    __asm {
        sub esp,8
        fnstcw word ptr [esp]
        mov ax,word ptr [esp]
        and ax,0300h
        or ax,007fh
        mov word ptr [esp+2],ax
        fld dword ptr [esp+12]
        fldcw word ptr [esp+2]
        fsqrt
        fldcw word ptr [esp]
        fstp dword ptr [esp+4]
        fld dword ptr [esp+4]
        add esp,8
        ret
    }
}

// 51D5D0: instruction-identical body except the relocated sqrt-wrapper CALL.
// Preserve the original x*x+y*y order and the double spill of the float result.
extern "C" __declspec(naked) float* __cdecl RF455_NormalizeLightVector(float*){
    __asm {
        push ebp
        mov ebp,esp
        sub esp,4ch
        push ebx
        push esi
        push edi
        mov eax,[ebp+8]
        fld dword ptr [eax]
        mov ecx,[ebp+8]
        fmul dword ptr [ecx]
        mov edx,[ebp+8]
        fld dword ptr [edx+4]
        mov eax,[ebp+8]
        fmul dword ptr [eax+4]
        faddp st(1),st
        mov ecx,[ebp+8]
        fld dword ptr [ecx+8]
        mov edx,[ebp+8]
        fmul dword ptr [edx+8]
        faddp st(1),st
        fstp dword ptr [ebp-4ch]
        fld dword ptr [ebp-4ch]
        push ecx
        fstp dword ptr [esp]
        call RF455_LightSqrt
        add esp,4
        fstp qword ptr [ebp-8]
        fld qword ptr [ebp-8]
        fstp dword ptr [ebp-4ch]
        fld dword ptr [ebp-4ch]
        mov eax,[ebp+8]
        fdivr dword ptr [eax]
        mov ecx,[ebp+8]
        fstp dword ptr [ecx]
        fld qword ptr [ebp-8]
        fstp dword ptr [ebp-4ch]
        fld dword ptr [ebp-4ch]
        mov eax,[ebp+8]
        fdivr dword ptr [eax+4]
        mov ecx,[ebp+8]
        fstp dword ptr [ecx+4]
        fld qword ptr [ebp-8]
        fstp dword ptr [ebp-4ch]
        fld dword ptr [ebp-4ch]
        mov eax,[ebp+8]
        fdivr dword ptr [eax+8]
        mov ecx,[ebp+8]
        fstp dword ptr [ecx+8]
        pop edi
        pop esi
        pop ebx
        mov esp,ebp
        pop ebp
        ret
    }
}

extern "C" void __cdecl RF455_BuildLightDirection(float* output,float world[4][4],float* light){
    float inverse[4][4];
    // The original ignores the inverse return value; do not add a fallback.
    RF455_MatrixInvert(inverse,world);
    inverse[3][0]=inverse[3][1]=inverse[3][2]=0;
    RF455_Vector3fTransform(output,light,inverse);
    RF455_NormalizeLightVector(output);
}
