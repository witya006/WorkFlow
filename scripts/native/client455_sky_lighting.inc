// Included after sky_atmosphere.inc in the single ordinary level.cpp owner.
#include "client455_sky_lighting.h"
#include "client455_sky_lighting_math.h"
#include "client455_weather_format.h"
#include <cstdlib>
#include <cstdio>

namespace {
RF455SkyFogEndpoint skyDayFog={},skyNightFog={};
DWORD skyTint=0xffffffffu,skyDirect=0xffffffffu;
float skyPosition[3]={},skyExposure=0;
unsigned skySampleCount=0,skySampleDivisor=0;

// Explicit float stores mirror the selected finite arithmetic in8B2670.
float skyMul(float a,float b){float out;__asm{fld a
    fmul b
    fstp out}return out;}
float skyAdd(float a,float b){float out;__asm{fld a
    fadd b
    fstp out}return out;}
float skyReciprocal(float a){float out;__asm{fld1
    fdiv a
    fstp out}return out;}
float skySqrt(float a){float out;__asm{fld a
    fsqrt
    fstp out}return out;}
float skyMulAdd(float a,float b,float c){float out;__asm{fld a
    fmul b
    fadd c
    fstp out}return out;}
float skyCube(float a){float out;__asm{fld a
    fld st
    fmul st,st
    fmulp st(1),st
    fstp out}return out;}
float skyLengthSquared(const float* xyz){
    const float x=xyz[0],y=xyz[1],z=xyz[2];float out;
    __asm{fld y
        fmul y
        fld x
        fmul x
        faddp st(1),st
        fld z
        fmul z
        faddp st(1),st
        fstp out}
    return out;
}
float skyRayPhase(float dot){float out;__asm{fld dot
    fmul dot
    fld1
    faddp st(1),st
    fstp out}return out;}
void skyPhaseFactors(float g,float& oneMinusSquare,float& onePlusSquare,float& twice){
    float a,b,c;
    __asm{fld g
        fmul g
        fld1
        fsub st,st(1)
        fstp a
        fld1
        faddp st(1),st
        fstp b
        fld g
        fadd st,st
        fstp c}
    oneMinusSquare=a;onePlusSquare=b;twice=c;
}
float skyGridHeight(float value){
    const double height=5160,quarter=.25;float out;
    __asm{fld value
        fmul height
        fmul quarter
        fstp out}
    return out;
}
DWORD readSkyColor(FILE* file,char* token){
    std::fscanf(file,"%s",token);const DWORD r=DWORD(std::atol(token));
    std::fscanf(file,"%s",token);const DWORD g=DWORD(std::atol(token));
    std::fscanf(file,"%s",token);const DWORD b=DWORD(std::atol(token));
    return b|((g|((r|0xffffff00u)<<8))<<8);
}
void updatePreviousSunPosition(){
    auto* state=GetR3State();float world[4][4],temp[4][4];
    MatrixIdentity(world);MatrixScale(temp,skySun.scale,skySun.scale,skySun.scale);
    MatrixMultiply(world,temp,world);world[3][2]=state->mFar;
    MatrixRotateX(temp,skyMul(skySun.orbit,-180));MatrixMultiply(world,temp,world);
    MatrixRotateZ(temp,-30);MatrixMultiply(world,temp,world);
    std::memcpy(skyPosition,world[3],sizeof(skyPosition));
}
void updateSoftwareFog(){
    DWORD red=0,green=0,blue=0,count=0;
    for(int i=0;i<=16;++i)for(int j=0;j<=16;++j){
        const float x=float(i-8),z=float(j-8);
        const float distance=skySqrt(skyAdd(skyMul(z,z),skyMul(x,x)));
        const float capped=distance>4?4:distance;
        const float height=RF455_FadeSubtract(4,capped);
        const float position[3]={skyMul(x,1290),skyGridHeight(height),-skyMul(z,1290)};
        const DWORD color=RF455_SampleSkyColor(position);
        if(color){red+=(color>>16)&255;green+=(color>>8)&255;blue+=color&255;++count;}
    }
    const DWORD divisor=RF455_SkyFogDivisor(count,skyExposure);
    skySampleCount=count;skySampleDivisor=divisor;
    // The reference performs unsigned DIV, including its divide-error behavior.
    // Do not introduce an alternate success/default color for divisor zero.
    red/=divisor;green/=divisor;blue/=divisor;
    if(red>255)red=255;if(green>255)green=255;if(blue>255)blue=255;
    GetR3State()->mFogColor=0xff000000u|(red<<16)|(green<<8)|blue;
}
}

const RF455SkyFogEndpoint& RF455_GetSkyDayFog(){return skyDayFog;}
const RF455SkyFogEndpoint& RF455_GetSkyNightFog(){return skyNightFog;}
void RF455_ResetSkyFogEndpoints(){skyDayFog={};skyNightFog={};}
void RF455_LoadSkyFogEndpoints(const RF455_ExtMaterial& mat){
    if(mat.mFlag&4)skyDayFog={mat.mFogStart,mat.mFogEnd,mat.mFogColor};
    if(mat.mFlag&8)skyNightFog={mat.mFogStart2,mat.mFogEnd2,mat.mFogColor2};
}
void RF455_ReadSkyFogToken(FILE* file,char* token){
    auto* state=GetR3State();
    if(!std::strcmp(token,"*FOG_START")){
        state->mIsFog=TRUE;std::fscanf(file,"%s",token);
        state->mMainFogStart=float(std::atof(token));state->mFogStart=float(std::atof(token));
        skyDayFog.start=state->mFogStart;
    }
    if(!std::strcmp(token,"*FOG_END")){
        state->mIsFog=TRUE;std::fscanf(file,"%s",token);
        state->mMainFogEnd=float(std::atof(token));state->mFogEnd=float(std::atof(token));
        skyDayFog.end=state->mFogEnd;state->mFar=state->mFogEnd;
    }
    if(!std::strcmp(token,"*FOG_COLOR")){
        state->mIsFog=TRUE;
        if(state->mFogEnd==0)state->mFogEnd=state->mMainFogEnd=5000;
        if(state->mFogStart==0)state->mFogStart=state->mMainFogStart=5;
        state->mFogColor=state->mMainFogColor=skyDayFog.color=readSkyColor(file,token);
        // Target auto-filled current/main distances do NOT fill day endpoints.
    }
    if(!std::strcmp(token,"*FOG_COLOR2"))skyNightFog.color=readSkyColor(file,token);
    if(!std::strcmp(token,"*FOG_START2")){std::fscanf(file,"%s",token);skyNightFog.start=float(std::atof(token));}
    if(!std::strcmp(token,"*FOG_END2")){std::fscanf(file,"%s",token);skyNightFog.end=float(std::atof(token));}
}
DWORD RF455_GetSkyTintColor(){return skyTint;}
DWORD RF455_GetSkyDirectColor(){return skyDirect;}
DWORD RF455_ApplySkyTint(DWORD color){return RF455_GetSkyDayEnabled()?RF455_ModulateSkyTint(color,skyTint):color;}
void RF455_GetSkySunPosition(float* xyz){std::memcpy(xyz,skyPosition,sizeof(skyPosition));}
void RF455_GetSkySunColor(float* rgba){sunColor(rgba);}
void RF455_GetSkyScatterParameters(float* values){std::memcpy(values,skyParams,sizeof(skyParams));}
void RF455_SetSkyFogExposure(float value){skyExposure=value;}
float RF455_GetSkyFogExposure(){return skyExposure;}
void RF455_SetSkyFogExposureColor(DWORD color){
    const unsigned value=color&255;const double maximum=255;float result;
    __asm{fild value
        fdiv maximum
        fstp result}
    RF455_SetSkyFogExposure(result);
}
unsigned RF455_GetSkyFogSampleCount(){return skySampleCount;}
unsigned RF455_GetSkyFogSampleDivisor(){return skySampleDivisor;}

DWORD RF455_SampleSkyColor(const float* xyz){
    float light[4];sunColor(light);light[3]=skySun.intensity;
    float beta[3],inverse[3],rayPhase[3],miePhase[3];
    for(unsigned i=0;i<3;++i){
        beta[i]=skyAdd(skyMul(skyParams[5+i],skyParams[3]),skyMul(skyParams[11+i],skyParams[4]));
        inverse[i]=skyReciprocal(beta[i]);
        rayPhase[i]=skyMul(skyParams[8+i],skyParams[3]);
        miePhase[i]=skyMul(skyParams[14+i],skyParams[4]);
    }
    float oneMinusSquare,onePlusSquare,twice;
    skyPhaseFactors(skyParams[0],oneMinusSquare,onePlusSquare,twice);
    const float logTwo=float(std::log(2.0)),inverseLog=skyReciprocal(logTwo);
    const float length=skySqrt(skyLengthSquared(xyz)),inverseLength=skyReciprocal(length);
    const float dot=-skyMul(xyz[1],inverseLength),ray=skyRayPhase(dot);
    const float denominator=skyMulAdd(twice,dot,onePlusSquare);
    const float inverseSqrt=denominator==0?0:skyReciprocal(skySqrt(denominator));
    const float mie=skyMul(oneMinusSquare,skyCube(inverseSqrt));
    DWORD channel[3];
    for(unsigned i=0;i<3;++i){
        const float optical=skyMul(inverseLog,skyMul(-length,beta[i]));
        const float attenuation=float(std::pow(2.0,double(optical)));
        const float scattering=skyAdd(skyMul(rayPhase[i],ray),skyMul(miePhase[i],mie));
        const float transmitted=skyMul(RF455_FadeComplement(attenuation),scattering);
        float value=skyMul(inverse[i],transmitted);
        value=skyMul(value,skyParams[1]);value=skyMul(value,light[i]);value=skyMul(value,light[3]);
        if(value<0)value=0;if(value>1)value=1;channel[i]=RF455_FadeAlphaByte(value);
    }
    return channel[2]|((channel[1]|((channel[0]|0xffffff00u)<<8))<<8);
}
void RF455_UpdateSkyLighting(){
    if(!RF455_GetSkyDayEnabled())return;
    updatePreviousSunPosition();RF455_UpdateSunValues();RF455_UpdateSkyNightWeight();
    float rgb[4];sunColor(rgb);auto* state=GetR3State();
    skyTint=RF455_SkyTintColor(rgb,state->mFogColor);skyDirect=RF455_SunDirectColor(rgb,skySun.alpha);
    if(state->mEnvironmentSceneFlags&2){
        const float weight=RF455_GetSkyNightWeight();
        state->mFogColor=RF455_SkyFogColor(skyDayFog.color,skyNightFog.color,weight);
        state->mFogStart=RF455_SkyWeightedFloat(skyDayFog.start,skyNightFog.start,weight);
        state->mFogEnd=RF455_SkyWeightedFloat(skyDayFog.end,skyNightFog.end,weight);
    }else updateSoftwareFog();
}
