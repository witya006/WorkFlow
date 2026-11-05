#include "Character.h"
#include "client455_normal_accounting.h"

namespace {RF455NormalCharacterAccounting accounting={};}
extern "C" RF455NormalCharacterAccounting* RF455_GetNormalCharacterAccounting(){return &accounting;}
CHMEMORYINFO RF455_GetCharacterMemoryInfo(){
    const auto textures=RF455_GetTextureAccounting();
    return {textures.estimatedBytes,textures.created,accounting.buffers.bytes,
        accounting.buffers.created,accounting.importedAnimationBytes,
        accounting.meshes.constructed,accounting.meshes.bytesConstructed};
}
