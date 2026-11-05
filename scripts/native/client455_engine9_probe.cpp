#include <windows.h>
#include <cstdio>
#include <cstring>
#include <string>
#include "r3math.h"
#include "jmalloc.h"
#include "client455_renderer_owner.h"
extern RF455R3VertexProgram stGrassVertexShader;

static bool checkEnginePrograms(){
    const bool ready=stGrassVertexShader.shader && stGrassVertexShader.declaration;
    FILE* file=std::fopen("engine-shaders.json","wb");if(file){std::fprintf(file,"{\"grass_program_created\":%s}\n",ready?"true":"false");std::fclose(file);}return ready;
}

static int connectCharacterOwner(IDirect3DDevice9* device){
    char directory[MAX_PATH];if(!GetSystemDirectoryA(directory,MAX_PATH))return 1;
    HMODULE runtime=LoadLibraryA((std::string(directory)+"\\d3dx9_36.dll").c_str());if(!runtime)return 2;
    RF455ShaderApi api={reinterpret_cast<decltype(api.compile)>(GetProcAddress(runtime,"D3DXCompileShader")),reinterpret_cast<decltype(api.sprite)>(GetProcAddress(runtime,"D3DXCreateSprite"))};
    RF455CharacterRenderer owner;RF455_ConstructCharacterRenderer(&owner);RF455RendererShared shared={};RF455_ConstructShaderManager(&shared.shaders);
    int result=RF455_SetCharacterRendererDevice(&owner,&shared,device,&api,nullptr);const bool valid=result==11 && shared.shaders.count==12 && owner.device==device && owner.vertices64.device==device && owner.textures.device==device && owner.sprite;
    const auto memory=RF455_CrtMeshMemoryOps();RF455_DestroyCharacterRenderer(&owner,&memory);RF455_ReleaseShaderManager(&shared.shaders);RF455_ReleaseCharacterDeclarations(&shared.declaration64,&shared.declaration36);FreeLibrary(runtime);return valid?0:3;
}
#include "client_graphics_lab.inc"
static LONG engineException(EXCEPTION_POINTERS* info){
    FILE* file=std::fopen("exception.json","wb");if(file){
        MEMORY_BASIC_INFORMATION region={};VirtualQuery(info->ExceptionRecord->ExceptionAddress,&region,sizeof(region));char module[MAX_PATH]={};GetModuleFileNameA(static_cast<HMODULE>(region.AllocationBase),module,MAX_PATH);
        CONTEXT* c=info->ContextRecord;std::fprintf(file,"{\"code\":%lu,\"address\":%lu,\"image_base\":%lu,\"eip\":%lu,\"esp\":%lu,\"ebp\":%lu,\"access\":%lu,\"target\":%lu,\"stack\":[",info->ExceptionRecord->ExceptionCode,reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress),reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)),c->Eip,c->Esp,c->Ebp,static_cast<DWORD>(info->ExceptionRecord->ExceptionInformation[0]),static_cast<DWORD>(info->ExceptionRecord->ExceptionInformation[1]));
        __try {for(unsigned i=0;i<24;++i)std::fprintf(file,"%s%lu",i?",":"",reinterpret_cast<const DWORD*>(c->Esp)[i]);} __except(EXCEPTION_EXECUTE_HANDLER){}
        std::fprintf(file,"]}\n");std::fclose(file);FILE* name=std::fopen("exception-module.txt","wb");if(name){std::fputs(module,name);std::fclose(name);}
    }return EXCEPTION_EXECUTE_HANDLER;
}
int WINAPI WinMain(HINSTANCE,HINSTANCE,LPSTR command,int){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    __try {return graphicsProbe(!std::strcmp(command,"--level")?3u:0u);}
    __except(engineException(GetExceptionInformation())){return 99;}
}
