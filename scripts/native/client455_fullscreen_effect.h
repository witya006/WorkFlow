#pragma once
// 455 8CE9D0/BF7850. Setter stores the float unchanged;the verified drawing
// domain is finite[0,1]. Other numerical/failure domains remain unaccepted.
void RF455_SetFullScreenEffectDensity(float);
float RF455_GetFullScreenEffectDensity();
