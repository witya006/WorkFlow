#include "client455_clock.h"
#include <stdio.h>
#include <string.h>

static unsigned checks,failures,firstFailure,calls;
static DWORD tick,tickStep;
static DWORD WINAPI testTick() { return tick+tickStep*calls++; }
static void check(bool value) { ++checks;if (!value) { ++failures;if (!firstFailure) firstFailure=checks; } }
static unsigned short control() { unsigned short result;__asm { fnstcw result } return result; }
static unsigned short top() { unsigned short result;__asm { fnstsw result } return result&0x3800; }
static void setControl(unsigned short value) { __asm fldcw value }
static unsigned bits(float f) { unsigned value;memcpy(&value,&f,4);return value; }
static float fromBits(unsigned value) { float f;memcpy(&f,&value,4);return f; }
static void unchanged(unsigned short cw,unsigned short st) { check(control()==cw);check(top()==st); }

static int runClockChecks(FILE* output) {
    const unsigned short original=control();
    check(RF455_ClockTickSource==&GetTickCount);
    check(RF455_GetDayRate()==3.0f);
    check(RF455_DayBase==0 && RF455_RealDayBase==0);
    RF455_ClockTickSource=&testTick;
    unsigned modes=0;
    for (unsigned precision=0;precision<3;++precision) for (unsigned rounding=0;rounding<4;++rounding) {
        const unsigned pcs[]={0,0x200,0x300};
        const unsigned short cw=(unsigned short)((original&~0xF00)|pcs[precision]|(rounding<<10)|0x3F);
        setControl(cw);++modes;const unsigned short st=top();
        calls=0;tick=0x12345678;tickStep=0;
        RF455_SetDayRate(3);check(RF455_GetDayRate()==3);unchanged(cw,st);
        RF455_SetDayTime(36,60,60);
        check(calls==1);check(RF455_DayBase==tick-14400000u);
        check(RF455_GetDayFraction()==.5f);unchanged(cw,st);
        unsigned h=99,m=99,s=99;RF455_GetDayTime(&h,&m,&s);
        check(h==12 && m==0 && s==0);unchanged(cw,st);
        calls=0;RF455_SetDayFraction(.25f);
        check(calls==1 && RF455_DayBase==tick-7200000u);
        check(RF455_GetDayFraction()==.25f);unchanged(cw,st);
        calls=0;RF455_SetRealDayFraction(.25f);
        check(calls==1 && RF455_RealDayBase==tick-21600000u);
        check(RF455_GetRealDayFraction()==.25f);unchanged(cw,st);
        // Exact periods exercise modulo, the independent real-time counter and
        // its two separate GetTickCount calls without a wall-clock race.
        RF455_DayBase=RF455_RealDayBase=0;tick=14400000;calls=0;
        RF455_AdvanceDayClock();check(calls==2);
        check(RF455_GetDayFraction()==.5f);unchanged(cw,st);
        RF455_SetDayRate(2);tick=43200000;calls=0;
        RF455_AdvanceDayClock();check(calls==2);
        check(RF455_GetDayFraction()==0 && RF455_GetRealDayFraction()==.5f);unchanged(cw,st);
        // Counter subtraction is unsigned32, including GetTickCount rollover.
        RF455_SetDayRate(1);RF455_DayBase=RF455_RealDayBase=0xFFFFFC18u;tick=0;calls=0;
        RF455_AdvanceDayClock();check(calls==2);
        check(RF455_GetDayFraction()>0 && RF455_GetDayFraction()<.001f);
        check(bits(RF455_GetDayFraction())==bits(RF455_GetRealDayFraction()));unchanged(cw,st);
        // Real time intentionally has no24h modulo; game time does.
        RF455_DayBase=RF455_RealDayBase=0;tick=129600000;calls=0;
        RF455_AdvanceDayClock();check(RF455_GetDayFraction()==.5f);
        check(RF455_GetRealDayFraction()==1.5f);unchanged(cw,st);
        tick=0x10000000;tickStep=0;
        const unsigned inputs[]={0,0x80000000,0x3E800000,0x3F800000,0x3FC00000,0xBE800000,0x7F800000,0xFF800000,0x7FC12345};
        for (unsigned i=0;i<sizeof(inputs)/sizeof(inputs[0]);++i) {
            RF455_SetDayRate(3);calls=0;RF455_SetDayFraction(fromBits(inputs[i]));
            check(calls==1 && bits(RF455_GetDayFraction())==inputs[i]);unchanged(cw,st);
            calls=0;RF455_SetRealDayFraction(fromBits(inputs[i]));
            check(calls==1 && bits(RF455_GetRealDayFraction())==inputs[i]);unchanged(cw,st);
        }
        RF455_SetDayRate(0);calls=0;RF455_SetDayFraction(.5f);
        check(calls==1 && RF455_DayBase==tick);unchanged(cw,st);
        RF455_SetDayRate(-3);RF455_SetDayTime(12,0,0);
        check(RF455_DayBase==tick+14400000u);unchanged(cw,st);
        RF455_SetDayRate(3);RF455_SetDayTime(0xFFFFFFFFu,0xFFFFFFFFu,0xFFFFFFFFu);
        check(RF455_DayBase==tick-18305000u);unchanged(cw,st);
        // Getter writes hour/minute/second in that order even when outputs alias.
        RF455_SetDayFraction(.5f);h=99;RF455_GetDayTime(&h,&h,&h);check(h==0);unchanged(cw,st);
        RF455_DayBase=RF455_RealDayBase=0;tick=0;tickStep=43200000;calls=0;
        RF455_AdvanceDayClock();check(calls==2);
        check(RF455_GetDayFraction()==0 && RF455_GetRealDayFraction()==.5f);unchanged(cw,st);
    }
    setControl(original);RF455_ClockTickSource=&GetTickCount;
    fprintf(output,"{\"checks\":%u,\"failures\":%u,\"first_failure\":%u,\"precision_rounding_modes\":%u,\"fake_ticks_only\":true}\n",checks,failures,firstFailure,modes);
    return failures?1:0;
}
#if !defined(RF455_CLOCK_EMBEDDED)
int main() { return runClockChecks(stdout); }
#endif
