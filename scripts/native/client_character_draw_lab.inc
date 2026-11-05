extern "C" int RF455_RunCharacterDrawChecks(const char*,const char*,const char*);
static int characterDrawScenarioProbe(){
    const char* dll=std::getenv("RF_SHADER_DLL");const char* fixture=std::getenv("RF_DRAW_FIXTURE");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!dll || !fixture || !output)return 244;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 245;
    const DWORD before=GetDmallocSize();const int result=RF455_RunCharacterDrawChecks(dll,fixture,output);
    if(GetDmallocSize()!=before)return 246;for(const auto* name:names)if(GetModuleHandleA(name))return 247;return result;
}
