// D3D9 headers stay in the separate texture test translation unit.
extern "C" int RF455_RunCharacterTextureChecks(const char*,const char*,const char*,int);
static int textureScenarioProbe(){
    const char* output=std::getenv("RF_LAB_HELPER_OUTPUT");const char* dll=std::getenv("RF_TEXTURE_DLL");const char* frame=std::getenv("RF_TEXTURE_FRAME");if(!output || !dll || !frame)return 141;
    const char* dlls[]={"mss32.dll","ABuse.dll","Adv.dll","PDLL.dll"};
    for(const auto* name:dlls)if(GetModuleHandleA(name))return 142;
    const DWORD before=GetDmallocSize();const int result=RF455_RunCharacterTextureChecks(dll,output,frame,1);
    if(GetDmallocSize()!=before)return 143;
    for(const auto* name:dlls)if(GetModuleHandleA(name))return 144;
    return result;
}
