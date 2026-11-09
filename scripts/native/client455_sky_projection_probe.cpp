#define main unusedWorldEntry123
#include "client455_world_probe.cpp"
#undef main
#include <array>
#include <vector>
using Transform123=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DTRANSFORMSTATETYPE,const D3DMATRIX*);
static Transform123 original123;static void **real123,**observed123;static std::vector<D3DMATRIX> projected123;
static HRESULT WINAPI observe123(IDirect3DDevice9* d,D3DTRANSFORMSTATETYPE type,const D3DMATRIX* m){if(type==D3DTS_PROJECTION)projected123.push_back(*m);*reinterpret_cast<void***>(d)=real123;const HRESULT result=original123(d,type,m);*reinterpret_cast<void***>(d)=observed123;return result;}
struct Hook123{IDirect3DDevice9* d;void** original;std::array<void*,119> table;Hook123(IDirect3DDevice9* device):d(device),original(*reinterpret_cast<void***>(device)){std::memcpy(table.data(),original,sizeof(table));original123=reinterpret_cast<Transform123>(table[44]);table[44]=reinterpret_cast<void*>(observe123);real123=original;observed123=table.data();resume();}void pause(){*reinterpret_cast<void***>(d)=original;}void resume(){*reinterpret_cast<void***>(d)=table.data();}~Hook123(){pause();}};
static void bits123(FILE* out,const float* p,unsigned n){std::fputc('[',out);for(unsigned i=0;i<n;++i){DWORD bits;std::memcpy(&bits,p+i,4);std::fprintf(out,"%s%u",i?",":"",bits);}std::fputc(']',out);}
static int run123(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);auto* s=GetR3State();check(!s->mOrthographic&&s->mOrthographicScale==5,"confirmed InitCore false/scale5");s->mScreenXsize=640;s->mScreenYsize=480;s->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"actual device");FILE* out=std::fopen("projection.jsonl","wb");check(out!=nullptr,"trace");unsigned cases=0;
    {
        CLevel level;phase("level-created123");check(!level.mSkyBox->IsLoaded455(),"actual unloaded sky");Hook123 hook(GetD3dDevice());phase("hook-ready123");
        for(unsigned preset=0;preset<2;++preset)for(unsigned mode=0;mode<2;++mode)for(float scale:{.25f,5.f,16.f}){
            s->mFov=preset?1.1f:.6f;s->mAsfectRatio=preset?16.f/9:4.f/3;s->mNear=preset?300.f:17.f;s->mFar=preset?12000.f:6000.f;s->mScreenXsize=preset?1600.f:640.f;s->mScreenYsize=preset?900.f:480.f;s->mOrthographic=mode;s->mOrthographicScale=scale;
            D3DXVECTOR3 eye(10,20,-40),at(0,0,0),up(0,1,0);D3DXMatrixLookAtLH(&s->mMatView,&eye,&at,&up);for(unsigned i=0;i<24;++i)(&s->mFrustumPlane[0][0])[i]=100.f+float(i);projected123.clear();phase("before-sky123");level.DrawSkyBoxRender();phase("after-sky123");check(projected123.size()==2,"sky/world projection binds even when unloaded");hook.pause();D3DMATRIX actual;check(SUCCEEDED(GetD3dDevice()->GetTransform(D3DTS_PROJECTION,&actual))&&!std::memcmp(&actual,&s->mMatProj,64)&&!std::memcmp(&actual,&projected123[1],64),"device and source projection exact");hook.resume();
            std::fprintf(out,"{\"id\":%u,\"mode\":%u,\"parameters\":[%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g],\"sky\":",cases++,mode,s->mFov,s->mAsfectRatio,s->mNear,s->mFar,s->mScreenXsize,s->mScreenYsize,scale);bits123(out,reinterpret_cast<float*>(&projected123[0]),16);std::fprintf(out,",\"world\":");bits123(out,reinterpret_cast<float*>(&projected123[1]),16);std::fprintf(out,",\"view\":");bits123(out,reinterpret_cast<float*>(&s->mMatView),16);std::fprintf(out,",\"planes\":");bits123(out,&s->mFrustumPlane[0][0],24);std::fprintf(out,"}\n");
        }
    }
    std::fclose(out);g_MainApp.ReleaseR3D3D();ReleaseR3Engine();check(!warnings,"unexpected warnings");FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result");std::fprintf(result,"{\"status\":\"PASS\",\"cases\":%u,\"actual_CLevel\":true,\"actual_device\":true,\"unloaded_sky\":true,\"initial_flag0_scale5\":true,\"full_renderer\":false}\n",cases);std::fclose(result);return 0;
}
int main(){try{return run123();}catch(const std::exception& e){std::fprintf(stderr,"sky-projection123:%s\n",e.what());return 1;}}
