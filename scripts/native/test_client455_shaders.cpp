#include "client455_shaders.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>

namespace {
unsigned checks=0;
#define SH_CHECK(value) do{++checks;if(!(value)){std::fprintf(stderr,"Shader check%u line%d\n",checks,__LINE__);return 1;}}while(0)
RF455ShaderApi realApi;
struct Call {std::string source,profile;DWORD flags;std::vector<unsigned char> code;};
std::vector<Call> calls;
HRESULT WINAPI compile(LPCSTR source,UINT size,const void* defines,void* includes,LPCSTR entry,LPCSTR profile,DWORD flags,RF455D3DXBuffer** code,RF455D3DXBuffer** errors,IUnknown** constants){
    calls.push_back({std::string(source,size),profile,flags,{}});
    const HRESULT hr=realApi.compile(source,size,defines,includes,entry,profile,flags,code,errors,constants);
    if(*code){const auto* bytes=static_cast<const unsigned char*>((*code)->GetBufferPointer());calls.back().code.assign(bytes,bytes+(*code)->GetBufferSize());}
    return hr;
}
bool save(const char* path,const void* bytes,std::size_t size){FILE* f=std::fopen(path,"wb");if(!f)return false;const bool ok=std::fwrite(bytes,1,size,f)==size;return !std::fclose(f) && ok;}
struct Vertex {float position[3],weights[3];short indices[4];float normal[3],uv[2],tangent[3];};
static_assert(sizeof(Vertex)==64,"Actual shader stream");
int run(const char* dll,const char* output){
    HMODULE d3dx=LoadLibraryA(dll);SH_CHECK(d3dx);
    realApi.compile=reinterpret_cast<decltype(realApi.compile)>(GetProcAddress(d3dx,"D3DXCompileShader"));realApi.sprite=reinterpret_cast<decltype(realApi.sprite)>(GetProcAddress(d3dx,"D3DXCreateSprite"));SH_CHECK(realApi.compile && realApi.sprite);
    RF455ShaderApi api={compile,realApi.sprite};char system[MAX_PATH];SH_CHECK(GetSystemDirectoryA(system,MAX_PATH));const std::string d3dPath=std::string(system)+"\\d3d9.dll";HMODULE library=LoadLibraryA(d3dPath.c_str());SH_CHECK(library);
    auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(library,"Direct3DCreate9"));SH_CHECK(create);IDirect3D9* d3d=create(D3D_SDK_VERSION);SH_CHECK(d3d);
    HWND window=CreateWindowExA(0,"STATIC","RF455 own shader probe",WS_OVERLAPPEDWINDOW,0,0,64,64,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);SH_CHECK(window);
    D3DPRESENT_PARAMETERS present={};present.Windowed=TRUE;present.hDeviceWindow=window;present.BackBufferWidth=present.BackBufferHeight=64;present.BackBufferFormat=D3DFMT_X8R8G8B8;present.SwapEffect=D3DSWAPEFFECT_DISCARD;
    IDirect3DDevice9* device=nullptr;SH_CHECK(SUCCEEDED(d3d->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&present,&device)));
    RF455ShaderManager manager;RF455_ConstructShaderManager(&manager);manager.device=device;IUnknown* sprite=nullptr;IDirect3DVertexDeclaration9* declaration64=nullptr;IDirect3DVertexDeclaration9* declaration36=nullptr;
    SH_CHECK(RF455_InitializeCharacterShaders(&manager,&api,&sprite,&declaration64,&declaration36)==11);
    SH_CHECK(sprite && declaration64 && declaration36 && manager.count==12 && manager.capacity==16 && calls.size()==15);
    unsigned vertexPrograms=0,pixelPrograms=0,callIndex=0;
    for(unsigned i=0;i<manager.count;++i){auto& p=manager.programs[i];SH_CHECK(p.vertex && p.vertexConstants);++vertexPrograms;
        UINT size=0;SH_CHECK(SUCCEEDED(p.vertex->GetFunction(nullptr,&size)));std::vector<unsigned char> code(size);SH_CHECK(SUCCEEDED(p.vertex->GetFunction(code.data(),&size)));
        SH_CHECK(callIndex<calls.size() && calls[callIndex].profile=="vs_2_0" && calls[callIndex].flags==0x8008 && calls[callIndex].code==code);++callIndex;
        if(p.pixel){++pixelPrograms;SH_CHECK(p.pixelConstants);size=0;SH_CHECK(SUCCEEDED(p.pixel->GetFunction(nullptr,&size)));code.resize(size);SH_CHECK(SUCCEEDED(p.pixel->GetFunction(code.data(),&size)));SH_CHECK(callIndex<calls.size() && calls[callIndex].profile=="ps_3_0" && calls[callIndex].flags==0x8008 && calls[callIndex].code==code);++callIndex;}
        SH_CHECK(SUCCEEDED(device->SetVertexShader(p.vertex)) && SUCCEEDED(device->SetPixelShader(p.pixel)));
    }
    SH_CHECK(vertexPrograms==12 && pixelPrograms==3 && callIndex==15);
    for(unsigned i=0;i<15;++i){char filename[64];std::snprintf(filename,sizeof(filename),"compiled-source-%02u.hlsl",i);SH_CHECK(save(filename,calls[i].source.data(),calls[i].source.size()));}
    const D3DVERTEXELEMENT9 expectedLarge[]={{0,0,2,0,0,0},{0,12,2,0,1,0},{0,24,7,0,2,0},{0,32,2,0,3,0},{0,44,1,0,5,0},{0,52,2,0,6,0},{255,0,17,0,0,0}};
    const D3DVERTEXELEMENT9 expectedSmall[]={{0,0,2,0,0,0},{0,12,0,0,1,0},{0,16,2,0,3,0},{0,28,1,0,5,0},{255,0,17,0,0,0}};
    D3DVERTEXELEMENT9 actual[16];UINT elements=16;SH_CHECK(SUCCEEDED(declaration64->GetDeclaration(actual,&elements)) && elements==7 && !std::memcmp(actual,expectedLarge,sizeof(expectedLarge)));elements=16;SH_CHECK(SUCCEEDED(declaration36->GetDeclaration(actual,&elements)) && elements==5 && !std::memcmp(actual,expectedSmall,sizeof(expectedSmall)));
    // Harness draw: actual sh_basic/declaration64, not recovered full Character draw.
    const float identity[]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};const float green[]={0,1,0,1},white[]={1,1,1,1},zero[]={0,0,0,0},direction[]={0,0,-1,0};
    SH_CHECK(SUCCEEDED(device->SetVertexShader(manager.programs[0].vertex)) && SUCCEEDED(device->SetPixelShader(nullptr)) && SUCCEEDED(device->SetVertexDeclaration(declaration64)));
    SH_CHECK(SUCCEEDED(device->SetVertexShaderConstantF(2,identity,4)) && SUCCEEDED(device->SetVertexShaderConstantF(6,identity,4)) && SUCCEEDED(device->SetVertexShaderConstantF(100,identity,4)));
    SH_CHECK(SUCCEEDED(device->SetVertexShaderConstantF(10,direction,1)) && SUCCEEDED(device->SetVertexShaderConstantF(11,zero,1)) && SUCCEEDED(device->SetVertexShaderConstantF(12,green,1)) && SUCCEEDED(device->SetVertexShaderConstantF(18,white,1)) && SUCCEEDED(device->SetVertexShaderConstantF(19,white,1)));
    device->SetRenderState(D3DRS_LIGHTING,FALSE);device->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE);device->SetRenderState(D3DRS_ZENABLE,FALSE);device->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);device->SetTexture(0,nullptr);
    device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1);device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_DIFFUSE);device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG1);device->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_DIFFUSE);device->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);
    Vertex triangle[3]={};const float positions[3][3]={{-.8f,-.8f,.5f},{0,.8f,.5f},{.8f,-.8f,.5f}};for(unsigned i=0;i<3;++i){std::memcpy(triangle[i].position,positions[i],12);triangle[i].normal[2]=1;triangle[i].tangent[0]=1;}
    SH_CHECK(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff000000,1,0)) && SUCCEEDED(device->BeginScene()));SH_CHECK(SUCCEEDED(device->DrawPrimitiveUP(D3DPT_TRIANGLELIST,1,triangle,64)));SH_CHECK(SUCCEEDED(device->EndScene()));
    IDirect3DSurface9* back=nullptr;IDirect3DSurface9* cpu=nullptr;SH_CHECK(SUCCEEDED(device->GetRenderTarget(0,&back)) && SUCCEEDED(device->CreateOffscreenPlainSurface(64,64,D3DFMT_X8R8G8B8,D3DPOOL_SYSTEMMEM,&cpu,nullptr)) && SUCCEEDED(device->GetRenderTargetData(back,cpu)));
    D3DLOCKED_RECT locked={};SH_CHECK(SUCCEEDED(cpu->LockRect(&locked,nullptr,D3DLOCK_READONLY)));DWORD center=0,corner=0;std::memcpy(&center,static_cast<const unsigned char*>(locked.pBits)+32*locked.Pitch+32*4,4);std::memcpy(&corner,locked.pBits,4);SH_CHECK((center&0xffffff)!=0 && (corner&0xffffff)==0);
    std::vector<unsigned char> pixels(64*64*4);for(unsigned y=0;y<64;++y)std::memcpy(pixels.data()+y*64*4,static_cast<const unsigned char*>(locked.pBits)+y*locked.Pitch,64*4);cpu->UnlockRect();cpu->Release();back->Release();SH_CHECK(save("shader-frame.bgra",pixels.data(),pixels.size()));
    device->SetVertexShader(nullptr);device->SetPixelShader(nullptr);device->SetVertexDeclaration(nullptr);
    RF455_ReleaseShaderManager(&manager);SH_CHECK(!manager.programs && !manager.count && manager.device==device);
    RF455ShaderSources parsed;SH_CHECK(RF455_ReadShaderSources("fallback.shr",&parsed) && parsed.hasVertex && !parsed.hasPixel);SH_CHECK(RF455_ReadShaderSources("priority.shr",&parsed) && !parsed.hasVertex && !parsed.hasPixel);SH_CHECK(!RF455_ReadShaderSources("missing.shr",&parsed));
    SH_CHECK(RF455_LoadShaderProgram(&manager,&api,"fallback.shr",nullptr,nullptr)==0 && manager.count==1);
    SH_CHECK(RF455_LoadShaderProgram(&manager,&api,"priority.shr",nullptr,nullptr)==-1 && manager.count==1);RF455_ReleaseShaderManager(&manager);
    const char* valid="float4 main(float4 p:POSITION):POSITION{return p;}";RF455ShaderFailure failed;
    SH_CHECK(RF455_CreateShaderProgram(&manager,&api,valid,"INVALID HLSL",nullptr,&failed)==-1 && !manager.count && failed.orphan.vertex && !failed.orphan.pixel && !failed.code && !failed.errors && !failed.diagnostic.empty());
    unsigned orphans=0;for(IUnknown* resource:{static_cast<IUnknown*>(failed.orphan.vertex),static_cast<IUnknown*>(failed.orphan.pixel),failed.orphan.vertexConstants,failed.orphan.pixelConstants})if(resource){++orphans;resource->Release();} // Explicit test cleanup AFTER observing reference stranded ownership.
    RF455_ReleaseShaderManager(&manager);RF455_ReleaseCharacterDeclarations(&declaration64,&declaration36);sprite->Release();SH_CHECK(!declaration64 && !declaration36);
    const ULONG deviceRefs=device->Release(),apiRefs=d3d->Release();SH_CHECK(!deviceRefs && !apiRefs);DestroyWindow(window);FreeLibrary(library);FreeLibrary(d3dx);
    FILE* report=std::fopen(output,"wb");if(!report)return 2;std::fprintf(report,"{\"status\":\"PASS\",\"checks\":%u,\"programs\":12,\"vertex_shaders\":%u,\"pixel_shaders\":%u,\"declarations\":2,\"harness_draws\":1,\"center_rgb\":%u,\"orphan_resources_observed_and_harness_freed\":%u,\"device_refs_after_release\":%lu,\"api_refs_after_release\":%lu}\n",checks,vertexPrograms,pixelPrograms,static_cast<unsigned>(center&0xffffff),orphans,deviceRefs,apiRefs);std::fclose(report);return 0;
}
}
extern "C" int RF455_RunShaderChecks(const char* dll,const char* output){checks=0;calls.clear();return run(dll,output);}
#ifndef RF455_SHADERS_EMBEDDED
int main(int argc,char** argv){return argc==3?RF455_RunShaderChecks(argv[1],argv[2]):3;}
#endif
