extern "C" int RF455_RunPoseChecks(const char*,const char*,const char*,const char*);
extern "C" int RF455_RunSecondaryChecks(const char*,const char*,const char*,const char*);
static int poseScenarioProbe(bool secondary=false){
    const char* workspace=std::getenv("RF_POSE_WORKSPACE");const char* golden=std::getenv(secondary?"RF_SECONDARY_GOLDEN":"RF_POSE_GOLDEN");const char* dll=std::getenv("RF_POSE_DLL");const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");if(!workspace || !golden || !dll || !output)return 201;
    const char* names[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};for(const auto* name:names)if(GetModuleHandleA(name))return 202;
    const DWORD before=GetDmallocSize();const int result=secondary?RF455_RunSecondaryChecks(workspace,golden,dll,output):RF455_RunPoseChecks(workspace,golden,dll,output);
    if(GetDmallocSize()!=before)return 203;for(const auto* name:names)if(GetModuleHandleA(name))return 204;return result;
}
