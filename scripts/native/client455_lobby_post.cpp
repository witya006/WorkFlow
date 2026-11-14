#include "client455_lobby_post.h"
#include <d3dx9.h>
#include <algorithm>
#include <cstdio>
#include <cstring>

// D3D9 constraints used here:
// learn.microsoft.com/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-stretchrect
// learn.microsoft.com/windows/win32/direct3d9/d3dusage-query
// learn.microsoft.com/windows/win32/direct3d9/gamma
// Own resources only; no reuse of the legacy 512px FSE or its capture lifetime.
namespace {
template<class T> void drop(T*& p) { if (p) { p->Release(); p=nullptr; } }
constexpr D3DFORMAT format = D3DFMT_A16B16G16R16F;
enum Program { Linearize, Bright, Downsample, Blur, Composite, Copy, ProgramCount };
const char shaderSource[] = R"HLSL(
sampler2D source0 : register(s0);
sampler2D source1 : register(s1);
sampler2D source2 : register(s2);
sampler2D source3 : register(s3);
float4 stepSize : register(c0); // source texel or directional blur step
float4 settings : register(c1); // exposure, bloom threshold, soft knee, intensity
float4 encoding : register(c2); // input already linear
struct Vertex { float4 position : POSITION; float2 uv : TEXCOORD0; };
Vertex VS(Vertex v) { return v; }
float3 decode(float3 x) {
    x=max(x,0);
    return lerp(pow((x+0.055)/1.055,2.4),x/12.92,step(x,0.04045));
}
float3 encode(float3 x) {
    x=max(x,0);
    return lerp(1.055*pow(x,1.0/2.4)-0.055,12.92*x,step(x,0.0031308));
}
float4 PSLinearize(Vertex i) : COLOR0 {
    float4 c=tex2D(source0,i.uv);
    // Do not clamp HDR values or transform alpha. Compatibility decoding does
    // not retroactively make legacy lighting/blending physically linear.
    return float4(min(encoding.x>0.5?max(c.rgb,0):decode(c.rgb),65504),c.a);
}
float3 fourSamples(float2 uv) {
    float2 s=stepSize.xy*0.5;
    return (tex2D(source0,uv+float2(-s.x,-s.y)).rgb+
            tex2D(source0,uv+float2( s.x,-s.y)).rgb+
            tex2D(source0,uv+float2(-s.x, s.y)).rgb+
            tex2D(source0,uv+float2( s.x, s.y)).rgb)*0.25;
}
float4 PSBright(Vertex i) : COLOR0 {
    float3 c=max(fourSamples(i.uv),0);
    float brightness=max(c.r,max(c.g,c.b));
    float knee=max(settings.z,0.0001);
    float soft=clamp(brightness-settings.y+knee,0,2*knee);
    soft=soft*soft/(4*knee);
    float weight=max(soft,brightness-settings.y)/max(brightness,0.0001);
    return float4(c*weight,1);
}
float4 PSDownsample(Vertex i) : COLOR0 { return float4(fourSamples(i.uv),1); }
float4 PSBlur(Vertex i) : COLOR0 {
    float2 d=stepSize.xy;
    float3 c=tex2D(source0,i.uv).rgb*0.2270270270;
    c+=(tex2D(source0,i.uv+d*1.3846153846).rgb+
        tex2D(source0,i.uv-d*1.3846153846).rgb)*0.3162162162;
    c+=(tex2D(source0,i.uv+d*3.2307692308).rgb+
        tex2D(source0,i.uv-d*3.2307692308).rgb)*0.0702702703;
    return float4(c,1);
}
float3 filmic(float3 x) {
    // Neutral exposure, smooth shoulder; no tint, saturation, vignette or LUT.
    return saturate((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14));
}
float4 PSComposite(Vertex i) : COLOR0 {
    float4 c=tex2D(source0,i.uv);
    float3 glow=tex2D(source1,i.uv).rgb*0.50+
                tex2D(source2,i.uv).rgb*0.30+tex2D(source3,i.uv).rgb*0.20;
    return float4(encode(filmic(max(c.rgb+glow*settings.w,0)*settings.x)),c.a);
}
float4 PSCopy(Vertex i) : COLOR0 {
    float4 c=tex2D(source0,i.uv);
    return float4(encoding.x>0.5?encode(c.rgb):c.rgb,c.a);
}
)HLSL";

struct Target {
    IDirect3DTexture9* texture=nullptr;
    IDirect3DSurface9* surface=nullptr;
    unsigned width=0,height=0;
    void release() { drop(surface);drop(texture);width=height=0; }
    HRESULT create(IDirect3DDevice9* d,unsigned w,unsigned h) {
        width=w;height=h;
        HRESULT hr=d->CreateTexture(w,h,1,D3DUSAGE_RENDERTARGET,format,D3DPOOL_DEFAULT,&texture,nullptr);
        if (SUCCEEDED(hr)) hr=texture->GetSurfaceLevel(0,&surface);
        return hr;
    }
};
struct State {
    IDirect3DDevice9* device=nullptr; // borrowed; owner calls Release before Reset
    Target resolved,linear,bloom[3][2];
    IDirect3DSurface9* multisampled=nullptr;
    IDirect3DSurface9* depth=nullptr;
    IDirect3DVertexShader9* vertex=nullptr;
    IDirect3DPixelShader9* pixels[ProgramCount]={};
    IDirect3DVertexDeclaration9* declaration=nullptr;
    IDirect3DStateBlock9* savedState=nullptr;
    IDirect3DSurface9* oldTargets[4]={};
    IDirect3DSurface9* oldDepth=nullptr;
    D3DVIEWPORT9 oldViewport{};
    D3DSURFACE_DESC oldDescription{};
    DWORD oldSrgbWrite=FALSE;
    unsigned targetCount=1;
    D3DFORMAT originalDepthFormat=D3DFMT_UNKNOWN;
    bool initialized=false,failed=false,enabled=false,inputLinear=false;
    RF455LobbyPostTelemetry info{};
} state;

void failure(HRESULT hr,const char* stage,RF455LobbyPostStatus status=RF455LobbyPostStatus::Failed) {
    state.info.error=hr;state.info.status=status;
    std::snprintf(state.info.errorStage,sizeof(state.info.errorStage),"%s",stage);
}
void savedRelease() {
    drop(state.savedState);for(auto& rt:state.oldTargets)drop(rt);drop(state.oldDepth);
}
void resourcesRelease() {
    state.resolved.release();state.linear.release();
    for(auto& level:state.bloom)for(auto& target:level)target.release();
    drop(state.multisampled);drop(state.depth);drop(state.vertex);drop(state.declaration);
    for(auto& pixel:state.pixels)drop(pixel);
    state.initialized=false;state.info.available=false;state.info.estimatedVideoBytes=0;
}
HRESULT restoreTargets(IDirect3DDevice9* d) {
    HRESULT result=d->SetDepthStencilSurface(nullptr);
    // Unbind auxiliary targets before changing RT0's sample count/format.
    for(unsigned i=1;i<state.targetCount;++i) {
        HRESULT hr=d->SetRenderTarget(i,nullptr);if(FAILED(hr)&&SUCCEEDED(result))result=hr;
    }
    HRESULT hr=d->SetRenderTarget(0,state.oldTargets[0]);if(FAILED(hr)&&SUCCEEDED(result))result=hr;
    for(unsigned i=1;i<state.targetCount;++i) {
        hr=d->SetRenderTarget(i,state.oldTargets[i]);if(FAILED(hr)&&SUCCEEDED(result))result=hr;
    }
    hr=d->SetDepthStencilSurface(state.oldDepth);if(FAILED(hr)&&SUCCEEDED(result))result=hr;
    hr=d->SetViewport(&state.oldViewport);if(FAILED(hr)&&SUCCEEDED(result))result=hr;
    return result;
}
HRESULT restoreAll(IDirect3DDevice9* d) {
    HRESULT result=restoreTargets(d);
    if(state.savedState) {
        const HRESULT hr=state.savedState->Apply();if(FAILED(hr)&&SUCCEEDED(result))result=hr;
    }
    // A state block can contain a viewport. Restore explicitly after Apply.
    const HRESULT hr=d->SetViewport(&state.oldViewport);if(FAILED(hr)&&SUCCEEDED(result))result=hr;
    const HRESULT srgb=d->SetRenderState(D3DRS_SRGBWRITEENABLE,state.oldSrgbWrite);
    if(FAILED(srgb)&&SUCCEEDED(result))result=srgb;
    return result;
}
HRESULT compile(IDirect3DDevice9* d,const char* entry,const char* profile,Program slot=Linearize) {
    ID3DXBuffer* code=nullptr;ID3DXBuffer* errors=nullptr;
    HRESULT hr=D3DXCompileShader(shaderSource,UINT(sizeof(shaderSource)-1),nullptr,nullptr,
                                entry,profile,D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
    if(FAILED(hr)&&errors)OutputDebugStringA(static_cast<const char*>(errors->GetBufferPointer()));
    if(SUCCEEDED(hr)) {
        if(profile[0]=='v')hr=d->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&state.vertex);
        else hr=d->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&state.pixels[slot]);
    }
    drop(errors);drop(code);return hr;
}
HRESULT initialize(IDirect3DDevice9* d,const D3DSURFACE_DESC& back,D3DFORMAT desiredDepth) {
    D3DCAPS9 caps{};D3DDEVICE_CREATION_PARAMETERS creation{};D3DDISPLAYMODE display{};
    HRESULT hr=d->GetDeviceCaps(&caps);if(FAILED(hr))return hr;
    if(caps.VertexShaderVersion<D3DVS_VERSION(3,0)||caps.PixelShaderVersion<D3DPS_VERSION(3,0)||
       caps.MaxTextureWidth<back.Width||caps.MaxTextureHeight<back.Height)return D3DERR_NOTAVAILABLE;
    IDirect3D9* api=nullptr;hr=d->GetDirect3D(&api);if(FAILED(hr))return hr;
    hr=d->GetCreationParameters(&creation);
    if(SUCCEEDED(hr))hr=api->GetAdapterDisplayMode(creation.AdapterOrdinal,&display);
    if(SUCCEEDED(hr))hr=api->CheckDeviceFormat(creation.AdapterOrdinal,creation.DeviceType,display.Format,
        D3DUSAGE_RENDERTARGET|D3DUSAGE_QUERY_FILTER|D3DUSAGE_QUERY_POSTPIXELSHADER_BLENDING,D3DRTYPE_TEXTURE,format);
    if(FAILED(hr)){drop(api);return hr;}
    IDirect3DSwapChain9* chain=nullptr;D3DPRESENT_PARAMETERS present{};
    hr=d->GetSwapChain(0,&chain);if(SUCCEEDED(hr))hr=chain->GetPresentParameters(&present);drop(chain);
    if(FAILED(hr)){drop(api);return hr;}
    // Keep the existing MSAA quality where supported; fall back through2x/noAA.
    // Colour and depth use exactly the same type/quality. No implicit downgrade
    // is hidden: telemetry records the actual type and format.
    const D3DMULTISAMPLE_TYPE candidates[]={back.MultiSampleType,D3DMULTISAMPLE_2_SAMPLES,D3DMULTISAMPLE_NONE};
    const D3DFORMAT depths[]={desiredDepth,D3DFMT_D24S8,D3DFMT_D16};
    bool found=false;D3DMULTISAMPLE_TYPE samples=D3DMULTISAMPLE_NONE;DWORD quality=0;D3DFORMAT depthFormat=D3DFMT_UNKNOWN;
    for(auto candidate:candidates) {
        // NONMASKABLE does not specify a sample count; do not invent one for
        // the allocation budget or silently select an arbitrary quality mode.
        if(candidate==D3DMULTISAMPLE_NONMASKABLE)continue;
        if(candidate==D3DMULTISAMPLE_2_SAMPLES&&back.MultiSampleType<D3DMULTISAMPLE_2_SAMPLES)continue;
        DWORD colorLevels=0;
        if(FAILED(api->CheckDeviceMultiSampleType(creation.AdapterOrdinal,creation.DeviceType,format,present.Windowed,candidate,&colorLevels)))continue;
        for(auto depth:depths) {
            if(depth==D3DFMT_UNKNOWN)continue;
            DWORD depthLevels=0;
            if(FAILED(api->CheckDeviceFormat(creation.AdapterOrdinal,creation.DeviceType,display.Format,D3DUSAGE_DEPTHSTENCIL,D3DRTYPE_SURFACE,depth))||
               FAILED(api->CheckDepthStencilMatch(creation.AdapterOrdinal,creation.DeviceType,display.Format,format,depth))||
               FAILED(api->CheckDeviceMultiSampleType(creation.AdapterOrdinal,creation.DeviceType,depth,present.Windowed,candidate,&depthLevels)))continue;
            samples=candidate;depthFormat=depth;
            const DWORD levels=(std::min)(colorLevels,depthLevels);
            quality=candidate==D3DMULTISAMPLE_NONE?0:(std::min)(back.MultiSampleQuality,levels?levels-1:0);
            found=true;break;
        }
        if(found)break;
    }
    drop(api);if(!found)return D3DERR_NOTAVAILABLE;
    state.targetCount=(std::min)(4u,unsigned(caps.NumSimultaneousRTs));
    hr=state.resolved.create(d,back.Width,back.Height);if(FAILED(hr))return hr;
    if(samples!=D3DMULTISAMPLE_NONE) {
        hr=d->CreateRenderTarget(back.Width,back.Height,format,samples,quality,FALSE,&state.multisampled,nullptr);
        if(FAILED(hr))return hr;
    }
    hr=d->CreateDepthStencilSurface(back.Width,back.Height,depthFormat,samples,quality,TRUE,&state.depth,nullptr);
    if(FAILED(hr))return hr;
    hr=state.linear.create(d,back.Width,back.Height);if(FAILED(hr))return hr;
    std::uint64_t bytes=std::uint64_t(back.Width)*back.Height*16;
    const unsigned sampleCount=samples==D3DMULTISAMPLE_NONE?1:unsigned(samples);
    if(state.multisampled)bytes+=std::uint64_t(back.Width)*back.Height*8*sampleCount;
    bytes+=std::uint64_t(back.Width)*back.Height*(depthFormat==D3DFMT_D16?2:4)*sampleCount;
    for(unsigned level=0;level<3;++level) {
        const unsigned w=(std::max)(1u,back.Width>>(level+1)),h=(std::max)(1u,back.Height>>(level+1));
        for(auto& target:state.bloom[level]) {hr=target.create(d,w,h);if(FAILED(hr))return hr;bytes+=std::uint64_t(w)*h*8;}
    }
    hr=compile(d,"VS","vs_3_0");if(FAILED(hr))return hr;
    const char* entries[]={"PSLinearize","PSBright","PSDownsample","PSBlur","PSComposite","PSCopy"};
    for(unsigned i=0;i<ProgramCount;++i){hr=compile(d,entries[i],"ps_3_0",Program(i));if(FAILED(hr))return hr;}
    const D3DVERTEXELEMENT9 elements[]={
        {0,0,D3DDECLTYPE_FLOAT4,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_POSITION,0},
        {0,16,D3DDECLTYPE_FLOAT2,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_TEXCOORD,0},D3DDECL_END()};
    hr=d->CreateVertexDeclaration(elements,&state.declaration);if(FAILED(hr))return hr;
    state.initialized=true;state.info.available=true;state.info.estimatedVideoBytes=bytes;
    state.info.colorFormat=format;state.info.depthFormat=depthFormat;state.info.multisampleCount=sampleCount;state.info.multisampleType=samples;
    state.info.width=back.Width;state.info.height=back.Height;
    return S_OK;
}
HRESULT snapshot(IDirect3DDevice9* d) {
    HRESULT hr=d->GetRenderTarget(0,&state.oldTargets[0]);if(FAILED(hr))return hr;
    for(unsigned i=1;i<state.targetCount;++i){hr=d->GetRenderTarget(i,&state.oldTargets[i]);if(FAILED(hr)&&hr!=D3DERR_NOTFOUND)return hr;}
    hr=d->GetDepthStencilSurface(&state.oldDepth);if(FAILED(hr)&&hr!=D3DERR_NOTFOUND)return hr;
    hr=d->GetViewport(&state.oldViewport);if(FAILED(hr))return hr;
    hr=d->GetRenderState(D3DRS_SRGBWRITEENABLE,&state.oldSrgbWrite);if(FAILED(hr))return hr;
    hr=d->CreateStateBlock(D3DSBT_ALL,&state.savedState);if(FAILED(hr))return hr;
    return state.savedState->Capture();
}
HRESULT postState(IDirect3DDevice9* d) {
#define POST(call) do { const HRESULT hr=(call);if(FAILED(hr))return hr; } while(0)
    POST(d->SetDepthStencilSurface(nullptr));
    for(unsigned i=1;i<state.targetCount;++i)POST(d->SetRenderTarget(i,nullptr));
    POST(d->SetVertexShader(state.vertex));POST(d->SetVertexDeclaration(state.declaration));
    POST(d->SetStreamSourceFreq(0,1));
    const struct {D3DRENDERSTATETYPE key;DWORD value;} settings[]={
        {D3DRS_ZENABLE,FALSE},{D3DRS_ZWRITEENABLE,FALSE},{D3DRS_STENCILENABLE,FALSE},
        {D3DRS_ALPHATESTENABLE,FALSE},{D3DRS_ALPHABLENDENABLE,FALSE},{D3DRS_SEPARATEALPHABLENDENABLE,FALSE},
        {D3DRS_FOGENABLE,FALSE},{D3DRS_LIGHTING,FALSE},{D3DRS_CULLMODE,D3DCULL_NONE},
        {D3DRS_SCISSORTESTENABLE,FALSE},{D3DRS_CLIPPLANEENABLE,0},{D3DRS_SRGBWRITEENABLE,FALSE},
        {D3DRS_FILLMODE,D3DFILL_SOLID},{D3DRS_COLORWRITEENABLE,15},{D3DRS_MULTISAMPLEMASK,0xffffffffu},
        {D3DRS_MULTISAMPLEANTIALIAS,TRUE}};
    for(const auto& setting:settings)POST(d->SetRenderState(setting.key,setting.value));
    for(unsigned sampler=0;sampler<4;++sampler){
        POST(d->SetSamplerState(sampler,D3DSAMP_ADDRESSU,D3DTADDRESS_CLAMP));
        POST(d->SetSamplerState(sampler,D3DSAMP_ADDRESSV,D3DTADDRESS_CLAMP));
        POST(d->SetSamplerState(sampler,D3DSAMP_MINFILTER,D3DTEXF_LINEAR));
        POST(d->SetSamplerState(sampler,D3DSAMP_MAGFILTER,D3DTEXF_LINEAR));
        POST(d->SetSamplerState(sampler,D3DSAMP_MIPFILTER,D3DTEXF_NONE));
        POST(d->SetSamplerState(sampler,D3DSAMP_SRGBTEXTURE,FALSE));
        POST(d->SetSamplerState(sampler,D3DSAMP_MAXMIPLEVEL,0));
        POST(d->SetSamplerState(sampler,D3DSAMP_MIPMAPLODBIAS,0));
    }
    return S_OK;
#undef POST
}
HRESULT pass(IDirect3DDevice9* d,IDirect3DSurface9* destination,unsigned width,unsigned height,
             Program shader,IDirect3DTexture9* first,float stepX=0,float stepY=0,
             IDirect3DTexture9* second=nullptr,IDirect3DTexture9* third=nullptr,IDirect3DTexture9* fourth=nullptr) {
    // A texture cannot remain bound for sampling when it becomes a target.
    for(unsigned i=0;i<4;++i){const HRESULT hr=d->SetTexture(i,nullptr);if(FAILED(hr))return hr;}
    HRESULT hr=d->SetRenderTarget(0,destination);if(FAILED(hr))return hr;
    D3DVIEWPORT9 viewport={0,0,width,height,0,1};hr=d->SetViewport(&viewport);if(FAILED(hr))return hr;
    IDirect3DTexture9* textures[]={first,second,third,fourth};
    for(unsigned i=0;i<4;++i){hr=d->SetTexture(i,textures[i]);if(FAILED(hr))return hr;}
    const float constants[12]={stepX,stepY,0,0,1.0f,1.0f,.5f,.10f,state.inputLinear?1.f:0.f,0,0,0};
    hr=d->SetPixelShaderConstantF(0,constants,3);if(FAILED(hr))return hr;
    hr=d->SetPixelShader(state.pixels[shader]);if(FAILED(hr))return hr;
    // D3D9 half-texel correction maps output pixel centres onto source centres.
    const float left=-1-1.f/width,right=1-1.f/width,top=1+1.f/height,bottom=-1+1.f/height;
    const float quad[][6]={{left,top,0,1,0,0},{right,top,0,1,1,0},{left,bottom,0,1,0,1},{right,bottom,0,1,1,1}};
    hr=d->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,quad,sizeof(quad[0]));
    if(SUCCEEDED(hr))++state.info.passCount;
    return hr;
}
HRESULT drawPost(IDirect3DDevice9* d) {
    HRESULT hr=postState(d);if(FAILED(hr))return hr;
    hr=pass(d,state.linear.surface,state.linear.width,state.linear.height,Linearize,state.resolved.texture);if(FAILED(hr))return hr;
    Target* previous=&state.linear;
    for(unsigned level=0;level<3;++level) {
        auto& a=state.bloom[level][0];auto& b=state.bloom[level][1];
        hr=pass(d,a.surface,a.width,a.height,level?Downsample:Bright,previous->texture,1.f/previous->width,1.f/previous->height);if(FAILED(hr))return hr;
        hr=pass(d,b.surface,b.width,b.height,Blur,a.texture,1.f/a.width,0);if(FAILED(hr))return hr;
        hr=pass(d,a.surface,a.width,a.height,Blur,b.texture,0,1.f/b.height);if(FAILED(hr))return hr;
        previous=&a;
    }
    return pass(d,state.oldTargets[0],state.info.width,state.info.height,Composite,state.linear.texture,0,0,
                state.bloom[0][0].texture,state.bloom[1][0].texture,state.bloom[2][0].texture);
}
}

bool RF455_SetLobbyPostEnabled(bool enabled) {
    if(state.info.active)return false;
    state.enabled=enabled;state.info.enabled=enabled;
    if(enabled){state.failed=false;state.info.status=state.initialized?RF455LobbyPostStatus::Ready:RF455LobbyPostStatus::Pending;}
    else state.info.status=RF455LobbyPostStatus::Disabled;
    return true;
}
bool RF455_LobbyPostEnabled(){return state.enabled;}
bool RF455_SetLobbyPostInputLinear(bool linear) {
    if(state.info.active)return false;state.inputLinear=linear;state.info.inputLinear=linear;return true;
}
RF455LobbyPostTelemetry RF455_GetLobbyPostTelemetry(){return state.info;}

bool RF455_BeginLobbyPost(IDirect3DDevice9* d) {
    if(state.info.active)return false;
    state.info.uiSceneReady=true;state.info.fallbackDrawn=false;state.info.passCount=0;
    if(!state.enabled||!d)return false;
    IDirect3DSurface9* current=nullptr;D3DSURFACE_DESC desc{};
    HRESULT hr=d->GetRenderTarget(0,&current);if(SUCCEEDED(hr))hr=current->GetDesc(&desc);drop(current);
    if(FAILED(hr)){failure(hr,"read scene target");return false;}
    IDirect3DSurface9* currentDepth=nullptr;D3DSURFACE_DESC depthDesc{};
    if(SUCCEEDED(d->GetDepthStencilSurface(&currentDepth))){currentDepth->GetDesc(&depthDesc);drop(currentDepth);}
    const bool changed=state.device!=d||state.oldDescription.Width!=desc.Width||state.oldDescription.Height!=desc.Height||
        state.oldDescription.Format!=desc.Format||state.oldDescription.MultiSampleType!=desc.MultiSampleType||
        state.oldDescription.MultiSampleQuality!=desc.MultiSampleQuality||state.originalDepthFormat!=depthDesc.Format;
    if(changed){resourcesRelease();savedRelease();state.failed=false;}
    state.device=d;state.oldDescription=desc;state.originalDepthFormat=depthDesc.Format;
    if(state.failed)return false;
    if(!state.initialized) {
        hr=initialize(d,desc,depthDesc.Format);
        if(FAILED(hr)){resourcesRelease();state.failed=true;failure(hr,"FP16/SM3/filter/blend/depth initialization",RF455LobbyPostStatus::Unsupported);return false;}
    }
    hr=snapshot(d);
    if(FAILED(hr)){savedRelease();failure(hr,"capture original state");return false;}
    if(state.oldViewport.X||state.oldViewport.Y||state.oldViewport.Width!=desc.Width||state.oldViewport.Height!=desc.Height){
        savedRelease();failure(D3DERR_INVALIDCALL,"requires full scene viewport");return false;
    }
    hr=d->SetDepthStencilSurface(nullptr);
    for(unsigned i=1;i<state.targetCount&&SUCCEEDED(hr);++i)hr=d->SetRenderTarget(i,nullptr);
    if(SUCCEEDED(hr))hr=d->SetRenderTarget(0,state.multisampled?state.multisampled:state.resolved.surface);
    if(SUCCEEDED(hr))hr=d->SetDepthStencilSurface(state.depth);
    if(SUCCEEDED(hr))hr=d->SetViewport(&state.oldViewport);
    // Do not enable sRGB reads on unknown normal/spec/data textures. Scene
    // producer states are preserved; the explicit decode pass owns conversion.
    if(SUCCEEDED(hr))hr=d->SetRenderState(D3DRS_SRGBWRITEENABLE,FALSE);
    if(FAILED(hr)){restoreAll(d);savedRelease();failure(hr,"bind HDR scene");return false;}
    state.info.active=true;state.info.status=RF455LobbyPostStatus::Rendering;state.info.error=S_OK;state.info.errorStage[0]=0;
    return true;
}

void RF455_EndLobbyPost(IDirect3DDevice9* d) {
    if(!state.info.active)return;
    if(d!=state.device||!d){
        if(state.device)restoreAll(state.device);
        savedRelease();state.info.active=false;state.failed=true;
        failure(D3DERR_INVALIDCALL,"end on another device");return;
    }
    // UI should inherit the state at the END of normal scene rendering, not
    // the state from its beginning. Explicit saved target/depth stay original.
    HRESULT hr=state.savedState->Capture();
    const HRESULT ended=d->EndScene();state.info.uiSceneReady=false;
    if(FAILED(ended)) {
        restoreAll(d);savedRelease();state.info.active=false;state.failed=true;
        failure(ended,"end HDR scene");return;
    }
    bool resolved=state.multisampled==nullptr;
    if(SUCCEEDED(hr)&&state.multisampled) {
        // Conservative D3D9 resolve: same-size/format DEFAULT targets, no
        // filtering, and explicitly outside a BeginScene/EndScene pair.
        hr=d->StretchRect(state.multisampled,nullptr,state.resolved.surface,nullptr,D3DTEXF_NONE);
        resolved=SUCCEEDED(hr);
    }
    const HRESULT restored=restoreTargets(d);
    if(FAILED(restored)&&SUCCEEDED(hr))hr=restored;
    const HRESULT begun=d->BeginScene();state.info.uiSceneReady=SUCCEEDED(begun);
    if(FAILED(begun)) {
        restoreAll(d);savedRelease();state.info.active=false;state.failed=true;
        failure(begun,"begin compositor/UI scene");return;
    }
    if(SUCCEEDED(hr))hr=drawPost(d);
    if(FAILED(hr)&&resolved) {
        // Keep a readable classic image on a post-pass error. No tonemap in
        // this path; only encode if the producer explicitly supplied linear.
        const HRESULT setup=postState(d);
        if(SUCCEEDED(setup))state.info.fallbackDrawn=SUCCEEDED(pass(d,state.oldTargets[0],state.info.width,state.info.height,Copy,state.resolved.texture));
    }
    const HRESULT restoredAll=restoreAll(d);
    if(FAILED(restoredAll)&&SUCCEEDED(hr))hr=restoredAll;
    savedRelease();state.info.active=false;
    if(FAILED(hr)){state.failed=true;failure(hr,"resolve/post/composite/restore");}
    else{++state.info.completedFrames;state.info.status=RF455LobbyPostStatus::Complete;state.info.error=S_OK;state.info.errorStage[0]=0;}
}

void RF455_ReleaseLobbyPost() {
    if(state.info.active&&state.device)restoreAll(state.device);
    savedRelease();resourcesRelease();state.device=nullptr;state.failed=false;state.info.active=false;
    state.info.uiSceneReady=true;state.info.passCount=0;state.info.fallbackDrawn=false;
    state.info.status=state.enabled?RF455LobbyPostStatus::Pending:RF455LobbyPostStatus::Disabled;
}
