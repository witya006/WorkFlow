#pragma once
#include "client455_renderer_owner.h"

// Recovered91D330 return is SetDepthStencilSurface(NULL)'s HRESULT, not BOOL.
// A successful S_OK is0 although the two original callers use if(result).
// End must only follow a pass that actually reached BeginScene. Reference error
// paths/retained released saved pointers are intentionally not made repeatable.
extern "C" {
// Process-global quad at original1189598; initially zero, populated before the
// first VB creation attempt. The ground-projection consumer will share it.
extern unsigned RF455_NormalShadowQuadBits[24];
int RF455_BeginNormalShadow(RF455CharacterRenderer*,unsigned index);
void RF455_EndNormalShadow(RF455CharacterRenderer*);
}
