#include "client455_loop_clock.h"
#include <cstddef>
#include <cstring>
static_assert(sizeof(RF455LoopClock)==96 && offsetof(RF455LoopClock,frequency)==56,"Owned loop state wire layout");

extern "C" std::uint64_t RF455_GetLoopTicks(RF455QueryPerformance counter,RF455MillisecondTimer timer){
    LARGE_INTEGER ticks;
    if(counter(&ticks)){
        while(!ticks.QuadPart)counter(&ticks);
        return static_cast<std::uint64_t>(ticks.QuadPart);
    }
    return timer();
}

static float unsignedAverage(std::uint32_t milliseconds,std::uint32_t count){
    float result;const float bias=4294967296.0f;const double thousand=1000.0;
    __asm {
        mov eax,milliseconds
        fild milliseconds
        test eax,eax
        jge positive_sum
        fadd bias
    positive_sum:
        mov eax,count
        fild count
        test eax,eax
        jge positive_count
        fadd bias
    positive_count:
        fdivp st(1),st
        fdiv thousand
        fstp result
    }
    return result;
}
static float multiply(float a,float b){float result;__asm {fld a
    fmul b
    fstp result}return result;}
static float add(float a,float b){float result;__asm {fld a
    fadd b
    fstp result}return result;}
static float subtract(float a,double b){float result;__asm {fld a
    fsub b
    fstp result}return result;}
static unsigned short compare(float a,float b){unsigned short status;__asm {fld a
    fcomp b
    fnstsw status}return status;}
static bool less(float a,float b){return (compare(a,b)&0x4500)==0x0100;}
static bool atLeast(float a,float b){return (compare(a,b)&0x0100)==0;}

extern "C" void RF455_UpdateLoopClock(RF455LoopClock* s,RF455QueryPerformance frequency,RF455QueryPerformance counter,RF455MillisecondTimer timer){
    if(!s->initialized){
        s->initialized=1;LARGE_INTEGER value;
        if(!frequency(&value))value.QuadPart=1000;
        s->frequency=static_cast<std::uint64_t>(value.QuadPart);
        float converted;__asm {fild qword ptr value
            fstp converted}
        s->frequencyFloat=converted;s->initialSecondsPerFrame=.001f;
        s->ticksPerFrame=s->frequency/1000;
        s->startTicks=s->ticks=RF455_GetLoopTicks(counter,timer);
    }
    const DWORD now=timer();++s->loopCount;
    s->loopMilliseconds+=now-s->oldTick;
    if(s->loopMilliseconds>10){
        s->loopSeconds=unsignedAverage(s->loopMilliseconds,s->loopCount);
        s->loopCount=0;s->loopMilliseconds=0;
    }
    s->oldTick=now;
    if(less(s->maximumSeconds,s->loopSeconds) || less(s->loopSeconds,0))s->loopSeconds=s->maximumSeconds;
    // The stored, scaled value is reused until the averaging window closes.
    s->loopSeconds=multiply(s->loopSeconds,s->timeScale);
    s->realSeconds=add(s->realSeconds,s->loopSeconds);
    const float thresholds[]={0.03333333507180214f,0.06666667014360428f,0.1428571492433548f};
    for(unsigned i=0;i<3;++i){
        s->toggleSeconds[i]=add(s->loopSeconds,s->toggleSeconds[i]);
        if(atLeast(s->toggleSeconds[i],thresholds[i])){
            // Use unsigned negation to retain x86 NEG at INT_MIN without C++ UB.
            const std::uint32_t negative=0u-static_cast<std::uint32_t>(s->toggles[i]);
            std::memcpy(&s->toggles[i],&negative,4);
            s->toggleSeconds[i]=subtract(s->toggleSeconds[i],static_cast<double>(thresholds[i]));
            if(atLeast(s->toggleSeconds[i],thresholds[i]))s->toggleSeconds[i]=0;
        }
    }
}
extern "C" float RF455_GetLoopDuration(const RF455LoopClock* state,RF455QueryPerformance counter,RF455MillisecondTimer timer){
    const std::uint64_t delta=RF455_GetLoopTicks(counter,timer)-state->startTicks;
    const std::uint64_t frequency=state->frequency;float result;
    // FILD interprets the wrapped QWORD as signed, then one final float spill.
    __asm {fild delta
        fild frequency
        fdivp st(1),st
        fstp result}
    return result;
}
