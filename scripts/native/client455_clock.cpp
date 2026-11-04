// x86 clock arithmetic reconstructed from the pinned455 engine. x87 operation
// order, spills, truncation and unsigned low-DWORD wrapping are observable.
// The scalar functions and the clock-only frame prefix are byte-compared to
// both reference PEs after verifying every absolute relocation and constant.
#include "client455_clock.h"

extern "C" {
float RF455_DayRate=3.0f,RF455_DayFraction=0,RF455_RealDayFraction=0;
DWORD RF455_DayBase=0,RF455_RealDayBase=0;
DWORD (WINAPI* RF455_ClockTickSource)()=&GetTickCount;
extern const double RF455_SecondsPerDay=86400.0,RF455_MillisecondsPerSecond=1000.0;
extern const float RF455_UInt32Bias=4294967296.0f;
}

extern "C" __declspec(naked) float RF455_GetDayRate() {
    __asm { fld RF455_DayRate
            ret }
}
extern "C" __declspec(naked) void RF455_SetDayRate(float) {
    __asm { fld dword ptr [esp+4]
            fstp RF455_DayRate
            ret }
}
extern "C" __declspec(naked) float RF455_GetDayFraction() {
    __asm { fld RF455_DayFraction
            ret }
}
extern "C" __declspec(naked) float RF455_GetRealDayFraction() {
    __asm { fld RF455_RealDayFraction
            ret }
}

// HMS setter: unsigned modulo24/60/60, float spill, day fraction, then elapsed
// whole seconds at the current rate. Preserve the caller's x87 control word.
extern "C" __declspec(naked) void RF455_SetDayTime(unsigned,unsigned,unsigned) {
    __asm {
        sub esp, 8
        mov ecx, [esp+0Ch]
        mov eax, 0AAAAAAABh
        mul ecx
        shr edx, 4
        imul edx, -18h
        add ecx, edx
        push esi
        mov esi, [esp+14h]
        mov eax, 88888889h
        mul esi
        shr edx, 5
        mov eax, edx
        shl eax, 4
        sub eax, edx
        neg eax
        lea esi, [esi+eax*4]
        push edi
        mov edi, [esp+1Ch]
        mov eax, 88888889h
        mul edi
        shr edx, 5
        mov eax, edx
        shl eax, 4
        sub eax, edx
        neg eax
        lea edx, [edi+eax*4]
        mov eax, ecx
        shl eax, 4
        sub eax, ecx
        lea eax, [esi+eax*4]
        mov ecx, eax
        shl ecx, 4
        sub ecx, eax
        lea edx, [edx+ecx*4]
        test edx, edx
        mov [esp+14h], edx
        fild dword ptr [esp+14h]
        jge hms_unsigned
        fadd RF455_UInt32Bias
    hms_unsigned:
        fstp dword ptr [esp+14h]
        fld dword ptr [esp+14h]
        fdiv RF455_SecondsPerDay
        fstp RF455_DayFraction
        call dword ptr [RF455_ClockTickSource]
        fld dword ptr [esp+14h]
        fdiv RF455_DayRate
        mov ecx, eax
        pop edi
        pop esi
        fnstcw word ptr [esp+0Ch]
        movzx eax, word ptr [esp+0Ch]
        or eax, 0C00h
        mov [esp+10h], eax
        fldcw word ptr [esp+10h]
        fistp qword ptr [esp]
        mov edx, [esp]
        fldcw word ptr [esp+0Ch]
        imul edx, 3E8h
        sub ecx, edx
        mov RF455_DayBase, ecx
        add esp, 8
        ret
    }
}

extern "C" __declspec(naked) void RF455_GetDayTime(unsigned*,unsigned*,unsigned*) {
    __asm {
        sub esp, 0Ch
        fld RF455_DayFraction
        push esi
        fmul RF455_SecondsPerDay
        push edi
        fnstcw word ptr [esp+0Ah]
        mov edi, 18h
        movzx eax, word ptr [esp+0Ah]
        or eax, 0C00h
        mov [esp+0Ch], eax
        mov eax, 91A2B3C5h
        fldcw word ptr [esp+0Ch]
        fistp qword ptr [esp+0Ch]
        mov esi, [esp+0Ch]
        mul esi
        fldcw word ptr [esp+0Ah]
        mov ecx, edx
        shr ecx, 0Bh
        mov eax, ecx
        imul ecx, 0E10h
        xor edx, edx
        div edi
        mov eax, [esp+18h]
        pop edi
        mov [eax], edx
        mov eax, esi
        sub eax, ecx
        mov ecx, 3Ch
        xor edx, edx
        div ecx
        mov ecx, [esp+18h]
        pop esi
        mov [ecx], eax
        mov eax, [esp+18h]
        mov [eax], edx
        add esp, 0Ch
        ret
    }
}

extern "C" __declspec(naked) void RF455_SetDayFraction(float) {
    __asm {
        sub esp, 8
        fld dword ptr [esp+0Ch]
        fstp RF455_DayFraction
        call dword ptr [RF455_ClockTickSource]
        fld dword ptr [esp+0Ch]
        mov ecx, eax
        fmul RF455_SecondsPerDay
        fnstcw word ptr [esp+0Ch]
        fdiv RF455_DayRate
        movzx eax, word ptr [esp+0Ch]
        or eax, 0C00h
        mov [esp], eax
        fldcw word ptr [esp]
        fistp qword ptr [esp]
        mov edx, [esp]
        fldcw word ptr [esp+0Ch]
        imul edx, 3E8h
        sub ecx, edx
        mov RF455_DayBase, ecx
        add esp, 8
        ret
    }
}

extern "C" __declspec(naked) void RF455_SetRealDayFraction(float) {
    __asm {
        sub esp, 8
        fld dword ptr [esp+0Ch]
        fstp RF455_RealDayFraction
        call dword ptr [RF455_ClockTickSource]
        fld dword ptr [esp+0Ch]
        mov ecx, eax
        fmul RF455_SecondsPerDay
        fnstcw word ptr [esp+0Ch]
        movzx eax, word ptr [esp+0Ch]
        or eax, 0C00h
        mov [esp], eax
        fldcw word ptr [esp]
        fistp qword ptr [esp]
        mov edx, [esp]
        fldcw word ptr [esp+0Ch]
        imul edx, 3E8h
        sub ecx, edx
        mov RF455_RealDayBase, ecx
        add esp, 8
        ret
    }
}

// The first256bytes of455's frame/lighting routine update both clocks. Retain
// that complete prefix; return before the separate lighting/material subsystem.
// This also retains the reference's unwrapped real-time fraction and low32bits
// of truncated game seconds. No improved modulo or counter rollover is added.
extern "C" __declspec(naked) void RF455_AdvanceDayClock() {
    __asm {
        push ebp
        mov ebp, esp
        and esp, -8
        sub esp, 30h
        push ebx
        push ebp
        push esi
        mov esi, RF455_ClockTickSource
        push edi
        call esi
        sub eax, RF455_DayBase
        test eax, eax
        mov [esp+20h], eax
        fild dword ptr [esp+20h]
        jge elapsed_unsigned
        fadd RF455_UInt32Bias
    elapsed_unsigned:
        fdiv RF455_MillisecondsPerSecond
        fmul RF455_DayRate
        fnstcw word ptr [esp+10h]
        fld st
        movzx eax, word ptr [esp+10h]
        or eax, 0C00h
        mov [esp+20h], eax
        mov eax, 0C22E4507h
        fldcw word ptr [esp+20h]
        fistp qword ptr [esp+20h]
        mov ecx, [esp+20h]
        fldcw word ptr [esp+10h]
        mul ecx
        shr edx, 10h
        imul edx, 15180h
        mov eax, ecx
        sub eax, edx
        test eax, eax
        mov [esp+20h], eax
        fild dword ptr [esp+20h]
        jge wrapped_unsigned
        fadd RF455_UInt32Bias
    wrapped_unsigned:
        test ecx, ecx
        mov [esp+20h], ecx
        fild dword ptr [esp+20h]
        jge whole_unsigned
        fadd RF455_UInt32Bias
    whole_unsigned:
        fsubp st(2), st
        fxch st(1)
        fstp dword ptr [esp+20h]
        fadd dword ptr [esp+20h]
        fstp dword ptr [esp+20h]
        fld dword ptr [esp+20h]
        fdiv RF455_SecondsPerDay
        fstp RF455_DayFraction
        call esi
        sub eax, RF455_RealDayBase
        test eax, eax
        mov [esp+20h], eax
        fild dword ptr [esp+20h]
        jge real_unsigned
        fadd RF455_UInt32Bias
    real_unsigned:
        fdiv RF455_MillisecondsPerSecond
        fstp dword ptr [esp+20h]
        fld dword ptr [esp+20h]
        fdiv RF455_SecondsPerDay
        fstp RF455_RealDayFraction
        fld1
        fcomp RF455_DayFraction
        fnstsw ax
        test ah, 5
        jp clock_done
        fldz
        fstp RF455_DayFraction
    clock_done:
        pop edi
        pop esi
        pop ebp
        pop ebx
        mov esp, ebp
        pop ebp
        ret
    }
}
