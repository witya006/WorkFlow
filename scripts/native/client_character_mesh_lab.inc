#include "Character.h"
namespace CharacterMeshProbe {
#define RF_CHARACTER_MESH_EMBEDDED
#include "test_character_mesh_bindings.cpp"
#undef RF_CHARACTER_MESH_EMBEDDED
}
static int characterMeshScenarioProbe() {
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if (!output) return 107;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for(unsigned i=0;i<4;++i) if(GetModuleHandleA(dlls[i])) return 108;
    FILE* file=std::fopen(output,"wt");if(!file)return 109;
    const DWORD before=GetDmallocSize();
    const int result=CharacterMeshProbe::runCharacterMeshChecks(file);
    if(std::fclose(file))return 110;
    if(GetDmallocSize()!=before)return 111;
    for(unsigned i=0;i<4;++i) if(GetModuleHandleA(dlls[i])) return 112;
    return result;
}
