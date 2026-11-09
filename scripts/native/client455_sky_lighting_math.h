#pragma once
#include "client455_sky_fade_math.h"

// Selected455 lighting arithmetic. These source components are not connected
// to the ordinary frame until the complete fog/profile ownership is restored.
// Inherit x87 precision/rounding; integer conversions restore the control word.
static __forceinline DWORD RF455_SkyTintColor(const float* rgb,DWORD previousFog) {
    const DWORD r=RF455_FadeAlphaByte(rgb[0]);
    const DWORD g=RF455_FadeAlphaByte(rgb[1]);
    const DWORD b=RF455_FadeAlphaByte(rgb[2]);
    const DWORD red=((r>>2)+((previousFog>>18)&63)+128)|0xffffff00u;
    const DWORD green=(g&0xfffffffcu)+((previousFog>>8)&252)+512;
    const DWORD blue=(b>>2)+((previousFog>>2)&63)+128;
    return (red<<16)|(green<<6)|blue;
}

static __forceinline DWORD RF455_SunChannel(float color,float alpha) {
    const double maximum=255;__int64 result;unsigned short saved,truncation;
    __asm { fld color
            fmul alpha
            fmul maximum
            fnstcw saved }
    truncation=saved|0xc00;
    __asm { fldcw truncation
            fistp result
            fldcw saved }
    return DWORD(result);
}

static __forceinline DWORD RF455_SunDirectColor(const float* rgb,float alpha) {
    const DWORD r=RF455_SunChannel(rgb[0],alpha);
    const DWORD g=RF455_SunChannel(rgb[1],alpha);
    const DWORD b=RF455_SunChannel(rgb[2],alpha);
    return b|((g|((r|0xffffff00u)<<8))<<8);
}

static __forceinline float RF455_SkyWeightedFloat(float day,float night,float weight) {
    float result;
    // Keep 1-weight on the x87 stack: storing it as float changes results.
    __asm { fld weight
            fld1
            fsub weight
            fld night
            fmul st,st(2)
            fld day
            fmul st,st(2)
            faddp st(1),st
            fstp result
            fstp st
            fstp st }
    return result;
}

static __forceinline DWORD RF455_SkyWeightedChannel(int day,int night,float weight) {
    __int64 result;unsigned short saved,truncation;
    __asm { fld weight
            fld1
            fsub weight
            fild night
            fmul st,st(2)
            fild day
            fmul st,st(2)
            faddp st(1),st
            fnstcw saved }
    truncation=saved|0xc00;
    __asm { fldcw truncation
            fistp result
            fldcw saved
            fstp st
            fstp st }
    return DWORD(result);
}

static __forceinline DWORD RF455_SkyFogColor(DWORD day,DWORD night,float weight) {
    const DWORD r=RF455_SkyWeightedChannel((day>>16)&255,(night>>16)&255,weight);
    const DWORD g=RF455_SkyWeightedChannel((day>>8)&255,(night>>8)&255,weight);
    const DWORD b=RF455_SkyWeightedChannel(day&255,night&255,weight);
    return b|((g|((r|0xffffff00u)<<8))<<8);
}

static __forceinline DWORD RF455_ModulateSkyTint(DWORD base,DWORD tint) {
    return (base&0xff000000u)
        |(((base&255)*(tint&255))>>8)
        |((((base>>8)&255)*((tint>>8)&255))&0xffffff00u)
        |(((((base>>16)&255)*((tint>>16)&255))&0xffffff00u)<<8);
}

static __forceinline DWORD RF455_SkyFogDivisor(DWORD count,float exposure) {
    const double scale=.89999997615814208984375;
    const float unsignedCorrection=4294967296.0f;
    const int signedCount=int(count);
    float factor;__int64 result;unsigned short saved,truncation;
    __asm { fld exposure
            fmul scale
            fadd scale
            fstp factor
            fild signedCount }
    if(count&0x80000000u) { __asm { fadd unsignedCorrection } }
    __asm { fmul factor
            fnstcw saved }
    truncation=saved|0xc00;
    __asm { fldcw truncation
            fistp result
            fldcw saved }
    // Original unsigned DIV has no zero-divisor fallback. Callers must retain
    // that behavior; this helper deliberately exposes zero for its boundary.
    return DWORD(result);
}
