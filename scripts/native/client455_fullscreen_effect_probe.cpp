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
#include "client455_fullscreen_effect.h"
#include "client455_scene_capture.h"
#include "jerror.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <stdexcept>
#include <vector>
#include <utility>
extern CMainApp g_MainApp;
extern CTextureRender stRToTMain,stRToTBlur;
extern CTextureRender stShadow;
static void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
static unsigned warnings=0;
static void errorMessage(char* text){std::fprintf(stderr,"engine-error:%s\n",text);std::exit(2);}
static void warningMessage(char* text){if(warnings++<16)std::fprintf(stderr,"engine-warning:%s\n",text);}
static unsigned resources137=0,captures137=0;
static void resources137check(unsigned width,unsigned height,bool perturbation){
    CTextureRender* targets[]={RF455_GetSceneCaptureTarget(),&stRToTMain,&stRToTBlur,RF455_GetAuxiliarySceneTarget(),&stShadow};
    const unsigned sizes[][2]={{width,height},{512,512},{512,512},{512,512},{256,256}};
    const BOOL depths[]={TRUE,TRUE,FALSE,TRUE,FALSE};
    static_assert(sizeof(CTextureRender)==40,"455 render texture layout");
    for(unsigned i=0;i<5;++i){
        for(unsigned j=0;j<i;++j)check(targets[i]!=targets[j],"five distinct render targets137");
        DWORD fields[10];std::memcpy(fields,targets[i],40);
        if(fields[4]!=TRUE||fields[6]!=DWORD(depths[i])||targets[i]->GetXSize()!=sizes[i][0]||targets[i]->GetYSize()!=sizes[i][1])std::fprintf(stderr,"resource137:%u loaded:%lu depth:%lu size:%lu,%lu expected:%u,%u\n",i,fields[4],fields[6],targets[i]->GetXSize(),targets[i]->GetYSize(),sizes[i][0],sizes[i][1]);
        check(fields[4]==TRUE&&fields[6]==DWORD(depths[i])&&targets[i]->GetXSize()==sizes[i][0]&&targets[i]->GetYSize()==sizes[i][1],"actual dimensions/depth flags137");
        D3DSURFACE_DESC desc={};check(targets[i]->GetD3DTexture()&&SUCCEEDED(targets[i]->GetD3DTexture()->GetLevelDesc(0,&desc))&&desc.Width==sizes[i][0]&&desc.Height==sizes[i][1],"actual allocated GPU texture137");
        check((fields[3]!=0)==bool(depths[i]),"actual depth surface ownership137");
    }
    check(bool(RF455_GetPerturbationTexture())==perturbation,"perturbation resource presence137");++resources137;
}
static void released137(){
    CTextureRender* targets[]={RF455_GetSceneCaptureTarget(),&stRToTMain,&stRToTBlur,RF455_GetAuxiliarySceneTarget(),&stShadow};
    for(auto* target:targets)check(!target->GetD3DTexture()&&!target->GetXSize()&&!target->GetYSize(),"release all five resources137");
    check(!RF455_GetPerturbationTexture(),"perturbation release/null137");
}
static std::vector<DWORD> surfacePixels137(IDirect3DSurface9* surface){
    auto* device=GetD3dDevice();IDirect3DSurface9* memory=nullptr;D3DSURFACE_DESC desc={};surface->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr))&&SUCCEEDED(device->GetRenderTargetData(surface,memory)),"capture GPU readback137");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"capture pixels137");
    std::vector<DWORD> result(desc.Width*desc.Height);for(unsigned y=0;y<desc.Height;++y)std::memcpy(result.data()+y*desc.Width,static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch,desc.Width*4);memory->UnlockRect();memory->Release();return result;
}
static std::vector<DWORD> texturePixels137(IDirect3DTexture9* texture){
    IDirect3DSurface9* surface=nullptr;check(SUCCEEDED(texture->GetSurfaceLevel(0,&surface)),"capture surface137");const auto result=surfacePixels137(surface);surface->Release();return result;
}
static void releaseRetainedCapture137(IDirect3DTexture9* texture){
    //The target helper retains one GetSurfaceLevel reference. Only this lab
    //compensates it after observation,so teardown can verify the other owners.
    IDirect3DSurface9* surface=nullptr;texture->GetSurfaceLevel(0,&surface);surface->Release();surface->Release();
}
static std::vector<DWORD> readback(const char* path){
    auto* device=GetD3dDevice();IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"readback target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"readback surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"readback lock");D3DVIEWPORT9 viewport={};device->GetViewport(&viewport);check(viewport.X==0&&viewport.Y==0&&viewport.Width==640&&viewport.Height==480,"restored screen viewport");
    std::vector<DWORD> pixels(640*480);for(unsigned y=0;y<480;++y)std::memcpy(pixels.data()+y*640,static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch,640*4);
    if(path){FILE* out=std::fopen(path,"wb");check(out!=nullptr,"GPU frame file");check(std::fwrite(pixels.data(),4,pixels.size(),out)==pixels.size(),"GPU frame write");std::fclose(out);}memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static void render(DWORD mode,float density,DWORD rgb,const char* frame,IDirect3DSurface9* expectedTarget,IDirect3DSurface9* expectedDepth){
    RF455_SetFullScreenEffectDensity(density);check(RF455_GetFullScreenEffectDensity()==density,"raw density storage");SetStateFullScreenEffect(mode);check(GetStateFullScreenEffect()==mode,"fullDWORD mode storage");check(R3BeginScene()!=FALSE,"R3BeginScene");R3ClearFrameBuffer();
    if(mode)check(GetR3State()->mScreenXsize==512&&GetR3State()->mScreenYsize==512,"actual effect target512");
    Draw2DRectangle(0,0,LONG(GetR3State()->mScreenXsize),LONG(GetR3State()->mScreenYsize),0xff000000|rgb);FullScreenEffect();
    auto* device=GetD3dDevice();IDirect3DSurface9 *target=nullptr,*depth=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target))&&target==expectedTarget,"restored actual framebuffer");check(SUCCEEDED(device->GetDepthStencilSurface(&depth))&&depth==expectedDepth,"restored actual depth");target->Release();depth->Release();check(GetStateFullScreenEffect()==mode,"requested fullDWORD mode survives composite");
    DWORD z=0;check(SUCCEEDED(device->GetRenderState(D3DRS_ZENABLE,&z))&&z==TRUE,"depth enable restored");check(GetR3State()->mScreenXsize==640&&GetR3State()->mScreenYsize==480,"screen dimensions restored");Draw2DRectangle(4,4,20,20,0xffffffff);R3EndScene();
    const auto pixels=readback(frame);check((pixels[240*640+320]&0xffffff)==rgb,"final opaque scene,without temporal residue");check((pixels[10*640+10]&0xffffff)==0xffffff,"UI drawn on actual framebuffer after composite");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetErrorMessageProc(errorMessage);SetWarningMessageProc(warningMessage);auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");check(RF455_GetFullScreenEffectDensity()==0.25f,"pinned default density");
    auto* device=GetD3dDevice();IDirect3DSurface9 *target=nullptr,*depth=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"baseline target");check(SUCCEEDED(device->GetDepthStencilSurface(&depth)),"baseline depth");unsigned frames=0;
    D3DSURFACE_DESC backbuffer137={};target->GetDesc(&backbuffer137);resources137check(backbuffer137.Width,backbuffer137.Height,false);
    for(const auto& size:{std::pair<unsigned,unsigned>{320,240},{800,600},{640,480}}){ReleaseFullScreenEffect();released137();state->mScreenXsize=float(size.first);state->mScreenYsize=float(size.second);InitFullScreenEffect();resources137check(size.first,size.second,false);}
    IDirect3DTexture9* fixture=nullptr;check(SUCCEEDED(D3DXCreateTexture(device,32,16,1,0,D3DFMT_A8R8G8B8,D3DPOOL_MANAGED,&fixture)),"perturbation fixture137");check(SUCCEEDED(D3DXSaveTextureToFileA("System/PerbMap.dds",D3DXIFF_DDS,fixture,nullptr)),"perturbation fixture file137");fixture->Release();
    for(unsigned i=0;i<2;++i){ReleaseFullScreenEffect();released137();InitFullScreenEffect();resources137check(640,480,true);D3DSURFACE_DESC desc={};RF455_GetPerturbationTexture()->GetLevelDesc(0,&desc);check(desc.Width==32&&desc.Height==16,"actual perturbation file loaded137");}
    ReleaseFullScreenEffect();released137();check(DeleteFileA("System/PerbMap.dds")!=FALSE,"remove own perturbation fixture137");InitFullScreenEffect();resources137check(640,480,false);
    //The existing wrapper allocates its backbuffer before RestoreDevice changes
    //the viewport dimensions. Use the actual full surface for an exact copy;
    //wrapper/viewport equivalence itself remains a separate open contract.
    ReleaseFullScreenEffect();state->mScreenXsize=float(backbuffer137.Width);state->mScreenYsize=float(backbuffer137.Height);InitFullScreenEffect();resources137check(backbuffer137.Width,backbuffer137.Height,false);state->mScreenXsize=640;state->mScreenYsize=480;
    SetStateFullScreenEffect(0);check(R3BeginScene()!=FALSE,"capture begin137");R3ClearFrameBuffer();Draw2DRectangle(0,0,640,480,0xff0040a0);Draw2DRectangle(64,96,320,240,0xffe03010);R3EndScene();
    const auto before137=surfacePixels137(target);auto* captured=RF455_CaptureCurrentScene();check(captured==RF455_GetSceneCaptureTarget()->GetD3DTexture()&&texturePixels137(captured)==before137&&surfacePixels137(target)==before137,"actual framebuffer copied without changing it137");releaseRetainedCapture137(captured);++captures137;
    SetStateFullScreenEffect(0x80000000u);check(R3BeginScene()!=FALSE,"active capture begin137");R3ClearFrameBuffer();Draw2DRectangle(0,0,512,512,0xff508020);R3EndScene();captured=RF455_CaptureCurrentScene();check(captured==stRToTMain.GetD3DTexture(),"active capture selects main137");const auto activePixels137=texturePixels137(captured);check((activePixels137[256*512+256]&0xffffff)==0x508020,"active target pixels137");releaseRetainedCapture137(captured);++captures137;SetStateFullScreenEffect(0);check(R3BeginScene()!=FALSE,"restore direct frame137");R3EndScene();
    for(float density:{0.0f,0.15f,0.25f,1.0f}){unsigned color=0;for(DWORD rgb:{0xff0000u,0x0000ffu,0x00ff00u}){char image[80];const char* output=nullptr;if(density==0.15f){std::sprintf(image,"primary-%u.bgra",color);output=image;}render(0x80000000u,density,rgb,output,target,depth);++color;++frames;}}
    render(0,0.25f,0x00ffffu,"disabled.bgra",target,depth);++frames;render(0x80000005u,0.15f,0xff00ffu,"combined-mode.bgra",target,depth);++frames;render(0,0.25f,0xffff00u,nullptr,target,depth);++frames;
    const auto oldLevel=state->mThisVidMemLevel;
    for(unsigned level:{0u,2u}){ReleaseFullScreenEffect();state->mThisVidMemLevel=level;InitFullScreenEffect();check(stRToTMain.GetXSize()==512&&stRToTMain.GetYSize()==512&&stRToTBlur.GetXSize()==512&&stRToTBlur.GetYSize()==512,"fixed512 even legacy low-video-memory mode");render(0x80000000u,0.15f,0xff0000u,nullptr,target,depth);++frames;}
    SetStateFullScreenEffect(0);ReleaseFullScreenEffect();SetStateFullScreenEffect(0x80000000u);check(!R3BeginScene(),"unloaded effect resource must fail BeginScene");SetStateFullScreenEffect(0);state->mThisVidMemLevel=oldLevel;InitFullScreenEffect();render(0x80000000u,0.25f,0x0000ffu,nullptr,target,depth);++frames;
    SetStateFullScreenEffect(0);target->Release();depth->Release();g_MainApp.ReleaseR3D3D();released137();ReleaseR3Engine();check(!warnings,"no engine warnings");FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"GPU_frames\":%u,\"saved_frames\":5,\"densities\":[0,0.15,0.25,1],\"warnings\":%u,\"actual_R3Begin_FullScreenEffect_End\":true,\"current_scene_opaque_final\":true,\"framebuffer_depth_viewport_UI_restored\":true,\"texture512_low_video_memory\":true,\"failed_BeginScene_reported\":true,\"resource_configurations\":%u,\"capture_cases\":%u,\"targets\":5,\"resize_cases\":3,\"perturbation_load_release\":true,\"missing_perturbation_supported\":true,\"framebuffer_copy_exact\":true,\"active_target_selection\":true,\"retained_capture_reference_compensated_by_lab\":true,\"complete_water_bloom_lifecycle\":false}\n",frames,warnings,resources137,captures137);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception:%08lX RVA:%08lX\n",info->ExceptionRecord->ExceptionCode,reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress)-reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Fullscreen effect:%s\n",error.what());return 1;}}
