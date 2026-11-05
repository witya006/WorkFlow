#include "client455_character_clock.h"
#include <mmsystem.h>

namespace {
RF455CharacterClock clockState;
RF455CharacterClockProviders providers={&QueryPerformanceFrequency,&QueryPerformanceCounter,&timeGetTime};
}
extern "C" RF455CharacterClock* RF455_GetNormalCharacterClock(){return &clockState;}
extern "C" RF455CharacterClockProviders* RF455_GetNormalCharacterClockProviders(){return &providers;}
void _R3CalculateTime(){RF455_UpdateCharacterClock(&clockState,&providers);}
