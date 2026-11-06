#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "rtmovie.h"
#include "client455_movie_state.h"
#include "jerror.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static unsigned warnings=0;
static void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
static void errorMessage(char* text){std::fprintf(stderr,"engine-error:%s\n",text);std::exit(2);}
static void warningMessage(char* text){if(warnings++<16)std::fprintf(stderr,"engine-warning:%s\n",text);}
static std::vector<DWORD> readback(const char* path){
    auto* device=GetD3dDevice();IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");std::vector<DWORD> pixels(640*480);
    for(unsigned y=0;y<480;++y)std::memcpy(pixels.data()+y*640,static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch,640*4);memory->UnlockRect();memory->Release();target->Release();FILE* out=std::fopen(path,"wb");check(out!=nullptr,"frame");check(std::fwrite(pixels.data(),4,pixels.size(),out)==pixels.size(),"frame write");std::fclose(out);return pixels;
}
static void projection(float expected){
    auto* state=GetR3State();check(state->mFov==expected,"currentFOV reset separate from defaultFOV");D3DXMATRIX actual,wanted;check(SUCCEEDED(GetD3dDevice()->GetTransform(D3DTS_PROJECTION,&actual)),"actual projection");D3DXMatrixPerspectiveFovLH(&wanted,expected,state->mAsfectRatio,state->mNear,state->mFar);for(unsigned i=0;i<16;++i)check(std::fabs(reinterpret_cast<float*>(&actual)[i]-reinterpret_cast<float*>(&wanted)[i])<0.000001f,"actual projection reset");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetErrorMessageProc(errorMessage);SetWarningMessageProc(warningMessage);auto* state=GetR3State();check(state->mFov==0.6f&&RF455_GetDefaultCameraFov()==0.6f,"pinned initial FOV0.6");state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D");
    // This is an explicit640x480 fixture. The legacy wrapper can retain its
    // outer-window height;R3SetViewPort updates viewport fields only.
    state->mScreenXsize=640;state->mScreenYsize=480;R3SetViewPort(0,0,640,480);RF455_SetDefaultCameraFov(0.73f);
    for(unsigned flags=0;flags<8;++flags){SetFov(1.1f);RF455_SetMovieState(flags);check(RF455_GetMovieState()==flags&&RF455_GetRequestedMovieState()==flags,"all low flag combinations");check(bool(state->mWideOn)==bool(flags&1)&&bool(state->mIsDrawLogo)==bool(flags&2),"real display state side effects");projection((flags&4)?0.73f:1.1f);}
    RF455_SetMovieState(0);SetFov(1.1f);RF455_AddMovieFlags(0x8000a100u);check(RF455_GetMovieState()==0x8000a100u&&!state->mWideOn&&!state->mIsDrawLogo,"add raw bits without display side effects");RF455_SetMovieState(0x12345672u);check(RF455_GetMovieState()==0x8000a102u&&RF455_GetRequestedMovieState()==0x12345672u&&!state->mWideOn&&state->mIsDrawLogo,"Set replaces only low3,records fullrequest,preserves old upperbits");projection(1.1f);RF455_RemoveMovieFlags(0xffffffffu);check(!RF455_GetMovieState()&&state->mIsDrawLogo,"remove raw bits without display side effects");RF455_SetMovieState(0);
    RTMovieSetState(7);check(RTMovieGetState()==7&&RF455_GetMovieState()==4&&!state->mWideOn&&!state->mIsDrawLogo,"legacy request API is distinct from455 state API");RTMovieSetState(0);check(RTMovieGetState()==0&&RF455_GetMovieState()==3&&state->mWideOn&&state->mIsDrawLogo,"legacy default request conversion");RF455_SetMovieState(0);RF455_SetDefaultCameraFov(0.6f);SetDefaultFov();projection(0.6f);
    IDirect3DTexture9* logo=nullptr;check(SUCCEEDED(GetD3dDevice()->CreateTexture(8,8,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&logo,nullptr)),"owned logo fixture");D3DLOCKED_RECT lock={};check(SUCCEEDED(logo->LockRect(0,&lock,nullptr,0)),"logo lock");for(unsigned y=0;y<8;++y)for(unsigned x=0;x<8;++x)reinterpret_cast<DWORD*>(static_cast<BYTE*>(lock.pBits)+y*lock.Pitch)[x]=0xffff4000;logo->UnlockRect(0);auto* savedLogo=state->mLogoTexture;state->mLogoTexture=logo;
    unsigned frames=0;
    for(unsigned effect:{0u,0x80000000u})for(unsigned flags:{1u,2u,3u}){
        RF455_SetMovieState(flags);SetStateFullScreenEffect(effect);check(R3BeginScene()!=FALSE,"begin scene");R3ClearFrameBuffer();D3DVIEWPORT9 viewport={};GetD3dDevice()->GetViewport(&viewport);check(viewport.Width==(effect?512u:640u)&&viewport.Height==(effect?512u:480u),"Clear retains full target viewport;letterbox belongs to display pass");Draw2DRectangle(0,0,LONG(state->mScreenXsize),LONG(state->mScreenYsize),0xff204060);FullScreenEffect();check(DrawFadeScreen()==TRUE,"clear fade domain");R3EndScene();char image[80];std::sprintf(image,"mode-%u-effect-%u.bgra",flags,effect?1u:0u);const auto pixels=readback(image);auto rgb=[&](unsigned x,unsigned y){return pixels[y*640+x]&0xffffff;};
        check(rgb(320,240)==0x204060,"unmodified scene center");if(flags&1){check(rgb(320,0)==0&&rgb(320,63)==0&&rgb(320,64)==0x204060&&rgb(320,(flags&2)?399:415)==0x204060&&rgb(320,479)==0,"exact640x480 letterbox bands outside logo overlay");}else check(rgb(320,0)==0x204060&&rgb(320,479)==0x204060,"no unintended letterbox");
        if(flags&2)check(rgb(320,399)==0x204060&&rgb(320,420)!=((flags&1)?0u:0x204060u)&&rgb(320,470)==((flags&1)?0u:0x204060u),"logo rows400..466 and DrawLogo after bars");++frames;
    }
    RF455_SetMovieState(4);SetStateFullScreenEffect(0);state->mLogoTexture=savedLogo;GetD3dDevice()->SetTexture(0,nullptr);logo->Release();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();check(!warnings,"warnings");FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"flag_combinations\":8,\"GPU_frames\":%u,\"warnings\":%u,\"real_positive_movie_flags\":true,\"fullrequest_and_upperbits\":true,\"raw_add_remove_without_display_sideeffects\":true,\"separate_defaultFov_and_projection\":true,\"real_letterbox_logo_plain_and_fullscreen\":true,\"legacy_request_api_explicit\":true,\"full_RVP_player\":false,\"full_Tutorial\":false}\n",frames,warnings);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception:%08lX RVA:%08lX\n",info->ExceptionRecord->ExceptionCode,reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress)-reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Movie state:%s\n",error.what());return 1;}}
