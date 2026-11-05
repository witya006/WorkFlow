extern "C" int RF455_RunRendererOwnerChecks(const char*,const char*,const char*,const char*);
static int rendererOwnerScenarioProbe(){
    const char* golden=std::getenv("RF_OWNER_GOLDEN");const char* dll=std::getenv("RF_SHADER_DLL");const char* fixture=std::getenv("RF_DRAW_FIXTURE");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!golden || !dll || !fixture || !output)return 242;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 243;
    const DWORD balance=GetDmallocSize();const int result=RF455_RunRendererOwnerChecks(golden,dll,fixture,output);
    if(GetDmallocSize()!=balance)return 244;for(const auto* name:names)if(GetModuleHandleA(name))return 245;return result;
}
