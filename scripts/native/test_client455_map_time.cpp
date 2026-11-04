#include "client455_map_time.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <time.h>

static DWORD tick;
static unsigned calls,checks,failures,firstFailure;
static DWORD WINAPI testTick() { ++calls;return tick; }
static void check(bool v) { ++checks;if (!v) { ++failures;if (!firstFailure) firstFailure=checks; } }
static unsigned short control() { unsigned short v;__asm { fnstcw v } return v; }
static unsigned short top() { unsigned short v;__asm { fnstsw v } return v&0x3800; }
static void setControl(unsigned short v) { __asm fldcw v }
static void receive(RF455_MapTimeState* state,DWORD value,DWORD timestamp) {
    unsigned char storage[11]={0xA5,0x7F};
    memcpy(storage+2,&value,4);memcpy(storage+6,&timestamp,4);
    RF455_ReceiveMapTime(state,storage+1);check(storage[0]==0xA5 && storage[10]==0);
}
static int runMapTimeChecks(FILE* output) {
    const char* env=getenv("TZ");const std::string oldTZ=env?env:"";
    _putenv_s("TZ","UTC0");_tzset();
    const unsigned short original=control();auto provider=RF455_ClockTickSource;
    RF455_ClockTickSource=&testTick;unsigned modes=0;
    for (unsigned pc=0;pc<3;++pc) for (unsigned rc=0;rc<4;++rc) {
        const unsigned pcs[]={0,0x200,0x300};const unsigned short cw=(unsigned short)((original&~0xF00)|pcs[pc]|(rc<<10)|0x3F);
        setControl(cw);const unsigned short st=top();++modes;
        RF455_MapTimeState state;memset(&state,0xA5,sizeof(state));RF455_InitMapTime(&state);
        check(state.value0==0 && state.timestamp==0);
        check(state.receiptTick==0xA5A5A5A5 && state.mapDay==0xA5A5A5A5);
        calls=0;tick=0x10000000;RF455_SetDayRate(3);
        receive(&state,0x11223344,43200);
        check(calls==1 && state.value0==0x11223344 && state.timestamp==43200 && state.receiptTick==tick);
        calls=0;RF455_ApplyMapTime(&state,12);
        check(calls==3 && state.mapDay==1);
        check(RF455_GetDayFraction()==.5f && RF455_GetRealDayFraction()==.5f);
        check(control()==cw && top()==st);
        tick+=3600000;calls=0;RF455_ApplyMapTime(&state,0);
        // Reference drops complete elapsed hours at this map-load boundary.
        check(calls==3 && state.mapDay==0);
        check(RF455_GetDayFraction()==.5f && RF455_GetRealDayFraction()==.5f);
        calls=0;receive(&state,0xFFFFFFFF,21600);RF455_ApplyMapTime(&state,12);
        check(state.value0==0xFFFFFFFF && state.mapDay==1);
        check(RF455_GetDayFraction()==.75f && RF455_GetRealDayFraction()==.25f);
        RF455_SetDayRate(1.5f);receive(&state,7,43200);RF455_ApplyMapTime(&state,12);
        check(RF455_GetDayFraction()==.75f && RF455_GetRealDayFraction()==.5f);
        RF455_SetDayRate(1);receive(&state,1,86399);tick+=61000;
        RF455_ApplyMapTime(&state,12);
        check(state.mapDay==1); // tm_mday is not normalized by the added seconds/minutes.
        check(RF455_GetDayFraction()>.00069f && RF455_GetDayFraction()<.00070f);
        check(RF455_GetRealDayFraction()>.00069f && RF455_GetRealDayFraction()<.00070f);
        tick=0xFFFFFC18;receive(&state,0,0);tick=0;RF455_ApplyMapTime(&state,12);
        check(RF455_GetDayFraction()>0 && RF455_GetDayFraction()<.001f);
        check(state.receiptTick==0xFFFFFC18 && state.mapDay==1);
        receive(&state,2,1672531200);RF455_ApplyMapTime(&state,12);check(state.mapDay==1 && RF455_GetDayFraction()==0);
        receive(&state,3,1675123200);RF455_ApplyMapTime(&state,12);check(state.mapDay==31 && RF455_GetDayFraction()==0);
        check(control()==cw && top()==st);
    }
    _putenv_s("TZ","JST-9");_tzset();setControl(original);
    RF455_MapTimeState state={};tick=0x12345678;RF455_SetDayRate(3);
    receive(&state,5,0);RF455_ApplyMapTime(&state,12);
    check(state.mapDay==1 && RF455_GetDayFraction()==.125f && RF455_GetRealDayFraction()==.375f);
    RF455_ClockTickSource=provider;_putenv_s("TZ",oldTZ.c_str());_tzset();
    fprintf(output,"{\"checks\":%u,\"failures\":%u,\"first_failure\":%u,\"precision_rounding_modes\":%u,\"timezone_cases\":[\"UTC0\",\"JST-9\"]}\n",checks,failures,firstFailure,modes);
    return failures?1:0;
}
#if !defined(RF455_MAP_TIME_EMBEDDED)
int main() { return runMapTimeChecks(stdout); }
#endif
