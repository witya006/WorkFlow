#include "r3particle.h"
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <new>
int main(){
    alignas(CParticle) unsigned char storage[sizeof(CParticle)],expected[sizeof(CParticle)]={};
    std::memset(storage,0xa5,sizeof(storage));auto* particle=new(storage)CParticle;
    const float gravity=-15;const int light=-1;std::memcpy(expected+160,&gravity,4);std::memcpy(expected+1292,&light,4);
    const bool constructorEqual=std::memcmp(storage,expected,sizeof(storage))==0;
    particle->~CParticle();
    if(!constructorEqual)return 1;
    std::printf("{\"CParticle\":%zu,\"CEntity\":%zu,\"element\":%zu,\"fields\":{",sizeof(CParticle),sizeof(CEntity),sizeof(_PARTICLE_ELEMENT));
    bool comma=false;
#define FIELD(name) std::printf("%s\"" #name "\":%zu",comma?",":"",offsetof(CParticle,name));comma=true;
    FIELD(mNum) FIELD(mElement) FIELD(mEntity) FIELD(mLiveTime) FIELD(mStartTimeRange)
    FIELD(mTimeSpeed) FIELD(mGravity) FIELD(mStartPower) FIELD(mStartScale)
    FIELD(mStartARGB) FIELD(mOnePerTimeEpsilon) FIELD(mRotMat) FIELD(mElasticity)
    FIELD(mZFront) FIELD(mEmitTime) FIELD(mSpecialID) FIELD(mTrackCnt)
    FIELD(mTimeTrack) FIELD(mTrackFlag) FIELD(mATrack) FIELD(mRTrack) FIELD(mScaleTrack)
    FIELD(mZRotTrack) FIELD(mYRotTrack) FIELD(mPowerTrack) FIELD(mSpecialARGV)
    FIELD(mBsp) FIELD(mFlag) FIELD(mAlphaType) FIELD(mStartPos) FIELD(mCreatePos)
#undef FIELD
    std::printf("},\"constructor_1296_equal\":true}\n");return 0;
}
