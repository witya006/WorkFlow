// Win32 x87 compatibility math. Instruction order and spills match pinned 455.
// Algebra/layout: affine 4x4 cofactor inverse and row-vector xyz transform.
// Keep the caller's x87 control word; precision and rounding are part of the ABI.
#include "client455_x87_math.h"
extern "C" const float RF455_AffineEpsilon=0.001f;

extern "C" __declspec(naked) int __cdecl RF455_MatrixInvert(float (*)[4],float (*)[4]) {
    __asm {
        mov ecx, [esp+8]
        fld dword ptr [ecx+3Ch]
        fld1
        fsub st(1), st
        fxch st(1)
        fstp dword ptr [esp+8]
        fld dword ptr [esp+8]
        fabs
        fstp dword ptr [esp+8]
        fld dword ptr [esp+8]
        fld RF455_AffineEpsilon
        fcom st(1)
        fnstsw ax
        fstp st(1)
        test ah, 5
        jnp fail_pop_two
        fld dword ptr [ecx+0Ch]
        fabs
        fstp dword ptr [esp+8]
        fld dword ptr [esp+8]
        fcomp st(1)
        fnstsw ax
        test ah, 41h
        jz fail_pop_two
        fld dword ptr [ecx+1Ch]
        fabs
        fstp dword ptr [esp+8]
        fld dword ptr [esp+8]
        fcomp st(1)
        fnstsw ax
        test ah, 41h
        jz fail_pop_two
        fld dword ptr [ecx+2Ch]
        fabs
        fstp dword ptr [esp+8]
        fcomp [esp+8]
        fnstsw ax
        test ah, 5
        jnp fail_pop_one
        fld dword ptr [ecx+28h]
        mov eax, [esp+4]
        fmul dword ptr [ecx+14h]
        fld dword ptr [ecx+24h]
        fmul dword ptr [ecx+18h]
        fsubp st(1), st
        fld dword ptr [ecx]
        fmul st, st(1)
        fld dword ptr [ecx+28h]
        fmul dword ptr [ecx+10h]
        fld dword ptr [ecx+20h]
        fmul dword ptr [ecx+18h]
        fsubp st(1), st
        fmul dword ptr [ecx+4]
        fsubp st(1), st
        fld dword ptr [ecx+10h]
        fmul dword ptr [ecx+24h]
        fld dword ptr [ecx+14h]
        fmul dword ptr [ecx+20h]
        fsubp st(1), st
        fmul dword ptr [ecx+8]
        faddp st(1), st
        fdivp st(2), st
        fxch st(1)
        fstp dword ptr [esp+8]
        fld dword ptr [esp+8]
        fld st
        fmulp st(2), st
        fxch st(1)
        fstp dword ptr [eax]
        fld st
        fchs
        fstp dword ptr [esp+8]
        fld dword ptr [ecx+28h]
        fmul dword ptr [ecx+4]
        fld dword ptr [ecx+8]
        fmul dword ptr [ecx+24h]
        fsubp st(1), st
        fld dword ptr [esp+8]
        fld st
        fmulp st(2), st
        fxch st(1)
        fstp dword ptr [eax+4]
        fld dword ptr [ecx+4]
        fmul dword ptr [ecx+18h]
        fld dword ptr [ecx+14h]
        fmul dword ptr [ecx+8]
        fsubp st(1), st
        fmul st, st(2)
        fstp dword ptr [eax+8]
        fldz
        fst dword ptr [eax+0Ch]
        fld dword ptr [ecx+28h]
        fmul dword ptr [ecx+10h]
        fld dword ptr [ecx+20h]
        fmul dword ptr [ecx+18h]
        fsubp st(1), st
        fmul st, st(2)
        fstp dword ptr [eax+10h]
        fld dword ptr [ecx+28h]
        fmul dword ptr [ecx]
        fld dword ptr [ecx+8]
        fmul dword ptr [ecx+20h]
        fsubp st(1), st
        fmul st, st(3)
        fstp dword ptr [eax+14h]
        fld dword ptr [ecx]
        fmul dword ptr [ecx+18h]
        fld dword ptr [ecx+10h]
        fmul dword ptr [ecx+8]
        fsubp st(1), st
        fmul st, st(2)
        fstp dword ptr [eax+18h]
        fst dword ptr [eax+1Ch]
        fld dword ptr [ecx+10h]
        fmul dword ptr [ecx+24h]
        fld dword ptr [ecx+14h]
        fmul dword ptr [ecx+20h]
        fsubp st(1), st
        fmul st, st(3)
        fstp dword ptr [eax+20h]
        fld dword ptr [ecx]
        fmul dword ptr [ecx+24h]
        fld dword ptr [ecx+4]
        fmul dword ptr [ecx+20h]
        fsubp st(1), st
        fmulp st(2), st
        fxch st(1)
        fstp dword ptr [eax+24h]
        fld dword ptr [ecx+14h]
        fmul dword ptr [ecx]
        fld dword ptr [ecx+10h]
        fmul dword ptr [ecx+4]
        fsubp st(1), st
        fmulp st(2), st
        fxch st(1)
        fstp dword ptr [eax+28h]
        fstp dword ptr [eax+2Ch]
        fld dword ptr [ecx+30h]
        fmul dword ptr [eax]
        fld dword ptr [ecx+34h]
        fmul dword ptr [eax+10h]
        faddp st(1), st
        fld dword ptr [eax+20h]
        fmul dword ptr [ecx+38h]
        faddp st(1), st
        fchs
        fstp dword ptr [eax+30h]
        fld dword ptr [ecx+34h]
        fmul dword ptr [eax+14h]
        fld dword ptr [eax+4]
        fmul dword ptr [ecx+30h]
        faddp st(1), st
        fld dword ptr [eax+24h]
        fmul dword ptr [ecx+38h]
        faddp st(1), st
        fchs
        fstp dword ptr [eax+34h]
        fld dword ptr [ecx+34h]
        fmul dword ptr [eax+18h]
        fld dword ptr [eax+8]
        fmul dword ptr [ecx+30h]
        faddp st(1), st
        fld dword ptr [eax+28h]
        fmul dword ptr [ecx+38h]
        faddp st(1), st
        fchs
        fstp dword ptr [eax+38h]
        fld1
        fstp dword ptr [eax+3Ch]
        mov eax, 1
        retn
fail_pop_two:
        fstp st
fail_pop_one:
        fstp st
        xor eax, eax
        retn
    }
}

extern "C" __declspec(naked) void __cdecl RF455_Vector3fTransform(float*,float*,float (*)[4]) {
    __asm {
        sub esp, 0Ch
        mov eax, [esp+20]
        fld dword ptr [eax]
        mov ecx, [esp+16]
        fstp dword ptr [esp]
        fld dword ptr [eax+4]
        fstp dword ptr [esp+4]
        fld dword ptr [eax+8]
        mov eax, [esp+24]
        fstp dword ptr [esp+8]
        fld dword ptr [eax+10h]
        fld dword ptr [esp+4]
        fld st
        fmulp st(2), st
        fld dword ptr [eax]
        fld dword ptr [esp]
        fld st
        fmulp st(2), st
        fxch st(3)
        faddp st(1), st
        fld dword ptr [eax+20h]
        fld dword ptr [esp+8]
        fld st
        fmulp st(2), st
        fxch st(2)
        faddp st(1), st
        fadd dword ptr [eax+30h]
        fstp dword ptr [ecx]
        fld dword ptr [eax+14h]
        fmul st, st(2)
        fld dword ptr [eax+4]
        fmul st, st(4)
        faddp st(1), st
        fld dword ptr [eax+24h]
        fmul st, st(2)
        faddp st(1), st
        fadd dword ptr [eax+34h]
        fstp dword ptr [ecx+4]
        fld dword ptr [eax+18h]
        fmulp st(2), st
        fld dword ptr [eax+8]
        fmulp st(3), st
        fxch st(1)
        faddp st(2), st
        fmul dword ptr [eax+28h]
        faddp st(1), st
        fadd dword ptr [eax+38h]
        fstp dword ptr [ecx+8]
        add esp, 0Ch
        retn
    }
}
