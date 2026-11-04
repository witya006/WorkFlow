extern "C" int RF455_RunLegacyRuntimeChecks(const char*,const char*,const char*,const char*,const char*,int);
static int legacyRuntimeScenarioProbe(){
    const char* workspace=std::getenv("RF_LEGACY_WORKSPACE");const char* golden=std::getenv("RF_LEGACY_GOLDEN");const char* pairs=std::getenv("RF_LEGACY_PAIRS");const char* dll=std::getenv("RF_LEGACY_DLL");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!workspace || !golden || !pairs || !dll || !output)return 181;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 182;
    const DWORD before=GetDmallocSize();const int result=RF455_RunLegacyRuntimeChecks(workspace,golden,pairs,dll,output,1);
    if(GetDmallocSize()!=before)return 183;for(const auto* name:names)if(GetModuleHandleA(name))return 184;return result;
}
