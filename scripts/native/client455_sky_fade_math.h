#pragma once
#include <windows.h>

// Pinned455:8B5900/8B5780/8B49B0. Keep the x87 operation order and the
// explicit float stores. Modern SSE float intermediates round too early.
// These helpers inherit the caller's precision/rounding control; integer
// conversion temporarily selects truncation and restores the control word.
static __forceinline float RF455_FadeSubtract(float total,float elapsed) {
    float result;
    __asm { fld total
            fsub elapsed
            fstp result }
    return result;
}
static __forceinline float RF455_FadeTick(float now,float start,float duration) {
    const double epsilon=double(0.0001f);float result;
    __asm { fld now
            fsub start
            fadd epsilon
            fdiv duration
            fstp result }
    return result;
}
static __forceinline float RF455_FadeComplement(float tick) {
    float result;
    __asm { fld1
            fsub tick
            fstp result }
    return result;
}
static __forceinline float RF455_FadeFog(float source,float destination,float alpha) {
    float result;
    __asm { fld destination
            fsub source
            fmul alpha
            fadd source
            fstp result }
    return result;
}
static __forceinline DWORD RF455_FadeChannel(int source,int destination,float alpha) {
    __int64 result;unsigned short saved,truncation;
    __asm { fild destination
            fisub source
            fmul alpha
            fiadd source
            fnstcw saved }
    truncation=saved|0x0c00;
    __asm { fldcw truncation
            fistp result
            fldcw saved }
    return DWORD(result);
}
static __forceinline DWORD RF455_FadeColor(DWORD source,DWORD destination,float alpha) {
    const DWORD r=RF455_FadeChannel((source>>16)&255,(destination>>16)&255,alpha);
    const DWORD g=RF455_FadeChannel((source>>8)&255,(destination>>8)&255,alpha);
    const DWORD b=RF455_FadeChannel(source&255,destination&255,alpha);
    return 0xff000000u|(r<<16)|(g<<8)|b;
}
static __forceinline DWORD RF455_FadeAlphaByte(float alpha) {
    const double maximum=255.0;__int64 result;unsigned short saved,truncation;
    __asm { fld alpha
            fmul maximum
            fnstcw saved }
    truncation=saved|0x0c00;
    __asm { fldcw truncation
            fistp result
            fldcw saved }
    return DWORD(result);
}
