#pragma once
#include "Character.h"
#include "client455_rvp.h"
#include <array>
#include <vector>
class CAniCamera;
class CLevel;

// Named source state. It is not an overlay of the original20600-byte actor.
struct RF455RvpPalette {
    unsigned count=0;
    std::array<unsigned char,256> bytes={};
};
struct RF455RvpActorRuntime {
    CHARACTEROBJECT* bone=nullptr;CHARACTEROBJECT* mesh=nullptr;
    unsigned dummy=0xffffffffu,color=0,renderColor=0;
    float previousFrame=0,frame=0,fadeDuration=0,fadeStart=0,fadeAmount=0;
    float low[3]={},high[3]={},matrix[4][4]={};
    bool visible=false;
    unsigned poseUpdates=0,draws=0,animationSelections=0;
    std::vector<RF455RvpPalette> palette;
};
void RF455_LoadRvpActor(RF455RvpActorRuntime&,const RF455RvpActor&,ChInterface&,
    RF455CharacterManager*,AnimationManager&);
void RF455_RvpActorAnimation(RF455RvpActorRuntime&,const RF455RvpActor&,
    ChInterface&,AnimationManager&,unsigned);
void RF455_RvpActorFrame(RF455RvpActorRuntime&,const RF455RvpActor&,
    ChInterface&,RF455CharacterManager*,CAniCamera&);
void RF455_RvpActorDraw(RF455RvpActorRuntime&,const RF455RvpActor&,
    ChInterface&,RF455CharacterManager*,EffectList&,CLevel&);
void RF455_SaveRvpPalette(RF455RvpActorRuntime&);
void RF455_RestoreRvpPalette(const RF455RvpActorRuntime&);
