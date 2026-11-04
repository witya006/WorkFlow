#include "Character.h"
#include "character_mesh_format.h"
namespace CharacterInitProbe {
#define RF_CHARACTER_INIT_EMBEDDED
#include "test_character_mesh_init.cpp"
#undef RF_CHARACTER_INIT_EMBEDDED
}
static int characterInitScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!output)return 113;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 114;
    FILE* file=std::fopen(output,"wt");if(!file)return 115;
    const DWORD before=GetDmallocSize();const int result=CharacterInitProbe::runCharacterInitChecks(file);
    if(std::fclose(file))return 116;if(GetDmallocSize()!=before)return 117;
    for(unsigned i=0;i<4;++i)if(GetModuleHandleA(dlls[i]))return 118;
    return result;
}
