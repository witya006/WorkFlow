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
#include "client455_linker_window.h"
#include "client455_image_text.h"
#include "client455_item_icon_metadata.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct QueueCreate{using Type=void(*)(WORD);friend Type access(QueueCreate);};struct QueueProcess{using Type=void(*)();friend Type access(QueueProcess);};
struct MouseSend{using Type=void(CGUIObject::*)(WORD);friend Type access(MouseSend);};template struct MemberAccess<MouseSend,&CGUIObject::SendMouseEvent>;
template struct MemberAccess<QueueCreate,&CGUIObject::CreateEventQueue>;template struct MemberAccess<QueueProcess,&CGUIObject::EventProcess>;
template<class Draw>static unsigned capture(Draw draw,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");draw();check(SUCCEEDED(device->EndScene()),"end");IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;check(std::fwrite(row,4,640,f)==640,"write");for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(f);memory->UnlockRect();memory->Release();target->Release();return pixels;
}

static FILE* fixture(const char* name,const char* magic,unsigned wanted){FILE* f=std::fopen(name,"rb");check(f!=nullptr,"fixture");char actual[4];unsigned count=0;check(std::fread(actual,1,4,f)==4&&!std::memcmp(actual,magic,4)&&std::fread(&count,4,1,f)==1&&count==wanted,"fixture header");return f;}
static void end(FILE* file){check(std::fgetc(file)==EOF,"fixture extent");std::fclose(file);}
static std::vector<MSG> messages(HWND window){std::vector<MSG> result;MSG message;while(PeekMessageW(&message,window,0x500,0x4000,PM_REMOVE))result.push_back(message);return result;}
class RecordingUse:public CGUILinkWindow455 {public:unsigned used=0;BYTE lastBank=0,lastSlot=0;BOOL UseItem455(BYTE bank,BYTE slot)override{++used;lastBank=bank;lastSlot=slot;return TRUE;}};
static void cpu(CGUILinkWindow455& window,HWND handle){
    FILE* file=fixture("window-layout.bin","LW97",21);
    for(unsigned i=0;i<21;++i){int row[18];check(std::fread(row,4,18,file)==18,"layout row");window.SetExpanded455(FALSE);
        for(BYTE bank=0;bank<5;++bank)window.Control455(6,bank)->SetPos(row[1],row[2]);window.Layout455(row[0]);check(window.GetSizeX()==row[3],"binary geometry panel width");
        for(BYTE bank=0;bank<5;++bank){auto* container=window.Control455(6,bank);check(container->GetSizeX()==row[4]&&container->GetSizeY()==row[5],"row size oracle");
            for(BYTE slot=0;slot<10;++slot){auto* icon=window.GetItem(bank,slot);check(icon->GetSizeX()==row[6]&&icon->GetSizeY()==row[6]&&icon->GetPosX()-container->GetPosX()==row[8+slot]&&icon->GetPosY()-container->GetPosY()==row[7],"1050 actual icon geometry cases including negative rounding");}}
    }end(file);window.Layout455(1024);
    file=fixture("window-cycle.bin","LC97",320);for(unsigned i=0;i<320;++i){unsigned row[4];check(std::fread(row,4,4,file)==4,"cycle row");window.SelectBank455(static_cast<BYTE>(row[0]));for(BYTE bank=0;bank<5;++bank)window.SetBankFlag455(bank,(row[1]>>bank)&1);window.CycleBank455(row[2]);check(window.HotbarState455().active==row[3],"320 sparse bank-cycle oracle cases");}end(file);
    window.SetBankFlag455(2,2);check(window.HotbarState455().bankFlags[2]==2,"raw nonboolean flag retained");window.ResetBankFlags455();window.SelectBank455(0);window.SetExpanded455(FALSE);messages(handle);
    file=fixture("window-glyphs.bin","LG97",1792);for(unsigned i=0;i<1792;++i){int row[4];check(std::fread(row,4,4,file)==4,"glyph row");check(CGUIImageText455::glyph(static_cast<BYTE>(row[0]),row[1],row[2])==row[3],"binary-mapped glyph and signed-width oracle");}end(file);
    RecordingUse input;input.SetID(101);input.Init();messages(handle);file=fixture("window-events.bin","LE97",48);
    for(unsigned i=0;i<48;++i){unsigned row[5];check(std::fread(row,4,5,file)==5,"event row");_mouse_event event={input.GetItem(4,9),static_cast<WORD>(row[0]),0,0};const auto used=input.used;input.DispatchMouse455(event,row[1]&1,row[1]&2,row[1]&4,row[1]&8);const auto sent=messages(handle);
        if(row[2]==1)check(sent.size()==1&&sent[0].message==row[3]&&sent[0].wParam==101&&static_cast<DWORD>(sent[0].lParam)==row[4]&&used==input.used,"actual PostMessage raw455 event oracle");
        else if(row[2]==2)check(sent.empty()&&input.used==used+1&&input.lastBank==4&&input.lastSlot==9,"recording Use callback,not actual gameplay");
        else check(sent.empty()&&input.used==used,"drag suppresses hover/use");
    }end(file);
    _mouse_event event={input.Control455(0),MOUSE_CLICKED,0,0};input.DispatchMouse455(event,FALSE,FALSE,FALSE,FALSE);check(input.Expanded455(),"real expand button dispatch");auto sent=messages(handle);check(sent.size()==1&&sent[0].message==0x50d,"expand message");
    event.source=input.Control455(4,4);input.DispatchMouse455(event,FALSE,FALSE,FALSE,FALSE);check(input.HotbarState455().bankFlags[4]==0,"pin button dispatch");event.source=input.Control455(5,3);event.id=MOUSE_STROKED;input.DispatchMouse455(event,FALSE,FALSE,FALSE,FALSE);check(input.HotbarState455().active==3,"bank selector dispatch");messages(handle);
    event.source=input.GetItem(4,9);event.id=MOUSE_HOVERED;input.MouseEvent(event);sent=messages(handle);check(sent.size()==1&&sent[0].message==0x501,"ordinary MouseEvent reaches actual455 queue");
    access(QueueCreate{})(100);const BOOL wasExpanded=input.Expanded455();(input.Control455(0)->*access(MouseSend{}))(MOUSE_CLICKED);access(QueueProcess{})();check(input.Expanded455()!=wasExpanded,"actual registered observer through GUI event queue");messages(handle);
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);auto& runtime=RF455_GameItems();auto& links=RF455_GameIconLinks();links.clear();check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"actual data owner");check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    HWND messageWindow=CreateWindowExA(0,"STATIC","RF455 Linker test messages",0,0,0,1,1,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);check(messageWindow!=nullptr,"owned hidden message window");const HWND oldHandle=gScreen.GetHWND();const POINT oldSize=gScreen.m_ptSize;gScreen.SetHWND(messageWindow);gScreen.SetSize(1024,768);const auto baseline=GetDmallocSize();unsigned frames=0;
    {
        CGUIInventoryBoard inventory;CBoardObject original[16];CLinkBoard board;board.Create(6,5,10);for(BYTE i=0;i<5;++i)check(board.AddPack(i),"activate banks");board.InitWindow(60,0,0);auto& window=board.LinkerWindow455();check(board.GetWindow()==&window&&window.HotbarState455().active==0&&window.GetSizeX()==481&&window.GetSizeY()==46&&window.GetPosX()==543&&window.GetPosY()==722,"ordinary InitWindow uses actual455 window and bottom-right placement");
        cpu(window,messageWindow);FILE* samples=fixture("metadata-samples.bin","MS94",16);
        for(BYTE i=0;i<16;++i){unsigned row[3];check(std::fread(row,4,3,samples)==3,"real item sample");original[i].SetItem455(runtime.create(static_cast<BYTE>(row[0]),static_cast<BYTE>(row[1]),row[2]));check(inventory.TakeInItem455(i,&original[i],0),"actual EDF-backed original");original[i].GetIcon()->SetNum(i+1);original[i].GetIcon()->SetUsable(TRUE);}end(samples);
        window.ResetBankFlags455();window.SelectBank455(0);window.SetExpanded455(FALSE);window.Layout455(1024);window.SetPos(64,300);
        for(BYTE bank=0;bank<5;++bank)for(BYTE slot=0;slot<10;++slot){unsigned index=(bank*10+slot)%16;
            // Potion11 correctly refuses until its real cooldown cache exists.
            // Keep this window fixture within the supported ownership domain.
            while(dynamic_cast<RF455BasicItem*>(original[index].GetItem455())->rawMetadata().data[88]==11)index=(index+1)%16;
            check(board.Add(bank,slot,&original[index]),"actual50 owned icon handoffs");}check(links.linkCount()==50,"actual registry members");window.Show(TRUE);
        auto draw=[&](){check(window.Draw()!=0,"ordinary CGUIWindow hierarchy draws new banked icons");};check(capture(draw,"window-collapsed.bgra")>500,"collapsed visible");++frames;
        window.SetExpanded455(TRUE);check(window.GetSizeY()==230&&window.GetPosY()==116,"expanded actual geometry");check(capture(draw,"window-expanded.bgra")>1000,"expanded visible");++frames;
        window.SelectBank455(3);check(capture(draw,"window-selected3.bgra")>1000,"bank selection visible");++frames;
        window.SetBankFlag455(1,0);window.SetBankFlag455(4,0);check(window.GetSizeY()==138,"unpinned banks removed from hierarchy");check(capture(draw,"window-pinned-subset.bgra")>500,"subset visible");++frames;
        window.Layout455(640);check(window.GetSizeX()==300&&window.GetSizeY()==84&&window.GetItem(4,9)->GetSizeX()==23,"real640 scaling applies to owners");check(capture(draw,"window-scaled640.bgra")>200,"scaled view visible");++frames;
        CGUIImageText455 glyph;glyph.Configure455(1,7,3,7,9);glyph.SetString455("1x2%+");glyph.SetPos(40,30);glyph.Show(TRUE);const float span=glyph.GetV()[1]-glyph.GetV()[0];
        check(capture([&](){check(glyph.Draw()!=0,"image text normal");},"glyph-normal.bgra")>0,"glyph pixels");++frames;RECT clip={42,32,62,37};
        check(capture([&](){check(glyph.Draw(clip)!=0,"image text clip");},"glyph-clipped.bgra")>0,"clipped glyph pixels");++frames;
        check(glyph.GetV()[0]==static_cast<float>(2.0*span/9)&&glyph.GetV()[1]==static_cast<float>(7.0*span/9),"target clip modifies persistent V span");
        check(capture([&](){check(glyph.Draw()!=0,"image text after clip");},"glyph-after-clip.bgra")>0,"persistent clip state");++frames;
        board.MsgProc(messageWindow,0x50c,60,3);check(board.GetActivePackNo()==3,"ordinary board active bank notification");board.MsgProc(messageWindow,0x50c,60,255);check(board.GetActivePackNo()==3,"invalid active bank ignored");
        board.MsgProc(messageWindow,0x50c,60,-1);check(board.GetActivePackNo()==255,"target signed JGE permits negative active-bank message");board.MsgProc(messageWindow,0x50c,60,-255);check(board.GetActivePackNo()==1,"target stores lowBYTE after signed message comparison");board.MsgProc(messageWindow,0x50c,60,3);
        bool refused=false;try{RF455_LinkerIconDelaying455(window.GetItem(0,0));}catch(const std::logic_error&){refused=true;}check(refused,"typed gameplay timer explicit gap");board.Clear();for(auto& item:original)item.Clear();check(!links.linkCount()&&runtime.manager.size()==0,"all actual icon and payload owners cleared");gScreen.Remove(&window);
    }
    links.clear();gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==baseline,"sprite allocator balance");gScreen.SetHWND(oldHandle);gScreen.SetSize(oldSize.x,oldSize.y);DestroyWindow(messageWindow);R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"layout_cases\":21,\"actual_icon_geometry\":1050,\"bank_cycle_cases\":320,\"event_cases\":48,\"glyph_cases\":1792,\"actual_Window_Init_Draw_MouseEvent\":true,\"actual_PostMessage\":true,\"Use_callback_recording\":true,\"actual_board_bank_notification\":true,\"actual_owned_icons\":50,\"real_originals\":16,\"GPU_frames\":%u,\"all_owners_released\":true,\"sprite_allocator_balanced\":true,\"typed_timer_explicit_refusal\":true,\"actual_gameplay_item_actions\":false,\"full_Linker\":false,\"full_client\":false}\n",frames);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx at ownRVA=%08lx\n",info->ExceptionRecord->ExceptionCode,DWORD(info->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Linker window:%s\n",e.what());return 1;}}
