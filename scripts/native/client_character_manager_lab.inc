// Kept separate from the test's D3D9 translation unit.
extern "C" int RF455_RunCharacterManagerChecks(const char*,const char*,const char*,const char*,const char*,int);
static int characterManagerScenarioProbe(){
    const char* workspace=std::getenv("RF_MODEL_WORKSPACE");const char* pair=std::getenv("RF_MODEL_GOLDEN");const char* ctor=std::getenv("RF_CHARACTER_CTOR_GOLDEN");const char* dll=std::getenv("RF_MODEL_DLL");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");
    if(!workspace || !pair || !ctor || !dll || !output)return 171;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 172;
    const DWORD before=GetDmallocSize();const int result=RF455_RunCharacterManagerChecks(workspace,pair,ctor,dll,output,1);
    if(GetDmallocSize()!=before)return 173;for(const auto* name:names)if(GetModuleHandleA(name))return 174;return result;
}
