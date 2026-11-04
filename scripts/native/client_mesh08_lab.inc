#include "client455_mesh08.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <limits>
namespace Mesh08Probe {
#define RF455_MESH08_EMBEDDED
#include "test_client455_mesh08.cpp"
#undef RF455_MESH08_EMBEDDED
}
static int mesh08ScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* golden=std::getenv("RF_MESH08_GOLDEN");if(!output || !golden)return 119;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 120;
    FILE* file=std::fopen(output,"wt");if(!file)return 121;
    const DWORD before=GetDmallocSize();const int result=Mesh08Probe::runMesh08Checks(golden,file);
    if(std::fclose(file))return 122;if(GetDmallocSize()!=before)return 123;
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 124;
    return result;
}
