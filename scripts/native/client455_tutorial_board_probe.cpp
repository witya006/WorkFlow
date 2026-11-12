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
#include "userinterface/guicontroller/guimessagebox.h"
#include "mainapp.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_tutorial_actions.h"
#include "client455_tutorial_board.h"
#include "client455_briefing_window.h"
#include <mbctype.h>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
#include "testing/client455_tutorial_recording_host.h"
#include "testing/client455_tutorial_actions_host.h"
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,TypeName,Class,member) struct Tag{using Type=TypeName Class::*;friend Type access(Tag);};template struct MemberAccess<Tag,&Class::member>;
FIELD(SpriteMember,CSpriteMgr,CMainApp,m_cSpriteMgr)
FIELD(ScreenMember,CGUIScreen,CMainApp,m_cScreen)
FIELD(MessageText,CGUITextBoard,CGUIMessagebox,m_uiMsgBoard)
FIELD(MessageBase,CGUIObject,CGUIMessagebox,m_cBase)
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};template struct MemberAccess<Load,&CMainApp::LoadData>;
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};template struct MemberAccess<Unload,&CMainApp::UnloadData>;

struct Host final : RF455TutorialBoardHost {
    bool skip=false;std::uint32_t now=0;unsigned clocks=0,reports=0;RF455TutorialRuntime* runtime=nullptr;
    std::vector<std::string> calls;
    bool skipTutorial()override{return skip;}
    void setSkipTutorial(std::uint32_t value)override{check(value==1,"skip argument");skip=true;calls.push_back("skip");}
    std::uint32_t milliseconds()override{++clocks;return now;}
    void releaseUiCapture()override{g_pUiScreen->SetCapture455(nullptr);calls.push_back("capture");}
    void stageVirtual52()override{calls.push_back("virtual52");}
    void setStageInput(std::uint32_t value)override{check(value==1,"stage input");calls.push_back("input");}
    void setAvatarStage(std::uint8_t value)override{check(value==3&&runtime&&runtime->quests.empty(),"unload before stage3");calls.push_back("stage3");}
    void reportProgressRequested()override{++reports;}
};

static CGUIMessagebox* modal(std::uint16_t id,std::uint16_t style){
    auto* box=dynamic_cast<CGUIMessagebox*>(g_pUiScreen->GetLastDialogBox());
    check(box&&box->GetUserDefinedID()==id&&box->GetStyleID()==style&&box->IsOpen(),"actual modal id/style/open");
    check(((box->*access(MessageBase{})).GetARGB()>>24)==0xb0,"actual modal alpha");
    return box;
}
static std::string textOf(CGUIMessagebox& box){
    auto& board=box.*access(MessageText{});std::string text;
    for(unsigned index=0;index<board.GetFragmentCount455();++index)text+=board.GetFragment455(index)->GetText();
    return text;
}
static std::string languageContent(unsigned index){
    return RF455_GetNormalLanguagePack()->get(index); //455 keeps raw fragments and separate line markers.
}
static unsigned frameWidth=0,frameHeight=0;
static unsigned renderModal(CGUIMessagebox& box,const char* path){
    auto* device=GetD3dDevice();check(device!=nullptr,"D3D");
    check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");
    check(SUCCEEDED(device->BeginScene()),"begin");box.Draw();check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;
    check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    D3DVIEWPORT9 viewport={};check(SUCCEEDED(device->GetViewport(&viewport))&&viewport.Width==640&&viewport.Height==480,"viewport size");
    frameWidth=viewport.Width;frameHeight=viewport.Height;
    check(desc.Width>=640&&desc.Height>=480&&(desc.Format==D3DFMT_A8R8G8B8||desc.Format==D3DFMT_X8R8G8B8),"backbuffer format");
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");
    check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"capture");D3DLOCKED_RECT lock={};
    check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");unsigned colored=0;
    FILE* file=std::fopen(path,"wb");check(file!=nullptr,"frame output");
    for(unsigned y=viewport.Y;y<viewport.Y+viewport.Height;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+viewport.X;
        std::fwrite(row,4,viewport.Width,file);for(unsigned x=0;x<viewport.Width;++x)colored+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(file);memory->UnlockRect();memory->Release();target->Release();return colored;
}
static void hasQuest(RF455TutorialRuntime& runtime){runtime.clear();runtime.quests.resize(2);runtime.currentQuest=1;}
static void coreChecks(){
    RF455TutorialMessage message;message.texts.resize(2);message.texts[0].bytes={'A',0,'Q'};message.texts[1].bytes={'B'};
    std::array<unsigned char,1024> text; text.fill(0xa5);
    check(RF455_JoinTutorialModalText(message,text)&&text[0]=='A'&&text[1]==0&&text[2]==0&&text[3]=='B'&&text[4]==0,"mbs segment padding");
    message.texts[0].bytes.assign(1023,'X');message.texts[1].bytes.clear();
    check(RF455_JoinTutorialModalText(message,text)&&text[1022]=='X'&&text[1023]==0,"1023 payload boundary");
    const auto previous=text;message.texts[1].bytes={'Y'};
    check(!RF455_JoinTutorialModalText(message,text)&&text==previous,"1024 unsafe domain refused atomically");
    check(_setmbcp(949)==0,"mbcp");message.texts.resize(1);message.texts[0].bytes={0x81};
    check(RF455_JoinTutorialModalText(message,text)&&text[0]==0,"truncated DBCS lead follows mbsnbcpy");
    message.texts[0].bytes={0x81,0x41};check(RF455_JoinTutorialModalText(message,text)&&text[0]==0x81&&text[1]==0x41&&text[2]==0,"DBCS pair");
    auto guide=RF455_TutorialKeyGuide(0xffff);check(!guide.visible&&guide.count==0,"hide keys");
    guide=RF455_TutorialKeyGuide(0x1207);check(guide.visible&&guide.count==1&&guide.rows[0][0]==7&&guide.rows[0][1]==18,"one key row");
    guide=RF455_TutorialKeyGuide(0x0311);check(guide.count==2&&guide.rows[0][0]==3&&guide.rows[0][1]==255&&guide.rows[1][0]==17&&guide.rows[1][1]==3,"special two key rows");
    guide=RF455_TutorialKeyGuide(0xff11);check(guide.count==2&&guide.rows[0][0]==255&&guide.rows[1][1]==255,"255 in special rows preserved");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);coreChecks();
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"real language");InitR3Engine();
    GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"init D3D");
    g_pUiSpriteMgr=&(g_MainApp.*access(SpriteMember{}));g_pUiScreen=&(g_MainApp.*access(ScreenMember{}));
    check((g_MainApp.*access(Load{}))()!=0,"actual LoadData");g_pUiScreen->SetSize(640,480);
    RF455TutorialRuntime runtime;Host host;host.runtime=&runtime;RF455TutorialBoardShared shared;
    CTutorialBoard unbound(runtime,host,shared);RF455TutorialMessage message;message.texts.resize(2);
    message.texts[0].bytes={'T','u','t','o','r','i','a','l',' '};message.texts[1].bytes={'4','5','5'};
    check(!unbound.message(0,&message,0)&&!unbound.message(1,&message,0)&&!unbound.message(4,nullptr,0x311),"missing rich/key provider is not a successful no-op");
    check(unbound.message(2,&message,0),"message2");auto* box=modal(0x6000,3);check(textOf(*box)=="Tutorial 455","actual message2 text");
    const unsigned colored=renderModal(*box,"modal2.bgra");check(colored>100,"actual modal rendered");_CloseDialogBox(nullptr,0x6000);
    check(unbound.message(3,&message,0),"message3");box=modal(0x6002,4);check(textOf(*box)=="Tutorial 455","actual message3 text");_CloseDialogBox(nullptr,0x6002);
    std::unique_ptr<RF455TutorialBriefingWindow> owner(new RF455TutorialBriefingWindow);auto& view=*owner;auto& actualWindow=view.briefing();CTutorialBoard board(runtime,host,shared,&view);board.InitWindow(38,-1,-3);
    check(!actualWindow.GetAutoSize455()&&actualWindow.GetPosX()==89&&actualWindow.GetPosY()==273,"base anchor/init contract");
    actualWindow.Show(FALSE); //455Add inherits the screen's visibility.
    runtime.context.input=11;board.FrameMove();check(runtime.context.input==3,"hidden briefing sets input3");
    actualWindow.Show(TRUE);runtime.context.input=9;board.FrameMove();check(runtime.context.input==9,"visible briefing preserves input");
    check(board.message(0,&message,0)&&board.closeBlocked()&&!g_pUiScreen->GetCapture455(),"rich0 close lock");
    board.MsgProc(nullptr,0x1201,38,1);check(actualWindow.IsShow(),"locked close suppressed");
    check(board.message(1,&message,0)&&!board.closeBlocked()&&g_pUiScreen->GetCapture455()==&actualWindow,"rich1 captures real briefing");
    check(actualWindow.GetTyping455().GetFragmentCount455()==2&&std::strcmp(actualWindow.GetTitle455().GetString(),RF455_GetNormalLanguagePack()->get(445))==0,"actual title and rich fragments");
    check(board.message(4,nullptr,0x0311)&&actualWindow.GetKeys455()&&actualWindow.GetKeyFrame455().IsAddedObject(actualWindow.GetKeys455()),"actual board key widget");
    check(board.message(4,nullptr,0xffff)&&!actualWindow.GetKeyFrame455().IsAddedObject(actualWindow.GetKeys455()),"actual board hides key widget");
    board.MsgProc(nullptr,0x1201,38,0);check(actualWindow.IsShow(),"base close disabled by zero argument");
    board.MsgProc(nullptr,0x1201,38,1);check(!actualWindow.IsShow(),"ordinary close");
    board.MsgProc(nullptr,0x1202,38,1);check(actualWindow.IsShow(),"ordinary toggle");
    host.calls.clear();hasQuest(runtime);board.questRefreshed();board.requestFinish(false);
    check(!board.ready()&&host.calls.empty(),"first incomplete finish asks confirmation");box=modal(0x6001,3);
    check(textOf(*box)==languageContent(444),"real language444");_CloseDialogBox(nullptr,0x6001);
    board.MsgProc(nullptr,0x1401,38,2);check(host.calls==std::vector<std::string>({"capture","skip","virtual52","input","stage3"}),"second finish transitions even with cancel argument");
    host.calls.clear();host.skip=false;hasQuest(runtime);board.questRefreshed();shared.quitRequested=true;shared.quitCooldown=1;
    board.FrameMove();check(board.busy()&&!shared.quitRequested&&shared.quitCooldown==5,"quit prompt/cooldown");
    box=modal(0x6003,3);check(textOf(*box)==languageContent(441),"real language441");_CloseDialogBox(nullptr,0x6003);
    board.MsgProc(nullptr,0x1403,38,2);check(!board.busy()&&host.calls.empty(),"quit cancel clears busy");
    shared.quitRequested=true;for(unsigned i=0;i<4;++i)board.FrameMove();check(!board.busy()&&shared.quitRequested,"five-frame cooldown");
    board.FrameMove();check(board.busy()&&shared.quitCooldown==5,"cooldown elapsed");_CloseDialogBox(nullptr,0x6003);
    board.MsgProc(nullptr,0x1403,38,1);check(!board.busy()&&host.calls==std::vector<std::string>({"capture","skip","virtual52","input","stage3"}),"forced quit ordering");
    shared.quitCooldown=2;board.FrameMove();check(shared.quitCooldown==1,"skip still decrements cooldown");
    shared.quitCooldown=-1;board.FrameMove();check(shared.quitCooldown==-1,"signed negative cooldown retained");
    runtime.context.input=11;board.MsgProc(nullptr,0x1400,38,2);check(runtime.context.input==0,"message2 cancel maps input0");
    runtime.context.input=11;board.MsgProc(nullptr,0x1402,38,1);check(runtime.context.input==0,"message3 result maps input0");
    shared.reportClockInitialized=false;host.clocks=0;host.now=0xfffffff0;
    board.MsgProc(nullptr,0,37,0);check(host.clocks==0,"foreign window before clock");
    board.MsgProc(nullptr,0,38,0);check(host.clocks==2,"first event reads two clocks");
    host.now=std::uint32_t(0xfffffff0U+60000);board.MsgProc(nullptr,0,38,0);check(host.reports==0,"strict 60000 report boundary");
    ++host.now;board.MsgProc(nullptr,0,38,0);check(host.reports==1&&shared.reportTime==host.now,"unsigned report wrap");
    host.skip = false;
    host.now += 60000;
    board.FrameMove();
    check(host.reports == 1, "idle frame preserves the strict report boundary");
    ++host.now;
    board.FrameMove();
    board.MsgProc(nullptr, 0, 38, 0);
    check(host.reports == 2 && shared.reportTime == host.now, "idle frame reports once across both entry points");
    RF455TutorialRecordingActionsHost runtimeHost;RF455TutorialActionsFactory factory(runtimeHost);host.skip=false;
    unsigned prepared=0;
    for(const auto pair:std::vector<std::pair<BYTE,BYTE>>{{0,0},{3,1},{5,3}}){
        check(board.startScript("DataTable\\en-gb",pair.first,pair.second,factory,runtimeHost),"real race/class script selected");
        check(!runtime.quests.empty()&&runtime.currentQuest==0&&runtime.quests[0].id==0xffffffff&&runtime.quests[0].declaredCount==0&&runtime.quests[0].flags==1,"real program refreshed");++prepared;
    }
    const auto count=runtime.quests.size();host.skip=true;check(!board.startScript("missing",0,0,factory,runtimeHost)&&runtime.quests.size()==count,"skip retains script");host.skip=false;
    check(!board.startScript("missing",0,0,factory,runtimeHost)&&runtime.quests.empty()&&runtime.context.input==11,"failed load unloads old script");
    check(!board.startScript("DataTable\\en-gb",6,0,factory,runtimeHost)&&!board.startScript("DataTable\\en-gb",0,4,factory,runtimeHost),"unsafe selector table domains refused");
    g_pUiScreen->SetCapture455(nullptr);g_pUiScreen->Remove(&actualWindow);owner.reset();_CloseAllDialogBox();(g_MainApp.*access(Unload{}))();R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"board_rules\":true,\"real_modal2_and3\":true,\"real_language441_and444\":true,\"mbsnbcpy_and_bounds\":true,\"key_guide_rows\":true,\"quit_and_finish_order\":true,\"report_clock_wrap\":true,\"race_class_programs_prepared\":%u,\"modal_colored_pixels\":%u,\"frame_width\":%u,\"frame_height\":%u,\"rich_view_is_test_fixture\":false,\"production_host\":false,\"source_briefing_window\":true,\"full_Tutorial\":false}\n",prepared,colored,frameWidth,frameHeight);std::fclose(out);return 0;
}
static LONG observe(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;FILE* out=std::fopen("exception.json","wb");if(out){std::fprintf(out,"{\"code\":%lu,\"address\":%lu,\"base\":%lu}\n",info->ExceptionRecord->ExceptionCode,reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress),reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)));std::fclose(out);}return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(observe(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Tutorial board: %s\n",error.what());return 1;}}
