// Actual model pipeline test stays in a separate D3D9 TU.
extern "C" int RF455_RunModelChecks(const char*,const char*,const char*,const char*,int);
static int modelScenarioProbe(){
    const char* workspace=std::getenv("RF_MODEL_WORKSPACE");const char* golden=std::getenv("RF_MODEL_GOLDEN");const char* dll=std::getenv("RF_MODEL_DLL");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!workspace || !golden || !dll || !output)return 161;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 162;
    const DWORD before=GetDmallocSize();const int result=RF455_RunModelChecks(workspace,golden,dll,output,1);
    if(GetDmallocSize()!=before)return 163;for(const auto* name:names)if(GetModuleHandleA(name))return 164;return result;
}
