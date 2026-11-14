#include "client455_render_diagnostics.h"
#include <cstring>
#include <algorithm>
namespace {
constexpr unsigned RingCount=6,Sections=4;
struct Sample {
    IDirect3DQuery9* stamp[Sections][2]{};
    IDirect3DQuery9 *frequency=nullptr,*disjoint=nullptr;
    bool pending=false;unsigned started=0,ended=0;
};
struct Diagnostics {
    IDirect3DDevice9* device=nullptr;Sample ring[RingCount];int active=-1;
    bool tried=false;RF455RenderDiagnostics info{};
    LARGE_INTEGER cpuFrequency{},start{},previous{};
    double intervalSum=0,cpuSum=0;unsigned intervalCount=0,cpuCount=0;
    DWORD published=0;
} diagnostics;
template<class T>void release(T*&p){if(p){p->Release();p=nullptr;}}
void releaseQueries(){for(auto&s:diagnostics.ring){for(auto&pair:s.stamp)for(auto*&q:pair)release(q);release(s.frequency);release(s.disjoint);s={};}diagnostics.active=-1;}
bool initialize(IDirect3DDevice9*d){
    auto&s=diagnostics;s.tried=true;s.device=d;
    D3DDEVICE_CREATION_PARAMETERS creation{};IDirect3D9*api=nullptr;D3DADAPTER_IDENTIFIER9 id{};
    if(SUCCEEDED(d->GetCreationParameters(&creation))&&SUCCEEDED(d->GetDirect3D(&api))){
        if(SUCCEEDED(api->GetAdapterIdentifier(creation.AdapterOrdinal,0,&id))){
            strncpy_s(s.info.adapter,id.Description,_TRUNCATE);s.info.vendorId=id.VendorId;s.info.deviceId=id.DeviceId;
        }
        s.info.adapterOrdinal=creation.AdapterOrdinal;s.info.hardware=creation.DeviceType==D3DDEVTYPE_HAL;
    }release(api);
    for(auto&sample:s.ring){
        HRESULT hr=d->CreateQuery(D3DQUERYTYPE_TIMESTAMPFREQ,&sample.frequency);
        if(SUCCEEDED(hr))hr=d->CreateQuery(D3DQUERYTYPE_TIMESTAMPDISJOINT,&sample.disjoint);
        for(auto&pair:sample.stamp)for(auto*&q:pair)if(SUCCEEDED(hr))hr=d->CreateQuery(D3DQUERYTYPE_TIMESTAMP,&q);
        if(FAILED(hr)){releaseQueries();s.info.gpuTimingSupported=false;return false;}
    }s.info.gpuTimingSupported=true;return true;
}
void poll(){
    auto&s=diagnostics;
    for(auto&sample:s.ring){if(!sample.pending)continue;
        BOOL disjoint=TRUE;UINT64 frequency=0,ticks[Sections][2]{};
        HRESULT hr=sample.disjoint->GetData(&disjoint,sizeof(disjoint),0);if(hr==S_FALSE)continue;
        if(SUCCEEDED(hr))hr=sample.frequency->GetData(&frequency,sizeof(frequency),0);if(hr==S_FALSE)continue;
        for(unsigned section=0;section<Sections&&hr==S_OK;++section)if(sample.ended&(1u<<section))
            for(unsigned i=0;i<2&&hr==S_OK;++i)hr=sample.stamp[section][i]->GetData(&ticks[section][i],sizeof(UINT64),0);
        if(hr==S_FALSE)continue;sample.pending=false;
        if(FAILED(hr)){++s.info.queryErrors;s.info.gpuTimingSupported=false;releaseQueries();return;}
        if(disjoint||!frequency)continue;
        for(unsigned section=0;section<Sections;++section)if((sample.ended&(1u<<section))&&ticks[section][1]>=ticks[section][0]){
            const double ms=double(ticks[section][1]-ticks[section][0])*1000/double(frequency);
            s.info.gpuMs[section]=s.info.samples?s.info.gpuMs[section]*.85+ms*.15:ms;
        }++s.info.samples;
    }
}
}
void RF455_DiagnosticsBeginFrame(IDirect3DDevice9*d){
    if(!d)return;auto&s=diagnostics;
    if(s.device&&s.device!=d)RF455_ReleaseRenderDiagnostics();
    if(!s.tried)initialize(d);
    if(!s.cpuFrequency.QuadPart)QueryPerformanceFrequency(&s.cpuFrequency);
    QueryPerformanceCounter(&s.start);
    if(s.previous.QuadPart){s.intervalSum+=double(s.start.QuadPart-s.previous.QuadPart)*1000/s.cpuFrequency.QuadPart;++s.intervalCount;}
    s.previous=s.start;++s.info.frames;
    D3DVIEWPORT9 viewport{};if(SUCCEEDED(d->GetViewport(&viewport))){s.info.width=viewport.Width;s.info.height=viewport.Height;}
    const DWORD now=GetTickCount();if(now-s.published>=500&&s.intervalCount){
        s.info.frameMs=s.intervalSum/s.intervalCount;s.info.fps=1000/s.info.frameMs;
        s.info.cpuSubmissionMs=s.cpuCount?s.cpuSum/s.cpuCount:0;
        s.intervalSum=s.cpuSum=0;s.intervalCount=s.cpuCount=0;s.published=now;
    }
    if(!s.info.gpuTimingSupported)return;
    // Close a frame aborted by a caller, then recycle only signalled queries.
    RF455_DiagnosticsEndFrame();poll();
    if(s.info.frames%4)return;
    for(unsigned i=0;i<RingCount;++i)if(!s.ring[i].pending){
        auto&sample=s.ring[i];sample.started=sample.ended=0;
        if(FAILED(sample.disjoint->Issue(D3DISSUE_BEGIN))){++s.info.queryErrors;break;}
        s.active=int(i);RF455_GpuSectionBegin(0);break;
    }
}
void RF455_GpuSectionBegin(unsigned section){
    auto&s=diagnostics;if(s.active<0||section>=Sections)return;auto&q=s.ring[s.active];
    if(q.started&(1u<<section))return;
    if(SUCCEEDED(q.stamp[section][0]->Issue(D3DISSUE_END)))q.started|=1u<<section;else ++s.info.queryErrors;
}
void RF455_GpuSectionEnd(unsigned section){
    auto&s=diagnostics;if(s.active<0||section>=Sections)return;auto&q=s.ring[s.active];
    if(!(q.started&(1u<<section))||(q.ended&(1u<<section)))return;
    if(SUCCEEDED(q.stamp[section][1]->Issue(D3DISSUE_END)))q.ended|=1u<<section;else ++s.info.queryErrors;
}
void RF455_DiagnosticsEndFrame(){
    auto&s=diagnostics;if(s.active<0)return;RF455_GpuSectionEnd(0);auto&q=s.ring[s.active];
    const HRESULT a=q.frequency->Issue(D3DISSUE_END),b=q.disjoint->Issue(D3DISSUE_END);
    q.pending=SUCCEEDED(a)&&SUCCEEDED(b);if(!q.pending)++s.info.queryErrors;s.active=-1;
}
void RF455_DiagnosticsCpuEnd(){auto&s=diagnostics;if(!s.start.QuadPart)return;LARGE_INTEGER now;QueryPerformanceCounter(&now);s.cpuSum+=double(now.QuadPart-s.start.QuadPart)*1000/s.cpuFrequency.QuadPart;++s.cpuCount;}
RF455RenderDiagnostics RF455_GetRenderDiagnostics(){return diagnostics.info;}
void RF455_ReleaseRenderDiagnostics(){releaseQueries();diagnostics={};}
