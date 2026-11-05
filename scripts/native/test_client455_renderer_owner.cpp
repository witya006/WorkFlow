#include "client455_renderer_owner.h"
#include "client455_pose.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <map>
#include <string>
#include <vector>

namespace owner455 {
unsigned checks=0,modelDraws=0;std::vector<unsigned> releases;
#define OW_CHECK(x) do{++checks;if(!(x)){std::fprintf(stderr,"Owner check%u line%d\n",checks,__LINE__);return 1;}}while(0)
template<class T>T get(const unsigned char* p,unsigned at){T v;std::memcpy(&v,p+at,sizeof(v));return v;}
template<class T>void put(unsigned char* p,unsigned at,T v){std::memcpy(p+at,&v,sizeof(v));}
void unit(float* matrix){std::memset(matrix,0,64);matrix[0]=matrix[5]=matrix[10]=matrix[15]=1;}
struct Memory {
    RF455AnimationMemoryOps crt=RF455_CrtAnimationMemoryOps();std::map<void*,std::size_t> live;bool bad=false;
    static void* __cdecl allocate(void* raw,std::size_t size){auto& m=*static_cast<Memory*>(raw);void* p=m.crt.memory.allocate(nullptr,size);if(p)m.live[p]=size;return p;}
    static void __cdecl release(void* raw,void* p){auto& m=*static_cast<Memory*>(raw);if(p && !m.live.erase(p)){m.bad=true;return;}m.crt.memory.release(nullptr,p);}
    static std::size_t __cdecl extent(void* raw,const void* p){auto& m=*static_cast<Memory*>(raw);auto it=m.live.find(const_cast<void*>(p));return it==m.live.end()?0:it->second;}
    RF455AnimationMemoryOps ops(){return {{this,allocate,release},extent};}
};
struct Resource : IUnknown {
    unsigned id;explicit Resource(unsigned value):id(value){}
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID,void**)override{return E_NOINTERFACE;}
    ULONG STDMETHODCALLTYPE AddRef()override{return 1;}
    ULONG STDMETHODCALLTYPE Release()override{releases.push_back(id);return 0;}
};
struct DeviceCapture {void** table;D3DCAPS9 caps;bool success=true;unsigned calls=0,retains=0;};
HRESULT WINAPI capsCapture(DeviceCapture* d,D3DCAPS9* output){++d->calls;if(!d->success)return E_FAIL;*output=d->caps;return S_OK;}
ULONG WINAPI retainCapture(DeviceCapture* d){++d->retains;return 1;}
int contracts(const char* golden){
    FILE* file=std::fopen(golden,"rb");OW_CHECK(file);char magic[4];unsigned version=0,size=0;
    OW_CHECK(std::fread(magic,4,1,file)==1 && !std::memcmp(magic,"RO45",4) && std::fread(&version,4,1,file)==1 && version==1 && std::fread(&size,4,1,file)==1 && size==sizeof(RF455CharacterRenderer));
    std::vector<unsigned char> image(size),mask(size);OW_CHECK(std::fread(image.data(),size,1,file)==1 && std::fread(mask.data(),size,1,file)==1 && std::fgetc(file)==EOF);std::fclose(file);
    for(unsigned seed:{0xa5u,0x5au}){RF455CharacterRenderer owner;std::memset(&owner,seed,sizeof(owner));RF455_ConstructCharacterRenderer(&owner);auto expected=image;for(unsigned i=0;i<size;++i)if(!mask[i])expected[i]=static_cast<unsigned char>(seed);OW_CHECK(!std::memcmp(&owner,expected.data(),size));}
    RF455CharacterRenderer owner;std::memset(&owner,0xa5,sizeof(owner));RF455_ConstructCharacterRenderer(&owner);RF455RendererShared shared={};
    void* table[119]={};table[1]=reinterpret_cast<void*>(retainCapture);table[7]=reinterpret_cast<void*>(capsCapture);DeviceCapture d={table,{}};
    shared.shaders.device=reinterpret_cast<IDirect3DDevice9*>(0x1234);
    for(unsigned i=0;i<5;++i){d.caps={};d.caps.MaxVertexBlendMatrices=i==0?2:i==1?4:i==2?3:0;d.caps.MaxVertexBlendMatrixIndex=i%2?255:0;d.caps.ShadeCaps=i%2?0x200:0;
        owner.vertexMode=i%2?2:4;owner.caps=d.caps;d.success=i!=4;auto expected=owner.caps;unsigned expectedMode=expected.MaxVertexBlendMatrices==2 || expected.MaxVertexBlendMatrices==4?expected.MaxVertexBlendMatrices:owner.vertexMode;
        OW_CHECK(RF455_SetCharacterRendererDevice(&owner,&shared,reinterpret_cast<IDirect3DDevice9*>(&d),nullptr,nullptr)==static_cast<int>((expected.ShadeCaps>>9)&1));
        OW_CHECK(owner.vertexMode==expectedMode && owner.indexedBlend==(expected.MaxVertexBlendMatrixIndex!=0) && owner.specular==((expected.ShadeCaps>>9)&1));
        OW_CHECK(owner.device==reinterpret_cast<IDirect3DDevice9*>(&d) && owner.textures.device==owner.device && owner.vertices64.device==owner.device && owner.vertices36.device==owner.device && owner.indices.device==owner.device);
        OW_CHECK(shared.shaders.device==reinterpret_cast<IDirect3DDevice9*>(0x1234) && !owner.sprite && !std::strcmp(shared.logPath,".\\NetLog\\CEngineLog.log"));
    }
    OW_CHECK(d.calls==5 && d.retains==0);
    Resource a(1),b(2),c(3),sprite(4),ib0(5),ib1023(6),vb36(7),vb64(8);
    owner.effects.resources[0]=&a;owner.effects.resources[19]=&b;owner.effects.extra=&c;owner.sprite=&sprite;
    // COM-ABI captures implement only IUnknown because destruction uses Release.
    owner.indices.buffers[0]=reinterpret_cast<IDirect3DIndexBuffer9*>(&ib0);owner.indices.buffers[1023]=reinterpret_cast<IDirect3DIndexBuffer9*>(&ib1023);
    owner.vertices36.buffers[1]=reinterpret_cast<IDirect3DVertexBuffer9*>(&vb36);owner.vertices64.buffers[2]=reinterpret_cast<IDirect3DVertexBuffer9*>(&vb64);
    Memory memory;const auto ops=memory.ops();OW_CHECK(RF455_CreateCharacter(&owner.bones,"root",nullptr,&ops.memory) && RF455_CreateCharacter(&owner.meshes,"mesh",nullptr,&ops.memory));
    RF455_DestroyCharacterRenderer(&owner,&ops.memory);
    OW_CHECK(releases==std::vector<unsigned>({1,2,3,4,5,6,7,8}) && !owner.sprite);
    OW_CHECK(owner.indices.buffers[0]==reinterpret_cast<IDirect3DIndexBuffer9*>(&ib0) && owner.effects.resources[0]==&a);
    OW_CHECK(memory.live.empty() && !memory.bad && shared.shaders.device==reinterpret_cast<IDirect3DDevice9*>(0x1234));return 0;
}
struct PoseOwner {RF455PoseSpan span;static int __cdecl resolve(void* p,const RF455AnimationData*,RF455PoseSpan* out){*out=static_cast<PoseOwner*>(p)->span;return 1;}};
void __cdecl diagnostic(void*,const char* message){std::fprintf(stderr,"Owner:%s\n",message);}
void __cdecl diagnosticWide(void*,const wchar_t* message){std::fwprintf(stderr,L"Owner:%ls\n",message);}
void __cdecl sine(float* out,const float* in){*out=static_cast<float>(std::sin(static_cast<double>(*in)));}
void __cdecl cosine(float* out,const float* in){*out=static_cast<float>(std::cos(static_cast<double>(*in)));}
unsigned WINAPI ticks(){return 1000;}
void __cdecl observe(void*,const RF455MeshStorage*,unsigned){++modelDraws;}
std::vector<unsigned char> capture(IDirect3DDevice9* device){
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* cpu=nullptr;std::vector<unsigned char> bytes;
    if(FAILED(device->GetRenderTarget(0,&target)))return bytes;D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    if(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,D3DFMT_X8R8G8B8,D3DPOOL_SYSTEMMEM,&cpu,nullptr)) && SUCCEEDED(device->GetRenderTargetData(target,cpu))){D3DLOCKED_RECT lock={};if(SUCCEEDED(cpu->LockRect(&lock,nullptr,D3DLOCK_READONLY))){bytes.resize(desc.Width*desc.Height*4);for(unsigned y=0;y<desc.Height;++y)std::memcpy(bytes.data()+4*desc.Width*y,static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch,4*desc.Width);cpu->UnlockRect();}}
    if(cpu)cpu->Release();target->Release();return bytes;
}
int model(const char* fixture,RF455CharacterRenderer& owner,RF455RendererShared& shared,RF455PoseMath math,RF455CharacterDrawMath drawMath){
    FILE* file=std::fopen(fixture,"rb");OW_CHECK(file);char paths[3][512];for(auto& path:paths){OW_CHECK(std::fgets(path,sizeof(path),file));path[std::strcspn(path,"\r\n")]=0;}std::fclose(file);
    Memory memory;const auto ops=memory.ops();RF455MeshAccounting meshes={};RF455BufferAccounting buffers={};RF455LegacyScratch scratch;unsigned imported=0;RF455LegacyDiagnostics log={nullptr,diagnostic,diagnosticWide};
    const auto base=RF455_RendererModelContext(&owner,&ops.memory,&math.matrix,&meshes,&buffers);
    RF455CharacterLoadContext load={{base,&owner.vertices36,owner.vertexMode,&scratch,log},{ops,log,&imported}};
    auto* root=RF455_CreateCharacter(&owner.bones,paths[1],nullptr,&ops.memory);auto* child=RF455_CreateCharacter(&owner.meshes,paths[0],root,&ops.memory);OW_CHECK(root && child);
    for(auto* p:{root,child})std::strcpy(reinterpret_cast<char*>(p->prefix.bytes+276),".\\tex");OW_CHECK(RF455_LoadCharacter(root,0,&load) && RF455_LoadCharacter(child,0,&load));RF455_RefreshModelTextures(&child->prefix,&owner.textures);
    RF455AnimationStorage animation;RF455_ConstructAnimation(&animation);std::strcpy(reinterpret_cast<char*>(animation.bytes+5),paths[2]);OW_CHECK(RF455_MatchAnimation(&animation,root,&load));
    PoseOwner input={{get<const unsigned char*>(animation.bytes,268),Memory::extent(&memory,get<const unsigned char*>(animation.bytes,268))}};RF455PoseScratch poseScratch={};RF455PoseContext pose={&load,math,&poseScratch,150,&input,PoseOwner::resolve};
    put<unsigned>(root->prefix.bytes,672,160);put<unsigned>(child->prefix.bytes,672,160);OW_CHECK(RF455_UpdateCharacterPose(root,&pose)==RF_POSE_OK && RF455_UpdateCharacterPose(child,&pose)==RF_POSE_OK);
    auto* parts=get<RF455MeshStorage*>(child->prefix.bytes,536);const unsigned count=get<unsigned>(child->prefix.bytes,532);float low[3]={1e30f,1e30f,1e30f},high[3]={-1e30f,-1e30f,-1e30f};unsigned geometry=0;
    for(unsigned i=0;i<count;++i){auto* mesh=parts[i].bytes;unsigned n=get<unsigned>(mesh,5086);if(!n)continue;++geometry;void* data=nullptr;const unsigned offset=get<unsigned>(mesh,4494);auto* buffer=owner.vertices64.buffers[offset/RF455_VERTEX_BLOCK_BYTES];OW_CHECK(buffer && SUCCEEDED(buffer->Lock(offset%RF455_VERTEX_BLOCK_BYTES,64*n,&data,D3DLOCK_READONLY)));bool valid=true;
        for(unsigned k=0;k<n && valid;++k){const auto* vertex=static_cast<const unsigned char*>(data)+64*k;float weight[]={get<float>(vertex,12),get<float>(vertex,16),get<float>(vertex,20),0};weight[3]=1-weight[0]-weight[1]-weight[2];float position[3]={};
            for(unsigned b=0;b<4;++b){unsigned slot=get<unsigned short>(vertex,24+2*b);if(slot>=(std::max)(4u,get<unsigned>(mesh,522))){valid=false;break;}const auto* transform=mesh+(get<unsigned>(mesh,522)?646+64*slot:4830);for(unsigned axis=0;axis<3;++axis){float v=get<float>(transform,48+4*axis);for(unsigned j=0;j<3;++j)v+=get<float>(vertex,4*j)*get<float>(transform,16*j+4*axis);position[axis]+=v*weight[b];}}
            for(unsigned axis=0;axis<3;++axis){low[axis]=(std::min)(low[axis],position[axis]);high[axis]=(std::max)(high[axis],position[axis]);}}
        buffer->Unlock();OW_CHECK(valid);}
    OW_CHECK(geometry==46 && owner.vertexMode==4);float world[16],projection[16],view[16];unit(world);unit(projection);unit(view);
    float scale=1.5f/(std::max)(high[0]-low[0],high[2]-low[2]),depth=.3f/(std::max)(1.0f,high[1]-low[1]);world[0]=scale;world[5]=world[10]=0;world[6]=-depth;world[9]=scale;world[12]=-.5f*(low[0]+high[0])*scale;world[13]=-.5f*(low[2]+high[2])*scale;world[14]=.5f+.5f*(low[1]+high[1])*depth;
    RF455CharacterDrawContext draw={};RF455_BindRendererDrawContext(&owner,&shared,&draw);draw.projection=projection;draw.view=view;draw.math=drawMath;draw.memory=ops.memory;draw.beforeDraw=observe;RF455CharacterDrawGlobals globals;draw.globals=&globals;RF455CharacterTransparency transparent;RF455_ResetCharacterTransparency(&transparent);unit(transparent.sortView);draw.transparent=&transparent;
    std::vector<unsigned char> first;IDirect3DDevice9* device=owner.device;
    for(unsigned phase=0;phase<2;++phase){unsigned frame=phase?get<unsigned>(animation.bytes,276)/2:160;put(root->prefix.bytes,672,frame);put(child->prefix.bytes,672,frame);OW_CHECK(RF455_UpdateCharacterPose(root,&pose)==RF_POSE_OK && RF455_UpdateCharacterPose(child,&pose)==RF_POSE_OK);RF455_SetCharacterDrawState(&draw.state);
        OW_CHECK(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101020,1,0)) && SUCCEEDED(device->BeginScene()));OW_CHECK(RF455_DrawCharacter455(&draw,child,world,nullptr)==RF_CHARACTER_DRAW_OK && RF455_FlushCharacterTransparency(&draw)==RF_CHARACTER_DRAW_OK && SUCCEEDED(device->EndScene()));auto pixels=capture(device);OW_CHECK(pixels.size()==256*256*4);unsigned colored=0;for(unsigned k=0;k<256*256;++k)if((get<DWORD>(pixels.data(),4*k)&0xffffff)!=0x101020)++colored;OW_CHECK(colored>1000 && colored<256*256-1000);
        std::string name="owner-frame-"+std::to_string(phase)+".bgra";file=std::fopen(name.c_str(),"wb");OW_CHECK(file && std::fwrite(pixels.data(),pixels.size(),1,file)==1);std::fclose(file);if(!phase)first=pixels;else OW_CHECK(first!=pixels);}
    OW_CHECK(modelDraws==92);RF455_DestroyAnimation(&animation,&ops.memory);RF455_DestroyCharacterRenderer(&owner,&ops.memory);OW_CHECK(memory.live.empty() && !memory.bad);return 0;
}
int gpu(const char* dll,const char* fixture){
    HMODULE runtime=LoadLibraryA(dll);OW_CHECK(runtime);RF455PoseMath pose={};RF455CharacterDrawMath math={};RF455ShaderApi shader={};RF455CharacterTextureApi texture={};
#define EXPORT(member,name) member=reinterpret_cast<decltype(member)>(GetProcAddress(runtime,name));OW_CHECK(member)
    EXPORT(pose.matrix.inverse,"D3DXMatrixInverse");EXPORT(pose.matrix.multiply,"D3DXMatrixMultiply");EXPORT(pose.slerp,"D3DXQuaternionSlerp");EXPORT(pose.rotationQuaternion,"D3DXMatrixRotationQuaternion");EXPORT(shader.compile,"D3DXCompileShader");EXPORT(shader.sprite,"D3DXCreateSprite");EXPORT(texture.memory2D,"D3DXCreateTextureFromFileInMemoryEx");EXPORT(texture.memoryCube,"D3DXCreateCubeTextureFromFileInMemoryEx");EXPORT(texture.file2D,"D3DXCreateTextureFromFileA");math.matrix=pose.matrix;EXPORT(math.transform3,"D3DXVec3Transform");EXPORT(math.ortho,"D3DXMatrixOrthoLH");math.ticks=ticks;math.sineFloat=sine;math.cosineFloat=cosine;
#undef EXPORT
    char directory[MAX_PATH];OW_CHECK(GetSystemDirectoryA(directory,MAX_PATH));HMODULE library=LoadLibraryA((std::string(directory)+"\\d3d9.dll").c_str());OW_CHECK(library);auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(library,"Direct3DCreate9"));OW_CHECK(create);IDirect3D9* api=create(D3D_SDK_VERSION);OW_CHECK(api);
    HWND window=CreateWindowExA(0,"STATIC","RF455 own renderer owner",WS_OVERLAPPEDWINDOW,0,0,256,256,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);OW_CHECK(window);D3DPRESENT_PARAMETERS pp={};pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.BackBufferWidth=pp.BackBufferHeight=256;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D16;IDirect3DDevice9* device=nullptr;OW_CHECK(SUCCEEDED(api->CreateDevice(0,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&device)));
    RF455CharacterRenderer owner;RF455_ConstructCharacterRenderer(&owner);RF455RendererShared shared={};RF455_ConstructShaderManager(&shared.shaders);OW_CHECK(RF455_SetCharacterRendererDevice(&owner,&shared,device,&shader,nullptr)==11 && owner.sprite && shared.shaders.count==12);
    IUnknown* sprite=owner.sprite;auto* declaration=shared.declaration64;auto* programs=shared.shaders.programs;unsigned expectedSpecular=owner.specular;OW_CHECK(RF455_SetCharacterRendererDevice(&owner,&shared,device,&shader,nullptr)==static_cast<int>(expectedSpecular) && owner.sprite==sprite && shared.declaration64==declaration && shared.shaders.programs==programs);
    auto* oldApi=RF455_SetCharacterTextureApi(&texture);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);OW_CHECK(model(fixture,owner,shared,pose,math)==0);OW_CHECK(shared.shaders.count==12 && shared.declaration64==declaration);
    for(unsigned i=0;i<8;++i)device->SetTexture(i,nullptr);device->SetStreamSource(0,nullptr,0,0);device->SetIndices(nullptr);device->SetVertexShader(nullptr);device->SetPixelShader(nullptr);device->SetVertexDeclaration(nullptr);RF455_ReleaseShaderManager(&shared.shaders);RF455_ReleaseCharacterDeclarations(&shared.declaration64,&shared.declaration36);RF455_SetCharacterTextureApi(oldApi);RF455_SetCharacterRfsCache(oldCache);
    OW_CHECK(!device->Release() && !api->Release());DestroyWindow(window);FreeLibrary(library);FreeLibrary(runtime);return 0;
}
}
extern "C" int RF455_RunRendererOwnerChecks(const char* golden,const char* dll,const char* fixture,const char* output){
    using namespace owner455;checks=modelDraws=0;releases.clear();int result=contracts(golden);if(!result)result=gpu(dll,fixture);FILE* file=std::fopen(output,"wb");if(!file)return 240;
    std::fprintf(file,"{\"status\":\"%s\",\"checks\":%u,\"constructor_seeds\":2,\"caps_cases\":5,\"release_order\":[1,2,3,4,5,6,7,8],\"real_model_draws\":%u,\"real_frames\":2,\"heap_com_balance\":%d}\n",result?"FAIL":"PASS",checks,modelDraws,result?-1:0);std::fclose(file);return result;
}
#ifndef RF455_RENDERER_OWNER_EMBEDDED
int main(int argc,char** argv){return argc==5?RF455_RunRendererOwnerChecks(argv[1],argv[2],argv[3],argv[4]):241;}
#endif
