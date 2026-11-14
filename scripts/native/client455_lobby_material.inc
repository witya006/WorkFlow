// Included once before DrawOneMatGroup. No changes to non-lobby submissions.
#include "client455_lobby_material.h"
#include "client455_lobby_post.h"
#include <d3dx9.h>
#include <cstring>
namespace {
struct LobbyMaterial455 {
    IDirect3DVertexShader9* vs = nullptr;
    IDirect3DPixelShader9* ps = nullptr;
    IDirect3DVertexDeclaration9* decl = nullptr;
    IDirect3DStateBlock9* saved = nullptr;
    RF455LobbyMaterialTelemetry info = {};
    bool failed = false, bound = false;
} lobbyMaterial455;
template<class T> void releaseLobbyMaterial455(T*& p) { if(p) { p->Release(); p=nullptr; } }
void lobbyMaterialError455(HRESULT hr, const char* stage) {
    auto& s=lobbyMaterial455; ++s.info.errors; s.info.error=hr;
    strncpy_s(s.info.errorStage,stage,_TRUNCATE);
}
void lobbyMaterialCompilerError455(ID3DXBuffer* errors) {
    auto& info=lobbyMaterial455.info;info.compilerError[0]=0;
    if(!errors)return;
    size_t count=errors->GetBufferSize();
    if(count>=sizeof(info.compilerError))count=sizeof(info.compilerError)-1;
    std::memcpy(info.compilerError,errors->GetBufferPointer(),count);info.compilerError[count]=0;
}
const char* lobbyMaterialShader455=R"HLSL(
row_major float4x4 world : register(c0);
row_major float4x4 view : register(c4);
row_major float4x4 projection : register(c8);
row_major float4x4 normalWorld : register(c12);
struct In { float3 pos:POSITION0; float3 normal:NORMAL0; float4 color:COLOR0; float2 uv:TEXCOORD0; float2 lm:TEXCOORD1; };
struct Out { float4 pos:POSITION0; float3 wp:TEXCOORD0; float3 normal:TEXCOORD1; float2 uv:TEXCOORD2; float2 lm:TEXCOORD3; float4 color:COLOR0; float2 distance:TEXCOORD4; };
Out VS(In i) {
    Out o; float4 p=mul(float4(i.pos,1),world); float4 v=mul(p,view);
    o.pos=mul(v,projection); o.wp=p.xyz;
    o.normal=mul(float4(i.normal,0),normalWorld).xyz;
    o.uv=i.uv; o.lm=i.lm; o.color=i.color; o.distance=float2(abs(v.z),length(v.xyz)); return o;
}
sampler2D albedoMap:register(s0);
sampler2D lightMap:register(s1);
float4 eye:register(c0);
// x: light source (0 texture,1 vertex,2 lightmap); y: linear output;
// z: fog mode; w: range fog.
float4 settings:register(c1);
float4 fogValues:register(c2); // start,end,density,unused
float4 fogColor:register(c3);
float3 decodeRGB(float3 c) { return lerp(c/12.92,pow(max((c+.055)/1.055,0),2.4),step(.04045,c)); }
float3 encodeRGB(float3 c) { c=max(c,0); return lerp(c*12.92,1.055*pow(c,1.0/2.4)-.055,step(.0031308,c)); }
float4 PS(Out i):COLOR0 {
    float4 a=tex2D(albedoMap,i.uv);
    float3 baked=1;
    if(settings.x>1.5) baked=2*tex2D(lightMap,i.lm).rgb*i.color.rgb;
    else if(settings.x>.5) baked=2*i.color.rgb;
    // Preserve the authored lightmap's multiplication in its original domain.
    // No fabricated normal maps, metallic maps, occlusion or shadow textures.
    float3 base=decodeRGB(max(a.rgb*baked,0));
    float3 n=i.normal*rsqrt(max(dot(i.normal,i.normal),1e-8));
    float3 v=eye.xyz-i.wp; v*=rsqrt(max(dot(v,v),1e-8));
    float3 l=normalize(float3(-.35,.8,-.45));
    float3 h=v+l; h*=rsqrt(max(dot(h,h),1e-8));
    float nl=saturate(dot(n,l)), nv=max(saturate(dot(n,v)),.001);
    float nh=saturate(dot(n,h)), vh=saturate(dot(v,h));
    float hemi=saturate(n.y*.5+.5);
    float3 fill=lerp(float3(.25,.22,.20),float3(.52,.60,.72),hemi);
    float3 key=float3(1.05,.93,.78);
    // Rough dielectric GGX, F0=.04 and roughness=.68 for every eligible BSP.
    // This is deliberately not a shiny metal/material classification.
    float alpha=.68*.68, a2=alpha*alpha;
    float den=nh*nh*(a2-1)+1;
    float D=a2/(3.14159265*den*den);
    float k=(.68+1)*(.68+1)/8;
    float G=(nl/(nl*(1-k)+k))*(nv/(nv*(1-k)+k));
    float F=.04+.96*pow(1-vh,5);
    float spec=D*G*F/max(4*nl*nv,.001)*nl;
    float visibility=saturate(dot(baked,float3(.2126,.7152,.0722)));
    float3 litLinear=base*(fill+.78*key*nl)+key*spec*visibility;
    float3 rgb=encodeRGB(litLinear);
    float z=lerp(i.distance.x,i.distance.y,settings.w), f=1;
    if(settings.z>.5 && settings.z<1.5) f=exp(-fogValues.z*z);
    else if(settings.z>1.5 && settings.z<2.5) f=exp(-pow(fogValues.z*z,2));
    else if(settings.z>2.5) f=(fogValues.y-z)/max(fogValues.y-fogValues.x,.0001);
    rgb=lerp(fogColor.rgb,rgb,saturate(f));
    if(settings.y>.5) rgb=decodeRGB(rgb);
    return float4(rgb,settings.x>1.5?i.color.a:a.a*i.color.a);
}
)HLSL";
bool initLobbyMaterial455(IDirect3DDevice9* d) {
    auto& s=lobbyMaterial455;
    if(s.info.ready) return true;
    if(s.failed) return false;
    D3DCAPS9 caps={}; HRESULT hr=d->GetDeviceCaps(&caps);
    if(FAILED(hr)||caps.VertexShaderVersion<D3DVS_VERSION(3,0)||caps.PixelShaderVersion<D3DPS_VERSION(3,0)) {
        s.failed=true; lobbyMaterialError455(FAILED(hr)?hr:D3DERR_NOTAVAILABLE,"shader-model-3"); return false;
    }
    ID3DXBuffer *code=nullptr,*errors=nullptr;
    hr=D3DXCompileShader(lobbyMaterialShader455,UINT(std::strlen(lobbyMaterialShader455)),nullptr,nullptr,"VS","vs_3_0",D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
    if(FAILED(hr))lobbyMaterialCompilerError455(errors);
    releaseLobbyMaterial455(errors);
    if(SUCCEEDED(hr)) hr=d->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&s.vs);
    releaseLobbyMaterial455(code);
    if(FAILED(hr)) {s.failed=true;lobbyMaterialError455(hr,"vertex-shader");return false;}
    hr=D3DXCompileShader(lobbyMaterialShader455,UINT(std::strlen(lobbyMaterialShader455)),nullptr,nullptr,"PS","ps_3_0",D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
    if(FAILED(hr))lobbyMaterialCompilerError455(errors);
    releaseLobbyMaterial455(errors);
    if(SUCCEEDED(hr)) hr=d->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&s.ps);
    releaseLobbyMaterial455(code);
    if(FAILED(hr)) {s.failed=true;lobbyMaterialError455(hr,"pixel-shader");return false;}
    const D3DVERTEXELEMENT9 elements[]={
        {0,0,D3DDECLTYPE_FLOAT3,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_POSITION,0},
        {0,12,D3DDECLTYPE_FLOAT3,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_NORMAL,0},
        {0,24,D3DDECLTYPE_D3DCOLOR,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_COLOR,0},
        {0,28,D3DDECLTYPE_FLOAT2,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_TEXCOORD,0},
        {0,36,D3DDECLTYPE_FLOAT2,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_TEXCOORD,1},D3DDECL_END()};
    hr=d->CreateVertexDeclaration(elements,&s.decl);
    if(SUCCEEDED(hr)) hr=d->CreateStateBlock(D3DSBT_ALL,&s.saved);
    if(FAILED(hr)) {s.failed=true;lobbyMaterialError455(hr,"declaration-stateblock");return false;}
    s.info.ready=true; return true;
}
bool beginLobbyMaterial455(IDirect3DDevice9* d,const _R3MATERIAL* mat,const _BSP_MAT_GROUP* group) {
    const auto post=RF455_GetLobbyPostTelemetry();
    if(!post.active) return false;
    auto& s=lobbyMaterial455; ++s.info.attempts;
    // Deliberately bounded. All unusual legacy material contracts retain their
    // original draw path, even while the postprocessing target is active.
    if((group->Type&~3u)||(mat->m_dwFlag&~3u)||mat->m_dwLayerNum!=1||mat->m_iDetailSurface!=-1||
       mat->m_Layer[0].m_dwAlphaType||(mat->m_Layer[0].m_dwFlag&~0x30000u)||
       (mat->m_Layer[1].m_dwFlag&0x8000u)||((mat->m_Layer[0].m_ARGB>>24)!=255)) {
        ++s.info.skips;return false;
    }
    IDirect3DVertexBuffer9* vb=nullptr;UINT offset=0,stride=0;DWORD fvf=0,blend=0;
    HRESULT hr=d->GetStreamSource(0,&vb,&offset,&stride);releaseLobbyMaterial455(vb);
    d->GetFVF(&fvf);d->GetRenderState(D3DRS_ALPHABLENDENABLE,&blend);
    if(FAILED(hr)||stride!=44||fvf!=D3DFVF_R3VERTEX_TEX2||blend) {++s.info.skips;return false;}
    IDirect3DVertexShader9* oldVS=nullptr;IDirect3DPixelShader9* oldPS=nullptr;
    d->GetVertexShader(&oldVS);d->GetPixelShader(&oldPS);
    bool programmable=oldVS||oldPS;releaseLobbyMaterial455(oldVS);releaseLobbyMaterial455(oldPS);
    if(programmable) {++s.info.skips;return false;}
    const bool lightmap=(mat->m_dwFlag&1u)&&group->LgtId!=-1;
    for(unsigned slot=0;slot<(lightmap?2u:1u);++slot) {
        IDirect3DBaseTexture9* tex=nullptr;hr=d->GetTexture(slot,&tex);
        bool valid=SUCCEEDED(hr)&&tex&&tex->GetType()==D3DRTYPE_TEXTURE;
        releaseLobbyMaterial455(tex);if(!valid) {++s.info.skips;return false;}
    }
    D3DXMATRIX w,v,p,ni,invV,normal;
    hr=d->GetTransform(D3DTS_WORLD,&w);
    if(SUCCEEDED(hr))hr=d->GetTransform(D3DTS_VIEW,&v);
    if(SUCCEEDED(hr))hr=d->GetTransform(D3DTS_PROJECTION,&p);
    if(FAILED(hr)||!D3DXMatrixInverse(&ni,nullptr,&w)||!D3DXMatrixInverse(&invV,nullptr,&v)) {
        ++s.info.skips;return false;
    }
    D3DXMatrixTranspose(&normal,&ni);
    if(!initLobbyMaterial455(d)) {++s.info.skips;return false;}
    hr=s.saved->Capture();if(FAILED(hr)) {lobbyMaterialError455(hr,"capture");return false;}
    DWORD fog=0,mode=0,range=0,start=0,end=0,density=0,color=0;
    d->GetRenderState(D3DRS_FOGENABLE,&fog);d->GetRenderState(D3DRS_FOGTABLEMODE,&mode);
    if(!mode)d->GetRenderState(D3DRS_FOGVERTEXMODE,&mode);
    d->GetRenderState(D3DRS_RANGEFOGENABLE,&range);
    d->GetRenderState(D3DRS_FOGSTART,&start);d->GetRenderState(D3DRS_FOGEND,&end);
    d->GetRenderState(D3DRS_FOGDENSITY,&density);d->GetRenderState(D3DRS_FOGCOLOR,&color);
    float constants[16]={invV._41,invV._42,invV._43,1,
        lightmap?2.f:((mat->m_dwFlag&1u)?1.f:0.f),post.inputLinear?1.f:0.f,float(fog?mode:0),range?1.f:0.f,
        0,0,0,0,float((color>>16)&255)/255,float((color>>8)&255)/255,float(color&255)/255,1};
    std::memcpy(&constants[8],&start,4);std::memcpy(&constants[9],&end,4);std::memcpy(&constants[10],&density,4);
    hr=d->SetVertexDeclaration(s.decl);
    if(SUCCEEDED(hr))hr=d->SetVertexShader(s.vs);
    if(SUCCEEDED(hr))hr=d->SetPixelShader(s.ps);
    if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(0,reinterpret_cast<const float*>(&w),4);
    if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(4,reinterpret_cast<const float*>(&v),4);
    if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(8,reinterpret_cast<const float*>(&p),4);
    if(SUCCEEDED(hr))hr=d->SetVertexShaderConstantF(12,reinterpret_cast<const float*>(&normal),4);
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(0,constants,4);
    if(SUCCEEDED(hr))hr=d->SetSamplerState(0,D3DSAMP_SRGBTEXTURE,FALSE);
    if(SUCCEEDED(hr))hr=d->SetSamplerState(1,D3DSAMP_SRGBTEXTURE,FALSE);
    if(SUCCEEDED(hr))hr=d->SetRenderState(D3DRS_SRGBWRITEENABLE,FALSE);
    if(SUCCEEDED(hr))hr=d->SetRenderState(D3DRS_FOGENABLE,FALSE);
    if(FAILED(hr)) {lobbyMaterialError455(hr,"bind");s.saved->Apply();return false;}
    s.bound=true;++s.info.binds;return true;
}
void endLobbyMaterial455() {
    auto& s=lobbyMaterial455;if(!s.bound)return;
    HRESULT hr=s.saved->Apply();s.bound=false;
    if(FAILED(hr))lobbyMaterialError455(hr,"restore");
}
}
void RF455_ReleaseLobbyMaterial() {
    auto& s=lobbyMaterial455;endLobbyMaterial455();
    releaseLobbyMaterial455(s.saved);releaseLobbyMaterial455(s.decl);
    releaseLobbyMaterial455(s.ps);releaseLobbyMaterial455(s.vs);
    s.failed=false;s.info.ready=false;
}
RF455LobbyMaterialTelemetry RF455_GetLobbyMaterialTelemetry() {return lobbyMaterial455.info;}
void RF455_ResetLobbyMaterialTelemetry() {
    const bool ready=lobbyMaterial455.info.ready;lobbyMaterial455.info={};lobbyMaterial455.info.ready=ready;
}
