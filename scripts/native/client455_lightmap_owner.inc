#include <limits.h>
#include "client455_resource_io.h"

R3Texture* RF455_ReserveLightmapR3T455(char* name, DWORD flag, RF455ResourceRead& source);
_LIGHTMAP** RF455_LoadPreparedLightmap455(R3Texture* tex, const RF455ResourceRead& source);

void LoadLightMap(char* name)
{
    ReleaseLightMap();
    if (!name || !*name || strlen(name) >= 256) return;
    char path[256];
    strcpy(path, name);
    RF455ResourceRead source;
    R3Texture* tex = RF455_ReserveLightmapR3T455(path, 0, source);
    if (!tex || !tex->mTexNum || tex->mTexNum > (INT_MAX - 4) / sizeof(int)) return;

    const DWORD count = tex->mTexNum;
    auto* ids = static_cast<int*>(Dmalloc(static_cast<int>(sizeof(int) * count)));
    if (!ids) return;
    auto** maps = RF455_LoadPreparedLightmap455(tex, source);
    if (!maps) { Dfree(ids); return; }
    for (DWORD i = 0; i < count; ++i) ids[i] = static_cast<int>(tex->mStartID + i);
    stLightmapTex = tex;
    stLightmap = maps;
    LightmapTexID = ids;
    Lightmap_cnt = static_cast<int>(count);
}
