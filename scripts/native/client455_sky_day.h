#pragma once
// Own storage for the selected455 sky day/night contract. This is not the
// private atmosphere object ABI; its sun/scattering fields remain separate work.
int RF455_SetSkyDayEnabled(int value);
int RF455_GetSkyDayEnabled();
float RF455_GetSkyNightWeight();
void RF455_UpdateSkyNightWeight();
