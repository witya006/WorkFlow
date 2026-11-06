#include "r3enginekernel.h"
#include "core.h"
#include "r3util.h"
#include "r3sound.h"
#include "client455_rvp_audio.h"
#include <cmath>
float RF455_RvpVolume(const float* position,float maximumDistance){
    const float inner=float(double(maximumDistance)*.25);float camera[3];GetCameraPos(&camera);
    const float x=float(double(position[0])-camera[0]),y=float(double(position[1])-camera[1]),z=float(double(position[2])-camera[2]);
    const float squared=float(double(y)*y+double(x)*x+double(z)*z),distance=float(std::sqrt(double(squared)));
    const float excess=float((double(distance)-inner)>0?double(distance)-inner:0);
    return float(1-double(excess)/(double(maximumDistance)-inner));
}
float RF455_RvpPan(const float* position){
    const auto* state=GetR3State();const auto& matrix=state->mMatView;const auto& inverse=state->mInvMatView;
    const float squared=float(double(matrix._32)*matrix._32+double(matrix._31)*matrix._31+double(matrix._33)*matrix._33),length=float(std::sqrt(double(squared)));
    const float vx=float(double(matrix._33)/length),vy=float(double(matrix._32)/length),vz=float(double(matrix._31)/length);
    const float x=float(double(inverse._41)-position[0]),y=float(double(inverse._42)-position[1]),z=float(double(inverse._43)-position[2]);
    const float d2=float(double(z)*z+double(x)*x+double(y)*y),d=float(std::sqrt(double(d2)));
    const float nx=float(double(x)/d),ny=float(double(y)/d),nz=float(double(z)/d);
    return float(.5-(double(ny)*vy+double(nx)*vx+double(nz)*vz)*.5);
}
void RF455_PlayRvpWave(unsigned id,const float* position,float maximumDistance){
    const float volume=RF455_RvpVolume(position,maximumDistance);if(volume>0)IM_PlayWave(id,volume,RF455_RvpPan(position));
}
