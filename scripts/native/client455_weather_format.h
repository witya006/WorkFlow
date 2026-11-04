#pragma once
#include <stdio.h>
#include <stddef.h>
#include "client455_clock.h"

#pragma pack(push,1)
struct RF455_ExtMaterial {
    unsigned int mFlag;
    float mFogStart,mFogEnd;
    unsigned int mFogColor;
    float mFogStart2,mFogEnd2;
    unsigned int mFogColor2;
    float BBMin2[3],BBMax2[3];
    float mLensFlareScale[16];
    char mLensTexName[128];
    float mLensFlarePos[3];
    char mEnvEntityName[128];
    unsigned int mEnvID;
    unsigned int mEnvReserved;
    char mEnvEntityName2[128];
    unsigned int mEnvID2;
    unsigned int mSceneFlags;
    unsigned char spare[504];
};
#pragma pack(pop)
static_assert(sizeof(RF455_ExtMaterial)==1032,"455 R3X payload");
static_assert(offsetof(RF455_ExtMaterial,mEnvEntityName)==256,"environment 0 name");
static_assert(offsetof(RF455_ExtMaterial,mEnvID)==384,"environment 0 id");
static_assert(offsetof(RF455_ExtMaterial,mEnvEntityName2)==392,"environment 1 name");
static_assert(offsetof(RF455_ExtMaterial,mEnvID2)==520,"environment 1 id");
static_assert(offsetof(RF455_ExtMaterial,mSceneFlags)==524,"scene flags");

// The format has version 1.1 for both 1024- and 1032-byte bodies. Short bodies
// copy their available bytes into zeroed storage, as the reference's fread does.
bool RF455_ReadExtMaterial(FILE*,RF455_ExtMaterial*);
void RF455_ReadWeatherTokens(FILE*,char* mutableToken);
