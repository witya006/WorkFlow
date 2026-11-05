extern "C" int RF455_RunDrawChecks(const char*,const char*,const char*);
static int drawScenarioProbe(){
    const char* dll=std::getenv("RF_SHADER_DLL");const char* fixture=std::getenv("RF_DRAW_FIXTURE");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!dll || !fixture || !output)return 240;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 241;
    const DWORD before=GetDmallocSize();const int result=RF455_RunDrawChecks(dll,fixture,output);
    if(GetDmallocSize()!=before)return 242;for(const auto* name:names)if(GetModuleHandleA(name))return 243;return result;
}
