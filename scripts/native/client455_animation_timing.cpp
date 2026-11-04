#include "client455_animation_timing.h"
#include <cstring>

extern "C" std::uint32_t RF455_AdvanceAnimationFrameValue(std::uint32_t current,std::uint32_t carried,float elapsedSeconds,float speed){
    const double milliseconds=1000.0,unitsPerMillisecond=5.0;
    const unsigned long long carried64=carried,current64=current;long long converted;
    double elapsedUnits;unsigned short previousControl,truncationControl;
    __asm{fld elapsedSeconds
        fmul milliseconds
        fmul unitsPerMillisecond
        fild carried64
        faddp st(1),st
        fstp elapsedUnits
        fld speed
        fmul elapsedUnits
        fild current64
        faddp st(1),st
        fnstcw previousControl
        mov ax,previousControl
        or ax,0c00h
        mov truncationControl,ax
        fldcw truncationControl
        fistp converted
        fldcw previousControl}
    return static_cast<std::uint32_t>(converted);
}
extern "C" void RF455_InitializeAnimationControl(void* storage){
    auto* b=static_cast<unsigned char*>(storage);std::memset(b,0,100);const unsigned invalid=0xffffffff,one=0x3f800000;
    std::memcpy(b+4,&invalid,4);std::memcpy(b+8,&one,4);for(unsigned i=0;i<10;++i)std::memcpy(b+16+4*i,&invalid,4);
}
extern "C" void RF455_InitializeSecondaryState(void* storage){
    // Known inline84byte region,not a claim about the full actor class size.
    const unsigned words[]={0x3f4ccccd,0,0x3ecccccd,0,0,1,1,1,1,1,0,0,0xbe4ccccd,0,0,0x3fa66666,0x3f666666,0x3f333333,0x3f800000,0x3f000000,0};
    std::memcpy(storage,words,84);
}
