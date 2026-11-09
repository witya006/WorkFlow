#define main unusedWorldEntryFade124
#include "client455_world_probe.cpp"
#undef main
#include <array>
#include <vector>
extern DWORD stSkyFadeColor;
extern float stSkyFadeTime,stSkyStartTick,stAllSkyFadeTime,stSkyFadeAlpha;
extern BOOL stIsFadeInStart;
extern DWORD GetColorToColorAlpha(DWORD,DWORD,float);
using State124=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DRENDERSTATETYPE,DWORD);
using Draw124=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRIMITIVETYPE,UINT,const void*,UINT);
static void **real124,**observed124;static State124 state124;static Draw124 draw124;
static std::vector<DWORD> colors124;static unsigned fogWrites124;
static HRESULT WINAPI observeState124(IDirect3DDevice9* d,D3DRENDERSTATETYPE state,DWORD value){
    if(state==D3DRS_FOGCOLOR||state==D3DRS_FOGSTART||state==D3DRS_FOGEND)++fogWrites124;
    *reinterpret_cast<void***>(d)=real124;const HRESULT hr=state124(d,state,value);*reinterpret_cast<void***>(d)=observed124;return hr;
}
static HRESULT WINAPI observeDraw124(IDirect3DDevice9* d,D3DPRIMITIVETYPE type,UINT count,const void* data,UINT stride){
    check(type==D3DPT_TRIANGLESTRIP&&count==2&&stride==28,"actual fade quad layout");
    DWORD color;std::memcpy(&color,static_cast<const BYTE*>(data)+16,4);colors124.push_back(color);
    for(unsigned i=1;i<4;++i){DWORD other;std::memcpy(&other,static_cast<const BYTE*>(data)+i*stride+16,4);check(other==color,"quad uniform color");}
    *reinterpret_cast<void***>(d)=real124;const HRESULT hr=draw124(d,type,count,data,stride);*reinterpret_cast<void***>(d)=observed124;return hr;
}
struct Hook124 {
    IDirect3DDevice9* d;std::array<void*,119> table;
    Hook124(IDirect3DDevice9* device):d(device){real124=*reinterpret_cast<void***>(d);std::memcpy(table.data(),real124,sizeof(table));state124=reinterpret_cast<State124>(table[57]);draw124=reinterpret_cast<Draw124>(table[83]);table[57]=reinterpret_cast<void*>(observeState124);table[83]=reinterpret_cast<void*>(observeDraw124);observed124=table.data();resume();}
    void pause(){*reinterpret_cast<void***>(d)=real124;}void resume(){*reinterpret_cast<void***>(d)=observed124;}~Hook124(){pause();}
};
static DWORD bits124(float f){DWORD u;std::memcpy(&u,&f,4);return u;}
static void dumpState124(FILE* f){std::fprintf(f,"[%u,%u,%u,%u,%u,%u]",stSkyFadeColor,bits124(stSkyFadeTime),bits124(stSkyStartTick),bits124(stAllSkyFadeTime),bits124(stSkyFadeAlpha),unsigned(stIsFadeInStart));}
static void setCW124(unsigned short cw){__asm fldcw cw}
static unsigned short getCW124(){unsigned short cw;__asm {fnstcw cw} return cw;}
static int runFade124(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);auto* s=GetR3State();s->mScreenXsize=640;s->mScreenYsize=480;s->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(s->MapPath,".\\Map\\");std::strcpy(s->EntityPath,".\\Map\\Entity\\");check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");auto* d=GetD3dDevice();const unsigned short originalCW=getCW124();FILE* out=std::fopen("fade.jsonl","wb");check(out!=nullptr,"trace");unsigned cases=0,blendCases=0;
    {
        Hook124 hook(d);
        for(unsigned precision:{0u,2u,3u}){
            const unsigned short cw=(originalCW&~0x0f00u)|(precision<<8);setCW124(cw);s->mFogColor=0xff13579b;s->mFogStart=123.4567f;s->mFogEnd=9876.543f;
            auto frame=[&](float now,float elapsed){
                R3SetTime(now);R3SetLoopTime(elapsed);hook.pause();check(SUCCEEDED(d->SetRenderState(D3DRS_FOGCOLOR,0x12345678))&&SUCCEEDED(d->SetRenderState(D3DRS_FOGSTART,0x3f800000))&&SUCCEEDED(d->SetRenderState(D3DRS_FOGEND,0x40000000))&&SUCCEEDED(d->BeginScene()),"begin numeric frame");hook.resume();colors124.clear();fogWrites124=0;
                std::fprintf(out,"{\"kind\":\"frame\",\"id\":%u,\"cw\":%u,\"now\":%u,\"loop\":%u,\"fog_input\":[%u,%u,%u],\"before\":",cases++,cw,bits124(now),bits124(elapsed),s->mFogColor,bits124(s->mFogStart),bits124(s->mFogEnd));dumpState124(out);const unsigned short before=getCW124();const BOOL result=DrawFadeSKy();check(getCW124()==before,"fade preserves x87 control word");std::fprintf(out,",\"after\":");dumpState124(out);hook.pause();DWORD fog[3];for(unsigned i=0;i<3;++i)check(SUCCEEDED(d->GetRenderState(D3DRENDERSTATETYPE(i?35+i:34),fog+i)),"actual fog query");check(SUCCEEDED(d->EndScene()),"end numeric frame");hook.resume();std::fprintf(out,",\"result\":%u,\"fog_writes\":%u,\"fog\":[%u,%u,%u],\"draws\":[",unsigned(result),fogWrites124,fog[0],fog[1],fog[2]);for(unsigned i=0;i<colors124.size();++i)std::fprintf(out,"%s%u",i?",":"",colors124[i]);std::fprintf(out,"]}\n");
            };
            for(float duration:{2.f,.2f}){
                R3SetTime(0);SetFadeSky(0x9a604020,duration);check(stSkyFadeTime==-0.600100040435791015625f&&stSkyStartTick==0&&stAllSkyFadeTime==duration&&stSkyFadeAlpha==0.0000001f&&!stIsFadeInStart,"actual SetFadeSky initial state");
                float previous=0;for(float now:{0.f,.1f,.3f,.6f,.60010004f,.8f,1.3f,1.41f,1.7f,2.01f,2.3f,2.7f}){const float elapsed=now-previous;frame(now,elapsed);previous=now;}
            }
            for(float sign:{-1.f,1.f})for(float now:{std::nextafter(.6f,0.f),.6f,std::nextafter(.6f,1.f)}){R3SetTime(0);SetFadeSky(0xffabcdef,10.f);stSkyFadeTime=sign*.60010004f;frame(now,0);}
            for(float alpha:{0.f,1.f,.5f,.1f,129.f/255.f,127.f/255.f,128.f/255.f,-.125f,1.125f}){
                const DWORD blended=GetColorToColorAlpha(0xff13579b,0x9a604020,alpha);hook.pause();check(SUCCEEDED(d->BeginScene()),"blend begin");hook.resume();colors124.clear();SetFadeFactor(0x9a604020,alpha);hook.pause();check(SUCCEEDED(d->EndScene()),"blend end");hook.resume();check(colors124.size()==1&&getCW124()==cw,"actual shared fade factor and CW");std::fprintf(out,"{\"kind\":\"blend\",\"cw\":%u,\"alpha\":%u,\"source\":%u,\"destination\":%u,\"color\":%u,\"quad\":%u,\"legacy_quad\":%u}\n",cw,bits124(alpha),0xff13579bu,0x9a604020u,blended,colors124[0],(0x604020u|(DWORD(alpha*255)<<24)));++blendCases;
            }
        }
    }
    setCW124(originalCW);std::fclose(out);
    {
        CCamera camera;g_pCamera=&camera;CLand land;check(land.Create()!=0,"land");char path[]=".\\Map\\bellato\\bellato.bsp";check(land.LoadLevel(path)!=0,"actual Bellato");auto& level=*land.GetLevel();check(level.mSkyBox->IsLoaded455(),"loaded sky");s->mFov=.6f;s->mAsfectRatio=640.f/480;s->mFar=6000;s->mNear=17;s->mOrthographic=FALSE;
        auto frame=[&](const char* name,float now,float elapsed){R3SetTime(now);R3SetLoopTime(elapsed);D3DXVECTOR3 eye(2466,477,-1429),at(2466,477,-1129),up(0,1,0);D3DXMATRIX view;D3DXMatrixLookAtLH(&view,&eye,&at,&up);float p[]={eye.x,eye.y,eye.z};level.SetCameraPos(p);level.SetViewMatrix(&view);D3DXMatrixInverse(&s->mInvMatView,nullptr,&s->mMatView);D3DXMatrixPerspectiveFovLH(&s->mMatProj,s->mFov,s->mAsfectRatio,s->mNear,s->mFar);D3DXMatrixMultiply(&s->mMatViewProj,&s->mMatView,&s->mMatProj);level.FrameMove();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"GPU begin");level.DrawSkyBoxRender();check(SUCCEEDED(d->EndScene()),"GPU end");if(name)capture(name);};
        stSkyFadeAlpha=0;frame("fade-base.bgra",0,0);SetFadeSky(0xff604020,2.f);frame("fade-middle.bgra",.3f,.3f);frame("fade-covered.bgra",.7f,.4f);frame(nullptr,1.5f,.8f);frame("fade-return.bgra",1.7f,.2f);frame("fade-done.bgra",2.3f,.6f);land.Destroy();g_pCamera=nullptr;
    }
    g_MainApp.ReleaseR3D3D();ReleaseR3Engine();check(!warnings,"unexpected warnings");FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result");std::fprintf(result,"{\"status\":\"PASS\",\"frame_cases\":%u,\"blend_cases\":%u,\"precision_modes\":3,\"GPU_frames\":5,\"actual_Bellato_sky\":true,\"warnings\":%u,\"original_cw\":%u,\"full_client\":false}\n",cases,blendCases,warnings,originalCW);std::fclose(result);return 0;
}
int main(){try{return runFade124();}catch(const std::exception& e){std::fprintf(stderr,"sky-fade124:%s\n",e.what());return 1;}}
