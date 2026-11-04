// CPU-only diagnostic paths within the complete client build.
#include "client455_weather_format.h"
#include "r3material.h"
#include "r3bsp.h"
#include "commonutil.h"
void LoadR3X(char*);

static bool weatherPaths(char* input,char* output) {
    const DWORD n=GetEnvironmentVariableA("RF_LAB_HELPER_INPUT",input,32768);
    const DWORD m=GetEnvironmentVariableA("RF_LAB_HELPER_OUTPUT",output,32768);
    return n && n<32768 && m && m<32768;
}
static unsigned weatherReadProbe() {
    struct Result {
        char magic[8];
        DWORD version,parsed,applied,checks,failures,ids[2],sceneFlags;
        char names[2][128];
        RF455_ExtMaterial material;
    } result={};
    static_assert(sizeof(Result)==1328,"Weather result layout");
    char input[32768],output[32768];
    if (!weatherPaths(input,output)) return 31;
    FILE* file=std::fopen(input,"rb");
    if (!file) return 32;
    std::memcpy(result.magic,"RFWEA455",8);result.version=1;
    result.parsed=RF455_ReadExtMaterial(file,&result.material);
    std::fclose(file);
    _R3ENGINE_STATE* state=GetR3State();
    state->mEnvIDs[0]=state->mEnvIDs[1]=0;
    std::memset(state->mEnvEntityNames,0,sizeof(state->mEnvEntityNames));
    if (result.parsed && !(result.material.mFlag&0x10)) {
        LoadR3X(input);
        result.applied=1;
        result.ids[0]=state->mEnvIDs[0];result.ids[1]=state->mEnvIDs[1];
        result.sceneFlags=state->mEnvironmentSceneFlags;
        std::memcpy(result.names,state->mEnvEntityNames,sizeof(result.names));
    }
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) { ++result.checks; if (GetModuleHandleA(dlls[i])) ++result.failures; }
    file=std::fopen(output,"wb");
    if (!file) return 33;
    bool ok=std::fwrite(&result,sizeof(result),1,file)==1;
    ok=std::fclose(file)==0 && ok;
    return !ok?34:result.failures?35:0;
}

static unsigned weatherScenarioProbe() {
    char input[32768],output[32768];
    if (!weatherPaths(input,output)) return 41;
    unsigned checks=0,failures=0,firstFailure=0;
    auto verify=[&](bool value) { ++checks;if (!value) { ++failures;if (!firstFailure) firstFailure=checks; } };
    const int before=GetDmallocSize();
    CExtDummy helpers;
    verify(helpers.LoadExtDummy(input)!=FALSE);
    CBsp* allocatedBsp=new CBsp;
    CBsp& bsp=*allocatedBsp;
    _R3ENGINE_STATE* state=GetR3State();
    state->mEnvironmentEnabled=TRUE;
    state->mEnvIDs[0]=state->mEnvIDs[1]=1;
    std::strcpy(state->mEnvEntityNames[0],"p0.spt");
    std::strcpy(state->mEnvEntityNames[1],"p1.spt");
    bsp.SetEnvironmentDummies455(&helpers);
    bsp.LoadEnvironment455();
    CParticle* first=bsp.GetEnvironmentParticle455(0);
    CParticle* second=bsp.GetEnvironmentParticle455(1);
    verify(first && second && first!=second);
    if (!first || !second) return 42;
    verify(bsp.GetEnvironmentKind455(0)==0x1001 && bsp.GetEnvironmentKind455(1)==0x1001);
    verify(first->mNum==1 && second->mNum==1 && first->mElement && second->mElement);
    verify((first->mFlag&0x10000)!=0 && (second->mFlag&0x10000)==0);
    R3SetLoopTime(0);
    MatrixIdentity(state->mMatView.m);
    MatrixIdentity(state->mInvMatView.m);
    verify(RF455_GetDayRate()==3.0f);
    RF455_SetDayRate(2.0f);verify(RF455_GetDayRate()==2.0f);
    RF455_SetDayTime(36,60,60);verify(RF455_GetDayFraction()==0.5f);
    RF455_SetDayRate(3.0f);verify(RF455_GetDayRate()==3.0f);
    RF455_SetDayFraction(0);
    bsp.UpdateEnvironment455();
    verify(first->GetParticleState()==0 && second->GetParticleState()==0);
    state->mInvMatView.m[3][0]=10000;
    state->mMatView.m[0][2]=.25f;
    state->mMatView.m[1][2]=.5f;
    bsp.UpdateEnvironment455();
    verify(first->GetParticleState()==1 && second->GetParticleState()==1);
    verify(first->mCreatePos[0]==10012.5f && first->mCreatePos[1]==25 && first->mCreatePos[2]==50);
    verify((first->mFlag&0x80000) && (second->mFlag&0x80000));
    verify(!first->mElement[0].mIsLive && !second->mElement[0].mIsLive);
    const unsigned values[]={0x3e75c28f,0x3e75c290,0x3f547ae1,0x3f547ae2}; // .24f/+ulp, .83f/+ulp
    const DWORD expected[]={1,0,0,1};
    for (unsigned i=0;i<4;++i) {
        float day;std::memcpy(&day,&values[i],4);
        RF455_SetDayFraction(day);
        verify(RF455_GetDayFraction()==day);
        bsp.UpdateEnvironment455();
        verify(first->GetParticleState()==expected[i] && second->GetParticleState()==1);
    }
    RF455_SetDayFraction(.5f);
    bsp.UpdateEnvironment455();
    verify(first->GetParticleState()==0 && second->GetParticleState()==1);
    RF455_SetDayFraction(0);
    state->mEnvironmentEnabled=FALSE;
    bsp.UpdateEnvironment455();
    verify(first->GetParticleState()==0);
    state->mEnvironmentEnabled=TRUE;
    bsp.UpdateEnvironment455();verify(first->GetParticleState()==1);
    first->SetParticleState(0);second->SetParticleState(0);
    state->mEnvIDs[0]=0;
    bsp.UpdateEnvironment455();verify(first->GetParticleState()==0 && second->GetParticleState()==0);
    state->mEnvIDs[0]=1;state->mEnvIDs[1]=2;
    state->mInvMatView.m[3][0]=0;
    bsp.UpdateEnvironment455();verify(first->GetParticleState()==0 && second->GetParticleState()==0);
    state->mInvMatView.m[3][0]=10000;
    bsp.UpdateEnvironment455();verify(first->GetParticleState()==1 && second->GetParticleState()==1);
    bsp.ReleaseEnvironment455();
    verify(!bsp.GetEnvironmentParticle455(0) && !bsp.GetEnvironmentParticle455(1));
    verify(!bsp.GetEnvironmentKind455(0) && !bsp.GetEnvironmentKind455(1));
    bsp.ReleaseEnvironment455();
    helpers.ReleaseExtDummy();
    delete allocatedBsp;
    verify(GetDmallocSize()==before);
    // The real material parser uses this same environment token consumer.
    FILE* text=std::fopen("weather.mst","rt");
    if (!text) return 43;
    char token[256];
    while (std::fscanf(text,"%s",token)!=EOF) { _strupr(token);RF455_ReadWeatherTokens(text,token); }
    std::fclose(text);
    verify(state->mEnvIDs[0]==2 && state->mEnvIDs[1]==1);
    verify(!std::strcmp(state->mEnvEntityNames[0],"FirstCase.SPT") && !std::strcmp(state->mEnvEntityNames[1],"SecondCase.SPT"));
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) verify(GetModuleHandleA(dlls[i])==NULL);
    FILE* result=std::fopen(output,"wt");
    if (!result) return 44;
    std::fprintf(result,"{\"checks\":%u,\"failures\":%u,\"first_failure\":%u,\"layers_loaded_released\":2,\"gpu_draw_called\":false}\n",checks,failures,firstFailure);
    std::fclose(result);
    return failures?45:0;
}
