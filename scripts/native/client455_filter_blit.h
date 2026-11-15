#ifndef RF455_FILTER_BLIT_H
#define RF455_FILTER_BLIT_H

struct IDirect3DTexture9;

bool RF455_FilterBlitAvailable();

// Call between scenes with two render-target textures. Input already contains
// the first source image and is reused as scratch. A successful result is in output.
bool RF455_FilterBlit(IDirect3DTexture9* output, IDirect3DTexture9* input, unsigned passes);

// Call between scenes. Quality 1 uses a 3x3 kernel and quality 2 uses a 5x5 kernel.
bool RF455_FilterBlitFixed(IDirect3DTexture9* output, IDirect3DTexture9* input, unsigned quality);

#endif
