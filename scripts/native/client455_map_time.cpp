#include "client455_map_time.h"
#include <string.h>
#include <time.h>
extern "C" const double RF455_SecondsPerDay;

extern "C" void RF455_InitMapTime(RF455_MapTimeState* state) {
    state->value0=0;state->timestamp=0;
    // Reference Init leaves receipt tick and special-map day unchanged. Valid
    // packet-before-map scenarios are tested; do not invent an early-load gate.
}
extern "C" void RF455_ReceiveMapTime(RF455_MapTimeState* state,const void* payload) {
    const char* bytes=static_cast<const char*>(payload);
    memcpy(&state->value0,bytes+1,4);
    memcpy(&state->timestamp,bytes+5,4);
    state->receiptTick=RF455_ClockTickSource();
    // Payload byte0 and transport length are not inspected by the455handler.
}

// The marked130-byte numeric body matches the map caller's x87 sequence,
// including double/float spills and a low-DWORD truncation before modulo.
extern "C" __declspec(naked) float RF455_MapGameFraction(DWORD) {
    __asm {
        push ebp
        mov ebp, esp
        sub esp, 0C4h
        mov eax, [ebp+8]
        mov [ebp-58h], eax
        // Begin body corresponding to455VA7C8DC4.
        mov eax, [ebp-58h]
        mov [ebp-0A4h], eax
        mov dword ptr [ebp-0A0h], 0
        fild qword ptr [ebp-0A4h]
        fstp qword ptr [ebp-0ACh]
        call RF455_GetDayRate
        fmul qword ptr [ebp-0ACh]
        fnstcw word ptr [ebp-0AEh]
        movzx eax, word ptr [ebp-0AEh]
        or eax, 0C00h
        mov [ebp-0B4h], eax
        fldcw word ptr [ebp-0B4h]
        fistp qword ptr [ebp-0BCh]
        fldcw word ptr [ebp-0AEh]
        mov eax, [ebp-0BCh]
        xor edx, edx
        mov ecx, 15180h
        div ecx
        mov [ebp-0C4h], edx
        mov dword ptr [ebp-0C0h], 0
        fild qword ptr [ebp-0C4h]
        fdiv RF455_SecondsPerDay
        fstp dword ptr [ebp-5Ch]
        // End matched body. Own balanced return of the spilled float.
        fld dword ptr [ebp-5Ch]
        mov esp, ebp
        pop ebp
        ret
    }
}

extern "C" void RF455_ApplyMapTime(RF455_MapTimeState* state,unsigned mapIndex) {
    __time32_t stamp;memcpy(&stamp,&state->timestamp,4);
    // Reference does not check localtime32's result. Invalid/negative calendar
    // input and complete old-CRT timezone/DST parity are outside scoped tests.
    struct tm* calendar=_localtime32(&stamp);
    const DWORD elapsed=(RF455_ClockTickSource()-state->receiptTick)/1000u;
    calendar->tm_sec+=(int)(elapsed%60u);
    calendar->tm_min+=(int)((elapsed/60u)%60u);
    const DWORD total=(DWORD)(calendar->tm_sec+60*calendar->tm_min+3600*calendar->tm_hour);
    RF455_SetDayFraction(RF455_MapGameFraction(total));
    const __int64 whole=total%86400u;
    float real;
    __asm { fild whole
            fdiv RF455_SecondsPerDay
            fstp real }
    RF455_SetRealDayFraction(real);
    state->mapDay=mapIndex==12?(DWORD)calendar->tm_mday:0;
}
