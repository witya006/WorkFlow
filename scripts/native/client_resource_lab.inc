// Full-client CPU probes: actual selected resource/particle/material consumers.
#include "client455_resource_io.h"
#include "r3particle.h"
#include "jerror.h"
#include "r3material.h"
void LoadR3X(char*);
static unsigned resourceWarnings=0;
static void resourceWarning(char*) { ++resourceWarnings; }
static unsigned resourceScenarioProbe() {
    char output[32768];
    DWORD length=GetEnvironmentVariableA("RF_LAB_HELPER_OUTPUT",output,sizeof(output));
    if (!length || length>=sizeof(output)) return 71;
    unsigned checks=0,failed=0;
#define RCHECK(expr) do { ++checks;if (!(expr)) ++failed; } while (0)
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) RCHECK(GetModuleHandleA(dlls[i])==NULL);
    int before=GetDmallocSize();
    SetWarningMessageProc(resourceWarning);
    RF455_RpkGroup owner;owner.LoadDirectory("resources\\");
    RCHECK(owner.count==1);
    RCHECK(RF455_SetResourceGroup(&owner)==&owner && RF455_GetResourceGroup()==&owner);
    const char* files[]={"RESOURCES\\FIRST.SPT","RESOURCES\\UPPER.SPT","RESOURCES\\INVALID.SPT"};
    const unsigned expected[]={3,4,0};
    for (unsigned i=0;i<3;++i) {
        char name[256];strcpy(name,files[i]);
        CParticle particle;
        BOOL loaded=particle.LoadParticleSPT(name);
        RCHECK(loaded==(i!=2));
        RCHECK(particle.mNum==expected[i]);
        RCHECK(particle.mEntity==NULL && particle.mElement==NULL);
        RCHECK(!strcmp(name,i==0?"resources\\first.spt":i==1?"resources\\upper.spt":"resources\\invalid.spt"));
    }
    RCHECK(resourceWarnings==1);
#if defined(RF_CLIENT_455_WEATHER)
    char material[]="RESOURCES\\WEATHER.R3X";
    LoadR3X(material);
    RCHECK(!strcmp(material,"resources\\weather.r3x"));
    RCHECK(GetR3State()->mEnvIDs[0]==1 && GetR3State()->mEnvIDs[1]==2);
    RCHECK(!strcmp(GetR3State()->mEnvEntityNames[0],"FirstCase.SPT"));
    RCHECK(!strcmp(GetR3State()->mEnvEntityNames[1],"SecondCase.SPT"));
    RCHECK(GetR3State()->mEnvironmentSceneFlags==123);
#endif
    char missing[]="RESOURCES\\MISSING.SPT";
    RCHECK(RF455_ResourceExists(missing)==FALSE && !strcmp(missing,"resources\\missing.spt"));
    RF455_SetResourceGroup(NULL);owner.Release();owner.Release();
    RCHECK(GetDmallocSize()==before);
    SetWarningMessageProc(NULL);
    for (unsigned i=0;i<4;++i) RCHECK(GetModuleHandleA(dlls[i])==NULL);
    FILE* fp=fopen(output,"wb");if (!fp) return 72;
    fprintf(fp,"{\"checks\":%u,\"failures\":%u,\"warnings\":%u,\"allocation_before\":%d,\"allocation_after\":%d}\n",checks,failed,resourceWarnings,before,GetDmallocSize());
    fclose(fp);
#undef RCHECK
    return failed?73:0;
}
