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
    DWORD captureTick=0;std::uint64_t captureFrame=0;
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
    bool collecting=false,captureReady=false;
    IDirect3DDevice9* captureDevice=nullptr;
    Actor captureState;
    D3DMATRIX captureWorld{};
    const void* sceneOwner=nullptr;const void* sceneVertices=nullptr;unsigned sceneVertexCount=0;
    bool fitInitialized=false;
    float envelopeMin[3]{},envelopeMax[3]{};
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
    if(!lo||!hi)return false;
    for(unsigned i=0;i<3;++i)if(!std::isfinite(lo[i])||!std::isfinite(hi[i])||lo[i]>hi[i])return false;
    D3DXVECTOR3 low(lo),high(hi);
    const D3DXVECTOR3 extent=high-low;float radius=D3DXVec3Length(&extent)*.5f+80.f;
    if(radius<1||radius>50000)return false;
    D3DXVECTOR3 sun(-.35f,.8f,-.45f);D3DXVec3Normalize(&sun,&sun);
    // World-anchored axes, independent of moving casters, camera and selection.
    // Orthographic z bounds may be negative: the resulting matrix maps the
    // complete interval to D3D's [0,1] clip depth without a perspective near cut.
    D3DXVECTOR3 origin(0,0,0),target=-sun,up(0,1,0);
    D3DXMATRIX view,projection;D3DXMatrixLookAtLH(&view,&origin,&target,&up);
    float requiredMin[3]={1e20f,1e20f,1e20f},requiredMax[3]={-1e20f,-1e20f,-1e20f};
    for(unsigned i=0;i<8;++i){D3DXVECTOR3 p(i&1?hi[0]:lo[0],i&2?hi[1]:lo[1],i&4?hi[2]:lo[2]),q;
        D3DXVec3TransformCoord(&q,&p,&view);const float values[3]={q.x,q.y,q.z};
        for(unsigned a=0;a<3;++a){requiredMin[a]=(std::min)(requiredMin[a],values[a]);requiredMax[a]=(std::max)(requiredMax[a],values[a]);}}
    auto& s=shadow;bool expanded=false;
    for(unsigned a=0;a<3;++a){
        // Slack accommodates ordinary motion without breathing the projection.
        // Outliers expand the envelope; no caster is omitted to stabilize it.
        const float quantum=a==2?128.f:64.f;
        const float margin=(std::max)(80.f,(requiredMax[a]-requiredMin[a])*.20f);
        if(!s.fitInitialized||requiredMin[a]<s.envelopeMin[a]+8.f){
            s.envelopeMin[a]=std::floor((requiredMin[a]-margin)/quantum)*quantum;expanded=true;}
        if(!s.fitInitialized||requiredMax[a]>s.envelopeMax[a]-8.f){
            s.envelopeMax[a]=std::ceil((requiredMax[a]+margin)/quantum)*quantum;expanded=true;}
    }
    float boundsMin[2],boundsMax[2];
    for(unsigned a=0;a<2;++a){
        const float span=s.envelopeMax[a]-s.envelopeMin[a];
        const float texel=span/float(s.info.resolution-2);
        const float center=(s.envelopeMin[a]+s.envelopeMax[a])*.5f;
        const float snapped=std::floor(center/texel+.5f)*texel;
        // One guard texel each side keeps snapping from clipping the envelope.
        const float half=texel*float(s.info.resolution)*.5f;
        boundsMin[a]=snapped-half;boundsMax[a]=snapped+half;
        if(a==0)s.info.worldUnitsPerTexelX=texel;else s.info.worldUnitsPerTexelY=texel;
    }
    D3DXMatrixOrthoOffCenterLH(&projection,boundsMin[0],boundsMax[0],boundsMin[1],boundsMax[1],s.envelopeMin[2],s.envelopeMax[2]);
    const D3DXMATRIX result=view*projection;
    s.info.lightMatrixMaxDelta=0;
    if(s.fitInitialized){for(unsigned i=0;i<16;++i)s.info.lightMatrixMaxDelta=(std::max)(s.info.lightMatrixMaxDelta,
        std::fabs(reinterpret_cast<const float*>(&result)[i]-reinterpret_cast<const float*>(&s.light)[i]));}
    if(!s.fitInitialized||s.info.lightMatrixMaxDelta>0)++s.info.lightMatrixChanges;
    if(s.fitInitialized&&expanded)++s.info.fitExpansions;
    s.light=result;s.fitInitialized=true;return true;
}
}
void RF455_InvalidateLobbyShadows(bool discardActors){
    auto& s=shadow;s.valid=false;s.info.bspDraws=s.info.actorDraws=0;
    if(discardActors){for(auto& a:s.actors)a.release();s.actors.clear();s.info.pendingActors=0;s.captureReady=false;s.info.actorCaptureComplete=false;}
}
bool RF455_BeginLobbyActorCapture(IDirect3DDevice9* d){
    auto& s=shadow;RF455_InvalidateLobbyShadows(true);
    if(s.collecting||!d||s.info.active)return false;
    auto& a=s.captureState;a.release();
    HRESULT hr=d->GetTransform(D3DTS_WORLD,&s.captureWorld);
    if(SUCCEEDED(hr))hr=d->GetStreamSource(0,&a.vb,&a.offset,&a.stride);
    if(SUCCEEDED(hr))hr=d->GetIndices(&a.ib);
    if(SUCCEEDED(hr))hr=d->GetVertexDeclaration(&a.decl);
    if(SUCCEEDED(hr))hr=d->GetVertexShaderConstantF(100,a.bones,120);
    if(FAILED(hr)){a.release();fail(hr,"actor capture state");++s.info.actorCaptureFailures;return false;}
    s.captureDevice=d;s.collecting=true;return true;
}
bool RF455_QueueLobbyActorShadow(IDirect3DVertexBuffer9* vb,IDirect3DIndexBuffer9* ib,IDirect3DVertexDeclaration9* decl,
    unsigned start,unsigned vertices,unsigned index,unsigned triangles,bool indexed,const float* palette){
    auto& s=shadow;if(!s.collecting||!vb||!decl||(indexed&&!ib)||!palette||!triangles||s.actors.size()>=4096)return false;
    for(unsigned i=0;i<480;++i)if(!std::isfinite(palette[i]))return false;
    Actor a;a.vb=vb;a.ib=indexed?ib:nullptr;a.decl=decl;a.stride=64;a.start=start;a.vertices=vertices;
    a.index=index;a.triangles=triangles;a.indexed=indexed;std::memcpy(a.bones,palette,sizeof a.bones);
    a.captureTick=GetTickCount();a.captureFrame=s.info.frames+1;
    // Allocate before AddRef so an allocation exception cannot leak resources.
    s.actors.push_back(a);vb->AddRef();decl->AddRef();if(a.ib)a.ib->AddRef();
    s.info.pendingActors=unsigned(s.actors.size());return true;
}
bool RF455_EndLobbyActorCapture(bool success){
    auto& s=shadow;if(!s.collecting)return false;
    auto* d=s.captureDevice;auto& before=s.captureState;Actor after;D3DMATRIX world{};
    HRESULT hr=d->GetTransform(D3DTS_WORLD,&world);
    if(SUCCEEDED(hr))hr=d->GetStreamSource(0,&after.vb,&after.offset,&after.stride);
    if(SUCCEEDED(hr))hr=d->GetIndices(&after.ib);
    if(SUCCEEDED(hr))hr=d->GetVertexDeclaration(&after.decl);
    if(SUCCEEDED(hr))hr=d->GetVertexShaderConstantF(100,after.bones,120);
    ++s.info.actorCaptureStateChecks;
    const bool intact=SUCCEEDED(hr)&&!std::memcmp(&world,&s.captureWorld,sizeof world)&&
        before.vb==after.vb&&before.ib==after.ib&&before.decl==after.decl&&before.offset==after.offset&&before.stride==after.stride&&
        !std::memcmp(before.bones,after.bones,sizeof before.bones);
    if(!intact){
        // A future collector must not silently change the visible pass state.
        d->SetTransform(D3DTS_WORLD,&s.captureWorld);d->SetStreamSource(0,before.vb,before.offset,before.stride);
        d->SetIndices(before.ib);d->SetVertexDeclaration(before.decl);d->SetVertexShaderConstantF(100,before.bones,120);
        fail(FAILED(hr)?hr:E_UNEXPECTED,"actor capture changed D3D state");
    }
    after.release();before.release();s.captureDevice=nullptr;s.collecting=false;
    if(!success||!intact){RF455_InvalidateLobbyShadows(true);++s.info.actorCaptureFailures;
        if(intact)fail(E_FAIL,"actor pose capture incomplete");return false;}
    s.captureReady=true;s.info.actorCaptureComplete=true;++s.info.actorCaptureFrames;return true;
}
void RF455_SetLobbyShadowScene(const void* owner,const void* vertices,unsigned vertexCount){
    auto& s=shadow;if(s.sceneOwner==owner&&s.sceneVertices==vertices&&s.sceneVertexCount==vertexCount)return;
    // Fresh current-frame packets are independent of BSP ownership. Everything
    // else is discarded; there is no previous-frame observer fallback.
    RF455_InvalidateLobbyShadows(!s.captureReady);s.sceneOwner=owner;s.sceneVertices=vertices;s.sceneVertexCount=vertexCount;
    s.fitInitialized=false;++s.info.sceneGeneration;
}
bool RF455_BeginLobbyShadows(IDirect3DDevice9* d,const float* lo,const float* hi){
    auto& s=shadow;RF455_InvalidateLobbyShadows(false);
    if(!d||s.info.active||!s.captureReady||!RF455_GetLobbyPostTelemetry().active||!initialize(d)||!fit(lo,hi))return false;
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
    s.info.actorPoseAgeMsMax=s.info.actorPoseAgeFramesMax=0;
    HRESULT setup=d->SetVertexShader(s.actorVS);
    if(SUCCEEDED(setup))setup=d->SetPixelShader(s.ps);
    if(SUCCEEDED(setup))setup=d->SetVertexShaderConstantF(4,reinterpret_cast<float*>(&s.light),4);
    for(auto& a:s.actors){
        s.info.actorPoseAgeMsMax=(std::max)(s.info.actorPoseAgeMsMax,unsigned(GetTickCount()-a.captureTick));
        const auto age=s.info.frames+1-a.captureFrame;
        s.info.actorPoseAgeFramesMax=(std::max)(s.info.actorPoseAgeFramesMax,unsigned((std::min)(age,std::uint64_t(0xffffffffu))));
        HRESULT hr=setup;
        if(SUCCEEDED(hr))hr=d->SetStreamSource(0,a.vb,a.offset,a.stride);
        if(SUCCEEDED(hr))hr=d->SetVertexDeclaration(a.decl);
        if(SUCCEEDED(hr))hr=d->SetIndices(a.ib);
        if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(100,a.bones,120);
        if(SUCCEEDED(hr))hr=a.indexed?d->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,a.start,a.vertices,a.index,a.triangles):d->DrawPrimitive(D3DPT_TRIANGLELIST,a.start,a.triangles);
        if(FAILED(hr))fail(hr,"actor caster");else ++s.info.actorDraws;a.release();
    }
    s.actors.clear();s.info.pendingActors=0;s.captureReady=false;++s.info.frames;restore(d);s.valid=s.info.errors==s.errorsAtBegin&&s.info.bspDraws>0;
}
void RF455_RecordLobbyActorShadow(IDirect3DDevice9* d,unsigned mode,unsigned start,unsigned vertices,unsigned index,unsigned triangles,bool indexed){
    // Compatibility entry point only. Late visible rendering must never enqueue
    // tomorrow's pose; all casters now come from the explicit current capture.
    (void)d;(void)mode;(void)start;(void)vertices;(void)index;(void)triangles;(void)indexed;
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
    auto& s=shadow;for(auto& a:s.actors)a.release();s.actors.clear();s.captureState.release();
    for(auto*& target:s.targets)drop(target);drop(s.oldDepth);drop(s.saved);drop(s.decl);
    drop(s.bspVS);drop(s.actorVS);drop(s.ps);drop(s.depth);drop(s.surface);drop(s.texture);s=Shadow{};
}
