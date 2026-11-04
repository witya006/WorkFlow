// Diagnostic entry linked into the complete client, never the normal game entry.
// The legacy WinMain is retained under RFOriginalWinMain by the lab-only macro.
#undef WinMain
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <cmath>
#include <cstddef>
#include "r3math.h"
#include "extdummy.h"
#include "jmalloc.h"
#include "core.h"

static_assert(sizeof(_EXT_DUMMY)==208,"Helper record ABI changed");
static_assert(sizeof(CExtDummy)==12,"Helper owner ABI changed");
static_assert(offsetof(_EXT_DUMMY,mFlag)==32,"flags");
static_assert(offsetof(_EXT_DUMMY,mBBmin)==36,"min");
static_assert(offsetof(_EXT_DUMMY,mBBmax)==48,"max");
static_assert(offsetof(_EXT_DUMMY,mID)==60,"id");
static_assert(offsetof(_EXT_DUMMY,mdwArgv)==64,"arguments");
static_assert(offsetof(_EXT_DUMMY,mMat)==80,"matrix");
static_assert(offsetof(_EXT_DUMMY,mInvMat)==144,"inverse");

struct Header {
    char magic[8];
    DWORD version,loaded,count,recordBytes,useBytes,checks,failures;
    DWORD missingCalled,countAfterMissing,clampMatches,memBefore,memAfter;
    DWORD fpBefore,fpAfter;
};
struct Use {
    float world[3],local[3];
    BOOL inside,outside,worldOk,localOk;
};
static_assert(sizeof(Header)==64 && sizeof(Use)==40,"Lab wire layout");

static unsigned short fpControl() {
    unsigned short value;
    __asm { fnstcw value }
    return value;
}

static void check(Header& header,bool ok) {
    ++header.checks;
    if (!ok) ++header.failures;
}

static unsigned probe() {
    char input[32768],output[32768],missing[32768];
    DWORD a=GetEnvironmentVariableA("RF_LAB_HELPER_INPUT",input,sizeof(input));
    DWORD b=GetEnvironmentVariableA("RF_LAB_HELPER_OUTPUT",output,sizeof(output));
    if (!a || a>=sizeof(input) || !b || b>=sizeof(output)) return 21;
    DWORD n=GetEnvironmentVariableA("RF_LAB_HELPER_MISSING",missing,sizeof(missing));
    if (n>=sizeof(missing)) return 22;
    Header header={ {'R','F','H','L','P','4','5','5'},2,0,0,208,40,0,0,0,0,0,0,0,0,0 };
    header.fpBefore=fpControl();
    const char* delayed[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) check(header,GetModuleHandleA(delayed[i])==NULL);
    CExtDummy owner;
    header.memBefore=GetDmallocSize();
    // Explicit, nondefault state to test the loader's fog-default reads.
    GetR3State()->mFogStart=123.5f;
    GetR3State()->mFogEnd=987.25f;
    header.loaded=owner.LoadExtDummy(input);
    header.count=owner.GetTotalNum();
    if (header.count>1000000) { owner.ReleaseExtDummy(); return 23; }
    FILE* fp=std::fopen(output,"wb");
    if (!fp) { owner.ReleaseExtDummy(); return 24; }
    bool io=std::fwrite(&header,sizeof(header),1,fp)==1;
    header.clampMatches=owner.GetDummy(0xffffffffu)==(header.count?owner.GetDummy(header.count-1):NULL);
    check(header,header.clampMatches!=0);
    Vector3f point={1.0f,2.0f,3.0f},sentinel={91.0f,92.0f,93.0f};
    check(header,owner.GetWorldFromLocal(&sentinel,header.count,point)==FALSE && sentinel[0]==91.0f);
    check(header,owner.GetLocalFromWorld(&sentinel,header.count,point)==FALSE && sentinel[0]==91.0f);
    check(header,owner.IsInBBox(header.count,point)==FALSE);
    for (DWORD i=0;i<header.count;++i) {
        _EXT_DUMMY* item=owner.GetDummy(i);
        Use use={};
        Vector3f center,outside,worldOutside;
        for (unsigned j=0;j<3;++j) {
            center[j]=(item->mBBmin[j]+item->mBBmax[j])*0.5f
                +(item->mBBmax[j]-item->mBBmin[j])*0.125f;
            outside[j]=item->mBBmax[j]+(float)std::fabs(item->mBBmax[j]-item->mBBmin[j])+1.0f;
        }
        use.worldOk=owner.GetWorldFromLocal(&use.world,i,center);
        use.localOk=owner.GetLocalFromWorld(&use.local,i,use.world);
        use.inside=owner.IsInBBox(i,use.world);
        owner.GetWorldFromLocal(&worldOutside,i,outside);
        use.outside=owner.IsInBBox(i,worldOutside);
        check(header,use.worldOk && use.localOk);
        io=io && std::fwrite(item,sizeof(*item),1,fp)==1 && std::fwrite(&use,sizeof(use),1,fp)==1;
    }
    DWORD* indices=new DWORD[header.count?header.count:1];
    for (DWORD mask=1;mask<=7;++mask) {
        DWORD count=0,expected=0;
        owner.GetDummyList(mask,&count,indices);
        for (DWORD i=0;i<header.count;++i) {
            if (owner.GetDummy(i)->mFlag & mask) {
                check(header,expected<count && indices[expected]==i);
                ++expected;
            }
        }
        check(header,count==expected);
    }
    delete[] indices;
    if (n) {
        header.missingCalled=1;
        check(header,owner.LoadExtDummy(missing)==FALSE);
        header.countAfterMissing=owner.GetTotalNum();
        check(header,header.countAfterMissing==0 && owner.GetDummy(0)==NULL);
    }
    owner.ReleaseExtDummy();
    header.memAfter=GetDmallocSize();
    header.fpAfter=fpControl();
    check(header,header.fpBefore==header.fpAfter);
    check(header,header.memBefore==header.memAfter && owner.GetTotalNum()==0 && owner.GetDummy(0)==NULL);
    for (unsigned i=0;i<4;++i) check(header,GetModuleHandleA(delayed[i])==NULL);
    io=io && std::fseek(fp,0,SEEK_SET)==0 && std::fwrite(&header,sizeof(header),1,fp)==1;
    io=std::fclose(fp)==0 && io;
    return io?(header.failures?26:0):25;
}

#if defined(RF_CLIENT_455_WEATHER)
#include "client_weather_lab.inc"
#endif
#if defined(RF_CLIENT_455_RESOURCE_IO)
#include "client_resource_lab.inc"
#include "client_graphics_lab.inc"
#endif

#if defined(RF_CLIENT_455_CLOCK)
#include "client455_clock.h"
namespace ClockProbe {
#define RF455_CLOCK_EMBEDDED
#include "test_client455_clock.cpp"
#undef RF455_CLOCK_EMBEDDED
}
static int clockScenarioProbe() {
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");
    if (!output) return 90;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) if (GetModuleHandleA(dlls[i])) return 91;
    FILE* file=std::fopen(output,"wt");if (!file) return 92;
    const int result=ClockProbe::runClockChecks(file);
    if (std::fclose(file)) return 93;
    for (unsigned i=0;i<4;++i) if (GetModuleHandleA(dlls[i])) return 94;
    return result;
}
#endif

#if defined(RF_CLIENT_455_MAP_TIME)
#include "client455_map_time.h"
namespace MapTimeProbe {
#define RF455_MAP_TIME_EMBEDDED
#include "test_client455_map_time.cpp"
#undef RF455_MAP_TIME_EMBEDDED
}
static int mapTimeScenarioProbe() {
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if (!output) return 95;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for (unsigned i=0;i<4;++i) if (GetModuleHandleA(dlls[i])) return 96;
    FILE* file=std::fopen(output,"wt");if (!file) return 97;
    const int result=MapTimeProbe::runMapTimeChecks(file);
    if (std::fclose(file)) return 98;
    for (unsigned i=0;i<4;++i) if (GetModuleHandleA(dlls[i])) return 99;
    return result;
}
#endif

#if defined(RF_CLIENT_455_TIME_COMMANDS)
#include "client_time_commands_lab.inc"
#endif

#if defined(RF_CHARACTER_MESH_SOURCE)
#include "client_character_mesh_lab.inc"
#include "client_character_init_lab.inc"
#endif

#if defined(RF_CLIENT_455_MESH08)
#include "client_mesh08_lab.inc"
#endif
#if defined(RF_CLIENT_455_MESH_BINDINGS)
#include "client_mesh_bindings_lab.inc"
#endif
#if defined(RF_CLIENT_455_MESH_RUNTIME)
#include "client_mesh_runtime_lab.inc"
#endif

#if defined(RF_CLIENT_455_TEXTURE)
#include "client_texture_lab.inc"
#endif
#if defined(RF_CLIENT_455_SHARED_BUFFERS)
#include "client_shared_buffers_lab.inc"
#endif
int WINAPI WinMain(HINSTANCE,HINSTANCE,LPSTR command,int) {
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
#if defined(RF_CLIENT_455_SHARED_BUFFERS)
    if (!std::strcmp(command,"--rf-shared-buffers-scenario")) ExitProcess(sharedBufferScenarioProbe());
#endif
#if defined(RF_CLIENT_455_TEXTURE)
    if (!std::strcmp(command,"--rf-texture-scenario")) ExitProcess(textureScenarioProbe());
#endif
#if defined(RF_CLIENT_455_MESH_RUNTIME)
    if (!std::strcmp(command,"--rf-mesh-runtime-scenario")) ExitProcess(meshRuntimeScenarioProbe());
#endif
#if defined(RF_CLIENT_455_MESH_BINDINGS)
    if (!std::strcmp(command,"--rf-mesh-binding-scenario")) ExitProcess(meshBindingsScenarioProbe());
#endif
#if defined(RF_CLIENT_455_MESH08)
    if (!std::strcmp(command,"--rf-mesh08-scenario")) ExitProcess(mesh08ScenarioProbe());
#endif
#if defined(RF_CHARACTER_MESH_SOURCE)
    if (!std::strcmp(command,"--rf-character-mesh-scenario")) ExitProcess(characterMeshScenarioProbe());
    if (!std::strcmp(command,"--rf-character-init-scenario")) ExitProcess(characterInitScenarioProbe());
#endif
#if defined(RF_CLIENT_455_TIME_COMMANDS)
    if (!std::strcmp(command,"--rf-time-commands-scenario")) ExitProcess(timeCommandsScenarioProbe());
#endif
#if defined(RF_CLIENT_455_CLOCK)
    if (!std::strcmp(command,"--rf-clock-scenario")) ExitProcess(clockScenarioProbe());
#endif
#if defined(RF_CLIENT_455_MAP_TIME)
    if (!std::strcmp(command,"--rf-map-time-scenario")) ExitProcess(mapTimeScenarioProbe());
#endif
#if defined(RF_CLIENT_455_RESOURCE_IO)
    if (!std::strcmp(command,"--rf-resource-scenario")) ExitProcess(resourceScenarioProbe());
    if (!std::strcmp(command,"--rf-graphics-device")) ExitProcess(graphicsProbe(0));
    if (!std::strcmp(command,"--rf-graphics-entity")) ExitProcess(graphicsProbe(1));
    if (!std::strcmp(command,"--rf-graphics-particle")) ExitProcess(graphicsProbe(2));
    if (!std::strcmp(command,"--rf-graphics-level")) ExitProcess(graphicsProbe(3));
#endif
#if defined(RF_CLIENT_455_WEATHER)
    if (!std::strcmp(command,"--rf-weather-read")) ExitProcess(weatherReadProbe());
    if (!std::strcmp(command,"--rf-weather-scenario")) ExitProcess(weatherScenarioProbe());
#endif
    if (std::strcmp(command,"--rf-helper-probe")) ExitProcess(20);
    unsigned result=probe();
    // All probe-owned resources are released. Normal game teardown requires
    // normal game initialization, which this explicit laboratory entry skips.
    ExitProcess(result);
}
