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
#include "client455_icon_links.h"
#include "client455_linker_owners.h"
#include "client455_item_icon_metadata.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Draw>static unsigned capture(Draw draw,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");draw();check(SUCCEEDED(device->EndScene()),"end");IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;check(std::fwrite(row,4,640,f)==640,"write");for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(f);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static void create(CLinkBoard& board){board.Create(6,5,10);for(BYTE bank=0;bank<5;++bank)check(board.AddPack(bank)!=0,"actual bank activation");}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);auto& runtime=RF455_GameItems();auto& links=RF455_GameIconLinks();links.clear();check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"actual data owner");check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");const auto baseline=GetDmallocSize();unsigned beforePixels=0,updatedPixels=0,removedPixels=0;
    FILE* file=std::fopen("metadata-samples.bin","rb");check(file!=nullptr,"sample");char magic[4];unsigned n=0,row[3];check(std::fread(magic,1,4,file)==4&&!std::memcmp(magic,"MS94",4)&&std::fread(&n,4,1,file)==1&&n==16&&std::fread(row,4,3,file)==3,"sample extent");std::fclose(file);
    {
        CGUIInventoryBoard inventory;CBoardObject original;original.SetItem455(runtime.create(static_cast<BYTE>(row[0]),static_cast<BYTE>(row[1]),row[2]));auto* payload=original.GetItem455();check(payload&&inventory.TakeInItem455(0,&original,0),"actual original payload/icon");auto* root=original.GetIcon();root->SetNum(1);root->SetUsable(TRUE);CGUIItem reference;root->SetRefItem(&reference);
        CLinkBoard board;create(board);
        for(BYTE bank=0;bank<5;++bank)for(BYTE slot=0;slot<10;++slot){
            board.LinkerIcon455(bank,slot)->SetPos(10+40*slot,50+45*bank);
            check(board.Add(bank,slot,&original)!=0,"ordinary Add invokes typed clone registration");auto* copy=board.GetObject(bank,slot);auto* icon=board.LinkerIcon455(bank,slot);
            check(copy&&copy!=&original&&copy->GetItem455()==payload&&copy->GetIcon()==icon&&icon!=root,"distinct actual wrapper/window icon owners");
            check(icon->GetOwnerContext455()==2&&icon->GetObjectIndex455()==original.GetIndex()&&icon->GetRefItem()==nullptr&&icon->m_ptSize.x==38&&icon->m_ptSize.y==38,"banked icon handoff fields");
            check(icon->m_ptPos.x==10+40*slot&&icon->m_ptPos.y==50+45*bank&&icon->m_gradeFrame455.m_ptPos.x==icon->m_ptPos.x&&icon->m_gradeFrame455.m_ptPos.y==icon->m_ptPos.y,"destination position and grade frame preserved on copy");
        }
        check(root->GetRefItem()==nullptr&&links.linkCount()==50&&payload->header().references==51,"original detached and 50 retained owners");
        check(!board.Add(0,0,&original)&&links.linkCount()==50&&payload->header().references==51,"occupied slot rejects and destroys attempted clone");check(!board.Add(5,0,&original)&&!board.Add(0,10,&original)&&!board.LinkerIcon455(5,0)&&!board.LinkerIcon455(0,10),"bank slot bounds");
        CGUIItem* icons[]={root,board.LinkerIcon455(0,0),board.LinkerIcon455(4,9)};for(unsigned i=0;i<3;++i){icons[i]->SetPos(32+130*i,40);icons[i]->SetSize(38,38);icons[i]->Show(TRUE);}
        auto draw=[&](){for(auto* icon:icons)check(icon->Draw()!=0,"actual owner icon draw");};beforePixels=capture(draw,"owners-before.bgra");root->SetNum(255);root->SetUsable(FALSE);
        for(BYTE bank=0;bank<5;++bank)for(BYTE slot=0;slot<10;++slot)check(board.LinkerIcon455(bank,slot)->m_wNum==255&&!board.LinkerIcon455(bank,slot)->IsUsable(),"all50 receive updates");updatedPixels=capture(draw,"owners-updated.bgra");
        check(board.Remove(4,9)&&links.linkCount()==49&&payload->header().references==50,"ordinary Remove unregisters and destroys clone");check(icons[2]->IsEmpty()&&icons[2]->GetObjectIndex455()==0xffffffff&&icons[2]->m_wNum==1&&icons[2]->GetGradeFrameColor455()==0,"target local icon reset");removedPixels=capture(draw,"owners-removed.bgra");
        board.LinkerIcon455(0,0)->SetNum(500);board.LinkerIcon455(0,0)->SetUsable(128);
        check(root->m_wNum==255&&!root->IsUsable()&&icons[2]->m_wNum==1,"registered initiator excludes original and removed slot");
        check(inventory.TakeOutItem(0,0),"clear original view");original.Clear();check(runtime.manager.size()==1&&payload->header().references==49,"copies retain payload after original owner released");
        for(BYTE bank=0;bank<5;++bank)for(BYTE slot=0;slot<10;++slot)if(auto* copy=board.GetObject(bank,slot))check(copy->GetItem455()==payload&&copy->GetIcon()->m_wNum==500&&copy->GetIcon()->IsUsable()==128,"retained copies valid after original release");
        board.Clear();check(!links.linkCount()&&runtime.manager.size()==0,"ordinary Clear unregisters all before deleting last shared payload");
    }
    links.clear();unsigned callbackNullCases=0,refusals=0;
    for(BYTE selector:{BYTE(0),BYTE(1),BYTE(2)}){
        // The permissive Animus factory accepts this real physical table too
        // (as covered by089);these CPU icons are explicit synthetic metadata,
        // not evidence of full SF/Animus original-window integration.
        CBoardObject original;CGUIItem icon;auto* item=selector==1?runtime.create(1,1,0):runtime.create(selector,static_cast<BYTE>(row[1]),row[2]);
        check(item!=nullptr,"actual payload for destructor case");original.SetItem455(item);icon.SetIconType455(selector==1?1:selector==2?4:0);icon.SetItemID(0x00a10001);icon.SetObjectIndex455(original.GetIndex());original.SetIcon(&icon);
        {CLinkBoard scoped;create(scoped);
            auto refuse=[&](){bool rejected=false;try{scoped.Add(4,9,&original);}catch(const std::logic_error&){rejected=true;}check(rejected&&!scoped.GetObject(4,9)&&!links.linkCount()&&item->header().references==1,"missing provider refusal leaves no owned clone/registration");++refusals;};
            if(selector==0){item->header().flag21=1;check(scoped.Add(4,9,&original)&&scoped.LinkerIcon455(4,9)->LockGlyph455().IsShow(),"actual flag21 lock provider");check(scoped.Remove(4,9),"remove locked clone");item->header().flag21=0;auto* basic=dynamic_cast<RF455BasicItem*>(item);auto* bytes=const_cast<unsigned char*>(basic->rawMetadata().data);const BYTE saved=bytes[88];bytes[88]=11;refuse();bytes[88]=saved;}
            if(selector==1){auto& state=const_cast<RF455SkillForceRecord&>(dynamic_cast<RF455SkillForceItem*>(item)->record());state.iconBoard=reinterpret_cast<void*>(1);refuse();state.iconBoard=nullptr;}
            if(selector==2){auto state=dynamic_cast<RF455BasicItem*>(item)->recordBytes();auto* bytes=const_cast<unsigned char*>(state.data);const DWORD marker=1,zero=0;std::memcpy(bytes+96,&marker,4);refuse();std::memcpy(bytes+96,&zero,4);}
            check(scoped.Add(4,9,&original)&&links.linkCount()==1&&item->header().references==2,"fresh source callback null path");}
        check(!links.linkCount()&&item->header().references==1,"derived destructor removes registration before window/base destruction");original.Clear();++callbackNullCases;
    }
    check(refusals==3&&runtime.manager.size()==0&&!links.linkCount(),"all actual owners released");links.clear();gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==baseline,"sprite allocator balance");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"ordinary_CLinkBoard_Add_Remove_Clear\":true,\"owned_clones\":50,\"banks\":5,\"slots_per_bank\":10,\"original_release_retains_copies\":true,\"occupied_clone_released\":true,\"fresh_null_callback_cases\":%u,\"explicit_missing_provider_refusals\":%u,\"SF_Animus_icons_synthetic\":true,\"actual_window_icon_owner\":true,\"registered_quantity_usable\":true,\"local_reset_after_unregister\":true,\"all_owners_released\":true,\"sprite_allocator_balanced\":true,\"GPU_frames\":3,\"before_pixels\":%u,\"updated_pixels\":%u,\"removed_pixels\":%u,\"full_Linker_window\":false,\"live_source_board_callbacks\":false,\"Macro_registration\":false,\"full_client\":false}\n",callbackNullCases,refusals,beforePixels,updatedPixels,removedPixels);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Linker owners:%s\n",e.what());return 1;}}
