#include <cstdlib>
extern "C" int RF455_RunAnimationManagerChecks(const char*,unsigned,unsigned);
static int animationManagerScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* bytes=std::getenv("RF_AM_BYTES");const char* maximum=std::getenv("RF_AM_MAXIMUM");
    if(!output || !bytes || !maximum)return 232;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:dlls)if(GetModuleHandleA(name))return 233;
    const DWORD before=GetDmallocSize();const int result=RF455_RunAnimationManagerChecks(output,static_cast<unsigned>(std::strtoul(bytes,nullptr,10)),static_cast<unsigned>(std::strtoul(maximum,nullptr,10)));
    if(GetDmallocSize()!=before)return 234;for(const auto* name:dlls)if(GetModuleHandleA(name))return 235;return result;
}
