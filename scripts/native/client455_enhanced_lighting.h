#pragma once
#include "client455_shaders.h"

// User-facing state. Persistence is internal; callers use the settings menu.
bool RF455_EnhancedActorLightingAvailable();
bool RF455_EnhancedActorLightingEnabled();
bool RF455_SetEnhancedActorLightingEnabled(bool enabled);

// Source-owned extension: original shader indices and packed renderer stay intact.
void RF455_InitializeEnhancedActorLighting(RF455ShaderManager*, const RF455ShaderApi*);
void RF455_ReleaseEnhancedActorLighting(RF455ShaderManager*);
void RF455_SetEnhancedActorLightingProtected(bool protectedEffect);
bool RF455_BindEnhancedActorLighting(RF455ShaderManager*, const float* material17,
                                    const float* view16, const float* lightDirection3,
                                    bool normalMap, bool specularMap, unsigned* selected);
