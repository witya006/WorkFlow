// Included once before DrawOneMatGroup. No changes to non-lobby submissions.
#include "client455_lobby_material.h"
#include "client455_lobby_post.h"
#include "client455_lobby_shadow.h"
#include "client455_lobby_sky.h"
#include "client455_lobby_lighting_shader.h"
#include <d3dx9.h>
#include <cstring>
#include <string>
#include <algorithm>
namespace {
struct AuthoredLobbySurface455 {
    IDirect3DTexture9* texture[2] = {};
    float texel[2] = {};
    bool tried = false, ready = false;
};
struct LobbyMaterial455 {
    IDirect3DVertexShader9* vs = nullptr;
    IDirect3DPixelShader9* ps = nullptr;
    IDirect3DVertexDeclaration9* decl = nullptr;
    IDirect3DStateBlock9* saved = nullptr;
    AuthoredLobbySurface455 authored[3];
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
int authoredSurface455(const char* name) {
    // Verified R3M/R3T mapping to T_Wa04. Excludes tani_fire01_37 even
    // though it shares the atlas: its alpha/effect contract remains legacy.
    const char* names[]={"wall_2","wall_6","wall_10","wall_30","T_Wa04_44",
        "wall_54","T_Wa04_72","wall_86","T_Wa04_93"};
    for(const char* candidate:names)if(!std::strcmp(name,candidate))return 0;
    const char* panels[]={"lobby_02_18","lobby_02_59","lobby_02_69","AC_en_pipe04_73"};
    for(const char* candidate:panels)if(!std::strcmp(name,candidate))return 1;
    const char* hull[]={"36_8","36_23","36_31","2_43","36_87","2_92"};
    for(const char* candidate:hull)if(!std::strcmp(name,candidate))return 2;
    return -1;
}
bool initAuthoredSurface455(IDirect3DDevice9* d,unsigned index) {
    auto& s=lobbyMaterial455;auto& surface=s.authored[index];
    if(surface.tried)return surface.ready;
    surface.tried=true;std::uint64_t bytes=0;
    const char* paths[3][2]={
        {"System/modern-lobby/titanium-wall-albedo-v1.png","System/modern-lobby/titanium-wall-height-v1.png"},
        {"System/modern-lobby/titanium-panel-albedo-v1.png","System/modern-lobby/titanium-panel-height-v1.png"},
        {"System/modern-lobby/titanium-hull-albedo-v1.png","System/modern-lobby/titanium-hull-height-v1.png"}};
    D3DSURFACE_DESC first{};
    for(unsigned i=0;i<2;++i){
        HRESULT hr=D3DXCreateTextureFromFileExA(d,paths[index][i],D3DX_DEFAULT_NONPOW2,D3DX_DEFAULT_NONPOW2,
            D3DX_DEFAULT,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,D3DX_FILTER_LINEAR,D3DX_FILTER_BOX,0,nullptr,nullptr,&surface.texture[i]);
        D3DSURFACE_DESC desc{};
        if(SUCCEEDED(hr))hr=surface.texture[i]->GetLevelDesc(0,&desc);
        if(SUCCEEDED(hr)&&i&&(desc.Width!=first.Width||desc.Height!=first.Height))hr=D3DERR_INVALIDCALL;
        if(FAILED(hr)){
            for(auto*& texture:surface.texture)releaseLobbyMaterial455(texture);
            lobbyMaterialError455(hr,paths[index][i]);return false;
        }
        first=desc;
        for(UINT level=0;level<surface.texture[i]->GetLevelCount();++level){
            if(SUCCEEDED(surface.texture[i]->GetLevelDesc(level,&desc)))bytes+=std::uint64_t(desc.Width)*desc.Height*4;
        }
    }
    surface.texel[0]=1.f/first.Width;surface.texel[1]=1.f/first.Height;surface.ready=true;
    s.info.authoredReady=s.authored[0].ready&&s.authored[1].ready&&s.authored[2].ready;
    s.info.authoredTextureBytes+=bytes;return true;
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
sampler2D shadowMap:register(s2);
sampler2D environmentMap:register(s3);
sampler2D heightMap:register(s4);
float4 eye:register(c0);
// x: light source (0 texture,1 vertex,2 lightmap); y: linear output;
// z: fog mode; w: range fog.
float4 settings:register(c1);
float4 fogValues:register(c2); // start,end,density,unused
float4 fogColor:register(c3);
row_major float4x4 lightMatrix:register(c4);
float4 shadowSettings:register(c8);
float4 surface:register(c9); // roughness,metal coverage,microrelief,coat
float4 authored:register(c10); // enabled,world-space relief depth,1/width,1/height
float3 decodeRGB(float3 c) { return lerp(c/12.92,pow(max((c+.055)/1.055,0),2.4),step(.04045,c)); }
float3 encodeRGB(float3 c) { c=max(c,0); return lerp(c*12.92,1.055*pow(c,1.0/2.4)-.055,step(.0031308,c)); }
float4 PS(Out i):COLOR0 {
    float4 a=tex2D(albedoMap,i.uv);
    float3 baked=1;
    if(settings.x>1.5) baked=2*tex2D(lightMap,i.lm).rgb*i.color.rgb;
    else if(settings.x>.5) baked=2*i.color.rgb;
    // Legacy baked lighting is indirect visibility, not albedo. Multiplying
    // it into albedo before another light pass was double-darkening platforms.
    float3 base=decodeRGB(a.rgb);
    // Station palette: titanium panels / graphite recesses, with the original
    // wear and panel boundaries retained. Only the old yellow pigment moves;
    // existing blue glass and emissive machinery keep their identity.
    float yellow=smoothstep(.06,.24,a.r-a.b)*smoothstep(.025,.19,a.g-a.b);
    float value=dot(a.rgb,float3(.2126,.7152,.0722));
    // A bounded pigment response: bright legacy paint is not an HDR light.
    // Keep the texture's seams/wear, without lifting its pale areas above white.
    float3 titanium=decodeRGB(float3(.44,.49,.54))*(.15+1.15*pow(max(value,.015),1.25));
    base=lerp(base,titanium,yellow*.98*(1-authored.x));
    float chroma=max(a.r,max(a.g,a.b))-min(a.r,min(a.g,a.b));
    float neutral=1-smoothstep(.08,.25,chroma);
    base*=1-.25*neutral*saturate(surface.y*1.4)*(1-authored.x);
    float blueAccent=saturate((a.b-a.r)*4)*smoothstep(.45,.85,max(a.g,a.b));
    float3 n=i.normal*rsqrt(max(dot(i.normal,i.normal),1e-8));
    // Small inferred surface relief from the existing panel texture. Bounded
    // world-space gradient; this is not claimed to be an authored normal map.
    float height=dot(a.rgb,float3(.2126,.7152,.0722));
    float dhdx=ddx(height),dhdy=ddy(height);
    float2 uvdx=ddx(i.uv),uvdy=ddy(i.uv);
    // Derive authored relief at the pixel footprint, not from a shared 2x2
    // screen quad difference. The latter produced checkerboard specular edges.
    // Explicit gradients also keep mip choice identical across offset samples.
    if(authored.x>.5){
        height=tex2Dgrad(heightMap,i.uv,uvdx,uvdy).r;
        float2 delta=max(authored.zw,abs(uvdx)+abs(uvdy));
        float hu=tex2Dgrad(heightMap,i.uv+float2(delta.x,0),uvdx,uvdy).r-
                 tex2Dgrad(heightMap,i.uv-float2(delta.x,0),uvdx,uvdy).r;
        float hv=tex2Dgrad(heightMap,i.uv+float2(0,delta.y),uvdx,uvdy).r-
                 tex2Dgrad(heightMap,i.uv-float2(0,delta.y),uvdx,uvdy).r;
        // Generated 8-bit flat plates contain +/-1-level quantization noise.
        // Measured flat-panel differences are <=2/255: do not turn those into
        // geometric facets. Subtract the deadband continuously; real seam and
        // bevel contrasts remain, without a discontinuous normal threshold.
        float2 difference=float2(hu,hv);
        difference=sign(difference)*max(abs(difference)-(2.0/255.0),0);
        float2 gradientUV=difference/(2*delta);
        dhdx=dot(gradientUV,uvdx);dhdy=dot(gradientUV,uvdy);
    }
    float3 dx=ddx(i.wp),dy=ddy(i.wp),rx=cross(dy,n),ry=cross(n,dx);
    float determinant=dot(dx,rx);
    float3 gradient=(rx*dhdx+ry*dhdy)*sign(determinant)/max(abs(determinant),.0001);
    gradient*=min(lerp(surface.z,authored.y,authored.x),lerp(.14,.30,authored.x)/max(length(gradient),.001));
    n=normalize(n-gradient);
    float3 v=eye.xyz-i.wp; v*=rsqrt(max(dot(v,v),1e-8));
    float3 l=LobbySun();
    float3 h=v+l; h*=rsqrt(max(dot(h,h),1e-8));
    float nl=saturate(dot(n,l)), nv=max(saturate(dot(n,v)),.001);
    float nh=saturate(dot(n,h)), vh=saturate(dot(v,h));
    // Station lighting has a stronger directional key than the soft actor fill.
    // Keep titanium neutral in shadow; warm colour comes from incident sunlight.
    float3 key=float3(1.65,1.43,1.15);
    float indirect=.68+.32*saturate(dot(baked,float3(.2126,.7152,.0722)));
    float visibility=LobbyShadow(shadowMap,mul(float4(i.wp,1),lightMatrix),shadowSettings,nl);
    // Roughness remains a bounded material estimate (height on the authored
    // wall, diffuse on old surfaces), not a separately authored roughness map.
    float roughness=clamp(surface.x+(.5-height)*.22,.26,.80);
    // Filter specular response where texture-derived normals vary within a
    // pixel. This suppresses tiny unstable highlights, not the panel detail.
    float3 normalDx=ddx(n),normalDy=ddy(n);
    roughness=sqrt(roughness*roughness+min(.065,.25*(dot(normalDx,normalDx)+dot(normalDy,normalDy))));
    float metallic=surface.y*(.70+.30*smoothstep(.12,.68,height))*(1-.75*blueAccent);
    // Saturated markings stay painted; do not turn red/green/cyan panels into
    // neutral conductors when they share the station's material group.
    metallic*=1-.80*saturate(1-neutral-yellow);
    float3 metalTint=lerp(float3(.39,.43,.48),float3(.55,.59,.64),saturate(height));
    float3 f0=lerp(.04,metalTint,metallic);
    float3 spec=LobbySpecular(n,v,l,f0,roughness);
    float3 reflected=reflect(-v,n);
    // A dark celestial hemisphere and a cool planet below produce distinct
    // reflected planes. This is broad illumination, not fabricated local SSR.
    float planetReflection=smoothstep(-.18,.62,-reflected.y);
    float3 environment=lerp(float3(.025,.04,.07),float3(.30,.46,.68),planetReflection);
    float2 environmentUV=float2(atan2(reflected.z,reflected.x)*.15915494+.67,acos(clamp(reflected.y,-1,1))*.31830989);
    environment+=decodeRGB(tex2Dlod(environmentMap,float4(environmentUV,0,roughness*7)).rgb)*.85;
    float3 fresnel=f0+(1-f0)*pow(1-nv,5);
    // Share energy between reflection and diffuse instead of adding a metal
    // highlight over almost the entire old chalk-like diffuse response.
    float3 diffuseWeight=(1-fresnel)*(1-metallic);
    float3 litLinear=base*diffuseWeight*(LobbyFill(n)*indirect+key*nl*visibility);
    // Rough metal still reflects the environment; roughness broadens the mip
    // rather than extinguishing reflection. Baked visibility affects indirect
    // response only, so the real directional shadow remains unchanged.
    litLinear+=key*spec*visibility+environment*fresnel*(1-.38*roughness)*indirect;
    litLinear+=key*LobbySpecular(n,v,l,.04,.24)*surface.w*visibility;
    litLinear+=float3(.015,.36,.65)*blueAccent;
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
    const std::string shader=std::string(RF455LobbyLightingShader)+lobbyMaterialShader455;
    hr=D3DXCompileShader(shader.c_str(),UINT(shader.size()),nullptr,nullptr,"VS","vs_3_0",D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
    if(FAILED(hr))lobbyMaterialCompilerError455(errors);
    releaseLobbyMaterial455(errors);
    if(SUCCEEDED(hr)) hr=d->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&s.vs);
    releaseLobbyMaterial455(code);
    if(FAILED(hr)) {s.failed=true;lobbyMaterialError455(hr,"vertex-shader");return false;}
    hr=D3DXCompileShader(shader.c_str(),UINT(shader.size()),nullptr,nullptr,"PS","ps_3_0",D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
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
    const int surfaceIndex=authoredSurface455(mat->m_name);
    const bool hasAuthored=surfaceIndex>=0&&initAuthoredSurface455(d,unsigned(surfaceIndex));
    const auto* authoredSurface=hasAuthored?&s.authored[surfaceIndex]:nullptr;
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
    float light[16],shadowValues[4];auto* shadow=RF455_LobbyShadowTexture(light,shadowValues);
    // The old albedo contains pixel-scale baked highlights. A restrained
    // inferred normal avoids amplifying them into glitter on broad metal plates.
    float finish[4]={.44f,.40f,.045f,.06f};
    if(std::strstr(mat->m_name,"wall")){finish[0]=.58f;finish[1]=.18f;finish[2]=.025f;finish[3]=.04f;}
    if(std::strstr(mat->m_name,"pipe")){finish[0]=.30f;finish[1]=.82f;finish[2]=.015f;finish[3]=0;}
    if(std::strstr(mat->m_name,"lobby_n_p")){finish[0]=.38f;finish[1]=.62f;finish[2]=.04f;}
    if(hasAuthored){finish[0]=.42f;finish[1]=.65f;finish[2]=0;finish[3]=.04f;}
    if(hasAuthored&&surfaceIndex==1){finish[0]=.53f;finish[1]=.48f;}
    // Broad exterior plates have a satin coating: retain panel form without
    // turning the orbital backdrop into a sharp mirror over every surface.
    if(hasAuthored&&surfaceIndex==2){finish[0]=.62f;finish[1]=.32f;finish[3]=.025f;}
    const float authoredValues[4]={hasAuthored?1.f:0.f,.55f,
        authoredSurface?authoredSurface->texel[0]:0,authoredSurface?authoredSurface->texel[1]:0};
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(4,light,4);
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(8,shadowValues,1);
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(9,finish,1);
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(10,authoredValues,1);
    if(SUCCEEDED(hr)&&hasAuthored)hr=d->SetTexture(0,authoredSurface->texture[0]);
    if(SUCCEEDED(hr))hr=d->SetTexture(4,hasAuthored?authoredSurface->texture[1]:nullptr);
    if(SUCCEEDED(hr))hr=d->SetTexture(2,shadow);
    if(SUCCEEDED(hr))hr=d->SetTexture(3,RF455_LobbyEnvironmentTexture());
    d->SetSamplerState(3,D3DSAMP_MINFILTER,D3DTEXF_LINEAR);d->SetSamplerState(3,D3DSAMP_MAGFILTER,D3DTEXF_LINEAR);
    d->SetSamplerState(3,D3DSAMP_MIPFILTER,D3DTEXF_LINEAR);d->SetSamplerState(3,D3DSAMP_SRGBTEXTURE,FALSE);
    d->SetSamplerState(3,D3DSAMP_ADDRESSU,D3DTADDRESS_WRAP);d->SetSamplerState(3,D3DSAMP_ADDRESSV,D3DTADDRESS_CLAMP);
    d->SetSamplerState(2,D3DSAMP_MINFILTER,D3DTEXF_POINT);d->SetSamplerState(2,D3DSAMP_MAGFILTER,D3DTEXF_POINT);
    d->SetSamplerState(2,D3DSAMP_MIPFILTER,D3DTEXF_NONE);d->SetSamplerState(2,D3DSAMP_SRGBTEXTURE,FALSE);
    d->SetSamplerState(2,D3DSAMP_ADDRESSU,D3DTADDRESS_CLAMP);d->SetSamplerState(2,D3DSAMP_ADDRESSV,D3DTADDRESS_CLAMP);
    // Match the original atlas addressing, including mirrored/tiled UVs. Data
    // height is always linear; state block restores every sampler after draw.
    for(D3DSAMPLERSTATETYPE type:{D3DSAMP_ADDRESSU,D3DSAMP_ADDRESSV,D3DSAMP_BORDERCOLOR}){
        DWORD value=0;if(SUCCEEDED(d->GetSamplerState(0,type,&value)))d->SetSamplerState(4,type,value);
    }
    // Do not inherit legacy point/mip-disabled settings for authored data.
    // Gradient-aware sampling still needs a continuous reconstruction filter.
    for(D3DSAMPLERSTATETYPE type:{D3DSAMP_MINFILTER,D3DSAMP_MAGFILTER,D3DSAMP_MIPFILTER}){
        d->SetSamplerState(4,type,D3DTEXF_LINEAR);
        if(hasAuthored)d->SetSamplerState(0,type,D3DTEXF_LINEAR);
    }
    d->SetSamplerState(4,D3DSAMP_SRGBTEXTURE,FALSE);
    d->SetSamplerState(4,D3DSAMP_MAXMIPLEVEL,0);d->SetSamplerState(4,D3DSAMP_MIPMAPLODBIAS,0);
    D3DCAPS9 caps{};if(SUCCEEDED(d->GetDeviceCaps(&caps))&&caps.MaxAnisotropy>1){
        d->SetSamplerState(0,D3DSAMP_MAXANISOTROPY,(std::min)(16u,unsigned(caps.MaxAnisotropy)));
        d->SetSamplerState(0,D3DSAMP_MINFILTER,D3DTEXF_ANISOTROPIC);
        d->SetSamplerState(4,D3DSAMP_MAXANISOTROPY,(std::min)(16u,unsigned(caps.MaxAnisotropy)));
        d->SetSamplerState(4,D3DSAMP_MINFILTER,D3DTEXF_ANISOTROPIC);
    }
    if(SUCCEEDED(hr))hr=d->SetSamplerState(0,D3DSAMP_SRGBTEXTURE,FALSE);
    if(SUCCEEDED(hr))hr=d->SetSamplerState(1,D3DSAMP_SRGBTEXTURE,FALSE);
    if(SUCCEEDED(hr))hr=d->SetRenderState(D3DRS_SRGBWRITEENABLE,FALSE);
    if(SUCCEEDED(hr))hr=d->SetRenderState(D3DRS_FOGENABLE,FALSE);
    if(FAILED(hr)) {lobbyMaterialError455(hr,"bind");s.saved->Apply();return false;}
    s.bound=true;++s.info.binds;
    if(hasAuthored){++s.info.authoredBinds;++s.info.authoredSetBinds[surfaceIndex];}
    return true;
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
    for(auto& surface:s.authored){
        for(auto*& texture:surface.texture)releaseLobbyMaterial455(texture);
        surface={};
    }
    s.info.authoredReady=false;s.info.authoredTextureBytes=0;
    s.failed=false;s.info.ready=false;
}
RF455LobbyMaterialTelemetry RF455_GetLobbyMaterialTelemetry() {return lobbyMaterial455.info;}
void RF455_ResetLobbyMaterialTelemetry() {
    auto& s=lobbyMaterial455;const bool ready=s.info.ready,authored=s.info.authoredReady;
    const auto bytes=s.info.authoredTextureBytes;s.info={};s.info.ready=ready;
    s.info.authoredReady=authored;s.info.authoredTextureBytes=bytes;
}
