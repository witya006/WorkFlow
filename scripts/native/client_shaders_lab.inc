extern "C" int RF455_RunShaderChecks(const char*,const char*);
static int shadersScenarioProbe(){
    const char* dll=std::getenv("RF_SHADER_DLL");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!dll || !output)return 236;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 237;
    const DWORD before=GetDmallocSize();const int result=RF455_RunShaderChecks(dll,output);
    if(GetDmallocSize()!=before)return 238;for(const auto* name:names)if(GetModuleHandleA(name))return 239;return result;
}
