#include "client455_lobby_sky.h"
#include "client455_lobby_post.h"
#include <d3dx9.h>
#include <cstring>
#include <cmath>

namespace {
template<class T> void dropSky455(T*& p){if(p){p->Release();p=nullptr;}}
struct Sky455 {
    IDirect3DVertexShader9* vs=nullptr;
    IDirect3DPixelShader9* ps=nullptr;
    IDirect3DVertexDeclaration9* decl=nullptr;
    IDirect3DStateBlock9* saved=nullptr;
    IDirect3DVolumeTexture9* noise=nullptr;
    RF455LobbySkyTelemetry info={};
    bool failed=false, cameraOverride=false;
    D3DXMATRIX view,projection;
} sky455;
void skyError455(HRESULT hr,const char* stage){
    ++sky455.info.errors;sky455.info.error=hr;
    strncpy_s(sky455.info.stage,stage,_TRUNCATE);
}
void compilerError455(ID3DXBuffer* errors){
    sky455.info.compilerError[0]=0;if(!errors)return;
    size_t n=errors->GetBufferSize();if(n>=sizeof(sky455.info.compilerError))n=sizeof(sky455.info.compilerError)-1;
    std::memcpy(sky455.info.compilerError,errors->GetBufferPointer(),n);sky455.info.compilerError[n]=0;
}
const char skyShader455[]=R"HLSL(
row_major float4x4 inverseProjection:register(c0);
row_major float4x4 inverseView:register(c4);
float4 eyeCloud:register(c8);
sampler3D volumeNoise:register(s0);
struct Vertex {float4 position:POSITION0;float2 uv:TEXCOORD0;};
Vertex VS(Vertex v){return v;}
float4 noiseChannels(float3 p){
    float3 cell=floor(p),f=frac(p);f=f*f*(3-2*f);
    // Texture centres are integer lattice corners. Warped interpolation
    // retains the smooth value-noise slope and exact one-cell world scale.
    // Explicit LOD is legal inside a dynamic SM3 raymarch; no derivatives.
    return tex3Dlod(volumeNoise,float4((cell+f+.5)/64,0));
}
float noise3(float3 p){return noiseChannels(p).r;}
float coverageAt(float3 p){
    // Broad separated cloud banks; the negative space is real empty volume.
    return smoothstep(.28,.65,noise3(float3(p.x*.85+17,5.7,p.z*.85-11)));
}
float cloudDensity(float3 p){
    float height=(p.y+1.6)/.95;
    float3 q=p*2.2;
    float n=noise3(q)*.57+noise3(q*2.03+float3(11.3,4.7,8.1))*.29+noise3(q*4.11+float3(3.1,17.2,1.7))*.14;
    float threshold=lerp(.68,.38,coverageAt(p))+height*height*.18;
    // Fine erosion changes the 3D boundary rather than colouring a flat cap.
    // Fade high frequency with distance to avoid replacing jitter with aliasing.
    float distanceToEye=length(p-eyeCloud.xyz);
    float detailWeight=1-smoothstep(3,12,distanceToEye);
    float erosion=noiseChannels(q*6.7+float3(7.2,2.1,9.4)).g*.65+noiseChannels(q*12.9+float3(13.4,6.8,1.3)).b*.35;
    float shape=saturate((n-threshold-(erosion-.30)*.10*detailWeight)*7);
    return shape*smoothstep(0,.14,height)*(1-smoothstep(.82,1,height));
}
float shadowDensity(float3 p){
    float height=(p.y+1.6)/.95;
    float threshold=lerp(.68,.38,coverageAt(p))+height*height*.18;
    float shape=saturate((noise3(p*2.2)-threshold)*6);
    return shape*smoothstep(0,.14,height)*(1-smoothstep(.82,1,height));
}
float3 encodeSky(float3 c){c=max(c,0);return lerp(c*12.92,1.055*pow(c,1.0/2.4)-.055,step(.0031308,c));}
float4 PS(Vertex i):COLOR0{
    float4 viewPoint=mul(float4(i.uv.x*2-1,1-i.uv.y*2,1,1),inverseProjection);
    float3 ray=normalize(mul(float4(viewPoint.xyz/viewPoint.w,0),inverseView).xyz);
    float3 sun=normalize(float3(-.35,.8,-.45));
    float elevation=saturate(ray.y);
    float horizon=exp(-abs(ray.y)*5.5);
    float3 sky=lerp(float3(.065,.14,.29),float3(.025,.075,.20),pow(elevation,.45));
    sky=lerp(sky,float3(.22,.36,.55),horizon*.65);
    float sunDot=saturate(dot(ray,sun));
    sky+=float3(1.0,.71,.39)*pow(sunDot,18)*.20;
    sky+=float3(1.0,.84,.63)*pow(sunDot,180)*.30;
    sky+=float3(7,5.8,4.1)*smoothstep(.99983,.99996,sunDot);
    float3 origin=eyeCloud.xyz;
    float dy=abs(ray.y)<.0001?.0001:ray.y;
    float nearT=(-1.6-origin.y)/dy,farT=(-.65-origin.y)/dy;
    float entry=max(0,min(nearT,farT)),exitT=min(24,max(nearT,farT));
    if(exitT>entry){
        float stepLength=(exitT-entry)/128;
        // Deterministic midpoint quadrature, no screen grain/temporal jitter.
        float distance=entry+stepLength*.5,transmission=1;
        float3 accumulated=0;
        [loop] for(int stepIndex=0;stepIndex<128;++stepIndex){
            float3 p=origin+ray*distance;
            float density=cloudDensity(p);
            if(density>.003){
                float optical=shadowDensity(p+sun*.10)*.18+shadowDensity(p+sun*.28)*.32+shadowDensity(p+sun*.62)*.50;
                float sunlight=exp(-optical*6.0);
                float height=saturate((p.y+1.6)/.95);
                float forward=pow(saturate(dot(ray,sun)),8)*.25;
                float3 ambient=lerp(float3(.035,.055,.10),float3(.10,.15,.23),height);
                float3 lit=ambient+float3(.72,.62,.49)*sunlight*(.65+forward);
                float haze=1-exp(-distance*.035);
                lit=lerp(lit,sky,saturate(haze));
                float opacity=1-exp(-density*stepLength*7.0);
                accumulated+=transmission*opacity*lit;
                transmission*=1-opacity;
                if(transmission<.012)break;
            }
            distance+=stepLength;
        }
        sky=accumulated+transmission*sky;
    }
    // Match the post producer contract: encode only for legacy-input mode.
    return float4(eyeCloud.w>.5?sky:encodeSky(sky),1);
}
)HLSL";
bool initVolume455(IDirect3DDevice9* d,const D3DCAPS9& caps){
    auto& s=sky455;
    const DWORD linearCaps=D3DPTFILTERCAPS_MINFLINEAR|D3DPTFILTERCAPS_MAGFLINEAR;
    if(!(caps.TextureCaps&D3DPTEXTURECAPS_VOLUMEMAP)||caps.MaxVolumeExtent<64||
       (caps.VolumeTextureFilterCaps&linearCaps)!=linearCaps){
        skyError455(D3DERR_NOTAVAILABLE,"volume-caps");return false;
    }
    IDirect3D9* api=nullptr;D3DDEVICE_CREATION_PARAMETERS creation={};D3DDISPLAYMODE mode={};
    HRESULT hr=d->GetDirect3D(&api);
    if(SUCCEEDED(hr))hr=d->GetCreationParameters(&creation);
    if(SUCCEEDED(hr))hr=d->GetDisplayMode(0,&mode);
    if(SUCCEEDED(hr))hr=api->CheckDeviceFormat(creation.AdapterOrdinal,creation.DeviceType,mode.Format,
        D3DUSAGE_QUERY_FILTER,D3DRTYPE_VOLUMETEXTURE,D3DFMT_A8R8G8B8);
    dropSky455(api);
    if(FAILED(hr)){skyError455(hr,"volume-format");return false;}
    hr=d->CreateVolumeTexture(64,64,64,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&s.noise,nullptr);
    if(FAILED(hr)){skyError455(hr,"volume-create");return false;}
    D3DLOCKED_BOX box={};hr=s.noise->LockBox(0,&box,nullptr,0);
    if(FAILED(hr)){dropSky455(s.noise);skyError455(hr,"volume-lock");return false;}
    for(unsigned z=0;z<64;++z)for(unsigned y=0;y<64;++y){
        auto* row=reinterpret_cast<DWORD*>(static_cast<unsigned char*>(box.pBits)+z*box.SlicePitch+y*box.RowPitch);
        for(unsigned x=0;x<64;++x){
            // Fixed integer avalanche: deterministic independent RGBA lattice
            // values, periodic through sampler wrap. No rand/time/files/assets.
            std::uint32_t h=x+64u*y+4096u*z+0x9e3779b9u;
            h^=h>>16;h*=0x7feb352du;h^=h>>15;h*=0x846ca68bu;h^=h>>16;
            row[x]=h;
        }
    }
    hr=s.noise->UnlockBox(0);
    if(FAILED(hr)){dropSky455(s.noise);skyError455(hr,"volume-unlock");return false;}
    s.info.volumeTextureBytes=64u*64u*64u*4u;return true;
}
bool initSky455(IDirect3DDevice9* d){
    auto& s=sky455;if(s.info.ready)return true;if(s.failed)return false;
    D3DCAPS9 caps={};HRESULT hr=d->GetDeviceCaps(&caps);
    if(FAILED(hr)||caps.VertexShaderVersion<D3DVS_VERSION(3,0)||caps.PixelShaderVersion<D3DPS_VERSION(3,0)){
        s.failed=true;skyError455(FAILED(hr)?hr:D3DERR_NOTAVAILABLE,"shader-model-3");return false;
    }
    ID3DXBuffer *code=nullptr,*errors=nullptr;
    hr=D3DXCompileShader(skyShader455,UINT(std::strlen(skyShader455)),nullptr,nullptr,"VS","vs_3_0",D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
    if(FAILED(hr))compilerError455(errors);dropSky455(errors);
    if(SUCCEEDED(hr))hr=d->CreateVertexShader(static_cast<const DWORD*>(code->GetBufferPointer()),&s.vs);dropSky455(code);
    if(FAILED(hr)){s.failed=true;skyError455(hr,"vertex-shader");return false;}
    hr=D3DXCompileShader(skyShader455,UINT(std::strlen(skyShader455)),nullptr,nullptr,"PS","ps_3_0",D3DXSHADER_OPTIMIZATION_LEVEL3,&code,&errors,nullptr);
    if(FAILED(hr))compilerError455(errors);dropSky455(errors);
    if(SUCCEEDED(hr))hr=d->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&s.ps);dropSky455(code);
    if(FAILED(hr)){s.failed=true;skyError455(hr,"pixel-shader");return false;}
    const D3DVERTEXELEMENT9 declaration[]={
        {0,0,D3DDECLTYPE_FLOAT4,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_POSITION,0},
        {0,16,D3DDECLTYPE_FLOAT2,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_TEXCOORD,0},D3DDECL_END()};
    hr=d->CreateVertexDeclaration(declaration,&s.decl);
    if(SUCCEEDED(hr))hr=d->CreateStateBlock(D3DSBT_ALL,&s.saved);
    if(FAILED(hr)){s.failed=true;skyError455(hr,"state-declaration");return false;}
    if(!initVolume455(d,caps)){s.failed=true;return false;}
    s.info.ready=true;return true;
}
}
bool RF455_RenderLobbySky(IDirect3DDevice9* d){
    if(!d)return false;
    auto& s=sky455;D3DXMATRIX view,projection,inverseView,inverseProjection;
    HRESULT hr=S_OK;
    if(s.cameraOverride){view=s.view;projection=s.projection;}
    else {hr=d->GetTransform(D3DTS_VIEW,&view);if(SUCCEEDED(hr))hr=d->GetTransform(D3DTS_PROJECTION,&projection);}
    if(FAILED(hr)||!D3DXMatrixInverse(&inverseView,nullptr,&view)||!D3DXMatrixInverse(&inverseProjection,nullptr,&projection)){
        skyError455(FAILED(hr)?hr:D3DERR_INVALIDCALL,"camera");return false;
    }
    D3DVIEWPORT9 viewport={};hr=d->GetViewport(&viewport);
    if(FAILED(hr)||!viewport.Width||!viewport.Height){skyError455(FAILED(hr)?hr:D3DERR_INVALIDCALL,"viewport");return false;}
    if(!initSky455(d))return false;
    // Fixed world-space cloud deck, below the station. No camera-relative
    // anchoring: a lobby camera translation produces genuine cloud parallax.
    const float origin[4]={inverseView._41*.001f,inverseView._42*.001f,inverseView._43*.001f,
        RF455_GetLobbyPostTelemetry().inputLinear?1.f:0.f};
    hr=s.saved->Capture();if(FAILED(hr)){skyError455(hr,"capture");return false;}
    // Vertex positions include D3D9's half-pixel offset. Z=1 tests against the
    // existing far depth; later scene geometry owns all nearer depth values.
    const float dx=1.f/viewport.Width,dy=1.f/viewport.Height;
    struct Quad {float x,y,z,w,u,v;};
    const Quad quad[]={{-1-dx,1+dy,1,1,0,0},{1-dx,1+dy,1,1,1,0},{-1-dx,-1+dy,1,1,0,1},{1-dx,-1+dy,1,1,1,1}};
    hr=d->SetVertexDeclaration(s.decl);
    if(SUCCEEDED(hr))hr=d->SetVertexShader(s.vs);
    if(SUCCEEDED(hr))hr=d->SetPixelShader(s.ps);
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(0,reinterpret_cast<const float*>(&inverseProjection),4);
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(4,reinterpret_cast<const float*>(&inverseView),4);
    if(SUCCEEDED(hr))hr=d->SetPixelShaderConstantF(8,origin,1);
    if(SUCCEEDED(hr))hr=d->SetTexture(0,s.noise);
    const D3DSAMPLERSTATETYPE samplerNames[]={D3DSAMP_ADDRESSU,D3DSAMP_ADDRESSV,D3DSAMP_ADDRESSW,
        D3DSAMP_MINFILTER,D3DSAMP_MAGFILTER,D3DSAMP_MIPFILTER,D3DSAMP_SRGBTEXTURE,D3DSAMP_MAXMIPLEVEL,D3DSAMP_MIPMAPLODBIAS};
    const DWORD samplerValues[]={D3DTADDRESS_WRAP,D3DTADDRESS_WRAP,D3DTADDRESS_WRAP,
        D3DTEXF_LINEAR,D3DTEXF_LINEAR,D3DTEXF_NONE,FALSE,0,0};
    for(unsigned n=0;n<sizeof(samplerNames)/sizeof(samplerNames[0])&&SUCCEEDED(hr);++n)
        hr=d->SetSamplerState(0,samplerNames[n],samplerValues[n]);
    const D3DRENDERSTATETYPE names[]={D3DRS_ZENABLE,D3DRS_ZWRITEENABLE,D3DRS_ZFUNC,D3DRS_ALPHABLENDENABLE,D3DRS_ALPHATESTENABLE,D3DRS_FOGENABLE,D3DRS_CULLMODE,D3DRS_SRGBWRITEENABLE,D3DRS_COLORWRITEENABLE,D3DRS_STENCILENABLE,D3DRS_SCISSORTESTENABLE,D3DRS_CLIPPLANEENABLE,D3DRS_FILLMODE,D3DRS_DEPTHBIAS,D3DRS_SLOPESCALEDEPTHBIAS};
    const DWORD values[]={D3DZB_TRUE,FALSE,D3DCMP_LESSEQUAL,FALSE,FALSE,FALSE,D3DCULL_NONE,FALSE,15,FALSE,FALSE,0,D3DFILL_SOLID,0,0};
    for(unsigned n=0;n<sizeof(names)/sizeof(names[0])&&SUCCEEDED(hr);++n)hr=d->SetRenderState(names[n],values[n]);
    if(SUCCEEDED(hr))hr=d->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,quad,sizeof(Quad));
    const HRESULT restored=s.saved->Apply();
    if(FAILED(hr)){skyError455(hr,"draw");return false;}
    if(FAILED(restored)){skyError455(restored,"restore");return false;}
    ++s.info.draws;return true;
}
void RF455_ReleaseLobbySky(){
    auto& s=sky455;dropSky455(s.saved);dropSky455(s.decl);dropSky455(s.ps);dropSky455(s.vs);
    dropSky455(s.noise);s.info.volumeTextureBytes=0;
    s.info.ready=false;s.failed=false;s.cameraOverride=false;
}
RF455LobbySkyTelemetry RF455_GetLobbySkyTelemetry(){return sky455.info;}
void RF455_SetLobbySkyCamera(const D3DMATRIX* view,const D3DMATRIX* projection){
    sky455.cameraOverride=view&&projection;
    if(sky455.cameraOverride){std::memcpy(&sky455.view,view,sizeof(*view));std::memcpy(&sky455.projection,projection,sizeof(*projection));}
}
