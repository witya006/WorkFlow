#include "client455_lobby_sky.h"
#include "client455_lobby_post.h"
#include "client455_render_diagnostics.h"
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
    IDirect3DTexture9 *space=nullptr,*planet=nullptr,*region=nullptr;
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
const char skyShader455[]=
#include "client455_lobby_orbit_shader.inc"
;
bool initOrbitTextures455(IDirect3DDevice9* d){
    auto& s=sky455;
    const char* files[]={"System/modern-lobby/space-panorama-v1.png","System/modern-lobby/novus-surface-v1.png","System/modern-lobby/novus-region-v1.png"};
    IDirect3DTexture9** textures[]={&s.space,&s.planet,&s.region};
    s.info.volumeTextureBytes=0;
    for(unsigned index=0;index<3;++index){
        const HRESULT hr=D3DXCreateTextureFromFileExA(d,files[index],D3DX_DEFAULT_NONPOW2,D3DX_DEFAULT_NONPOW2,
            D3DX_DEFAULT,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,D3DX_FILTER_LINEAR,D3DX_FILTER_BOX,0,nullptr,nullptr,textures[index]);
        if(FAILED(hr)){skyError455(hr,index==2?"region-texture":index?"planet-texture":"space-texture");return false;}
        for(UINT level=0;level<(*textures[index])->GetLevelCount();++level){D3DSURFACE_DESC desc{};
            if(SUCCEEDED((*textures[index])->GetLevelDesc(level,&desc)))s.info.volumeTextureBytes+=std::uint64_t(desc.Width)*desc.Height*4;}
    }return true;
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
    // Orbital surface/atmosphere intersections replace the cloud raymarch.
    hr=D3DXCompileShader(skyShader455,UINT(std::strlen(skyShader455)),nullptr,nullptr,"PS","ps_3_0",D3DXSHADER_OPTIMIZATION_LEVEL1,&code,&errors,nullptr);
    if(FAILED(hr))compilerError455(errors);dropSky455(errors);
    if(SUCCEEDED(hr))hr=d->CreatePixelShader(static_cast<const DWORD*>(code->GetBufferPointer()),&s.ps);dropSky455(code);
    if(FAILED(hr)){s.failed=true;skyError455(hr,"pixel-shader");return false;}
    const D3DVERTEXELEMENT9 declaration[]={
        {0,0,D3DDECLTYPE_FLOAT4,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_POSITION,0},
        {0,16,D3DDECLTYPE_FLOAT2,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_TEXCOORD,0},D3DDECL_END()};
    hr=d->CreateVertexDeclaration(declaration,&s.decl);
    if(SUCCEEDED(hr))hr=d->CreateStateBlock(D3DSBT_ALL,&s.saved);
    if(FAILED(hr)){s.failed=true;skyError455(hr,"state-declaration");return false;}
    if(!initOrbitTextures455(d)){s.failed=true;return false;}
    s.info.ready=true;return true;
}
}
bool RF455_RenderLobbySky(IDirect3DDevice9* d){
    if(!d)return false;
    RF455GpuSection timing(1);
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
    // Fixed world-space orbital bodies; translation produces real parallax.
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
    if(SUCCEEDED(hr))hr=d->SetTexture(0,s.space);
    if(SUCCEEDED(hr))hr=d->SetTexture(1,s.planet);
    if(SUCCEEDED(hr))hr=d->SetTexture(2,s.region);
    const D3DSAMPLERSTATETYPE samplerNames[]={D3DSAMP_ADDRESSU,D3DSAMP_ADDRESSV,D3DSAMP_ADDRESSW,
        D3DSAMP_MINFILTER,D3DSAMP_MAGFILTER,D3DSAMP_MIPFILTER,D3DSAMP_SRGBTEXTURE,D3DSAMP_MAXMIPLEVEL,D3DSAMP_MIPMAPLODBIAS};
    const DWORD samplerValues[]={D3DTADDRESS_WRAP,D3DTADDRESS_CLAMP,D3DTADDRESS_WRAP,
        D3DTEXF_LINEAR,D3DTEXF_LINEAR,D3DTEXF_LINEAR,FALSE,0,0};
    for(unsigned slot=0;slot<3&&SUCCEEDED(hr);++slot)
    for(unsigned n=0;n<sizeof(samplerNames)/sizeof(samplerNames[0])&&SUCCEEDED(hr);++n)
        hr=d->SetSamplerState(slot,samplerNames[n],samplerValues[n]);
    if(SUCCEEDED(hr))hr=d->SetSamplerState(2,D3DSAMP_ADDRESSU,D3DTADDRESS_CLAMP);
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
    dropSky455(s.space);dropSky455(s.planet);dropSky455(s.region);s.info.volumeTextureBytes=0;
    s.info.ready=false;s.failed=false;s.cameraOverride=false;
}
RF455LobbySkyTelemetry RF455_GetLobbySkyTelemetry(){return sky455.info;}
IDirect3DTexture9* RF455_LobbyEnvironmentTexture(){return sky455.info.ready?sky455.space:nullptr;}
void RF455_SetLobbySkyCamera(const D3DMATRIX* view,const D3DMATRIX* projection){
    sky455.cameraOverride=view&&projection;
    if(sky455.cameraOverride){std::memcpy(&sky455.view,view,sizeof(*view));std::memcpy(&sky455.projection,projection,sizeof(*projection));}
}
