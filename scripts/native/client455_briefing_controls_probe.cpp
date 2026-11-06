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
#include "client455_briefing_controls.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_sprites.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static DWORD nowMs=1000;static float seconds=0;static unsigned clockQueries=0,deltaQueries=0;
static DWORD clockNow(){++clockQueries;return nowMs;}
static float deltaNow(){++deltaQueries;return seconds;}
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static std::vector<DWORD> capture(CGUIObject& object,const char* filename){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");check(object.Draw()!=0,"actual controls draw");check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");std::vector<DWORD> pixels(640*480);
    for(unsigned y=0;y<480;++y)std::memcpy(pixels.data()+y*640,static_cast<const BYTE*>(lock.pBits)+(y+view.Y)*lock.Pitch+view.X*4,640*4);
    FILE* out=std::fopen(filename,"wb");check(out!=nullptr,"frame");std::fwrite(pixels.data(),4,pixels.size(),out);std::fclose(out);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    unsigned selectors=0;const auto previous=RF455_SetGuiAnimationReplay({clockNow,deltaNow});
    {
        CSprite common,tutorial;char path[260];check(RF455_SelectSpritePath(1,path,sizeof(path)),"common path");common.LoadSprite(path);check(RF455_SelectSpritePath(21,path,sizeof(path)),"tutorial path");tutorial.LoadSprite(path);check(tutorial.GetMaxActions()==3&&tutorial.GetMaxFrames(2)==12,"real tutorial resource");
        CGUIBriefingBoard frame;frame.Show(TRUE);frame.SetPos(30,40);frame.SetCaps455(&common,TRUE);frame.SetSize(462,207);frame.SetColors455(0xff223344,0xffaabbcc);frame.SetBorder455(1,3);
        check(frame.GetAddedObjectNum()==2&&frame.GetUpper455().GetSizeX()==462&&frame.GetUpper455().GetSizeY()==32&&frame.GetLower455().GetPosY()==215,"real cap geometry");
        auto opaque=capture(frame,"briefing-frame.bgra");check((opaque[100*640+100]&0xffffff)==0x223344&&(opaque[100*640+33]&0xffffff)==0xaabbcc&&(opaque[100*640+32]&0xffffff)==0x223344&&(opaque[100*640+488]&0xffffff)==0xaabbcc,"body/border GPU pixels independent coordinates");
        frame.SetARGB(0xff556677);auto ownFill=capture(frame,"briefing-frame-self-fill.bgra");check((ownFill[100*640+100]&0xffffff)==0x556677&&(ownFill[100*640+33]&0xffffff)==0x556677,"base fill covers manual body/border before cap children");frame.SetARGB(0xffffffff);
        frame.SetAlpha455(96);check(frame.GetBodyColor455()==0x60223344&&frame.GetBorderColor455()==0x60aabbcc&&(frame.GetUpper455().GetARGB()>>24)==96,"alpha preserves RGB");capture(frame,"briefing-frame-alpha.bgra");frame.SetAlpha455(255);frame.SetCaps455(&common,FALSE);frame.SetPos(15,40);frame.SetSize(611,207);check(frame.GetUpper455().GetSizeX()==611&&frame.GetLower455().GetPosY()==215,"portrait cap resource width611");capture(frame,"briefing-frame-wide.bgra");
        CGUITutorialKeyBoard keys;keys.SetSprite455(&tutorial);keys.Show(TRUE);keys.SetPos(300,40);keys.SetSize(300,207);std::array<std::array<BYTE,2>,2> rows={{{{255,255}},{{255,255}}}};
        const BYTE supported[]={0,1,2,3,4,17,18,32,65,70,73,77,79,83,87,90,112};
        for(unsigned key=0;key<256;++key){rows[0][0]=static_cast<BYTE>(key);rows[0][1]=255;keys.SetRows455(1,rows);bool valid=false;for(BYTE known:supported)valid|=key==known;check(keys.GetAddedObjectNum()==(valid?1:0),"all BYTE key selector membership");selectors+=valid;}
        rows={{{{0,32}},{{255,255}}}};keys.SetRows455(1,rows);check(keys.GetAddedObjectNum()==3,"first+plus+second");check(keys.GetKey455(0,0).GetPosX()==359&&keys.GetPlus455(0).GetPosX()==428&&keys.GetKey455(0,1).GetPosX()==445,"width includes one5px but placement two5px gaps");
        check(keys.GetKey455(0,1).GetU()[1]==0.78125f&&keys.GetKey455(0,1).GetV()[1]==0.625f,"static glyph excludes texture padding");capture(keys,"briefing-keys-single.bgra");
        rows={{{{3,255}},{{17,3}}}};keys.SetRows455(2,rows);const auto labelHeight=keys.GetOr455().GetSizeY();check(keys.GetAddedObjectNum()==5&&keys.GetKey455(0,0).GetPosX()==384&&keys.GetKey455(0,0).GetPosY()==74&&keys.GetOr455().GetPosY()==138-labelHeight&&keys.GetKey455(1,0).GetPosY()==160,"two rows share widest width and64height");capture(keys,"briefing-keys-two.bgra");
        keys.GetKey455(0,0).SetFrame455(2);rows={{{{255,255}},{{65,255}}}};keys.SetRows455(2,rows);check(keys.GetKey455(0,0).GetFrame455()==2&&keys.GetKey455(0,0).GetSizeY()==64&&keys.GetKey455(1,0).GetPosY()==160,"255 preserves animation and stale size affects height");capture(keys,"briefing-keys-stale.bgra");
        rows[0][0]=51;keys.SetRows455(1,rows);check(keys.GetKey455(0,0).GetFrame455()==0&&keys.GetKey455(0,0).GetSizeY()==64,"unsupported non255 resets animation but keeps size");keys.SetRows455(0,rows);check(!keys.GetAddedObjectNum(),"zero rows clear only");
        RF455GuiAnimatedImage animation;animation.Show(TRUE);animation.SetPos(40,300);animation.SetImage455(&tutorial,1,0);check(animation.GetV()[1]==1,"SetImage samples full original sheet");animation.SetSheet455(1,2);check(animation.GetSizeX()==64&&animation.GetSizeY()==64&&animation.GetV()[1]==1,"SetSheet delays UV until advance");animation.SetFPS455(1);seconds=0.25f;animation.Update();check(animation.GetFrame455()==0.25f&&animation.GetV()[1]==0.5f,"quarter frame and first cell");capture(animation,"briefing-animation-first.bgra");seconds=0.75f;animation.Update();check(animation.GetFrame455()==1&&animation.GetV()[0]==0.5f&&animation.GetV()[1]==1,"second cell");capture(animation,"briefing-animation-second.bgra");seconds=1;animation.Update();check(animation.GetFrame455()==0&&animation.IsPaused455()&&animation.GetPauseTime455()==1000,"loop discards excess and stamps pause");animation.Update();check(animation.IsPaused455(),"pause elapsed equal0 does not resume");nowMs=1001;animation.Update();check(!animation.IsPaused455()&&animation.GetFrame455()==0,"resume does not advance in same Update");
        animation.SetLoop455(FALSE);seconds=10;const unsigned priorClocks=clockQueries;animation.Update();check(animation.IsFinished455()&&animation.GetFrame455()==1&&clockQueries==priorClocks,"nonloop clamps and finishes without clock");const auto priorDeltas=deltaQueries;animation.Update();check(deltaQueries==priorDeltas,"finished no delta query");
        animation.Reset455();animation.SetImage455(&tutorial,1,2);animation.SetUVExtent455(32,32);animation.SetSheet455(1,3);animation.SetFrame455(1);check(animation.GetSizeY()==64&&animation.GetU()[1]==0.5f&&animation.GetV()[0]==0.125f&&animation.GetV()[1]==0.25f,"forced UV extents independent of cell size");capture(animation,"briefing-animation-cropped.bgra");animation.SetSheet455(0,0);animation.SetFrame455(500,TRUE);check(animation.GetTotal455()==1&&animation.GetFrame455()==0&&animation.IsFinished455(),"BYTE zero grid and out-of-range frame reset");animation.Show(FALSE);const auto hiddenDeltas=deltaQueries;animation.Update();check(deltaQueries==hiddenDeltas&&!animation.Draw(),"hidden gate");
        tutorial.ReleaseSprite();common.ReleaseSprite();
    }
    RF455_SetGuiAnimationReplay(previous);R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"real_frame_caps\":true,\"body_border_GPU\":true,\"alpha_RGB\":true,\"key_selectors\":%u,\"key_rows_gaps_stale\":true,\"sprite_padding_UV\":true,\"sheet_animation_pause_loop\":true,\"forced_UV_and_zero_grid\":true,\"ordinary_briefing\":false,\"full_Tutorial\":false}\n",selectors);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Briefing controls: %s\n",error.what());return 1;}}
