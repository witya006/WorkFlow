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


#include "client455_board_hover.h"
#include <vector>
static DWORD now=100,clocks=0;
static DWORD clock455(){++clocks;return now;}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct Boards{using Type=CBaseBoard* (CBoardManager::*)[MAX_BOARD_TYPE];friend Type access(Boards);};
template struct MemberAccess<Boards,&CBoardManager::m_listBoard>;
struct TooltipCount{using Type=BYTE CGUIScreen::*;friend Type access(TooltipCount);};
template struct MemberAccess<TooltipCount,&CGUIScreen::m_byTooltipStringNum>;
struct NetworkMember{using Type=CNetworkMgr CMainApp::*;friend Type access(NetworkMember);};
template struct MemberAccess<NetworkMember,&CMainApp::m_cNetworkMgr>;
struct NetworkScope{CNetworkMgr& network=g_MainApp.*access(NetworkMember{});NetworkScope(){check(network.Create()!=0,"actual network owner initialization");}~NetworkScope(){network.Destroy();}};
struct PickObserver:CGUIWindow{std::vector<BOOL> events;void PickingObjectEvent(BOOL value)override{events.push_back(value);}};
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    auto& runtime=RF455_GameItems();auto& links=RF455_GameIconLinks();links.clear();
    check(!_GetAvatar(),"actual null-avatar branch;live cancellation not admitted");
    check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"real inputs");
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();
    GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");NetworkScope network;const auto baseline=GetDmallocSize();
    auto oldClock=RF455_SetGuiInputClock(clock455);gScreen.SetSize(1024,768);gScreen.RemoveTooltip();
    unsigned routes=0,refusals=0,kinds=0;
    for(unsigned id=0;id<256;++id){const bool expected=id<=15||id==0x23||id==0x24||id==0x26||id==0x27;
        check(RF455_ForwardsBoardAdd455(BYTE(id))==expected,"BYTE board-forward domain");++routes;}
    {
        FILE* input=std::fopen("metadata-samples.bin","rb");check(input!=nullptr,"sample");char magic[4];unsigned count,row[3];
        check(std::fread(magic,1,4,input)==4&&!std::memcmp(magic,"MS94",4)&&std::fread(&count,4,1,input)==1&&count==16&&std::fread(row,4,3,input)==3,"real sample extent");std::fclose(input);
        CGUIInventoryBoard inventory;CBoardObject original;original.SetItem455(runtime.create(row[0],row[1],row[2]));
        auto* payload=original.GetItem455();check(payload&&inventory.TakeInItem455(0,&original,0),"actual EDF source owner");
        auto* icon=original.GetIcon();icon->SetPos(64,96);icon->Show(TRUE);icon->SetNum(1);payload->header().flag21=255;original.RefreshLock455();
        {
            CBoardObject copied;copied.Copy455(nullptr);check(copied.IsEmpty()&&!copied.GetItem455(),"null Copy no-op");
            const auto refs=payload->header().references;copied.Copy455(&original);
            check(payload->header().references==refs+1&&!std::memcmp(&copied,&original,620),"full620 copy including padding andone retain");
            copied.Copy455(&original);check(payload->header().references==refs+1&&!std::memcmp(&copied,&original,620),"overwrite clears then retains");
            copied.Copy455(&copied);check(copied.IsEmpty()&&!copied.GetItem455()&&!copied.GetIcon()&&payload->header().references==refs,"selfcopy observescleared source");
        }
        check(payload->header().references==1,"copy destructor releases retain");
        PickObserver observer;observer.Show(FALSE);gScreen.Add(&observer);
        auto* cursor=gScreen.GetMouse();auto* mouseSprite=gSpriteMgr.GetTargetSprite455(0);check(mouseSprite!=nullptr,"actual mouse sprite");
        SPRITE_INFO mouseInfo={mouseSprite,0,0};cursor->SetSpriteInfo(&mouseInfo);cursor->SetSize(mouseSprite->GetSpriteOrgXL(0,0),mouseSprite->GetSpriteOrgYL(0,0));cursor->SetPos(300,150);cursor->Show(TRUE);
        capture([&](){icon->Draw();gScreen.Draw();},"hover-idle.bgra");
        {
            CBoardManager manager;check(manager.GetOrgBoardType()==255&&manager.GetTarBoardType()==255&&manager.GetOrgPackNo()==0,"ctor partial IDs");
            check(manager.PreviousHover455()->IsEmpty()&&!manager.OperationObject455()&&!manager.GetHoverObject(),"distinct empty backups");
            manager.SetOperationObject455(&original);check(!manager.HaveHoverObject()&&manager.GetHoverObject()==manager.OperationObject455()&&payload->header().references==2,"operation fallback without live hover");
            gScreen.*access(TooltipCount{})=1;
            now=100;icon->BeginDelayAnimation455(1000);clocks=0;
            auto* hovered=manager.SetHoverObject(&original);check(hovered&&hovered!=&original&&hovered->GetItem455()==payload&&hovered->GetIcon()==gScreen.GetObject(),"actual clone andscreen handoff");
            check(payload->header().references==3&&manager.GetHoverObject()==hovered&&manager.HaveHoverObject(),"livehover takesprecedence overoperation");
            check(gScreen.ExistObject()&&gScreen.GetObject()->IsShow()&&!cursor->IsShow()&&!(gScreen.*access(TooltipCount{}))&&observer.events==std::vector<BOOL>{TRUE},"screen visibility/tooltip/picking");
            check(gScreen.GetObject()->GetPosX()==284&&gScreen.GetObject()->GetPosY()==134&&gScreen.GetObject()->GetSizeX()==64,"centerbefore64resize");
            check(gScreen.GetObject()->LockGlyph455().IsShow()==255,"hover usesrawflag21 ratherthanwrappernormalized1");
            capture([&](){icon->Draw();gScreen.Draw();},"hover-picked.bgra");
            now=600;clocks=0;gScreen.Update();check(clocks==0,"screen doesnot doubleupdate catched timer");manager.FrameMove();
            check(clocks==1&&gScreen.GetObject()->Timer455().State455().remaining==500,"ordinary manager FrameMove updates hovericon");
            capture([&](){icon->Draw();gScreen.Draw();},"hover-updated.bgra");
            hovered=manager.SetHoverObject(&original);
            check(payload->header().references==3&&manager.PreviousHover455()->IsEmpty()&&observer.events==std::vector<BOOL>({TRUE,FALSE,TRUE}),"replacement releasesold beforecopy withoutpreviousbackup");
            bool refused=false;try{manager.GetHoverItem();}catch(const std::logic_error&){refused=true;}check(refused,"mixed legacypayload getter explicitrefusal");++refusals;
            CBoardItem legacy;refused=false;try{manager.SetHoverObject(&legacy);}catch(const std::logic_error&){refused=true;}check(refused&&manager.GetHoverObject()==hovered,"mixed replacement refusal preservescurrent");++refusals;
            capture([&](){icon->Draw();gScreen.Draw();},"hover-replaced.bgra");
            manager.SetOperationType(IOT_SWAP);manager.SetOrgObject(6,4,9,&original);manager.SetTarObject(6,0,1,nullptr);manager.ClearOperation();
            check(!manager.HaveHoverObject()&&!manager.GetHoverObject()&&!manager.OperationObject455()&&manager.PreviousHover455()->GetItem455()==payload&&payload->header().references==2,"nullhover previouscopy andoperationclear");
            check(manager.GetOrgBoardType()==255&&manager.GetTarBoardType()==255&&manager.GetOrgPackNo()==255&&manager.GetTarPackNo()==255&&manager.GetOrgSocketNo()==255&&manager.GetTarSocketNo()==255&&!manager.GetOrgObject()&&!manager.GetTarObject()&&manager.GetOperationType()==IOT_SWAP,"ClearOperation partialwrites");
            check(!gScreen.ExistObject()&&!gScreen.GetObject()->IsShow()&&cursor->IsShow()&&observer.events==std::vector<BOOL>({TRUE,FALSE,TRUE,FALSE}),"remove screen/cursor/notification");
            capture([&](){icon->Draw();gScreen.Draw();},"hover-cleared.bgra");
            auto* linker=new CLinkBoard;(manager.*access(Boards{}))[6]=linker;
            linker->Create(6,5,10);for(BYTE bank=0;bank<5;++bank)check(linker->AddPack(bank),"actual destination packs");
            linker->InitWindow(60,0,0);linker->LinkerWindow455().SetPos(64,300);linker->LinkerWindow455().Show(TRUE);gScreen.Add(&linker->LinkerWindow455());
            manager.SetOperationObject455(&original);manager.SetOrgObject(6,0,0,nullptr);manager.ReturnHoverObject();
            check(linker->GetObject(0,0)&&linker->GetObject(0,0)->GetItem455()==payload&&links.linkCount()==1,"ordinary ReturnHover forwardsoperationbackup toactualLinker");
            check(!manager.AddObject(6,0,1,manager.GetHoverObject())&&linker->GetObject(0,1)&&links.linkCount()==2,"AddObject returns0 afterreal successfulforward");
            (manager.*access(Boards{}))[1]=new CEquipBoard;
            check(manager.GetBoard(2)==manager.GetBoard(1)&&!manager.AddObject(2,0,0,manager.GetHoverObject()),"forward usesrawboard2slot,notGetBoard equipalias");
            capture([&](){icon->Draw();gScreen.Draw();},"hover-returned.bgra");
            gScreen.Remove(&linker->LinkerWindow455());manager.ClearOperation();manager.ClearHoverBackups455();
        }
        check(payload->header().references==1&&!links.linkCount(),"manager dtor releasesboards andbothbackups");
        gScreen.Remove(&observer);cursor->SetSpriteInfo(nullptr);original.Clear();check(runtime.manager.size()==0,"lastactualpayloadreleased");
        {
            CBoardManager manager;
            for(BYTE kind=0;kind<5;++kind){
                CBoardObject source;CGUIItem cpuIcon;
                auto* item=kind==1?runtime.create(1,1,0):runtime.create(kind,BYTE(row[1]),row[2]);
                check(item!=nullptr,"actual payload forkind size/lifetime case");source.SetItem455(item);cpuIcon.SetData(icon);source.SetIcon(&cpuIcon);
                //Nonphysical cases deliberately use a synthetic CPU icon copied
                //from the real inventory view;not fullSF/Animus UI proof.
                check(manager.SetHoverObject(&source)&&gScreen.GetObject()->GetSizeX()==(kind==0||kind==3||kind==4?64:40),"actual5payload kinds select64/40");
                manager.SetHoverObject(nullptr);manager.ClearHoverBackups455();source.Clear();
                check(runtime.manager.size()==0,"allkind source/hover/backups released");++kinds;
            }
            CBoardObject bare;CGUIItem cpuIcon;cpuIcon.SetData(icon);bare.SetIndex(33);bare.SetIcon(&cpuIcon);
            check(manager.SetHoverObject(&bare)&&gScreen.GetObject()->GetSizeX()==40,"nullpayload wrapper selectsdefault40");
            manager.SetHoverObject(nullptr);manager.ClearHoverBackups455();bare.Clear();
        }
        bool questRefused=false;
        {auto* item=runtime.create(5,0,0xf0000000);check(item!=nullptr,"real Quest alias payload");
            CBoardObject quest;try{quest.SetItem455(item);}catch(const std::logic_error&){questRefused=true;}}
        check(questRefused&&runtime.manager.size()==0,"Quest sentence provider stillrefuses withoutownerleak");
        CGUIItem empty;empty.SetObjectIndex455(33);empty.SetSize(33,35);cursor->SetPos(1,-1);
        gScreen.AddObject(&empty);check(gScreen.ExistObject()&&gScreen.GetObject()->GetItemID()==0&&gScreen.GetObject()->GetPosX()==-15&&gScreen.GetObject()->GetPosY()==-18,"emptyID0 andnegativehalfcentering");gScreen.RemoveObject();
    }
    check(routes==256&&refusals==2&&kinds==5,"coverage");links.clear();gSpriteMgr.UnloadTargetSprites455();
    check(GetDmallocSize()==baseline,"sprite allocations balanced");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();RF455_SetGuiInputClock(oldClock);
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"copy620\":true,\"actual_EDF_owner\":true,\"ordinary_SetHover_ClearOperation_ReturnHover\":true,\"dual_backups_operation_fallback\":true,\"replacement_release_order\":true,\"screen_notifications_cursor_tooltip\":true,\"ordinary_FrameMove_hover_update\":true,\"raw_lock_flag21\":true,\"forward_board_BYTE_cases\":%u,\"AddObject_false_after_success\":true,\"rawslot_not_equipalias\":true,\"mixed_legacy_refusals\":%u,\"item_kind_size_cases\":%u,\"nonphysical_CPU_icons_synthetic\":true,\"empty_wrapper_size_case\":true,\"Quest_name_refusal\":true,\"emptyID0_negativehalf\":true,\"GPU_frames\":6,\"actual_avatar_null\":true,\"live_avatar_cancellation\":false,\"full_operation_queue\":false,\"full_three_layer_tooltips\":false,\"all_owners_released\":true,\"sprite_allocator_balanced\":true,\"full_gameplay_handlers\":false,\"full_client\":false}\n",routes,refusals,kinds);
    std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx ownRVA=%08lx\n",info->ExceptionRecord->ExceptionCode,DWORD(info->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Board hover:%s\n",e.what());return 1;}}
