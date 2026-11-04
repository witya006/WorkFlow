#include "client455_mesh_bindings.h"
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
namespace MeshBindingsProbe {
#define RF455_MESH_BINDINGS_EMBEDDED
#include "test_client455_mesh_bindings.cpp"
#undef RF455_MESH_BINDINGS_EMBEDDED
}
static int meshBindingsScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* golden=std::getenv("RF_MESH_BINDING_GOLDEN");const char* workspace=std::getenv("RF_MESH_BINDING_WS");if(!output || !golden || !workspace)return 125;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 126;
    FILE* file=std::fopen(output,"wt");if(!file)return 127;
    const DWORD before=GetDmallocSize();const int result=MeshBindingsProbe::runMeshBindingChecks(golden,workspace,file);
    if(std::fclose(file))return 128;if(GetDmallocSize()!=before)return 129;
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 130;
    return result;
}
