#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/guiinventorywindow.h"
#include "mainapp.h"
#include "client455_gui_animation.h"
#include "client455_gui_input.h"
#include "client455_icon_links.h"
#include "client455_linker_cooldown.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
extern CMainApp g_MainApp;
static void check(bool b,const char* message){if(!b)throw std::runtime_error(message);}
template<class Draw>static void capture(Draw draw,const char* name){auto* d=GetD3dDevice();check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(d->BeginScene()),"begin");draw();check(SUCCEEDED(d->EndScene()),"end");IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(d->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(d->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 viewport={};d->GetViewport(&viewport);FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");for(unsigned y=viewport.Y;y<viewport.Y+480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+viewport.X;check(std::fwrite(row,4,640,f)==640,"pixels");}std::fclose(f);memory->UnlockRect();memory->Release();target->Release();}

static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    auto& runtime=RF455_GameItems();auto& links=RF455_GameIconLinks();links.clear();
    check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"real inputs");
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();
    GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");const auto baseline=GetDmallocSize();
    unsigned direct=0,normalized=0,geometry=0;
    {
        CGUIItem fresh;check(!fresh.LockGlyph455().IsShow(),"constructor hides lock");
        FILE* input=std::fopen("metadata-samples.bin","rb");check(input!=nullptr,"sample");char magic[4];unsigned n=0,row[3];
        check(std::fread(magic,1,4,input)==4&&!std::memcmp(magic,"MS94",4)&&std::fread(&n,4,1,input)==1&&n==16&&std::fread(row,4,3,input)==3,"real sample extent");std::fclose(input);
        CGUIInventoryBoard inventory;CBoardObject original;original.SetItem455(runtime.create(row[0],row[1],row[2]));
        auto* payload=original.GetItem455();check(payload&&inventory.TakeInItem455(0,&original,0),"actual EDF inventory owner");
        auto& icon=*original.GetIcon();auto& glyph=icon.LockGlyph455();auto* sprite=gSpriteMgr.GetTargetSprite455(52);
        check(sprite&&glyph.GetSpriteInfo()->pSprite==sprite&&!glyph.GetSpriteInfo()->wActionNo&&!glyph.GetSpriteInfo()->wFrameNo,"actual52/0/0");
        const auto width=sprite->GetSpriteOrgXL(0,0),height=sprite->GetSpriteOrgYL(0,0);
        check(glyph.GetSizeX()==width&&glyph.GetSizeY()==height&&width&&height,"real glyph geometry");
        for(unsigned flag=0;flag<256;++flag){icon.SetLock455(BYTE(flag));check(glyph.IsShow()==flag,"GUI setter preserves BYTE visibility");++direct;
            payload->header().flag21=BYTE(flag);original.RefreshLock455();check(glyph.IsShow()==(flag?1:0),"wrapper normalizes nonzero flag21");++normalized;}
        CBoardObject empty;empty.SetIcon(&icon);icon.SetLock455(7);empty.RefreshLock455();check(glyph.IsShow()==7,"null payload refresh leaves state");empty.SetIcon(nullptr);
        for(LONG x:{-40L,0L,100L})for(LONG y:{-20L,100L})for(LONG size:{32L,40L,64L}){
            icon.SetSize(size,size);icon.SetPos(x,y);check(glyph.GetPosX()==x+size-width-3&&glyph.GetPosY()==y+3,"SetPos lock geometry");
            const auto previous=glyph.GetPosX();icon.SetSize(size+4,size+4);check(glyph.GetPosX()==previous,"Size alone leaves lock position");
            icon.SetLock455(0);check(glyph.GetPosX()==x+size+4-width-3&&glyph.GetPosY()==y+3,"setter repositions even when hidden");++geometry;
        }
        icon.Show(TRUE);icon.SetSize(64,64);icon.SetPos(64,96);icon.SetNum(1);icon.SetLock455(255);
        CGUIItem copied;copied.SetPos(200,96);copied.SetData(&icon);copied.Show(TRUE);
        check(copied.LockGlyph455().IsShow()==255&&copied.LockGlyph455().GetSpriteInfo()->pSprite==sprite,"SetData copies descriptor and rawShow");
        check(copied.GetPosX()==200&&copied.LockGlyph455().GetPosX()==200+64-width-3,"copy reapplies destination position");
        CLinkBoard linker;linker.Create(6,5,10);for(BYTE bank=0;bank<5;++bank)check(linker.AddPack(bank),"actual packs");
        auto* linked=linker.LinkerIcon455(0,0);linked->SetPos(344,96);payload->header().flag21=128;
        check(linker.Add(0,0,&original)&&linked->LockGlyph455().IsShow()==1&&links.linkCount()==1,"ordinary Add accepts and refreshes real flag21 lock");linked->Show(TRUE);
        icon.SetLock455(0);copied.SetLock455(0);linker.GetObject(0,0)->GetItem455()->header().flag21=0;linker.GetObject(0,0)->RefreshLock455();
        capture([&](){icon.Draw();copied.Draw();linked->Draw();},"lock-off.bgra");
        payload->header().flag21=255;original.RefreshLock455();linker.GetObject(0,0)->RefreshLock455();copied.SetLock455(255);
        capture([&](){icon.Draw();copied.Draw();linked->Draw();},"lock-on.bgra");
        RECT partial={64,96,68,100};capture([&](){check(icon.Draw(partial)!=FALSE,"partial clip returns outer success");},"lock-partial-clip.bgra");
        RECT outside={0,0,1,1};capture([&](){check(icon.Draw(outside)!=FALSE,"lock normalDraw survives image clip rejection");},"lock-outside-clip.bgra");
        icon.SetEmpty();check(glyph.IsShow()==1,"Empty preserves lock child visibility");
        capture([&](){icon.Draw();copied.Draw();linked->Draw();},"lock-empty.bgra");
        check(linker.Remove(0,0)&&!links.linkCount()&&linked->LockGlyph455().IsShow()==1,"Remove preserves child state while detaching icon");
        capture([&](){icon.Draw();copied.Draw();linked->Draw();},"lock-removed.bgra");
        original.Clear();check(runtime.manager.size()==0,"last payload owner released");
    }
    check(direct==256&&normalized==256&&geometry==18,"coverage");links.clear();gSpriteMgr.UnloadTargetSprites455();
    check(GetDmallocSize()==baseline,"sprite allocations balanced");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"direct_BYTE_cases\":%u,\"wrapper_flag21_cases\":%u,\"geometry_cases\":%u,\"GPU_frames\":6,\"actual_EDF_inventory_owner\":true,\"actual_Linker_Add_Remove\":true,\"copy_descriptor_rawShow\":true,\"empty_preserves_lock\":true,\"clipped_route_lock_unclipped\":true,\"all_owners_released\":true,\"sprite_allocator_balanced\":true,\"full_drag_handlers\":false,\"full_client\":false}\n",direct,normalized,geometry);
    std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Item lock:%s\n",e.what());return 1;}}
