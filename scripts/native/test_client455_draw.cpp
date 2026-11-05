#include "client455_draw.h"
#include "client455_pose.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <map>
#include <string>
#include <vector>

namespace {
unsigned checks,draws,realParts,animatedParts,paletteUploads,textureParts;
unsigned frameValues[2],coloredPixels[2];
#define DR_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"Draw check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>T get(const unsigned char* p,unsigned at){T v;std::memcpy(&v,p+at,sizeof(v));return v;}
template<class T>void put(unsigned char* p,unsigned at,T v){std::memcpy(p+at,&v,sizeof(v));}
void unit(float* m){std::memset(m,0,64);m[0]=m[5]=m[10]=m[15]=1;}
bool save(const char* name,const std::vector<unsigned char>& bytes){FILE* f=std::fopen(name,"wb");if(!f)return false;const bool ok=std::fwrite(bytes.data(),1,bytes.size(),f)==bytes.size();return !std::fclose(f) && ok;}
struct Memory {
    RF455AnimationMemoryOps real=RF455_CrtAnimationMemoryOps();std::map<void*,std::size_t> live;bool bad=false;
    ~Memory(){for(const auto& p:live)real.memory.release(nullptr,p.first);}
    static void* __cdecl allocate(void* raw,std::size_t size){auto& m=*static_cast<Memory*>(raw);void* p=m.real.memory.allocate(nullptr,size);if(p)m.live[p]=size;return p;}
    static void __cdecl release(void* raw,void* p){auto& m=*static_cast<Memory*>(raw);if(p && !m.live.erase(p)){m.bad=true;return;}m.real.memory.release(nullptr,p);}
    static std::size_t __cdecl extent(void* raw,const void* p){auto& m=*static_cast<Memory*>(raw);const auto i=m.live.find(const_cast<void*>(p));if(i==m.live.end()){m.bad=true;return 0;}return i->second;}
    RF455AnimationMemoryOps ops(){return {{this,allocate,release},extent};}
};
struct Scene {
    RF455TextureManager textures;RF455VertexBufferPool v36,v64;RF455IndexBufferPool indices;RF455MeshAccounting meshes={};RF455BufferAccounting buffers={};RF455LegacyScratch scratch;
    Scene(IDirect3DDevice9* device){RF455_ConstructTextureManager(&textures);RF455_ConstructVertexPool(&v36);RF455_ConstructVertexPool(&v64);RF455_ConstructIndexPool(&indices);textures.device=v36.device=v64.device=indices.device=device;}
    ~Scene(){RF455_DestroyTextureManager(&textures);RF455_DestroyIndexPool(&indices);RF455_DestroyVertexPool(&v64);RF455_DestroyVertexPool(&v36);}
};
struct Owners {RF455PoseSpan span;static int __cdecl resolve(void* raw,const RF455AnimationData*,RF455PoseSpan* out){*out=static_cast<Owners*>(raw)->span;return 1;}};
void __cdecl diagnostic(void*,const char* text){std::fprintf(stderr,"Character:%s\n",text);}
void __cdecl diagnosticWide(void*,const wchar_t* text){std::fwprintf(stderr,L"Character:%ls\n",text);}
std::vector<unsigned char> capture(IDirect3DDevice9* device){
    std::vector<unsigned char> result;IDirect3DSurface9* target=nullptr;IDirect3DSurface9* cpu=nullptr;
    if(FAILED(device->GetRenderTarget(0,&target)))return result;D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    if(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,D3DFMT_X8R8G8B8,D3DPOOL_SYSTEMMEM,&cpu,nullptr)) && SUCCEEDED(device->GetRenderTargetData(target,cpu))){D3DLOCKED_RECT lock={};if(SUCCEEDED(cpu->LockRect(&lock,nullptr,D3DLOCK_READONLY))){result.resize(desc.Width*desc.Height*4);for(unsigned y=0;y<desc.Height;++y)std::memcpy(result.data()+y*desc.Width*4,static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch,desc.Width*4);cpu->UnlockRect();}}
    if(cpu)cpu->Release();target->Release();return result;
}
int contracts(RF455CharacterDrawState state,RF455ShaderManager* shaders,const RF455MeshMatrixOps& math){
    auto* d=state.device;float expected[16],actual[64];unsigned selected=0;DWORD value=0;
    for(unsigned mode:{2u,4u})for(DWORD specular:{0u,1u}){
        state.vertexMode=mode;state.specularEnable=specular;d->SetRenderState(D3DRS_SPECULARENABLE,FALSE);d->SetRenderState(D3DRS_DIFFUSEMATERIALSOURCE,D3DMCS_COLOR1);d->SetRenderState(D3DRS_NORMALIZENORMALS,FALSE);RF455_SetCharacterDrawState(&state);
        DR_CHECK(SUCCEEDED(d->GetRenderState(D3DRS_VERTEXBLEND,&value)) && value==(mode==2?1u:3u));DR_CHECK(SUCCEEDED(d->GetRenderState(D3DRS_SPECULARENABLE,&value)) && value==specular);
        DR_CHECK(SUCCEEDED(d->GetRenderState(D3DRS_DIFFUSEMATERIALSOURCE,&value)) && value==(specular?0u:1u));DR_CHECK(SUCCEEDED(d->GetRenderState(D3DRS_NORMALIZENORMALS,&value)) && value==specular);
        IDirect3DVertexDeclaration9* declaration=nullptr;DR_CHECK(SUCCEEDED(d->GetVertexDeclaration(&declaration)) && declaration==(mode==2?state.declaration36:state.declaration64));declaration->Release();
        DR_CHECK(SUCCEEDED(d->GetVertexShaderConstantF(10,actual,1)) && !std::memcmp(actual,state.light104+16,16));
        DR_CHECK(SUCCEEDED(d->GetRenderState(D3DRS_FOGENABLE,&value)) && value==0);
    }
    for(unsigned index:{0u,4u,11u,12u,0xffffffffu}){
        DR_CHECK(SUCCEEDED(RF455_SelectCharacterShader(shaders,index,&selected)) && selected==index);IDirect3DVertexShader9* v=nullptr;IDirect3DPixelShader9* p=nullptr;
        DR_CHECK(SUCCEEDED(d->GetVertexShader(&v)) && v==(index<12?shaders->programs[index].vertex:nullptr));DR_CHECK(SUCCEEDED(d->GetPixelShader(&p)) && p==(index<12?shaders->programs[index].pixel:nullptr));if(v)v->Release();if(p)p->Release();
    }
    float material[17];for(unsigned i=0;i<17;++i)material[i]=static_cast<float>(i+1)/32;
    DR_CHECK(SUCCEEDED(RF455_SetCharacterMaterial(d,material)) && SUCCEEDED(d->GetVertexShaderConstantF(18,actual,2)) && !std::memcmp(actual,material,32));
    RF455MeshStorage mesh={};float world[16],other[16];unit(world);unit(other);world[0]=2;world[5]=3;world[10]=4;world[12]=17;world[13]=19;world[14]=23;other[0]=-3;other[5]=2;other[12]=100;other[13]=200;other[14]=300;
    for(unsigned bones:{0u,2u})for(bool overrideTranslation:{false,true}){
        put(mesh.bytes,522,bones);float skin[16];unit(skin);skin[0]=.5f;skin[1]=.25f;skin[4]=-.75f;skin[12]=3;skin[13]=5;skin[14]=7;
        std::memcpy(mesh.bytes+4830,skin,64);for(unsigned i=0;i<bones;++i){skin[12]+=1;std::memcpy(mesh.bytes+646+64*i,skin,64);}
        DR_CHECK(SUCCEEDED(RF455_UploadCharacterPalette(d,&mesh,world,overrideTranslation?other:nullptr,&math)));
        const unsigned count=bones?bones:4;DR_CHECK(SUCCEEDED(d->GetVertexShaderConstantF(100,actual,4*count)));
        for(unsigned i=0;i<count;++i){const auto* source=mesh.bytes+(bones?646+64*i:4830);float translation[16];math.multiply(expected,source,world);if(overrideTranslation){math.multiply(translation,source,other);std::memcpy(expected+12,translation+12,12);}DR_CHECK(!std::memcmp(actual+16*i,expected,64));}
    }
    return 0;
}
struct Vertex64 {float position[3],weight[3];short index[4];float normal[3],uv[2],tangent[3];};
int sharedDraw(RF455CharacterDrawState state,RF455ShaderManager* shaders,Scene& scene,const RF455MeshMatrixOps& math){
    auto* d=state.device;float identity[16],material[17]={};unit(identity);for(unsigned i=0;i<8;++i)material[i]=1;unsigned selected=0;
    Vertex64 triangle[3]={};const float positions[3][3]={{-.8f,-.8f,.5f},{0,.8f,.5f},{.8f,-.8f,.5f}};for(unsigned i=0;i<3;++i){std::memcpy(triangle[i].position,positions[i],12);triangle[i].normal[2]=1;}
    std::vector<unsigned char> first;
    for(unsigned mode:{2u,4u}){
        state.vertexMode=mode;state.specularEnable=0;RF455_SetCharacterDrawState(&state);d->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE);d->SetRenderState(D3DRS_ZENABLE,FALSE);d->SetTexture(0,nullptr);d->SetTexture(1,nullptr);d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1);d->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_DIFFUSE);d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG1);d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_DIFFUSE);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);
        DR_CHECK(SUCCEEDED(RF455_SelectCharacterShader(shaders,0,&selected)) && SUCCEEDED(RF455_SetCharacterMaterial(d,material)));d->SetVertexShaderConstantF(2,identity,4);d->SetVertexShaderConstantF(6,identity,4);
        unsigned padding=0,vertex=0,index=0;unsigned short rebased[]={3,4,5},dummy[]={0,0,0};RF455MeshStorage mesh={};std::memcpy(mesh.bytes+4830,identity,64);put<unsigned>(mesh.bytes,5086,3);put<unsigned>(mesh.bytes,5090,3);
        if(mode==4){DR_CHECK(RF455_UploadVertices64(&scene.v64,triangle,sizeof(triangle),&padding,&scene.buffers) && RF455_UploadVertices64(&scene.v64,triangle,sizeof(triangle),&vertex,&scene.buffers));}
        else{unsigned char converted[3*36];RF455_ConvertLegacyVertices36(triangle,converted,3);DR_CHECK(RF455_UploadVertices36(&scene.v36,converted,sizeof(converted),&padding,&scene.buffers) && RF455_UploadVertices36(&scene.v36,converted,sizeof(converted),&vertex,&scene.buffers));}
        DR_CHECK(padding==0 && vertex==(mode==4?192u:108u));DR_CHECK(RF455_UploadIndices(&scene.indices,dummy,6,&padding,&scene.buffers) && RF455_UploadIndices(&scene.indices,rebased,6,&index,&scene.buffers));put(mesh.bytes,4494,vertex);DR_CHECK(SUCCEEDED(RF455_UploadCharacterPalette(d,&mesh,identity,nullptr,&math)));
        for(bool indexed:{false,true}){
            put(mesh.bytes,4502,indexed?index:0xffffffffu);DR_CHECK(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff000000,1,0)) && SUCCEEDED(d->BeginScene()));DR_CHECK(SUCCEEDED(RF455_SubmitSharedCharacterMesh(d,mode,&scene.v36,&scene.v64,&scene.indices,&mesh)));++draws;DR_CHECK(SUCCEEDED(d->EndScene()));auto pixels=capture(d);DR_CHECK(pixels.size()==256*256*4 && (get<DWORD>(pixels.data(),(128*256+128)*4)&0xffffff)==0xffffff && (get<DWORD>(pixels.data(),0)&0xffffff)==0);if(first.empty())first=pixels;else DR_CHECK(first==pixels);
        }
    }
    RF455MeshStorage empty={};put<unsigned>(empty.bytes,5086,0);DR_CHECK(RF455_SubmitSharedCharacterMesh(d,4,&scene.v36,&scene.v64,&scene.indices,&empty)==S_FALSE);put<void*>(empty.bytes,4506,&empty);DR_CHECK(RF455_SubmitSharedCharacterMesh(d,4,&scene.v36,&scene.v64,&scene.indices,&empty)==D3DERR_INVALIDCALL);return 0;
}
int animated(const char* fixture,RF455CharacterDrawState state,RF455ShaderManager* shaders,Scene& scene,RF455PoseMath math){
    FILE* input=std::fopen(fixture,"rb");DR_CHECK(input);char paths[3][512];for(auto& p:paths){DR_CHECK(std::fgets(p,sizeof(p),input));p[std::strcspn(p,"\r\n")]=0;}std::fclose(input);
    Memory memory;const auto ops=memory.ops();unsigned bytes=0;RF455LegacyDiagnostics log={nullptr,diagnostic,diagnosticWide};RF455CharacterLoadContext load={{{ops.memory,math.matrix,&scene.textures,&scene.v64,&scene.indices,&scene.meshes,&scene.buffers},&scene.v36,4,&scene.scratch,log},{ops,log,&bytes}};
    RF455CharacterStorage root,child;RF455_ConstructCharacter(&root);RF455_ConstructCharacter(&child);
    // fixture lists MSH,BN,ANI: assign their actual source roles.
    std::strcpy(reinterpret_cast<char*>(root.prefix.bytes+4),paths[1]);std::strcpy(reinterpret_cast<char*>(child.prefix.bytes+4),paths[0]);for(auto* p:{&root,&child})std::strcpy(reinterpret_cast<char*>(p->prefix.bytes+276),".\\tex");put(child.prefix.bytes,272,&root.prefix);
    DR_CHECK(RF455_LoadCharacter(&root,0,&load) && RF455_LoadCharacter(&child,0,&load));RF455_RefreshModelTextures(&child.prefix,&scene.textures);
    RF455AnimationStorage animation;RF455_ConstructAnimation(&animation);std::strcpy(reinterpret_cast<char*>(animation.bytes+5),paths[2]);DR_CHECK(RF455_MatchAnimation(&animation,&root,&load));const auto* raw=get<const unsigned char*>(animation.bytes,268);Owners owners={{raw,Memory::extent(&memory,raw)}};RF455PoseScratch scratch={};RF455PoseContext pose={&load,math,&scratch,150,&owners,Owners::resolve};
    auto* meshes=get<RF455MeshStorage*>(child.prefix.bytes,536);const auto count=get<unsigned>(child.prefix.bytes,532);DR_CHECK(count==51);float world[16],identity[16];unit(world);unit(identity);
    put<unsigned>(root.prefix.bytes,672,160);put<unsigned>(child.prefix.bytes,672,160);DR_CHECK(RF455_UpdateCharacterPose(&root,&pose)==RF_POSE_OK && RF455_UpdateCharacterPose(&child,&pose)==RF_POSE_OK);
    // Camera is harness policy. Fit the first posed positions, same transform
    // for both animation frames, with Z depth in0..1. No game camera claim.
    float low[3]={1e30f,1e30f,1e30f},high[3]={-1e30f,-1e30f,-1e30f};bool found=false;
    for(unsigned i=0;i<count;++i){auto* m=meshes[i].bytes;if(!get<unsigned>(m,5086))continue;IDirect3DVertexBuffer9* vb=scene.v64.buffers[get<unsigned>(m,4494)/RF455_VERTEX_BLOCK_BYTES];void* vertices=nullptr;DR_CHECK(vb && SUCCEEDED(vb->Lock(get<unsigned>(m,4494)%RF455_VERTEX_BLOCK_BYTES,64*get<unsigned>(m,5086),&vertices,D3DLOCK_READONLY)));
        bool validSlots=true;
        for(unsigned k=0;k<get<unsigned>(m,5086) && validSlots;++k){const auto* v=static_cast<const unsigned char*>(vertices)+64*k;float weight[4]={get<float>(v,12),get<float>(v,16),get<float>(v,20),0};weight[3]=1-weight[0]-weight[1]-weight[2];float position[3]={};for(unsigned j=0;j<4;++j){const unsigned slot=get<unsigned short>(v,24+2*j);if(slot>=(std::max)(4u,get<unsigned>(m,522))){validSlots=false;break;}const auto* matrix=m+(get<unsigned>(m,522)?646+64*slot:4830);for(unsigned axis=0;axis<3;++axis){float coordinate=get<float>(matrix,48+4*axis);for(unsigned component=0;component<3;++component)coordinate+=get<float>(v,4*component)*get<float>(matrix,16*component+4*axis);position[axis]+=coordinate*weight[j];}}for(unsigned axis=0;axis<3;++axis){low[axis]=(std::min)(low[axis],position[axis]);high[axis]=(std::max)(high[axis],position[axis]);found=true;}}
        vb->Unlock();DR_CHECK(validSlots);}
    DR_CHECK(found);const float scale=1.5f/(std::max)(high[0]-low[0],high[2]-low[2]);const float depth=.3f/(std::max)(1.0f,high[1]-low[1]);world[0]=scale;world[5]=world[10]=0;world[6]=-depth;world[9]=scale;world[12]=-.5f*(low[0]+high[0])*scale;world[13]=-.5f*(low[2]+high[2])*scale;world[14]=.5f+.5f*(low[1]+high[1])*depth;
    std::vector<unsigned char> before;auto* d=state.device;unsigned selected=0;state.vertexMode=4;state.specularEnable=0;const unsigned maxFrame=get<unsigned>(animation.bytes,276);DR_CHECK(maxFrame>=320);
    for(unsigned phase=0;phase<2;++phase){
        const unsigned frame=phase?maxFrame/2:160;frameValues[phase]=frame;put(root.prefix.bytes,672,frame);put(child.prefix.bytes,672,frame);DR_CHECK(RF455_UpdateCharacterPose(&root,&pose)==RF_POSE_OK && RF455_UpdateCharacterPose(&child,&pose)==RF_POSE_OK);
        RF455_SetCharacterDrawState(&state);d->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE);d->SetRenderState(D3DRS_ZENABLE,TRUE);d->SetRenderState(D3DRS_ZWRITEENABLE,TRUE);d->SetTexture(1,nullptr);d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);d->SetVertexShaderConstantF(2,identity,4);d->SetVertexShaderConstantF(6,identity,4);DR_CHECK(SUCCEEDED(RF455_SelectCharacterShader(shaders,0,&selected)) && SUCCEEDED(RF455_SetCharacterMaterial(d,child.prefix.bytes+720)));
        DR_CHECK(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101020,1,0)) && SUCCEEDED(d->BeginScene()));
        for(unsigned i=0;i<count;++i){auto* m=meshes[i].bytes;const auto vertices=get<unsigned>(m,5086);if(!vertices)continue;DR_CHECK(!get<void*>(m,4506) && get<unsigned>(m,522)<=30);const auto* texture=get<IDirect3DBaseTexture9*>(m,5107);DR_CHECK(texture && SUCCEEDED(d->SetTexture(0,const_cast<IDirect3DBaseTexture9*>(texture))));
            DR_CHECK(SUCCEEDED(RF455_UploadCharacterPalette(d,meshes+i,world,nullptr,&math.matrix)));++paletteUploads;DR_CHECK(SUCCEEDED(RF455_SubmitSharedCharacterMesh(d,4,&scene.v36,&scene.v64,&scene.indices,meshes+i)));++draws;if(!phase){++realParts;++textureParts;if(get<unsigned>(m,522))++animatedParts;}
        }
        DR_CHECK(SUCCEEDED(d->EndScene()));auto pixels=capture(d);DR_CHECK(pixels.size()==256*256*4);unsigned colored=0;for(unsigned i=0;i<256*256;++i)if((get<DWORD>(pixels.data(),4*i)&0xffffff)!=0x101020)++colored;coloredPixels[phase]=colored;char name[40];std::snprintf(name,sizeof(name),"character-frame-%u.bgra",phase);DR_CHECK(save(name,pixels));std::fprintf(stderr,"Frame%u: %u pixels, bbox %f,%f,%f to %f,%f,%f\n",phase,colored,low[0],low[1],low[2],high[0],high[1],high[2]);DR_CHECK(colored>1000 && colored<256*256-1000);if(!phase)before=pixels;else DR_CHECK(before!=pixels);
    }
    DR_CHECK(realParts>0 && animatedParts>0 && textureParts==realParts);RF455_ReleaseModelMeshArray(&child.prefix,&ops.memory);RF455_ReleaseModelMeshArray(&root.prefix,&ops.memory);RF455_DestroyAnimation(&animation,&ops.memory);DR_CHECK(memory.live.empty() && !memory.bad);return 0;
}
int run(const char* dll,const char* fixture){
    HMODULE provider=LoadLibraryA(dll);DR_CHECK(provider);RF455PoseMath math={};math.matrix.inverse=reinterpret_cast<decltype(math.matrix.inverse)>(GetProcAddress(provider,"D3DXMatrixInverse"));math.matrix.multiply=reinterpret_cast<decltype(math.matrix.multiply)>(GetProcAddress(provider,"D3DXMatrixMultiply"));math.slerp=reinterpret_cast<decltype(math.slerp)>(GetProcAddress(provider,"D3DXQuaternionSlerp"));math.rotationQuaternion=reinterpret_cast<decltype(math.rotationQuaternion)>(GetProcAddress(provider,"D3DXMatrixRotationQuaternion"));DR_CHECK(math.matrix.inverse && math.matrix.multiply && math.slerp && math.rotationQuaternion);
    RF455ShaderApi shaderApi={reinterpret_cast<decltype(shaderApi.compile)>(GetProcAddress(provider,"D3DXCompileShader")),reinterpret_cast<decltype(shaderApi.sprite)>(GetProcAddress(provider,"D3DXCreateSprite"))};RF455CharacterTextureApi textureApi={reinterpret_cast<decltype(textureApi.memory2D)>(GetProcAddress(provider,"D3DXCreateTextureFromFileInMemoryEx")),reinterpret_cast<decltype(textureApi.memoryCube)>(GetProcAddress(provider,"D3DXCreateCubeTextureFromFileInMemoryEx")),reinterpret_cast<decltype(textureApi.file2D)>(GetProcAddress(provider,"D3DXCreateTextureFromFileA"))};DR_CHECK(shaderApi.compile && shaderApi.sprite && textureApi.memory2D && textureApi.memoryCube && textureApi.file2D);
    char system[MAX_PATH];DR_CHECK(GetSystemDirectoryA(system,MAX_PATH));HMODULE library=LoadLibraryA((std::string(system)+"\\d3d9.dll").c_str());DR_CHECK(library);auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(library,"Direct3DCreate9"));DR_CHECK(create);IDirect3D9* api=create(D3D_SDK_VERSION);DR_CHECK(api);HWND window=CreateWindowExA(0,"STATIC","RF455 own connected draw",WS_OVERLAPPEDWINDOW,0,0,256,256,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);DR_CHECK(window);
    D3DPRESENT_PARAMETERS present={};present.Windowed=TRUE;present.hDeviceWindow=window;present.BackBufferWidth=present.BackBufferHeight=256;present.BackBufferFormat=D3DFMT_X8R8G8B8;present.SwapEffect=D3DSWAPEFFECT_DISCARD;present.EnableAutoDepthStencil=TRUE;present.AutoDepthStencilFormat=D3DFMT_D16;IDirect3DDevice9* device=nullptr;DR_CHECK(SUCCEEDED(api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&present,&device)));
    RF455ShaderManager shaders;RF455_ConstructShaderManager(&shaders);shaders.device=device;IUnknown* sprite=nullptr;IDirect3DVertexDeclaration9* d64=nullptr;IDirect3DVertexDeclaration9* d36=nullptr;DR_CHECK(RF455_InitializeCharacterShaders(&shaders,&shaderApi,&sprite,&d64,&d36)==11);float light[26]={};light[18]=-1;RF455CharacterDrawState state={device,4,d36,d64,light,0};
    DR_CHECK(contracts(state,&shaders,math.matrix)==0);{Scene scene(device);DR_CHECK(sharedDraw(state,&shaders,scene,math.matrix)==0);}
    auto* oldApi=RF455_SetCharacterTextureApi(&textureApi);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);
    {Scene scene(device);DR_CHECK(animated(fixture,state,&shaders,scene,math)==0);}
    for(unsigned i=0;i<8;++i)device->SetTexture(i,nullptr);device->SetStreamSource(0,nullptr,0,0);device->SetIndices(nullptr);device->SetVertexShader(nullptr);device->SetPixelShader(nullptr);device->SetVertexDeclaration(nullptr);RF455_ReleaseShaderManager(&shaders);RF455_ReleaseCharacterDeclarations(&d64,&d36);sprite->Release();RF455_SetCharacterTextureApi(oldApi);RF455_SetCharacterRfsCache(oldCache);DR_CHECK(!device->Release() && !api->Release());DestroyWindow(window);FreeLibrary(library);FreeLibrary(provider);return 0;
}
}
extern "C" int RF455_RunDrawChecks(const char* dll,const char* fixture,const char* output){checks=draws=realParts=animatedParts=paletteUploads=textureParts=0;std::memset(frameValues,0,sizeof(frameValues));std::memset(coloredPixels,0,sizeof(coloredPixels));const int result=run(dll,fixture);FILE* f=std::fopen(output,"wb");if(!f)return 2;std::fprintf(f,"{\"status\":\"%s\",\"checks\":%u,\"draws\":%u,\"real_drawn_parts\":%u,\"animated_parts\":%u,\"palette_uploads\":%u,\"textured_parts\":%u,\"real_animation_frames\":2,\"frame_values\":[%u,%u],\"colored_pixels\":[%u,%u],\"owned_heap_balance\":%d,\"device_and_api_release_counts\":%d}\n",result?"FAIL":"PASS",checks,draws,realParts,animatedParts,paletteUploads,textureParts,frameValues[0],frameValues[1],coloredPixels[0],coloredPixels[1],result?-1:0,result?-1:0);std::fclose(f);return result;}
#ifndef RF455_DRAW_EMBEDDED
int main(int argc,char** argv){return argc==4?RF455_RunDrawChecks(argv[1],argv[2],argv[3]):3;}
#endif
