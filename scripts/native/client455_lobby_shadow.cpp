#include "client455_lobby_shadow.h"
#include "client455_lobby_post.h"
#include "client455_draw_observer.h"
#include <d3dx9.h>
#include <algorithm>
#include <vector>
#include <cstring>
#include <cmath>
namespace {
template<class T>void drop(T*& p){if(p){p->Release();p=nullptr;}}
struct Actor {
    IDirect3DVertexBuffer9* vb=nullptr;IDirect3DIndexBuffer9* ib=nullptr;
    IDirect3DVertexDeclaration9* decl=nullptr;
    unsigned offset=0,stride=0,start=0,vertices=0,index=0,triangles=0;
    bool indexed=false;float bones[120*4]{};
    void release(){drop(vb);drop(ib);drop(decl);}
};
struct Shadow {
    IDirect3DTexture9* texture=nullptr;IDirect3DSurface9* surface=nullptr,*depth=nullptr;
    IDirect3DSurface9* targets[4]{},*oldDepth=nullptr;
    IDirect3DStateBlock9* saved=nullptr;
    IDirect3DVertexShader9* bspVS=nullptr,*actorVS=nullptr;
    IDirect3DPixelShader9* ps=nullptr;
    IDirect3DVertexDeclaration9* decl=nullptr;
    D3DVIEWPORT9 viewport{};D3DXMATRIX light;unsigned targetCount=1;
    RF455LobbyShadowTelemetry info{};bool failed=false,valid=false;
    std::uint64_t errorsAtBegin=0;
    std::vector<Actor> actors;
} shadow;
const char source[]=R"HLSL(
row_major float4x4 world:register(c0);
row_major float4x4 light:register(c4);
float4x4 bones[30]:register(c100);
struct Vertex{float4 position:POSITION0;float depth:TEXCOORD0;};
Vertex BSP(float3 p:POSITION0){Vertex o;o.position=mul(mul(float4(p,1),world),light);o.depth=o.position.z;return o;}
struct Skin{float3 position:POSITION0;float3 weights:BLENDWEIGHT0;int4 indices:BLENDINDICES0;};
Vertex Skinned(Skin i){
    float4 w=float4(i.weights,1-dot(i.weights,1));float4 p=float4(i.position,1);
    float4 wp=mul(p,bones[i.indices.x])*w.x+mul(p,bones[i.indices.y])*w.y+mul(p,bones[i.indices.z])*w.z+mul(p,bones[i.indices.w])*w.w;
    Vertex o;o.position=mul(wp,light);o.depth=o.position.z;return o;
}
float4 PS(Vertex i):COLOR0{return i.depth;}
)HLSL";
void fail(HRESULT hr,const char* stage){++shadow.info.errors;shadow.info.error=hr;strncpy_s(shadow.info.stage,stage,_TRUNCATE);}
bool program(IDirect3DDevice9* d,const char* entry,IDirect3DVertexShader9** vs){
    ID3DXBuffer *code=nullptr,*errors=nullptr;
    HRESULT hr=D3DXCompileShader(source,UINT(std::strlen(source)),nullptr,nullptr,entry,vs?"vs_3_0":"ps_3_0",D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
    if(FAILED(hr)&&errors)OutputDebugStringA(static_cast<const char*>(errors->GetBufferPointer()));drop(errors);
    if(SUCCEEDED(hr))hr=vs?d->CreateVertexShader(static_cast<DWORD*>(code->GetBufferPointer()),vs):d->CreatePixelShader(static_cast<DWORD*>(code->GetBufferPointer()),&shadow.ps);
    drop(code);if(FAILED(hr)){fail(hr,entry);return false;}return true;
}
bool initialize(IDirect3DDevice9* d){
    auto& s=shadow;if(s.info.ready)return true;if(s.failed)return false;s.failed=true;
    D3DCAPS9 caps{};HRESULT hr=d->GetDeviceCaps(&caps);
    if(FAILED(hr)||caps.VertexShaderVersion<D3DVS_VERSION(3,0)||caps.PixelShaderVersion<D3DPS_VERSION(3,0)){fail(D3DERR_NOTAVAILABLE,"SM3");return false;}
    s.info.resolution=(std::min)(4096u,unsigned((std::min)(caps.MaxTextureWidth,caps.MaxTextureHeight)));
    s.targetCount=(std::min)(4u,unsigned(caps.NumSimultaneousRTs));
    IDirect3D9* api=nullptr;D3DDEVICE_CREATION_PARAMETERS creation{};D3DDISPLAYMODE display{};
    hr=d->GetDirect3D(&api);if(SUCCEEDED(hr))hr=d->GetCreationParameters(&creation);if(SUCCEEDED(hr))hr=d->GetDisplayMode(0,&display);
    if(SUCCEEDED(hr))hr=api->CheckDeviceFormat(creation.AdapterOrdinal,creation.DeviceType,display.Format,D3DUSAGE_RENDERTARGET,D3DRTYPE_TEXTURE,D3DFMT_R32F);
    D3DFORMAT depthFormat=D3DFMT_D24X8;
    if(SUCCEEDED(hr)&&FAILED(api->CheckDepthStencilMatch(creation.AdapterOrdinal,creation.DeviceType,display.Format,D3DFMT_R32F,depthFormat)))depthFormat=D3DFMT_D16;
    if(SUCCEEDED(hr))hr=api->CheckDepthStencilMatch(creation.AdapterOrdinal,creation.DeviceType,display.Format,D3DFMT_R32F,depthFormat);
    drop(api);if(FAILED(hr)){fail(hr,"R32F/depth capability");return false;}
    hr=d->CreateTexture(s.info.resolution,s.info.resolution,1,D3DUSAGE_RENDERTARGET,D3DFMT_R32F,D3DPOOL_DEFAULT,&s.texture,nullptr);
    if(SUCCEEDED(hr))hr=s.texture->GetSurfaceLevel(0,&s.surface);
    if(SUCCEEDED(hr))hr=d->CreateDepthStencilSurface(s.info.resolution,s.info.resolution,depthFormat,D3DMULTISAMPLE_NONE,0,TRUE,&s.depth,nullptr);
    if(SUCCEEDED(hr))hr=d->CreateStateBlock(D3DSBT_ALL,&s.saved);
    const D3DVERTEXELEMENT9 elements[]={{0,0,D3DDECLTYPE_FLOAT3,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_POSITION,0},D3DDECL_END()};
    if(SUCCEEDED(hr))hr=d->CreateVertexDeclaration(elements,&s.decl);
    if(FAILED(hr)){fail(hr,"shadow resources");return false;}
    if(!program(d,"BSP",&s.bspVS)||!program(d,"Skinned",&s.actorVS)||!program(d,"PS",nullptr))return false;
    s.info.bytes=std::uint64_t(s.info.resolution)*s.info.resolution*(depthFormat==D3DFMT_D16?6:8);
    s.info.ready=true;s.failed=false;return true;
}
void restore(IDirect3DDevice9* d){
    auto& s=shadow;auto check=[](HRESULT hr){if(FAILED(hr))fail(hr,"restore");};
    check(d->SetDepthStencilSurface(nullptr));
    for(unsigned i=0;i<s.targetCount;++i){check(d->SetRenderTarget(i,s.targets[i]));drop(s.targets[i]);}
    check(d->SetDepthStencilSurface(s.oldDepth));drop(s.oldDepth);
    if(s.saved)check(s.saved->Apply());check(d->SetViewport(&s.viewport));s.info.active=false;
}
bool fit(const float* lo,const float* hi){
    for(unsigned i=0;i<3;++i)if(!std::isfinite(lo[i])||!std::isfinite(hi[i])||lo[i]>hi[i])return false;
    D3DXVECTOR3 low(lo),high(hi),center=(low+high)*.5f;
    const D3DXVECTOR3 extent=high-low;float radius=D3DXVec3Length(&extent)*.5f+80.f;
    if(radius<1||radius>50000)return false;
    D3DXVECTOR3 sun(-.35f,.8f,-.45f);D3DXVec3Normalize(&sun,&sun);
    D3DXVECTOR3 eye=center+sun*(radius*2+100),up(0,1,0);
    D3DXMATRIX view,projection;D3DXMatrixLookAtLH(&view,&eye,&center,&up);
    float x0=1e20f,y0=x0,z0=x0,x1=-x0,y1=-x0,z1=-x0;
    for(unsigned i=0;i<8;++i){D3DXVECTOR3 p(i&1?hi[0]:lo[0],i&2?hi[1]:lo[1],i&4?hi[2]:lo[2]),q;
        D3DXVec3TransformCoord(&q,&p,&view);x0=(std::min)(x0,q.x);x1=(std::max)(x1,q.x);y0=(std::min)(y0,q.y);y1=(std::max)(y1,q.y);z0=(std::min)(z0,q.z);z1=(std::max)(z1,q.z);}
    D3DXMatrixOrthoOffCenterLH(&projection,x0-35,x1+35,y0-35,y1+35,(std::max)(1.f,z0-80),z1+80);
    shadow.light=view*projection;return true;
}
}
void RF455_InvalidateLobbyShadows(bool discardActors){
    auto& s=shadow;s.valid=false;s.info.bspDraws=s.info.actorDraws=0;
    if(discardActors){for(auto& a:s.actors)a.release();s.actors.clear();}
}
bool RF455_BeginLobbyShadows(IDirect3DDevice9* d,const float* lo,const float* hi){
    auto& s=shadow;RF455_InvalidateLobbyShadows(false);
    if(!d||s.info.active||!RF455_GetLobbyPostTelemetry().active||!initialize(d)||!fit(lo,hi))return false;
    HRESULT hr=s.saved->Capture();if(FAILED(hr)){fail(hr,"capture");return false;}
    for(unsigned i=0;i<s.targetCount&&SUCCEEDED(hr);++i){
        hr=d->GetRenderTarget(i,&s.targets[i]);
        if(i&&hr==D3DERR_NOTFOUND)hr=S_OK;
    }
    if(SUCCEEDED(hr))hr=d->GetDepthStencilSurface(&s.oldDepth);
    if(SUCCEEDED(hr))hr=d->GetViewport(&s.viewport);
    if(FAILED(hr)){fail(hr,"save targets");for(auto*& t:s.targets)drop(t);drop(s.oldDepth);return false;}
    s.errorsAtBegin=s.info.errors;
    for(unsigned i=0;i<16;++i)d->SetTexture(i,nullptr);
    hr=d->SetDepthStencilSurface(nullptr);
    for(unsigned i=1;i<s.targetCount&&SUCCEEDED(hr);++i)hr=d->SetRenderTarget(i,nullptr);
    if(SUCCEEDED(hr))hr=d->SetRenderTarget(0,s.surface);if(SUCCEEDED(hr))hr=d->SetDepthStencilSurface(s.depth);
    D3DVIEWPORT9 vp{0,0,s.info.resolution,s.info.resolution,0,1};if(SUCCEEDED(hr))hr=d->SetViewport(&vp);
    d->SetRenderState(D3DRS_SCISSORTESTENABLE,FALSE);d->SetRenderState(D3DRS_SRGBWRITEENABLE,FALSE);
    d->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);d->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);
    d->SetRenderState(D3DRS_ZENABLE,TRUE);d->SetRenderState(D3DRS_ZWRITEENABLE,TRUE);d->SetRenderState(D3DRS_ZFUNC,D3DCMP_LESSEQUAL);
    d->SetRenderState(D3DRS_COLORWRITEENABLE,0xf);d->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE);
    d->SetRenderState(D3DRS_FOGENABLE,FALSE);d->SetRenderState(D3DRS_STENCILENABLE,FALSE);d->SetRenderState(D3DRS_CLIPPLANEENABLE,0);
    d->SetRenderState(D3DRS_DEPTHBIAS,0);d->SetRenderState(D3DRS_SLOPESCALEDEPTHBIAS,0);
    if(SUCCEEDED(hr))hr=d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xffffffff,1,0);
    if(FAILED(hr)){fail(hr,"bind/clear");restore(d);return false;}
    RF455_SetGeometryObserver(&RF455_RecordLobbyActorShadow);
    s.info.active=true;return true;
}
bool RF455_LobbyShadowPass(){return shadow.info.active;}
void RF455_DrawLobbyShadowGroup(IDirect3DDevice9* d,unsigned minimum,unsigned vertices,unsigned start,unsigned triangles){
    auto& s=shadow;if(!s.info.active)return;
    D3DXMATRIX world;HRESULT hr=d->GetTransform(D3DTS_WORLD,&world);
    if(SUCCEEDED(hr))hr=d->SetVertexDeclaration(s.decl);if(SUCCEEDED(hr))hr=d->SetVertexShader(s.bspVS);if(SUCCEEDED(hr))hr=d->SetPixelShader(s.ps);
    if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(0,reinterpret_cast<float*>(&world),4);
    if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(4,reinterpret_cast<float*>(&s.light),4);
    d->SetRenderState(D3DRS_ZWRITEENABLE,TRUE);
    if(SUCCEEDED(hr))hr=d->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,minimum,vertices,start,triangles);
    if(FAILED(hr))fail(hr,"BSP caster");else ++s.info.bspDraws;
}
void RF455_EndLobbyShadows(IDirect3DDevice9* d){
    auto& s=shadow;if(!s.info.active)return;
    HRESULT setup=d->SetVertexShader(s.actorVS);
    if(SUCCEEDED(setup))setup=d->SetPixelShader(s.ps);
    if(SUCCEEDED(setup))setup=d->SetVertexShaderConstantF(4,reinterpret_cast<float*>(&s.light),4);
    for(auto& a:s.actors){
        HRESULT hr=setup;
        if(SUCCEEDED(hr))hr=d->SetStreamSource(0,a.vb,a.offset,a.stride);
        if(SUCCEEDED(hr))hr=d->SetVertexDeclaration(a.decl);
        if(SUCCEEDED(hr))hr=d->SetIndices(a.ib);
        if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(100,a.bones,120);
        if(SUCCEEDED(hr))hr=a.indexed?d->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,a.start,a.vertices,a.index,a.triangles):d->DrawPrimitive(D3DPT_TRIANGLELIST,a.start,a.triangles);
        if(FAILED(hr))fail(hr,"actor caster");else ++s.info.actorDraws;a.release();
    }
    s.actors.clear();++s.info.frames;restore(d);s.valid=s.info.errors==s.errorsAtBegin&&s.info.bspDraws>0;
}
void RF455_RecordLobbyActorShadow(IDirect3DDevice9* d,unsigned mode,unsigned start,unsigned vertices,unsigned index,unsigned triangles,bool indexed){
    auto& s=shadow;if(!s.info.ready||s.info.active||!RF455_GetLobbyPostTelemetry().active||mode!=4||s.actors.size()>=256)return;
    // Eligibility comes from the opaque draw owner. The legacy renderer leaves
    // blending enabled even for alpha=1 opaque characters.
    IDirect3DVertexShader9* vs=nullptr;d->GetVertexShader(&vs);if(!vs)return;drop(vs);
    Actor a;a.start=start;a.vertices=vertices;a.index=index;a.triangles=triangles;a.indexed=indexed;
    HRESULT hr=d->GetStreamSource(0,&a.vb,&a.offset,&a.stride);
    if(SUCCEEDED(hr))hr=d->GetVertexDeclaration(&a.decl);if(indexed&&SUCCEEDED(hr))hr=d->GetIndices(&a.ib);
    if(SUCCEEDED(hr))hr=d->GetVertexShaderConstantF(100,a.bones,120);
    if(FAILED(hr)||!a.vb||!a.decl||a.stride!=64||(indexed&&!a.ib)){a.release();return;}
    // One previous frame of copied bone constants and AddRef-owned geometry.
    // No retained character/model pointers; deletion cannot invalidate casters.
    s.actors.push_back(a);
}
IDirect3DTexture9* RF455_LobbyShadowTexture(float* matrix,float* params){
    auto& s=shadow;D3DXMATRIX identity;D3DXMatrixIdentity(&identity);
    const bool ready=s.info.ready&&s.valid&&!s.info.active&&RF455_GetLobbyPostTelemetry().active;
    std::memcpy(matrix,ready?&s.light:&identity,64);params[0]=ready?1.f:0.f;
    params[1]=s.info.resolution?1.f/s.info.resolution:0;params[2]=.00015f;params[3]=.00045f;
    return ready?s.texture:nullptr;
}
RF455LobbyShadowTelemetry RF455_GetLobbyShadowTelemetry(){return shadow.info;}
void RF455_ReleaseLobbyShadows(){
    RF455_SetGeometryObserver(nullptr);
    auto& s=shadow;for(auto& a:s.actors)a.release();s.actors.clear();
    for(auto*& target:s.targets)drop(target);drop(s.oldDepth);drop(s.saved);drop(s.decl);
    drop(s.bspVS);drop(s.actorVS);drop(s.ps);drop(s.depth);drop(s.surface);drop(s.texture);s=Shadow{};
}
