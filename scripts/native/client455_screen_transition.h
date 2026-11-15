#ifndef RF455_SCREEN_TRANSITION_H
#define RF455_SCREEN_TRANSITION_H

struct IDirect3DTexture9;

// Draw inside the caller's active scene. The caller owns both input textures.
bool RF455_DrawScreenTransition(IDirect3DTexture9* image, IDirect3DTexture9* mask, float progress);

#endif
