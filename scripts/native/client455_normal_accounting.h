#pragma once
#include "client455_shared_buffers.h"

// Source process ownership for original global cumulative DWORD counters.
// These are not live allocation totals and must survive renderer destruction.
struct RF455NormalCharacterAccounting {
    RF455MeshAccounting meshes;
    RF455BufferAccounting buffers;
    unsigned importedAnimationBytes;
};
extern "C" RF455NormalCharacterAccounting* RF455_GetNormalCharacterAccounting();
