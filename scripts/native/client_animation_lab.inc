extern "C" int RF455_RunAnimationChecks(const char*,const char*,const char*,const char*,const char*,int);
static int animationScenarioProbe(){
    const char* workspace=std::getenv("RF_ANI_WORKSPACE");const char* golden=std::getenv("RF_ANI_GOLDEN");const char* pairs=std::getenv("RF_ANI_PAIRS");const char* dll=std::getenv("RF_ANI_DLL");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!workspace || !golden || !pairs || !dll || !output)return 191;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 192;
    const DWORD before=GetDmallocSize();const int result=RF455_RunAnimationChecks(workspace,golden,pairs,dll,output,1);
    if(GetDmallocSize()!=before)return 193;for(const auto* name:names)if(GetModuleHandleA(name))return 194;return result;
}
