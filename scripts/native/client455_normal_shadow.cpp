#include "Character.h"
#include "client455_normal_shadow.h"
#include "client455_normal_shadow_constants.h"
#include <cstring>

extern "C" {unsigned RF455_NormalShadowQuadBits[24]={};}
namespace {
// Confirmed owner8920/8924 slots are the last8bytes of effects storage.
constexpr unsigned SavedTarget=208,SavedDepth=212;
void save(RF455RendererEffects& effects,unsigned offset,IDirect3DSurface9* surface){
    std::memcpy(reinterpret_cast<unsigned char*>(&effects)+offset,&surface,4);
}
IDirect3DSurface9* saved(const RF455RendererEffects& effects,unsigned offset){
    IDirect3DSurface9* value;std::memcpy(&value,reinterpret_cast<const unsigned char*>(&effects)+offset,4);return value;
}
// 9335F0 uses current render-target format/usage/pool and accepts only S_OK,
// not every nonnegative HRESULT. Its first two COM return codes are ignored.
IDirect3DTexture9* createTexture(IDirect3DDevice9* device){
    IDirect3DSurface9* target;device->GetRenderTarget(0,&target);D3DSURFACE_DESC desc;target->GetDesc(&desc);
    IDirect3DTexture9* texture;const HRESULT result=device->CreateTexture(512,512,1,desc.Usage,desc.Format,desc.Pool,&texture,nullptr);
    target->Release();return result==D3D_OK?texture:nullptr;
}
}
extern "C" int RF455_BeginNormalShadow(RF455CharacterRenderer* owner,unsigned index){
    if(index>=20)return 0;
    auto& effects=owner->effects;auto* device=owner->device;
    if(!effects.resources[index]){effects.resources[index]=createTexture(device);if(!effects.resources[index])return 0;}
    if(!effects.extra){
        std::memcpy(RF455_NormalShadowQuadBits,RF455_SHADOW_QUAD_BITS,96);
        IDirect3DVertexBuffer9* buffer=nullptr;
        const HRESULT result=device->CreateVertexBuffer(96,8,322,D3DPOOL_MANAGED,&buffer,nullptr);effects.extra=buffer;
        if(FAILED(result))return 0;
        void* vertices;if(FAILED(buffer->Lock(0,96,&vertices,0)))return 0;
        std::memcpy(vertices,RF455_NormalShadowQuadBits,96);buffer->Unlock();
    }
    IDirect3DSurface9* depth;device->GetDepthStencilSurface(&depth);save(effects,SavedDepth,depth);
    IDirect3DSurface9* surface=nullptr;static_cast<IDirect3DTexture9*>(effects.resources[index])->GetSurfaceLevel(0,&surface);
    IDirect3DSurface9* target;device->GetRenderTarget(0,&target);save(effects,SavedTarget,target);
    device->SetRenderTarget(0,surface);const HRESULT result=device->SetDepthStencilSurface(nullptr);surface->Release();
    device->Clear(0,nullptr,D3DCLEAR_TARGET,0,1,0);device->BeginScene();device->SetRenderState(D3DRS_ZENABLE,FALSE);
    return result;
}
extern "C" void RF455_EndNormalShadow(RF455CharacterRenderer* owner){
    auto* device=owner->device;device->SetRenderState(D3DRS_ZENABLE,TRUE);device->EndScene();
    auto* target=saved(owner->effects,SavedTarget);auto* depth=saved(owner->effects,SavedDepth);
    device->SetRenderTarget(0,target);device->SetDepthStencilSurface(depth);target->Release();depth->Release();
    // The reference retains these released pointer values,not nulls. They are
    // overwritten by the next successful Begin;the owner destructor ignores them.
}
int CRender::BeginShadow(unsigned long index){return RF455_BeginNormalShadow(&native,index);}
void CRender::EndShadow(){RF455_EndNormalShadow(&native);}
