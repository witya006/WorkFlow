#include "client455_enhanced_lighting.h"
#include "client455_character_draw.h"
#include "client455_model_lifecycle.h"
#include <wrl/client.h>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <cmath>

namespace {
using Microsoft::WRL::ComPtr;
using SaveSurface = HRESULT (WINAPI*)(LPCSTR,int,IDirect3DSurface9*,const PALETTEENTRY*,const RECT*);
void require(bool value,const char* why){if(!value)throw std::runtime_error(why);}
struct Vertex {float position[3],weights[3];short indices[4];float normal[3],uv[2],tangent[3];};
static_assert(sizeof(Vertex)==64,"production actor stream");
RF455ShaderApi realApi{};
unsigned compileCount=0,failCompile=0;
HRESULT WINAPI controlledCompile(LPCSTR code,UINT size,const void* macros,void* includes,LPCSTR entry,
    LPCSTR profile,DWORD flags,RF455D3DXBuffer** bytecode,RF455D3DXBuffer** errors,IUnknown** constants){
    if(++compileCount==failCompile){if(bytecode)*bytecode=nullptr;if(errors)*errors=nullptr;if(constants)*constants=nullptr;return E_FAIL;}
    return realApi.compile(code,size,macros,includes,entry,profile,flags,bytecode,errors,constants);
}
ComPtr<IDirect3DTexture9> texture(IDirect3DDevice9* device,DWORD colour){
    ComPtr<IDirect3DTexture9> result;
    require(SUCCEEDED(device->CreateTexture(1,1,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&result,nullptr)),"texture");
    D3DLOCKED_RECT lock{};require(SUCCEEDED(result->LockRect(0,&lock,nullptr,0)),"lock texture");
    *static_cast<DWORD*>(lock.pBits)=colour;result->UnlockRect(0);return result;
}
std::vector<DWORD> pixels(IDirect3DDevice9* device,SaveSurface save,const char* filename){
    ComPtr<IDirect3DSurface9> target,memory;
    require(SUCCEEDED(device->GetRenderTarget(0,&target)),"render target");
    D3DSURFACE_DESC desc{};target->GetDesc(&desc);
    require(desc.Width==1920&&desc.Height==1080,"actual Full HD surface");
    if(filename)require(SUCCEEDED(save(filename,3,target.Get(),nullptr,nullptr)),"PNG frame");
    require(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr))&&
        SUCCEEDED(device->GetRenderTargetData(target.Get(),memory.Get())),"readback");
    D3DLOCKED_RECT lock{};require(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"readback lock");
    std::vector<DWORD> out(desc.Width*desc.Height);
    for(unsigned y=0;y<desc.Height;++y)std::memcpy(out.data()+y*desc.Width,
        static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch,desc.Width*4);
    memory->UnlockRect();return out;
}
unsigned centreRed(const std::vector<DWORD>& data){return (data[540*1920+960]>>16)&255;}
template<class T> void put(void* data,unsigned offset,T value){std::memcpy(static_cast<BYTE*>(data)+offset,&value,sizeof(value));}
unsigned WINAPI fixedTicks(){return 7000;}
void __cdecl sineFloat(float* out,const float* value){*out=static_cast<float>(std::sin(*value));}
void __cdecl cosineFloat(float* out,const float* value){*out=static_cast<float>(std::cos(*value));}
struct DrawObservation {
    IDirect3DDevice9* device;
    RF455ShaderManager* shaders;
    std::vector<unsigned> selected;
    std::vector<bool> bound;
    static void __cdecl observe(void* user,const RF455MeshStorage*,unsigned index){
        auto& self=*static_cast<DrawObservation*>(user);self.selected.push_back(index);
        ComPtr<IDirect3DVertexShader9> vertex;ComPtr<IDirect3DPixelShader9> pixel;
        self.device->GetVertexShader(&vertex);self.device->GetPixelShader(&pixel);
        self.bound.push_back(index<self.shaders->count&&vertex.Get()==self.shaders->programs[index].vertex&&
                             pixel.Get()==self.shaders->programs[index].pixel);
    }
};
unsigned productionRoutes(IDirect3DDevice9* device,RF455ShaderManager& shaders,HMODULE d3dx,
    IDirect3DVertexDeclaration9* d36,IDirect3DVertexDeclaration9* d64,
    const Vertex* vertices,const float* material,const float* identity,SaveSurface save){
    RF455VertexBufferPool v36{},v64{};RF455IndexBufferPool indices{};
    RF455_ConstructVertexPool(&v36);RF455_ConstructVertexPool(&v64);RF455_ConstructIndexPool(&indices);
    v36.device=v64.device=indices.device=device;
    RF455BufferAccounting buffers{};unsigned vertex=0;
    Vertex curved[6];std::memcpy(curved,vertices,sizeof(curved));
    for(auto& v:curved){v.normal[0]=v.position[0]<0?-.6f:.6f;v.normal[2]=-.8f;}
    require(RF455_UploadVertices64(&v64,curved,sizeof(curved),&vertex,&buffers)!=0,"actual shared vertex upload");
    RF455MeshAccounting accounting{};RF455MeshStorage meshes[2];auto& mesh=meshes[0];RF455_ConstructMeshStorage(&mesh,&accounting);
    put(mesh.bytes,5455,mesh.bytes+5163);put<unsigned>(mesh.bytes,5086,6);
    put(mesh.bytes,4494,vertex);put<unsigned>(mesh.bytes,4502,0xffffffffu);
    put<unsigned>(mesh.bytes,5143,1);put<unsigned>(mesh.bytes,5359,1);
    std::memcpy(mesh.bytes+4830,identity,64);
    auto albedo=texture(device,0xff808080),normalMap=texture(device,0xff8080ff),specularMap=texture(device,0xffffffff);
    put(mesh.bytes,5107,static_cast<IDirect3DBaseTexture9*>(albedo.Get()));
    RF455CharacterStorage model;RF455_ConstructCharacter(&model);
    put(model.prefix.bytes,532,1u);put(model.prefix.bytes,536,&mesh);
    std::memcpy(model.prefix.bytes+720,material,68);
    float light[26]{};light[18]=1;float projection[16];std::memcpy(projection,identity,64);
    RF455CharacterDrawContext context{};context.shaders=&shaders;context.state={device,4,d36,d64,light,0};
    context.vertices36=&v36;context.vertices64=&v64;context.indices=&indices;context.projection=projection;context.view=identity;
    context.math.matrix.multiply=reinterpret_cast<decltype(context.math.matrix.multiply)>(GetProcAddress(d3dx,"D3DXMatrixMultiply"));
    context.math.matrix.inverse=reinterpret_cast<decltype(context.math.matrix.inverse)>(GetProcAddress(d3dx,"D3DXMatrixInverse"));
    context.math.transform3=reinterpret_cast<decltype(context.math.transform3)>(GetProcAddress(d3dx,"D3DXVec3Transform"));
    context.math.ortho=reinterpret_cast<decltype(context.math.ortho)>(GetProcAddress(d3dx,"D3DXMatrixOrthoLH"));
    context.math.ticks=fixedTicks;context.math.sineFloat=sineFloat;context.math.cosineFloat=cosineFloat;
    require(context.math.matrix.multiply&&context.math.matrix.inverse&&context.math.transform3,"matrix providers");
    RF455CharacterDrawGlobals globals{};context.globals=&globals;
    RF455CharacterTransparency transparent;RF455_ResetCharacterTransparency(&transparent);
    std::memcpy(transparent.sortView,identity,64);context.transparent=&transparent;
    context.memory=RF455_CrtMeshMemoryOps();
    DrawObservation observation{device,&shaders};context.observer=&observation;context.beforeDraw=DrawObservation::observe;
    float sentinel[20];for(unsigned i=0;i<20;++i)sentinel[i]=float(i+1)/20;
    auto draw=[&](unsigned expected,const char* filename,bool flush=false){
        observation.selected.clear();observation.bound.clear();
        RF455_SetCharacterDrawState(&context.state);device->SetRenderState(D3DRS_ZENABLE,FALSE);
        require(SUCCEEDED(device->SetPixelShaderConstantF(0,sentinel,5)),"seed existing pixel constants");
        require(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"route begin");
        require(RF455_DrawCharacter455(&context,&model,identity,nullptr)==RF_CHARACTER_DRAW_OK,"actual character route");
        if(flush)require(RF455_FlushCharacterTransparency(&context)==RF_CHARACTER_DRAW_OK,"actual transparent route");
        require(SUCCEEDED(device->EndScene()),"route end");
        require(observation.selected==std::vector<unsigned>{expected}&&observation.bound==std::vector<bool>{true},"actual selected shader at GPU submission");
        float restored[20];device->GetPixelShaderConstantF(0,restored,5);
        require(!std::memcmp(sentinel,restored,sizeof(sentinel)),"enhanced constants do not leak into later passes");
        return pixels(device,save,filename);
    };
    require(RF455_SetEnhancedActorLightingEnabled(false),"route classic");
    const auto classic=draw(0,"route-classic.png");
    require(RF455_SetEnhancedActorLightingEnabled(true),"route enhanced");
    const auto enhanced=draw(12,"route-enhanced.png");
    require(centreRed(enhanced)>centreRed(classic)+5,"per-pixel normals improve curved shared mesh shading");
    put(mesh.bytes,5791,static_cast<IDirect3DBaseTexture9*>(normalMap.Get()));draw(13,nullptr);
    put(mesh.bytes,5795,static_cast<IDirect3DBaseTexture9*>(specularMap.Get()));draw(14,nullptr);
    put<IDirect3DBaseTexture9*>(mesh.bytes,5791,nullptr);put<IDirect3DBaseTexture9*>(mesh.bytes,5795,nullptr);
    // A following excluded mapped part must inherit the same material scratch
    // that the classic basic part prepared before modernisation.
    meshes[1]=mesh;put(meshes[1].bytes,5455,meshes[1].bytes+5163);
    put(meshes[1].bytes,5791,static_cast<IDirect3DBaseTexture9*>(normalMap.Get()));
    put(meshes[1].bytes,5115,static_cast<IDirect3DBaseTexture9*>(albedo.Get()));
    put(model.prefix.bytes,532,2u);observation.selected.clear();observation.bound.clear();
    RF455_SetCharacterDrawState(&context.state);device->SetRenderState(D3DRS_ZENABLE,FALSE);
    require(SUCCEEDED(device->BeginScene()),"mixed route begin");
    require(RF455_DrawCharacter455(&context,&model,identity,nullptr)==RF_CHARACTER_DRAW_OK,"mixed enhanced/classic parts");
    require(SUCCEEDED(device->EndScene()),"mixed route end");
    require(observation.selected==std::vector<unsigned>({12,1})&&observation.bound==std::vector<bool>({true,true}),"mixed shader routing");
    float inherited[8];device->GetVertexShaderConstantF(18,inherited,2);
    require(!std::memcmp(inherited,material,32),"excluded mapped part retains material from preceding basic part");
    put(model.prefix.bytes,532,1u);
    RF455_SetEnhancedActorLightingProtected(true);
    require(draw(0,nullptr)==classic,"protected actor retains classic pixels");
    RF455_SetEnhancedActorLightingProtected(false);
    require(RF455_SetEnhancedActorLightingEnabled(false)&&draw(0,nullptr)==classic,"production route off-on-off");
    require(RF455_SetEnhancedActorLightingEnabled(true),"route exclusions");
    put<float>(mesh.bytes,5131,.5f);draw(11,nullptr,true);put<float>(mesh.bytes,5131,1);
    put(mesh.bytes,5115,static_cast<IDirect3DBaseTexture9*>(albedo.Get()));draw(0,nullptr);
    put<IDirect3DBaseTexture9*>(mesh.bytes,5115,nullptr);
    require(RF455_SetEnhancedActorLightingEnabled(false),"route cleanup setting");
    for(unsigned i=0;i<8;++i)device->SetTexture(i,nullptr);
    device->SetStreamSource(0,nullptr,0,0);device->SetIndices(nullptr);
    RF455_DestroyMeshStorage(&mesh,&context.memory);
    RF455_DestroyIndexPool(&indices);RF455_DestroyVertexPool(&v64);RF455_DestroyVertexPool(&v36);
    return 9;
}
int run(const char* d3dxPath){
    HMODULE library=LoadLibraryA(d3dxPath);require(library!=nullptr,"D3DX compiler");
    realApi.compile=reinterpret_cast<decltype(realApi.compile)>(GetProcAddress(library,"D3DXCompileShader"));
    realApi.sprite=reinterpret_cast<decltype(realApi.sprite)>(GetProcAddress(library,"D3DXCreateSprite"));
    auto save=reinterpret_cast<SaveSurface>(GetProcAddress(library,"D3DXSaveSurfaceToFileA"));
    require(realApi.compile&&realApi.sprite&&save,"D3DX exports");
    HWND window=CreateWindowExA(0,"STATIC","RF455 enhanced actor component",WS_POPUP,0,0,1920,1080,
        nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);
    require(window&&!IsWindowVisible(window),"hidden window");
    ComPtr<IDirect3D9> api;api.Attach(Direct3DCreate9(D3D_SDK_VERSION));require(api!=nullptr,"D3D9");
    D3DPRESENT_PARAMETERS pp{};pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.BackBufferWidth=1920;pp.BackBufferHeight=1080;
    pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;
    ComPtr<IDirect3DDevice9> device;
    require(SUCCEEDED(api->CreateDevice(0,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&device)),"hardware device");
    RF455ShaderManager manager{};RF455_ConstructShaderManager(&manager);manager.device=device.Get();
    IUnknown* sprite=nullptr;IDirect3DVertexDeclaration9* declaration64=nullptr,*declaration36=nullptr;
    require(RF455_InitializeCharacterShaders(&manager,&realApi,&sprite,&declaration64,&declaration36)==11&&manager.count==12,"original bootstrap unchanged");
    RF455_InitializeEnhancedActorLighting(&manager,&realApi);
    require(RF455_EnhancedActorLightingAvailable()&&manager.count==15,"optional programs compiled");
    require(RF455_SetEnhancedActorLightingEnabled(false),"classic mode persisted");
    const float identity[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
    const float direction[4]={0,0,1,0};
    float material[17]={.35f,.35f,.35f,1,.15f,.15f,.15f,1,.35f,.35f,.35f,1,0,0,0,0,24};
    auto albedo=texture(device.Get(),0xff808080),flatNormal=texture(device.Get(),0xff8080ff),
         extremeNormal=texture(device.Get(),0xffffffff),black=texture(device.Get(),0xff000000),white=texture(device.Get(),0xffffffff);
    Vertex vertices[6]{};
    const float xy[6][2]={{-.7f,-.7f},{-.7f,.7f},{.7f,.7f},{-.7f,-.7f},{.7f,.7f},{.7f,-.7f}};
    for(unsigned i=0;i<6;++i){vertices[i].position[0]=xy[i][0];vertices[i].position[1]=xy[i][1];vertices[i].position[2]=.5f;
        vertices[i].weights[0]=1;vertices[i].normal[2]=-1;vertices[i].tangent[0]=1;vertices[i].uv[0]=vertices[i].uv[1]=.5f;}
    device->SetVertexDeclaration(declaration64);device->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE);
    device->SetRenderState(D3DRS_ZENABLE,FALSE);device->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);
    device->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);device->SetRenderState(D3DRS_LIGHTING,FALSE);
    device->SetTexture(0,albedo.Get());device->SetTexture(1,nullptr);device->SetTexture(3,flatNormal.Get());
    for(unsigned sampler:{0u,3u,4u}){device->SetSamplerState(sampler,D3DSAMP_MINFILTER,D3DTEXF_POINT);device->SetSamplerState(sampler,D3DSAMP_MAGFILTER,D3DTEXF_POINT);}
    device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
    device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);device->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);
    device->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);
    device->SetVertexShaderConstantF(2,identity,4);device->SetVertexShaderConstantF(6,identity,4);
    device->SetVertexShaderConstantF(100,identity,4);device->SetVertexShaderConstantF(10,direction,1);
    device->SetVertexShaderConstantF(18,material,1);device->SetVertexShaderConstantF(19,material+4,1);
    auto draw=[&](bool normal,bool specular,const float* cameraView,const char* filename){
        unsigned selected=0;
        if(!RF455_BindEnhancedActorLighting(&manager,material,cameraView,direction,normal,specular,&selected)){
            require(!RF455_EnhancedActorLightingEnabled(),"unexpected enhanced bind failure");
            device->SetVertexShader(manager.programs[0].vertex);device->SetPixelShader(nullptr);
        }
        require(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"begin");
        require(SUCCEEDED(device->DrawPrimitiveUP(D3DPT_TRIANGLELIST,2,vertices,sizeof(Vertex))),"draw actor stream");
        require(SUCCEEDED(device->EndScene()),"end");return pixels(device.Get(),save,filename);
    };
    const auto classic=draw(false,false,identity,"classic.png");
    require(RF455_SetEnhancedActorLightingEnabled(true)&&RF455_EnhancedActorLightingEnabled(),"enhanced mode");
    const auto enhanced=draw(false,false,identity,"enhanced-basic.png");
    require(std::abs(int(centreRed(classic))-int(centreRed(enhanced)))<=1,"front-lit albedo retained");
    device->SetTexture(4,black.Get());const auto masked=draw(true,true,identity,nullptr);
    device->SetTexture(4,white.Get());const auto glossy=draw(true,true,identity,"enhanced-masked-specular.png");
    require(centreRed(glossy)>centreRed(masked)+20,"specular mask controls highlight");
    float shiftedView[16];std::memcpy(shiftedView,identity,sizeof(identity));shiftedView[12]=-4;
    const auto shifted=draw(true,true,shiftedView,nullptr);
    require(centreRed(shifted)+10<centreRed(glossy),"world camera uniform controls highlight");
    // This fixture deliberately holds clip position fixed while varying the
    // lighting view input; full scene camera matching is a separate live check.
    float actualCamera[4]{};device->GetPixelShaderConstantF(3,actualCamera,1);
    require(std::fabs(actualCamera[0]-4)<1e-5f&&std::fabs(actualCamera[1])<1e-5f,"inverse-view camera position");
    device->SetTexture(3,extremeNormal.Get());const auto extreme=draw(true,false,identity,nullptr);
    require(centreRed(extreme)>10&&centreRed(extreme)<40,"normal reconstruction remains finite at boundary");
    unsigned selected=0xffffffffu;
    RF455_SetEnhancedActorLightingProtected(true);
    require(!RF455_BindEnhancedActorLighting(&manager,material,identity,direction,false,false,&selected)&&selected==0xffffffffu,"protected effects retain original route");
    RF455_SetEnhancedActorLightingProtected(false);
    float singular[16]{};require(!RF455_BindEnhancedActorLighting(&manager,material,singular,direction,false,false,&selected),"invalid view rejected");
    require(RF455_SetEnhancedActorLightingEnabled(false),"switch back");
    require(draw(false,false,identity,nullptr)==classic,"off-on-off restores exact classic frame");
    require(GetPrivateProfileIntA("RenderState","EnhancedActorLighting",-1,".\\R3Engine.ini")==0,"menu setting persisted");
    const unsigned routes=productionRoutes(device.Get(),manager,library,declaration36,declaration64,vertices,material,identity,save);
    device->SetVertexShader(nullptr);device->SetPixelShader(nullptr);device->SetVertexDeclaration(nullptr);
    for(unsigned sampler:{0u,1u,3u,4u})device->SetTexture(sampler,nullptr);
    RF455_ReleaseShaderManager(&manager);require(!RF455_EnhancedActorLightingAvailable(),"release clears capability");
    RF455_ReleaseCharacterDeclarations(&declaration64,&declaration36);sprite->Release();sprite=nullptr;
    unsigned failures=0;
    for(unsigned fail:{1u,4u,6u}){
        require(RF455_InitializeCharacterShaders(&manager,&realApi,&sprite,&declaration64,&declaration36)==11,"failure-control baseline");
        RF455ShaderApi controlled{controlledCompile,realApi.sprite};compileCount=0;failCompile=fail;
        RF455_InitializeEnhancedActorLighting(&manager,&controlled);
        require(!RF455_EnhancedActorLightingAvailable()&&manager.count==12&&!RF455_SetEnhancedActorLightingEnabled(true),"compile failure keeps originals and rejects unavailable option");
        RF455_ReleaseShaderManager(&manager);RF455_ReleaseCharacterDeclarations(&declaration64,&declaration36);sprite->Release();sprite=nullptr;++failures;
    }
    albedo.Reset();flatNormal.Reset();extremeNormal.Reset();black.Reset();white.Reset();
    device.Reset();api.Reset();DestroyWindow(window);FreeLibrary(library);
    FILE* report=std::fopen("result.json","wb");require(report!=nullptr,"report");
    std::fprintf(report,"{\"status\":\"PASS\",\"resolution\":[1920,1080],\"classic_restored\":true,\"specular_mask\":true,"
        "\"camera_uniform\":true,\"finite_normal_boundary\":true,\"protected_effect_bind\":true,\"compile_failures\":%u,"
        "\"actual_shared_mesh_routes\":%u,\"pixel_constants_restored\":true,"
        "\"scope\":\"shader and production shared-mesh route component; not live actor or full scene\"}\n",failures,routes);std::fclose(report);return 0;
}
}
int main(int argc,char** argv){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    try{require(argc==2,"D3DX DLL argument required");return run(argv[1]);}
    catch(const std::exception& error){std::fprintf(stderr,"Enhanced actor lighting: %s\n",error.what());return 1;}
}
