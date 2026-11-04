#pragma once
void RF455_EffectLog(const char* text);
// Matches the nearby clear routine; lifecycle is unproven, so no automatic call.
void RF455_ClearPendingEffectLog();
