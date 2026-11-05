#include "Character.h"
#include "client455_normal_shadow.h"
#include "client455_normal_shadow_constants.h"
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#define S_REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Shadow failure line%d\n",__LINE__);return 1;}}while(0)
namespace shadow455 {
struct Capture;
struct Surface {void** table;Capture* capture;unsigned refs=1;bool target;};
struct Buffer {void** table;Capture* capture;unsigned releases=0;unsigned char bytes[96];};
struct Texture {void** table;Capture* capture;};
struct Device {void** table;Capture* capture;};
struct Capture {
    void* deviceTable[119]={};void* surfaceTable[13]={};void* bufferTable[14]={};void* textureTable[22]={};
    Device device={deviceTable,this};Surface back={surfaceTable,this,1,true},depth={surfaceTable,this,1,false},level={surfaceTable,this,1,true};
    Buffer buffer={bufferTable,this};Texture texture={textureTable,this};RF455CharacterRenderer owner={};
    std::vector<std::string> events;bool bad=false;HRESULT textureResult=S_OK,vertexResult=S_OK,lockResult=S_OK,depthResult=S_OK;
    unsigned createTextures=0,createBuffers=0,locks=0,clearCalls=0,sceneCalls=0;
    Capture();void record(const char* name){events.push_back(name);}
};
ULONG WINAPI surfaceRelease(Surface* s){s->capture->record(s==&s->capture->back?"releaseBack":s==&s->capture->depth?"releaseDepth":"releaseLevel");return --s->refs;}
HRESULT WINAPI surfaceDesc(Surface* s,D3DSURFACE_DESC* out){s->capture->record("getDesc");*out={D3DFMT_A8R8G8B8,D3DRTYPE_SURFACE,D3DUSAGE_RENDERTARGET,D3DPOOL_DEFAULT,D3DMULTISAMPLE_NONE,0,256,256};return S_OK;}
HRESULT WINAPI getTarget(Device* d,DWORD index,IDirect3DSurface9** out){auto& c=*d->capture;c.record("getRT");c.bad|=index!=0;++c.back.refs;*out=reinterpret_cast<IDirect3DSurface9*>(&c.back);return S_OK;}
HRESULT WINAPI getDepth(Device* d,IDirect3DSurface9** out){auto& c=*d->capture;c.record("getDS");++c.depth.refs;*out=reinterpret_cast<IDirect3DSurface9*>(&c.depth);return S_OK;}
HRESULT WINAPI createTexture(Device* d,UINT w,UINT h,UINT levels,DWORD usage,D3DFORMAT format,D3DPOOL pool,IDirect3DTexture9** out,HANDLE* shared){auto& c=*d->capture;c.record("createTexture");++c.createTextures;c.bad|=w!=512||h!=512||levels!=1||usage!=D3DUSAGE_RENDERTARGET||format!=D3DFMT_A8R8G8B8||pool!=D3DPOOL_DEFAULT||shared;
    *out=reinterpret_cast<IDirect3DTexture9*>(&c.texture);return c.textureResult;}
HRESULT WINAPI createVertex(Device* d,UINT length,DWORD usage,DWORD fvf,D3DPOOL pool,IDirect3DVertexBuffer9** out,HANDLE* shared){auto& c=*d->capture;c.record("createVB");++c.createBuffers;c.bad|=length!=96||usage!=8||fvf!=322||pool!=D3DPOOL_MANAGED||shared;*out=FAILED(c.vertexResult)?nullptr:reinterpret_cast<IDirect3DVertexBuffer9*>(&c.buffer);return c.vertexResult;}
HRESULT WINAPI lock(Buffer* b,UINT offset,UINT count,void** out,DWORD flags){auto& c=*b->capture;c.record("lockVB");++c.locks;c.bad|=offset!=0||count!=96||flags!=0;if(FAILED(c.lockResult))return c.lockResult;*out=b->bytes;return S_OK;}
HRESULT WINAPI unlock(Buffer* b){b->capture->record("unlockVB");return E_FAIL;}
HRESULT WINAPI getLevel(Texture* t,UINT index,IDirect3DSurface9** out){auto& c=*t->capture;c.record("getLevel");c.bad|=index!=0;++c.level.refs;*out=reinterpret_cast<IDirect3DSurface9*>(&c.level);return S_OK;}
HRESULT WINAPI setTarget(Device* d,DWORD index,IDirect3DSurface9* target){auto& c=*d->capture;c.record(target==reinterpret_cast<IDirect3DSurface9*>(&c.back)?"restoreRT":"setRT");c.bad|=index!=0;return E_FAIL;}
HRESULT WINAPI setDepth(Device* d,IDirect3DSurface9* depth){auto& c=*d->capture;c.record(depth?"restoreDS":"nullDS");return depth?S_OK:c.depthResult;}
HRESULT WINAPI clear(Device* d,DWORD count,const D3DRECT* rect,DWORD flags,D3DCOLOR color,float z,DWORD stencil){auto& c=*d->capture;c.record("clear");++c.clearCalls;c.bad|=count||rect||flags!=D3DCLEAR_TARGET||color||z!=1||stencil;return E_FAIL;}
HRESULT WINAPI begin(Device* d){d->capture->record("begin");++d->capture->sceneCalls;return E_FAIL;}
HRESULT WINAPI end(Device* d){d->capture->record("end");return E_FAIL;}
HRESULT WINAPI state(Device* d,D3DRENDERSTATETYPE name,DWORD value){auto& c=*d->capture;c.record(value?"zTrue":"zFalse");c.bad|=name!=D3DRS_ZENABLE||value>1;return E_FAIL;}
Capture::Capture(){
    deviceTable[23]=reinterpret_cast<void*>(createTexture);deviceTable[26]=reinterpret_cast<void*>(createVertex);deviceTable[37]=reinterpret_cast<void*>(setTarget);deviceTable[38]=reinterpret_cast<void*>(getTarget);deviceTable[39]=reinterpret_cast<void*>(setDepth);deviceTable[40]=reinterpret_cast<void*>(getDepth);deviceTable[41]=reinterpret_cast<void*>(begin);deviceTable[42]=reinterpret_cast<void*>(end);deviceTable[43]=reinterpret_cast<void*>(clear);deviceTable[57]=reinterpret_cast<void*>(state);
    surfaceTable[2]=reinterpret_cast<void*>(surfaceRelease);surfaceTable[12]=reinterpret_cast<void*>(surfaceDesc);bufferTable[11]=reinterpret_cast<void*>(lock);bufferTable[12]=reinterpret_cast<void*>(unlock);textureTable[18]=reinterpret_cast<void*>(getLevel);
    owner.device=reinterpret_cast<IDirect3DDevice9*>(&device);std::memset(buffer.bytes,0x6a,96);
}
static std::vector<unsigned char> pixels(IDirect3DDevice9* d,IDirect3DSurface9* source){
    IDirect3DSurface9* surface=source;surface->AddRef();IDirect3DSurface9* memory=nullptr;std::vector<unsigned char> out;D3DSURFACE_DESC desc={};surface->GetDesc(&desc);
    if(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)) && SUCCEEDED(d->GetRenderTargetData(surface,memory))){D3DLOCKED_RECT lock={};if(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY))){out.resize(4*desc.Width*desc.Height);for(unsigned y=0;y<desc.Height;++y)std::memcpy(out.data()+4*y*desc.Width,static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch,4*desc.Width);memory->UnlockRect();}}
    if(memory)memory->Release();surface->Release();return out;
}
}
int RF455_CheckNormalShadowCapture(){
    using namespace shadow455;
    unsigned initial[24]={};S_REQUIRE(!std::memcmp(RF455_NormalShadowQuadBits,initial,96));
    const std::vector<std::string> expected={"getRT","getDesc","createTexture","releaseBack","createVB","lockVB","unlockVB","getDS","getLevel","getRT","setRT","nullDS","releaseLevel","clear","begin","zFalse","zTrue","end","restoreRT","restoreDS","releaseBack","releaseDepth"};
    Capture c;S_REQUIRE(RF455_BeginNormalShadow(&c.owner,0)==S_OK);RF455_EndNormalShadow(&c.owner);
    S_REQUIRE(!c.bad && c.events==expected && c.back.refs==1 && c.depth.refs==1 && c.level.refs==1 && !std::memcmp(c.buffer.bytes,RF455_SHADOW_QUAD_BITS,96) && !std::memcmp(RF455_NormalShadowQuadBits,RF455_SHADOW_QUAD_BITS,96));
    const auto retained=std::vector<unsigned char>(c.owner.effects.opaque208,c.owner.effects.opaque208+8);c.events.clear();
    S_REQUIRE(RF455_BeginNormalShadow(&c.owner,0)==S_OK);RF455_EndNormalShadow(&c.owner);S_REQUIRE(c.createTextures==1 && c.createBuffers==1 && c.locks==1 && !std::memcmp(retained.data(),c.owner.effects.opaque208,8));
    c.events.clear();S_REQUIRE(!RF455_BeginNormalShadow(&c.owner,20) && !RF455_BeginNormalShadow(&c.owner,0xffffffffu) && c.events.empty());
    Capture positive;positive.textureResult=S_FALSE;S_REQUIRE(!RF455_BeginNormalShadow(&positive.owner,0) && !positive.owner.effects.resources[0] && positive.createTextures==1 && !positive.createBuffers);
    Capture failed;failed.vertexResult=E_OUTOFMEMORY;S_REQUIRE(!RF455_BeginNormalShadow(&failed.owner,19) && failed.owner.effects.resources[19] && !failed.owner.effects.extra && !failed.sceneCalls);
    Capture partial;partial.lockResult=E_FAIL;S_REQUIRE(!RF455_BeginNormalShadow(&partial.owner,0) && partial.owner.effects.extra && !partial.sceneCalls);
    // A failed first lock leaves the VB cached; the next begin skips its upload.
    partial.lockResult=S_OK;S_REQUIRE(RF455_BeginNormalShadow(&partial.owner,0)==S_OK && partial.locks==1 && partial.buffer.bytes[0]==0x6a);RF455_EndNormalShadow(&partial.owner);
    Capture status;status.depthResult=E_FAIL;S_REQUIRE(RF455_BeginNormalShadow(&status.owner,0)==E_FAIL && status.clearCalls==1 && status.sceneCalls==1);RF455_EndNormalShadow(&status.owner);
    return 0;
}
int RF455_CheckNormalShadowHal(CRender* renderer,CHARACTEROBJECT* model,IDirect3DDevice9* device){
    using namespace shadow455;
    IDirect3DSurface9* originalTarget=nullptr;IDirect3DSurface9* originalDepth=nullptr;S_REQUIRE(SUCCEEDED(device->GetRenderTarget(0,&originalTarget)) && SUCCEEDED(device->GetDepthStencilSurface(&originalDepth)));
    D3DSURFACE_DESC originalDesc={};originalTarget->GetDesc(&originalDesc);D3DVIEWPORT9 clipped={3,4,100,120,0,1};S_REQUIRE(SUCCEEDED(device->SetViewport(&clipped)));
    S_REQUIRE(!renderer->BeginShadow(20) && !renderer->BeginShadow(0xffffffffu));D3DVIEWPORT9 viewport={};device->GetViewport(&viewport);S_REQUIRE(!std::memcmp(&viewport,&clipped,sizeof(viewport)));
    IUnknown* first=nullptr;IUnknown* firstBuffer=nullptr;
    for(unsigned attempt=0;attempt<3;++attempt){
        const unsigned index=attempt==1?19:0;renderer->SetState();const int result=renderer->BeginShadow(index);
        S_REQUIRE(result==S_OK && !static_cast<bool>(result)); // Original callers would skip End here.
        auto* texture=static_cast<IDirect3DTexture9*>(renderer->native.effects.resources[index]);S_REQUIRE(texture && renderer->native.effects.extra && texture->GetLevelCount()==1);
        D3DSURFACE_DESC desc={};S_REQUIRE(SUCCEEDED(texture->GetLevelDesc(0,&desc)) && desc.Width==512 && desc.Height==512 && desc.Format==originalDesc.Format && desc.Usage==originalDesc.Usage && desc.Pool==originalDesc.Pool);
        D3DVERTEXBUFFER_DESC vertexDesc={};S_REQUIRE(SUCCEEDED(static_cast<IDirect3DVertexBuffer9*>(renderer->native.effects.extra)->GetDesc(&vertexDesc)) && vertexDesc.Size==96 && vertexDesc.Usage==8 && vertexDesc.FVF==322 && vertexDesc.Pool==D3DPOOL_MANAGED);
        if(!attempt){first=texture;firstBuffer=renderer->native.effects.extra;}else if(attempt==2)S_REQUIRE(texture==first && renderer->native.effects.extra==firstBuffer);
        IDirect3DSurface9* active=nullptr;IDirect3DSurface9* level=nullptr;S_REQUIRE(SUCCEEDED(device->GetRenderTarget(0,&active)) && SUCCEEDED(texture->GetSurfaceLevel(0,&level)) && active==level);active->Release();level->Release();
        IDirect3DSurface9* absent=nullptr;S_REQUIRE(device->GetDepthStencilSurface(&absent)==D3DERR_NOTFOUND && !absent);DWORD z=9;device->GetRenderState(D3DRS_ZENABLE,&z);device->GetViewport(&viewport);S_REQUIRE(z==FALSE && viewport.Width==512 && viewport.Height==512);
        if(!attempt){float position[3]={};renderer->DrawCharacterShadow(model,position,0,1,.5f);}
        renderer->EndShadow();
        S_REQUIRE(SUCCEEDED(device->GetRenderTarget(0,&active)) && active==originalTarget);active->Release();S_REQUIRE(SUCCEEDED(device->GetDepthStencilSurface(&active)) && active==originalDepth);active->Release();device->GetRenderState(D3DRS_ZENABLE,&z);device->GetViewport(&viewport);S_REQUIRE(z==TRUE && viewport.X==0 && viewport.Y==0 && viewport.Width==originalDesc.Width && viewport.Height==originalDesc.Height);
        if(attempt<2){IDirect3DSurface9* level=nullptr;S_REQUIRE(SUCCEEDED(texture->GetSurfaceLevel(0,&level)));const auto rendered=pixels(device,level);level->Release();
            S_REQUIRE(rendered.size()==512*512*4);unsigned colored=0;for(unsigned i=0;i<512*512;++i){DWORD color;std::memcpy(&color,rendered.data()+4*i,4);colored+=(color&0xffffff)!=0;}std::fprintf(stderr,"Shadow%u colored %u\n",attempt,colored);
            if(!attempt){S_REQUIRE(colored>100 && colored<512*512-100);FILE* file=std::fopen("normal-shadow.bgra","wb");S_REQUIRE(file && std::fwrite(rendered.data(),1,rendered.size(),file)==rendered.size());std::fclose(file);}else S_REQUIRE(!colored);
        }
    }
    originalTarget->Release();originalDepth->Release();return 0;
}
