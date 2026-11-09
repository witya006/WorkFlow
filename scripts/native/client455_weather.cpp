#include <windows.h>
#include <stdio.h>
#include <string.h>
#include "client455_weather_format.h"
#include "client455_weather_parameters.inc"
#include "r3math.h"
#include "core.h"
#include "r3bsp.h"
#include "extdummy.h"
#include "r3render.h"
#include "renderparticle.h"
#include "collision.h"
#include "r3util.h"
#include "commonutil.h"

bool RF455_ReadExtMaterial(FILE* file,RF455_ExtMaterial* material) {
    memset(material,0,sizeof(*material));
    // Preserve the unchecked reference header read. Inputs shorter than four
    // bytes leave an indeterminate float and are outside verified scenarios.
    float version;
    fread(&version,4,1,file);
    if (version!=1.1f) return false;
    fread(material,sizeof(*material),1,file);
    return true;
}

void RF455_ReadWeatherTokens(FILE* file,char* token) {
    _R3ENGINE_STATE* state=GetR3State();
    if (!strcmp(token,"*ENVIRONMENT")) { fscanf(file,"%s",token); strcpy(state->mEnvEntityNames[0],token); }
    if (!strcmp(token,"*ENVIRONMENT_ID")) { fscanf(file,"%s",token); state->mEnvIDs[0]=(DWORD)atoi(token); }
    if (!strcmp(token,"*ENVIRONMENT2")) { fscanf(file,"%s",token); strcpy(state->mEnvEntityNames[1],token); }
    if (!strcmp(token,"*ENVIRONMENT_ID2")) { fscanf(file,"%s",token); state->mEnvIDs[1]=(DWORD)atoi(token); }
    _strlwr(token); //90ACEC:case folding happens after the uppercase sections.
    RF455_ReadWeatherParameters(file,token);
    if (!strcmp(token,"*no_sun")) state->mEnvironmentSceneFlags|=1;
    if (!strcmp(token,"*no_sky_color")) state->mEnvironmentSceneFlags|=4;
    if (!strcmp(token,"*use_fog_fog2")) state->mEnvironmentSceneFlags|=2;
}

#if !defined(RF_CLIENT_455_CLOCK)
static DWORD dayBase=0;
static float dayFraction=0;
static float dayRate=3.0f;
float RF455_GetDayRate() { return dayRate; }
void RF455_SetDayRate(float value) { dayRate=value; }
float RF455_GetDayFraction() { return dayFraction; }
void RF455_SetDayFraction(float value) {
    dayFraction=value;
    dayBase=GetTickCount()-1000u*(DWORD)(__int64)((double)value*86400.0/dayRate);
}
void RF455_SetDayTime(unsigned hours,unsigned minutes,unsigned seconds) {
    const float value=(float)(seconds%60u+60u*(minutes%60u+60u*(hours%24u)));
    dayFraction=(float)((double)value/86400.0);
    dayBase=GetTickCount()-1000u*(DWORD)(__int64)((double)value/dayRate);
}
void RF455_AdvanceDayClock() {
    const double seconds=(double)(DWORD)(GetTickCount()-dayBase)/1000.0*dayRate;
    const DWORD whole=(DWORD)(__int64)seconds;
    const float fraction=(float)(seconds-(double)whole);
    const float wrapped=(float)((double)(whole%86400u)+(double)fraction);
    dayFraction=(float)((double)wrapped/86400.0);
    if (dayFraction>1.0f) dayFraction=0;
}

#endif

void CBsp::LoadEnvironment455() {
    _R3ENGINE_STATE* state=GetR3State();
    for (unsigned i=0;i<2;++i) {
        mEnvIDs[i]=state->mEnvIDs[i];
        if (!mEnvIDs[i]) continue;
        if (IsParticle(state->mEnvEntityNames[i])) mEnvIDs[i]|=_ENV_PARTICLE;
        if (mEnvIDs[i]&_ENV_PARTICLE) {
            mEnvParticles[i]=new CParticle;
            if (mEnvParticles[i]->LoadParticleSPT(state->mEnvEntityNames[i])) {
                mEnvParticles[i]->InitParticle();
                mEnvParticles[i]->SetParticleState(_PARTICLE_STATE_START);
            } else {
                delete mEnvParticles[i];
                mEnvIDs[i]=0;
                state->mEnvIDs[i]=0;
                // Reference leaves this inactive slot's raw pointer unchanged.
            }
        } else {
            mEnvEntities[i]=new CEntity;
            if (!mEnvEntities[i]->LoadEntity(state->mEnvEntityNames[i]))
                delete mEnvEntities[i];
            // Reference does not clear the ID on this failure edge. Its later
            // invalid-pointer behavior is not exercised by the native fixtures.
        }
    }
}

void CBsp::ReleaseEnvironment455() {
    for (unsigned i=0;i<2;++i) {
        if (!mEnvIDs[i]) continue;
        if (mEnvIDs[i]&_ENV_PARTICLE) {
            mEnvParticles[i]->ReleaseParticle();
            mEnvParticles[i]->ReleaseEntity();
            delete mEnvParticles[i];
        } else {
            mEnvEntities[i]->ReleaseEntity();
            delete mEnvEntities[i];
        }
        mEnvParticles[i]=NULL;
        mEnvIDs[i]=0;
    }
    mEnvironmentDummies=NULL;
}

void CBsp::UpdateEnvironment455() {
    _R3ENGINE_STATE* state=GetR3State();
    if (!state->mEnvironmentEnabled || !state->mEnvIDs[0]) return;
    DWORD indices[1024],count;
    mEnvironmentDummies->GetDummyList(4,&count,indices);
    Vector3f camera;
    Vector3fCopy(state->mInvMatView.m[3],camera);
    float identity[4][4];
    MatrixIdentity(identity);
    for (unsigned layer=0;layer<2;++layer) {
        const DWORD kind=state->mEnvIDs[layer];
        if (kind!=1 && kind!=2) continue;
        CParticle* particle=mEnvParticles[layer];
        Vector3f origin;
        Vector3fCopy(camera,origin);
        bool stop=false;
        if (kind==1) {
            for (unsigned j=0;j<3;++j) {
                float forward=(float)((double)state->mMatView.m[j][0]*0.0+
                    (double)state->mMatView.m[j][1]*0.0+state->mMatView.m[j][2]);
                float offset=(float)((double)forward*50.0);
                origin[j]=(float)((double)camera[j]+offset);
            }
            for (DWORD i=0;i<count;++i) {
                if (mEnvironmentDummies->IsInBBox(indices[i],camera)) { stop=true; break; }
            }
            const double day=RF455_GetDayFraction();
            if ((particle->mFlag&0x10000) && day>0.24 && day<0.83) stop=true;
        } else {
            Vector3f min={-4256,-5779,-4591},max={4385,3139,4943};
            stop=IsCollisionBBoxPoint(min,max,camera)!=FALSE;
        }
        particle->SetCreatePos(origin);
        particle->mFlag|=_PARTICLE_ATTR_BOUNDED_BOX;
        const DWORD oldState=particle->GetParticleState();
        if (stop) particle->SetParticleState(_PARTICLE_STATE_STOP);
        else if (oldState==_PARTICLE_STATE_STOP) particle->SetParticleState(_PARTICLE_STATE_START);
        if (!particle->Loop()) continue;
        particle->SetStartBoxArea();
        MatrixCopy(particle->mRotMat,identity);
    }
}

void CBsp::DrawEnvironment455() {
    _R3ENGINE_STATE* state=GetR3State();
    if (!state->mEnvironmentEnabled || !state->mEnvIDs[0]) return;
    float matrix[4][4];
    MatrixIdentity(matrix);
    Vector3fCopy(state->mInvMatView.m[3],matrix[3]);
    for (unsigned i=0;i<2;++i) {
        if (state->mEnvIDs[i]==1 || state->mEnvIDs[i]==2)
            DrawCParticle(mEnvParticles[i],mEnvParticles[i]->mEntity,matrix);
    }
}
