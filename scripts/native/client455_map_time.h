#pragma once
#include "client455_clock.h"

// Own client storage, not the455CLand binary layout. The opaque first DWORD is
// preserved; its other consumers have not yet been reconstructed.
struct RF455_MapTimeState {
    DWORD value0,timestamp,receiptTick,mapDay;
};
static_assert(sizeof(RF455_MapTimeState)==16,"Own map time state");
extern "C" {
void RF455_InitMapTime(RF455_MapTimeState*);
void RF455_ReceiveMapTime(RF455_MapTimeState*,const void* payload);
void RF455_ApplyMapTime(RF455_MapTimeState*,unsigned mapIndex);
float RF455_MapGameFraction(DWORD totalSeconds);
}
