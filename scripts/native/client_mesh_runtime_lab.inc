#include "client455_mesh_runtime.h"
#include <windows.h>
#include <cstdio>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
namespace MeshRuntimeProbe {
#define RF455_MESH_RUNTIME_EMBEDDED
#include "test_client455_mesh_runtime.cpp"
#undef RF455_MESH_RUNTIME_EMBEDDED
}
static int meshRuntimeScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* golden=std::getenv("RF_MESH_RUNTIME_GOLDEN");const char* workspace=std::getenv("RF_MESH_RUNTIME_WS");const char* dll=std::getenv("RF_MESH_RUNTIME_MATRIX_DLL");if(!output || !golden || !workspace || !dll)return 131;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 132;
    FILE* file=std::fopen(output,"wt");if(!file)return 133;
    const DWORD before=GetDmallocSize();const int result=MeshRuntimeProbe::runMeshRuntimeChecks(golden,workspace,dll,file);
    if(std::fclose(file))return 134;if(GetDmallocSize()!=before)return 135;
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 136;
    return result;
}
