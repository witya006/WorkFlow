#include "client455_lobby_shadow.h"
#include "client455_lobby_post.h"
#include <algorithm>
#include <cmath>
#include <vector>
#include <new>
void RF455_RenderLobbyShadows(CBsp* bsp){
    auto abandon=[](){RF455_InvalidateLobbyShadows(true);};
    if(!bsp||!bsp->IsLoaded()||!RF455_GetLobbyPostTelemetry().active){abandon();return;}
    auto* groups=bsp->GetMatGroup();const unsigned count=bsp->GetMatGroupNum();
    if(!groups||!count||count>65535||bsp->mObjectNum>65535||
       (bsp->mObjectNum&&!bsp->mObject)||!bsp->mCVertex||!bsp->mCVertexId){abandon();return;}
    float low[3]={1e20f,1e20f,1e20f},high[3]={-1e20f,-1e20f,-1e20f};
    auto opaque=[](const _BSP_MAT_GROUP& g){
        if(g.MtlId<0||(g.Type&~3u)||!g.TriNum)return false;
        const auto& m=GetMainMaterial()[g.MtlId];
        return m.m_dwLayerNum && !m.m_Layer[0].m_dwAlphaType && (m.m_Layer[0].m_ARGB>>24)==255;
    };
    // Needs the one narrow friend declaration in CBsp; no layout/ABI change.
    // The loader stores mCVertex in bind-world coordinates (bsp.cpp's
    // LoadStaticVertexBuffer applies the time-zero object matrix), while the
    // GPU VB retains decoded object-local positions. Serialized BBMin/BBMax
    // are not local bounds: actual lobby animated vertices lie outside them.
    // Fit actual CPU geometry with inverse(bind)*current, never BB*current.
    std::vector<D3DXMATRIX> matrices,delta;
    std::vector<unsigned char> needed;
    try{
        matrices.resize(bsp->mObjectNum+1);delta.resize(bsp->mObjectNum+1);
        needed.resize(bsp->mObjectNum+1,0);
        for(unsigned i=0;i<count;++i)if(opaque(groups[i])){
            const auto& g=groups[i];
            if(g.ObjectId>bsp->mObjectNum||g.VertexBufferId>=bsp->mStaticVBCnt||
               g.CFaceStartVId>bsp->mVertexNum||g.VCnt>bsp->mVertexNum-g.CFaceStartVId){abandon();return;}
            needed[g.ObjectId]=1;
        }
        D3DXMatrixIdentity(&matrices[0]);D3DXMatrixIdentity(&delta[0]);
        std::vector<_ANI_OBJECT> bindObjects,currentObjects;
        if(bsp->mObjectNum){
            bindObjects.assign(bsp->mObject,bsp->mObject+bsp->mObjectNum);
            currentObjects=bindObjects;
        }
        for(auto& object:bindObjects)object.AniFrameCache=0;
        for(auto& object:currentObjects)object.AniFrameCache=0;
        // Reuse the exact event/time logic on isolated object records. This
        // also isolates flag, now_frame, f_matrix/s_matrix and parent caches.
        // Live state is restored before Begin, including every early return.
        struct ObjectScope {
            _ANI_OBJECT*& slot;_ANI_OBJECT* original;
            ObjectScope(_ANI_OBJECT*& p,_ANI_OBJECT* copy):slot(p),original(p){slot=copy;}
            ~ObjectScope(){slot=original;}
        } objects(bsp->mObject,currentObjects.empty()?nullptr:currentObjects.data());
        for(unsigned id=1;id<=bsp->mObjectNum;++id)if(needed[id]){
            D3DXMATRIX bind,inverseBind;
            ::GetObjectMatrix(bind.m,WORD(id),bindObjects.data(),0);
            bsp->GetBspObjectMatrix(matrices[id].m,WORD(id));
            if(!D3DXMatrixInverse(&inverseBind,nullptr,&bind)){abandon();return;}
            delta[id]=inverseBind*matrices[id];
            for(unsigned n=0;n<16;++n)if(!std::isfinite(reinterpret_cast<float*>(&delta[id])[n])||
                !std::isfinite(reinterpret_cast<float*>(&matrices[id])[n])){abandon();return;}
        }
    }catch(const std::bad_alloc&){abandon();return;}
    unsigned casters=0;
    for(unsigned i=0;i<count;++i)if(opaque(groups[i])){
        const auto& g=groups[i];if(!g.VCnt)continue;
        ++casters;
        for(unsigned v=0;v<g.VCnt;++v){
            const DWORD id=bsp->mCVertexId[g.CFaceStartVId+v];
            if(id>=bsp->mCVertexNum){abandon();return;}
            const D3DXVECTOR3 position(bsp->mCVertex[id]);D3DXVECTOR3 world;
            D3DXVec3TransformCoord(&world,&position,&delta[g.ObjectId]);
            const float values[3]={world.x,world.y,world.z};
            for(unsigned axis=0;axis<3;++axis){
                if(!std::isfinite(values[axis])){abandon();return;}
                low[axis]=(std::min)(low[axis],values[axis]);
                high[axis]=(std::max)(high[axis],values[axis]);
            }
        }
    }
    auto* d=GetD3dDevice();
    if(!casters||!RF455_BeginLobbyShadows(d,low,high)){abandon();return;}
    bool submitted=true;
    for(unsigned i=0;i<count;++i)if(opaque(groups[i])){
        const auto& g=groups[i];
        // Do not call RenderIndepentMatGroup: it obtains/advances object state
        // again. The exact matrix used by fitting is also used for this draw.
        HRESULT hr=d->SetTransform(D3DTS_WORLD,&matrices[g.ObjectId]);
        if(SUCCEEDED(hr))hr=d->SetStreamSource(0,bsp->mStaticVertexBuffer[g.VertexBufferId].m_lpVertexBuffer,0,sizeof(_D3DR3VERTEX_TEX2));
        if(SUCCEEDED(hr))hr=d->SetIndices(bsp->mStaticIndexedBuffer.m_lpIndexBuffer);
        if(FAILED(hr)){submitted=false;break;}
        RF455_DrawLobbyShadowGroup(d,g.VBMinIndex,g.VCnt,g.IBMinIndex,g.TriNum);
    }
    RF455_EndLobbyShadows(d);
    if(!submitted)abandon();
}
