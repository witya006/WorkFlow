// D3D9 interfaces are isolated in their own test TU,away from old D3D8 headers.
extern "C" int RF455_RunSharedBufferChecks(const char*,const char*,const char*,int);
static int sharedBufferScenarioProbe(){
    const char* workspace=std::getenv("RF_BUFFER_WORKSPACE");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* frames=std::getenv("RF_BUFFER_FRAMES");if(!workspace || !output || !frames)return 151;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:dlls)if(GetModuleHandleA(name))return 152;
    const DWORD before=GetDmallocSize();const int result=RF455_RunSharedBufferChecks(workspace,output,frames,1);
    if(GetDmallocSize()!=before)return 153;for(const auto* name:dlls)if(GetModuleHandleA(name))return 154;return result;
}
